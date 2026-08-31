#!/usr/bin/env python3
"""위키 → Notion 발행 — specs/120

레퍼런스(임커밋 Stop Hook → Notion DB)를 우리 상황에 번안했다:
  · 레퍼런스의 트리거는 Claude Code Stop Hook — 우리 학생은 Codex 를 쓰고
    수업 단위가 주차이므로, **트리거는 일요일 20시 위키 cron** 이다
    (build-wiki.py 뒤에 이 스크립트가 이어 돈다).
  · 레퍼런스의 DB 속성(작업/날짜/프로젝트/세션ID)을 수업 단위로 매핑:
    제목(주차·반) / 날짜 / 반(Select) / 주차(Number) / 커밋 수 / 활동 학생 수.
    "세션ID로 같은 카드에 누적" 아이디어는 → **(반, 주차) 키로 업서트**가 대응된다.
  · 날짜별·프로젝트별 뷰는 Notion UI 에서 만든다(강사 1회 작업) —
    그룹화 기준이 되는 속성(날짜·반)을 여기서 넣어 주는 것까지가 스크립트 몫.

설계 원칙 (120 결정 유지):
  · 크론 발행은 MCP 가 아니라 REST 직결 — LLM·MCP 는 불필요한 실패 지점
  · 정본은 서버 위키(Gitea). Notion 은 읽기 좋은 발행본 — 실패해도 수업 데이터는 서버에 있다
  · 학생 이름 없이 계정 ID만 (위키와 동일 규칙)

설정: /opt/scripts/.env (600)
    NOTION_TOKEN=ntn_...           내부 통합(Internal integration) 토큰
    NOTION_PARENT_PAGE=<page_id>   DB 를 처음 만들 부모 페이지 (통합 연결 필수)
    NOTION_DB_ID=<db_id>           (자동 기록됨 — 최초 생성 후 이 파일에 추가)

사용:
    publish-notion.py --dry-run          토큰 없이 페이로드 확인
    publish-notion.py                    이번 주차 발행 (반별 1페이지 업서트)
    publish-notion.py --week 3
"""
import argparse, json, os, re, sys, urllib.error, urllib.request
from datetime import date, datetime
from pathlib import Path

WORK = Path("/var/lib/wiki-build")
ENV = Path("/opt/scripts/.env")
API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"   # 구버전이지만 안정 지원 — 2025-09 data source 개편과 무관하게 동작
TERM = os.environ.get("TERM_NAME", "2026-fall")
CLASS_LABEL = {"class1": "Class 1", "class2": "Class 2"}
# 주차 페이지 아이콘 — 반 select 색(보라/파랑)과 맞춘다. 로고가 생기면
# {"type":"external","external":{"url":"https://aitf.excusa.uk/slides/brand/…png"}}
# 형태의 커스텀 이미지 아이콘으로 교체 가능.
CLASS_ICON = {"class1": "🟣", "class2": "🔵"}


def load_env():
    cfg = {}
    if ENV.exists():
        for ln in ENV.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1)
                cfg[k.strip()] = v.strip()
    return cfg


def call(cfg, method, path, payload=None):
    req = urllib.request.Request(f"{API}{path}", method=method,
                                 data=json.dumps(payload).encode() if payload else None)
    req.add_header("Authorization", f"Bearer {cfg['NOTION_TOKEN']}")
    req.add_header("Notion-Version", NOTION_VERSION)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"Notion API {e.code}: {e.read().decode('utf-8','replace')[:300]}")


def rt(text):
    """rich_text 축약. 문자열이면 평문 세그먼트 하나, 리스트면 그대로 통과 —
    seg()가 만든 주석(굵게·색) 세그먼트 배열을 받을 수 있게 했다."""
    if isinstance(text, list):
        return text
    return [{"type": "text", "text": {"content": text[:2000]}}]


# 인라인 마크다운 → Notion 주석 세그먼트. **굵게** `코드` *기울임* 만 다룬다 —
# weeks/*.md 가 실제로 쓰는 전부다. 이전 구현은 * ` 를 그냥 지워버려서
# 위키에 적힌 강조가 Notion 에서 전부 민짜 텍스트가 됐다 (2026-08-31 피드백).
_INLINE = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\*[^*]+\*)")


