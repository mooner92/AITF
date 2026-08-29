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
CLASS_LABEL = {"mid": "중등부", "high": "고등부"}


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


def rt(text):  # rich_text 축약
    return [{"type": "text", "text": {"content": text[:2000]}}]


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
                        {"name": "중등부", "color": "blue"},
                        {"name": "고등부", "color": "purple"}]}},
            "주차":   {"number": {}},
            "커밋":   {"number": {}},
            "활동 학생": {"number": {}},
        },
    }


def week_payload(cls, data, cls_dir=None):
    """raw JSON → Notion 페이지 속성 + 본문 블록. 계정 ID만, 실명 없음."""
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

    blocks = [
        {"object": "block", "type": "heading_2",
         "heading_2": {"rich_text": rt(f"{week}주차 활동")}},
    ]
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
        line = f"{s['account']} — " + (" · ".join(parts) if parts else "활동 없음")
        blocks.append({"object": "block", "type": "bulleted_list_item",
                       "bulleted_list_item": {"rich_text": rt(line)}})
    # 이번 주 새로 생긴 스킬·프로젝트 + 위키에 쌓인 서술
    if cls_dir:
        skills, projects = new_this_week(cls_dir, week)
        entries = ([(s, cls_dir / "skills" / f"{s}.md", "뭘 하는 스킬인가") for s in skills]
                   + [(p, cls_dir / "projects" / f"{p}.md", "무엇을 만드는 폴더인가")
                      for p in projects])
        if entries:
            blocks.append({"object": "block", "type": "heading_2",
                           "heading_2": {"rich_text": rt("이번 주 새로 생긴 것")}})
            for name, path, heading in entries:
                text = prose_of(path, heading)
                blocks.append({"object": "block", "type": "paragraph",
                               "paragraph": {"rich_text": rt(
                                   f"{name} — {text}" if text else name)}})

    blocks.append({"object": "block", "type": "paragraph",
                   "paragraph": {"rich_text": rt(
                       "정본은 서버 위키(Gitea)입니다. 계정 ID만 기록합니다.")}})
    return props, blocks


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

    if hits:
        page = hits[0]["id"]
        call(cfg, "PATCH", f"/pages/{page}", {"properties": props})
        # 본문은 지우고 다시 쓴다 (멱등)
        kids = call(cfg, "GET", f"/blocks/{page}/children?page_size=100").get("results", [])
        for k in kids:
            call(cfg, "DELETE", f"/blocks/{k['id']}")
        call(cfg, "PATCH", f"/blocks/{page}/children", {"children": blocks})
        print(f"  갱신: {data['week']}주차 {label}")
    else:
        call(cfg, "POST", "/pages", {
            "parent": {"database_id": dbid},
            "properties": props, "children": blocks})
        print(f"  생성: {data['week']}주차 {label}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", type=int)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    cfg = load_env()
    if not a.dry_run and not cfg.get("NOTION_TOKEN"):
        print(f"NOTION_TOKEN 미설정({ENV}) — 발행 생략. 위키는 서버에 그대로 있다.")
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