def seg(text, base=None):
    """문자열 → 주석 달린 rich_text 세그먼트 배열."""
    out = []
    for part in _INLINE.split(text):
        if not part:
            continue
        ann = dict(base or {})
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            part, ann["bold"] = part[2:-2], True
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            part, ann["code"] = part[1:-1], True
            ann.setdefault("color", "red")      # 템플릿들처럼 코드는 붉은 강조
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            part, ann["italic"] = part[1:-1], True
        item = {"type": "text", "text": {"content": part[:2000]}}
        if ann:
            item["annotations"] = ann
        out.append(item)
    return out or [{"type": "text", "text": {"content": ""}}]


PLACEHOLDER = "(아직 기록 없음)"


def prose_of(path: Path, heading: str) -> str:
    """엔티티 페이지에서 **마커 밖 서술**만 꺼낸다.

    마커 안(<!-- auto:… -->)은 build-wiki.py 가 매주 덮어쓰는 사실이고,
    밖은 사람·LLM 이 쓴 서술이다. Notion 에는 서술을 싣는다 —
    **LLM 은 git 으로 검토 가능한 위키 파일에 쓰고, 이 스크립트는 운반만 한다**
    (발행 경로에 모델을 두지 않는다는 120·180 원칙).
    """
    if not path.exists():
        return ""
    m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |^<!-- auto:|\Z)",
                  path.read_text(encoding="utf-8"), re.S | re.M)
    if not m:
        return ""
    body = m.group(1).strip()
    return "" if (not body or PLACEHOLDER in body) else re.sub(r"\s+", " ", body)


def new_this_week(cls_dir: Path, week: int):
    """이번 주에 처음 등장한 스킬·프로젝트 (지난주 raw 와 비교)."""
    def load(w):
        f = cls_dir / "raw" / f"{TERM}-w{w:02d}.json"
        if not f.exists():
            return None
        return json.loads(f.read_text(encoding="utf-8"))

    cur, prev = load(week), load(week - 1)
    if not cur:
        return [], []
    def collect(d, key):
        return {v for s in d["students"] for v in s.get(key, [])} if d else set()
    skills = sorted(collect(cur, "skills") - collect(prev, "skills"))
    projects = sorted(collect(cur, "folders") - collect(prev, "folders"))
    return skills, projects


def db_schema(cfg):
    """레퍼런스의 속성 설계를 수업 단위로 매핑한 DB."""
    return {
        "parent": {"type": "page_id", "page_id": cfg["NOTION_PARENT_PAGE"]},
        "title": rt("AITF 주간 수업 기록"),
        "properties": {
            "제목":   {"title": {}},
            "날짜":   {"date": {}},
            "반":     {"select": {"options": [
                        {"name": "Class 1", "color": "purple"},
                        {"name": "Class 2", "color": "blue"}]}},
            "주차":   {"number": {}},
            "커밋":   {"number": {}},
            "활동 학생": {"number": {}},
        },
    }


def _b(type_, **payload):
    return {"object": "block", "type": type_, type_: payload}


def _callout(text, emoji, color="gray_background"):
    return _b("callout", rich_text=rt(text),
              icon={"type": "emoji", "emoji": emoji}, color=color)


USELESS = re.compile(r"알 수 없|확인할 수 없")   # LLM 이 "모른다"고만 쓴 서술은 싣지 않는다

# 두 템플릿("과외 수업 관리"·"수업 계획 정리")에서 배운 문법:
#   · 섹션 제목은 색 글자(heading + color) 그리고 바로 아래 divider — 구획이 또렷해진다
#   · 메타·부가 정보는 회색, 강조 숫자는 굵게, 코드류는 붉은 강조
#   · 접는 토글 제목은 굵은 회색 — 본문과 급이 다름을 색으로 표시
_H_COLOR = "green"          # 수업 정리 섹션 제목색 (템플릿 A의 초록 헤딩)


def lesson_blocks(cls_dir: Path, week: int):
    """weeks/wNN.md(수업 정리)를 Notion 블록으로 변환 — 페이지의 본문이 되는 부분.

    다루는 문법만: 제목(#·##·###), 불릿, 인용(>), 표, 문단. 그 외는 문단 취급.
    인라인 **굵게** `코드` *기울임* 은 seg()가 Notion 주석으로 살린다.
    표는 Notion table 블록이 아니라 "셀1 — 셀2" 불릿으로 편다 (API table 은
    행 단위 자식 구조라 복잡한데, 우리 표는 2~3열 나열이라 불릿이 더 읽기 좋다).
    """
    f = cls_dir / "weeks" / f"w{week:02d}.md"
    if not f.exists():
        return []
    out = []
    for line in f.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("---"):
            continue
        if s.startswith("# "):          # 문서 제목은 페이지 제목과 중복 — 생략
            continue
        if s.startswith("### "):
            out.append(_b("heading_3", rich_text=seg(s[4:]), color=_H_COLOR))
        elif s.startswith("## "):
            out.append(_b("heading_2", rich_text=seg(s[3:]), color=_H_COLOR))
            out.append(_b("divider"))   # 템플릿 문법: 색 헤딩 + 바로 아래 구분선
        elif s.startswith("> "):
            out.append(_callout(seg(s[2:]), "💡", "yellow_background"))
        elif s.startswith("- "):
            out.append(_b("bulleted_list_item", rich_text=seg(s[2:])))
        elif s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if all(re.fullmatch(r":?-+:?", c) for c in cells):   # |---|---| 구분선
                continue
            cells = [c for c in cells if c]
            if not cells:
                continue
            # 첫 칸(항목명)은 굵게, 나머지는 평문 — 표의 열 구조를 굵기로 대신한다
            row = seg(f"**{cells[0]}**")
            for c in cells[1:]:
                row += seg("  —  " + c)
            out.append(_b("bulleted_list_item", rich_text=row))
        elif s.startswith("*") and s.endswith("*"):              # 이탤릭 각주
            continue
        else:
            out.append(_b("paragraph", rich_text=seg(s)))
    return out


def week_payload(cls, data, cls_dir=None):
    """raw JSON + weeks/wNN.md → Notion 페이지. 계정 ID만, 실명 없음."""
    label = CLASS_LABEL.get(cls, cls)
    week = data["week"]
    students = data["students"]
    total_commits = sum(len(s["commits"]) for s in students)
    active = sum(1 for s in students
                 if s["commits"] or s.get("touched") or s["folders"])

    props = {
        "제목": {"title": rt(f"{week}주차 — {label}")},
        "날짜": {"date": {"start": data["date"]}},
        "반":   {"select": {"name": label}},
        "주차": {"number": week},
        "커밋": {"number": total_commits},
        "활동 학생": {"number": active},
    }

    # ① 요약 콜아웃 — 페이지를 열면 제일 먼저 보이는 것. 숫자는 굵게(템플릿 문법)
    blocks = [_callout(
        seg(f"이번 주 {label} — 활동 학생 **{active}/{len(students)}명** · "
            f"커밋 **{total_commits}건**"),
        "📊", "blue_background")]

    # ② 수업 정리 (weeks/wNN.md) — 페이지의 본문
    if cls_dir:
        lesson = lesson_blocks(cls_dir, week)
        if lesson:
            blocks += lesson
            blocks.append(_b("divider"))

    # ③ 학생별 활동 — 토글 안에 접어 둔다 (요약은 콜아웃이 이미 했다)
    student_items = []
    for s in students:
        parts = []
        if s["folders"]:
            parts.append("폴더 " + " ".join(s["folders"]))
        if s.get("touched"):
            parts.append(f"바꾼 파일 {len(s['touched'])}")
        if s["commits"]:
            parts.append(f"커밋 {len(s['commits'])}")
        if s["pages"]:
            parts.append(f"작품 {s['pages']}")
        dot = "🟢" if parts else "⚪"
        # 계정 ID 는 코드체(붉은 강조), 활동 요약은 평문, 무활동은 회색
        line = seg(f"{dot} `{s['account']}`")
        if parts:
            line += seg("  " + " · ".join(parts))
        else:
            line += [{"type": "text", "text": {"content": "  이번 주 기록 없음"},
                      "annotations": {"color": "gray"}}]
        student_items.append(_b("bulleted_list_item", rich_text=line))
    blocks.append(_b("toggle",
                     rich_text=[{"type": "text",
                                 "text": {"content": f"👥 학생별 활동 ({len(students)}명)"},
                                 "annotations": {"bold": True, "color": "gray"}}],
                     children=student_items))

    # ④ 이번 주 새로 생긴 것 — 의미 있는 서술만. "모른다"뿐인 서술은 이름만 나열
    if cls_dir:
        skills, projects = new_this_week(cls_dir, week)
        entries = ([(s, cls_dir / "skills" / f"{s}.md", "뭘 하는 스킬인가") for s in skills]
                   + [(p, cls_dir / "projects" / f"{p}.md", "무엇을 만드는 폴더인가")
                      for p in projects])
        if entries:
            blocks.append(_b("heading_2", rich_text=rt("✨ 이번 주 새로 생긴 것"),
                             color="purple"))
            blocks.append(_b("divider"))
            bare = []
            for name, path, heading in entries:
                text = prose_of(path, heading)
                if text and not USELESS.search(text):
                    blocks.append(_callout(seg(f"**{name}** — {text}"), "🧩"))
                else:
                    bare.append(name)
            if bare:
                blocks.append(_b("paragraph", rich_text=(
                    seg("그 외: " + " · ".join(f"`{n}`" for n in bare))
                    + [{"type": "text",
                        "text": {"content": "  (서술은 다음 주부터 쌓여요)"},
                        "annotations": {"color": "gray", "italic": True}}])))

    # ⑤ 수업 자료 — /srv/slides/wNN/ 에 올려 둔 발표자료를 임베드.
    #    실제 열람 가능 여부는 Cloudflare Access 의 /slides Bypass 정책이 결정한다.
    blocks += slides_blocks(week)

    blocks.append(_b("paragraph", rich_text=[{
        "type": "text",
        "text": {"content": "정본은 서버 위키(Gitea)예요 · 계정 ID만 기록해요"},
        "annotations": {"italic": True, "color": "gray"}}]))
    return props, blocks


SLIDES_DIR = Path("/srv/slides")
SLIDES_BASE = os.environ.get("SLIDES_BASE_URL", "https://aitf.excusa.uk/slides")
SLIDE_LABEL = {"orientation": "이번 주 발표자료", "terminal": "터미널 명령어 정리"}


def slides_blocks(week):
    """주차 발표자료 임베드 블록. 파일이 없으면 빈 리스트 (섹션 자체 생략)."""
    d = SLIDES_DIR / f"w{week:02d}"
    if not d.is_dir():
        return []
    files = sorted(f for f in d.glob("*.html")
                   if not f.name.endswith(".embed.html"))
    if not files:
        return []
    out = [_b("heading_2", rich_text=rt("📎 수업 자료"), color="orange"),
           _b("divider")]
    for f in files:
        label = SLIDE_LABEL.get(f.stem, f.stem)
        # 덱별 메타데이터 래퍼(.embed.html) — oEmbed/player 메타로 노션이
        # 처음부터 큰 16:9 로 그리게 한다 (build-slides-index.py 가 생성).
        # v=mtime 은 엣지 캐시 무효화 — 파일을 갈아끼우면 URL이 바뀐다.
        url = (f"{SLIDES_BASE}/w{week:02d}/{f.stem}.embed.html"
               f"?v={int(f.stat().st_mtime)}")
        out.append(_b("paragraph", rich_text=seg(f"**{label}**")))
        out.append(_b("embed", url=url))
    out.append(_b("paragraph", rich_text=[{
        "type": "text",
        "text": {"content": "화면이 안 뜨면 카드를 눌러 새 창에서 열어 주세요 · 슬라이드는 ←→ 키로 넘겨요"},
        "annotations": {"color": "gray", "italic": True}}]))
    return out


def upsert(cfg, dbid, cls, data, dry, cls_dir=None):
    label = CLASS_LABEL.get(cls, cls)
    props, blocks = week_payload(cls, data, cls_dir)
    if dry:
        print(f"  [dry-run] {data['week']}주차 {label}: "
              f"블록 {len(blocks)}개, 속성 {list(props)}")
        return

    # (반, 주차) 로 기존 페이지 검색 — 레퍼런스의 "세션ID 누적"에 대응하는 업서트 키
    q = call(cfg, "POST", f"/databases/{dbid}/query", {
        "filter": {"and": [
            {"property": "주차", "number": {"equals": data["week"]}},
            {"property": "반", "select": {"equals": label}},
        ]}})
    hits = q.get("results", [])

    icon = {"type": "emoji", "emoji": CLASS_ICON.get(cls, "📝")}
    if hits:
        page = hits[0]["id"]
        page_url = hits[0].get("url", "")
        call(cfg, "PATCH", f"/pages/{page}", {"properties": props, "icon": icon})
        # 본문은 지우고 다시 쓴다 (멱등)
        kids = call(cfg, "GET", f"/blocks/{page}/children?page_size=100").get("results", [])
        for k in kids:
            call(cfg, "DELETE", f"/blocks/{k['id']}")
        call(cfg, "PATCH", f"/blocks/{page}/children", {"children": blocks})
        print(f"  갱신: {data['week']}주차 {label}")
    else:
        made = call(cfg, "POST", "/pages", {
            "parent": {"database_id": dbid}, "icon": icon,
            "properties": props, "children": blocks})
        page_url = made.get("url", "")
        print(f"  생성: {data['week']}주차 {label}")

    # 페이지 URL 을 남긴다 — notify-slack.py 등이 알림에 링크를 붙일 수 있게.
    # 실패해도 발행 자체는 성공이므로 경고만 하고 넘어간다.
    if page_url:
        try:
            links_f = WORK / "notion-links.json"
            links = json.loads(links_f.read_text(encoding="utf-8")) if links_f.exists() else {}
            links[cls] = {"week": data["week"], "url": page_url, "label": label}
            links_f.write_text(json.dumps(links, ensure_ascii=False, indent=2),
                               encoding="utf-8")
        except Exception as e:
            print(f"  ! notion-links.json 기록 실패(발행은 정상): {e}")


WEEKS_JSON = Path("/srv/hub/weeks.json")
OVERVIEW_TITLE = "🗺️ 12주 커리큘럼"


def publish_overview(cfg):
    """부모 페이지 아래 '12주 커리큘럼' 하위 페이지를 (재)작성한다.

    원장님·학부모가 이 페이지 하나로 수업 전반을 보게 하는 용도 — 주차별
    제목·만들기 목표·배우는 것을 weeks.json(정본: curriculum/detailed-plan.md)에서
    결정적으로 옮긴다. 실행할 때마다 본문을 지우고 다시 쓴다(멱등)."""
    parent = cfg.get("NOTION_PARENT_PAGE")
    if not parent or not WEEKS_JSON.exists():
        print("overview 생략 — NOTION_PARENT_PAGE 또는 weeks.json 없음")
        return
    weeks = json.loads(WEEKS_JSON.read_text(encoding="utf-8"))["weeks"]

    # 기존 하위 페이지 찾기 (부모의 child_page 블록 중 제목 일치)
    kids = call(cfg, "GET", f"/blocks/{parent}/children?page_size=100").get("results", [])
    page_id = next((k["id"] for k in kids
                    if k["type"] == "child_page"
                    and k["child_page"]["title"] == OVERVIEW_TITLE), None)
    if not page_id:
        page = call(cfg, "POST", "/pages", {
            "parent": {"page_id": parent},
            "icon": {"type": "emoji", "emoji": "🗺️"},
            "properties": {"title": {"title": rt(OVERVIEW_TITLE)}}})
        page_id = page["id"]
        print(f"커리큘럼 페이지 생성: {page_id}")
    else:
        old = call(cfg, "GET", f"/blocks/{page_id}/children?page_size=100").get("results", [])
        for k in old:
            call(cfg, "DELETE", f"/blocks/{k['id']}")

    blocks = [
        _callout(seg("**12주 동안 이렇게 갑니다** — 매주 결과물이 하나씩 나오는 실습 중심 수업이에요. "
                     "두 반(Class 1·Class 2)은 같은 내용·같은 진도로 진행합니다."),
                 "🎯", "blue_background"),
        _b("paragraph", rich_text=[]),
    ]
    for w in weeks:
        title = re.sub(r"\s*\(.*진행 기록\)\s*", "", w["title"])   # 1주차 실측 꼬리표 제거
        inner = []
        if w.get("goal"):
            inner.append(_b("paragraph", rich_text=seg(f"**만드는 것** — {w['goal']}")))
        if w.get("skill"):
            inner.append(_b("paragraph", rich_text=seg(f"**배우는 것** — {w['skill']}")))
        if w.get("tech"):
            inner.append(_b("paragraph", rich_text=[
                {"type": "text", "text": {"content": f"도구 — {w['tech']}"},
                 "annotations": {"color": "gray"}}]))
        blocks.append(_b("toggle",
                         rich_text=seg(f"**{w['week']}주 — {title}**"),
                         color="green" if w.get("tag") else "default",
                         children=inner))
    blocks.append(_b("paragraph", rich_text=[{
        "type": "text",
        "text": {"content": "주차별 실제 수업 내용은 아래 'AITF 주간 수업 기록'에서 매주 볼 수 있어요"},
        "annotations": {"italic": True, "color": "gray"}}]))

    # Notion 은 한 번에 100블록 제한 — 나눠 붙인다
    for i in range(0, len(blocks), 90):
        call(cfg, "PATCH", f"/blocks/{page_id}/children", {"children": blocks[i:i+90]})
    print(f"커리큘럼 개요 발행 — {len(weeks)}주 / 블록 {len(blocks)}개")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", type=int)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--overview", action="store_true",
                    help="부모 페이지에 12주 커리큘럼 개요 페이지를 (재)작성")
    a = ap.parse_args()

    cfg = load_env()
    if not a.dry_run and not cfg.get("NOTION_TOKEN"):
        print(f"NOTION_TOKEN 미설정({ENV}) — 발행 생략. 위키는 서버에 그대로 있다.")
        return 0

    if a.overview:
        publish_overview(cfg)
        return 0

    # 주차 결정 (build-wiki 와 동일 규칙 — scripts/term_calendar.py)
    week = a.week
    if week is None:
        import sys as _sys
        _sys.path.insert(0, str(Path(__file__).parent))
        import term_calendar
        week = term_calendar.week_of()
        if week is None:
            if term_calendar.is_after_course():
                print("과정 종료일이 지났다 — Notion 발행을 생략한다")
                return 0
            m = re.search(r"^COURSE_START=(.+)$",
                          Path("/opt/scripts/hub.env").read_text(encoding="utf-8"), re.M)
            if m and m.group(1).strip():
                d0 = datetime.strptime(m.group(1).strip(), "%Y-%m-%d").date()
                week = max(0, (date.today() - d0).days // 7 + 1)
            else:
                week = 0

    # DB 준비 (최초 1회 생성 → .env 에 기록 안내)
    dbid = cfg.get("NOTION_DB_ID", "")
    if not a.dry_run and not dbid:
        if not cfg.get("NOTION_PARENT_PAGE"):
            sys.exit("NOTION_PARENT_PAGE 미설정 — DB 를 만들 부모 페이지 ID 가 필요합니다.")
        db = call(cfg, "POST", "/databases", db_schema(cfg))
        dbid = db["id"]
        print(f"DB 생성됨: {dbid}")
        print(f"→ {ENV} 에 NOTION_DB_ID={dbid} 를 추가하세요 (다음 실행부터 재사용)")

    found = 0
    for cls_dir in sorted(WORK.iterdir()) if WORK.exists() else []:
        if not cls_dir.is_dir() or cls_dir.name.startswith("_"):
            continue
        raw = cls_dir / "raw" / f"{TERM}-w{week:02d}.json"
        if not raw.exists():
            continue
        data = json.loads(raw.read_text(encoding="utf-8"))
        upsert(cfg, dbid, cls_dir.name, data, a.dry_run, cls_dir)
        found += 1
    if not found:
        print(f"w{week:02d} raw 자료 없음 — build-wiki.py 를 먼저 실행하세요.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
