#!/usr/bin/env python3
"""위키 발행 알림 — Slack Incoming Webhook (specs/120)

앱을 만들지 않는다. 채널마다 웹훅 URL 하나면 끝이라 개강 전에 붙일 수 있는
유일한 봇이다. 반별 채널로 각각 보낸다 — 공용 채널로 보내면 2주차 블라인드
테스트처럼 반끼리 보이면 안 되는 것이 섞인다.

설정: /opt/scripts/.env (600)
    SLACK_WEBHOOK_CLASS1=https://hooks.slack.com/services/...
    SLACK_WEBHOOK_CLASS2=https://hooks.slack.com/services/...
    BASE_DOMAIN=aitf.excusa.uk          (링크용, 없으면 hub.env 에서 읽음)

원칙:
  · 웹훅이 없으면 조용히 생략한다 — 위키는 이미 완성돼 있다
  · 계정 ID만. 실명 없음 (위키·Notion 과 동일 규칙)
  · 실패해도 종료 코드 0 — cron 체인의 뒷단이 이것 때문에 멈추지 않게

사용:
    notify-slack.py --dry-run
    notify-slack.py                 이번 주차
    notify-slack.py --week 3
"""
import argparse, json, os, re, sys, urllib.error, urllib.request
from datetime import date, datetime
from pathlib import Path

WORK = Path("/var/lib/wiki-build")
ENV = Path("/opt/scripts/.env")
TERM = os.environ.get("TERM_NAME", "2026-fall")
LABEL = {"class1": "Class 1", "class2": "Class 2"}
HOOK_KEY = {"class1": "SLACK_WEBHOOK_CLASS1", "class2": "SLACK_WEBHOOK_CLASS2"}


def load_env(path=ENV):
    cfg = {}
    if path.exists():
        for ln in path.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1)
                cfg[k.strip()] = v.strip()
    return cfg


def post(url, payload, dry):
    if dry:
        print(json.dumps(payload, ensure_ascii=False, indent=1))
        return True
    req = urllib.request.Request(url, method="POST",
                                 data=json.dumps(payload).encode())
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status == 200
    except urllib.error.HTTPError as e:
        print(f"  ! Slack {e.code}: {e.read().decode('utf-8','replace')[:200]}")
    except Exception as e:
        print(f"  ! Slack 전송 실패: {e}")
    return False


def build(cls, data, domain):
    """블록 구성. 숫자와 링크만 — 평가·비교 문구는 넣지 않는다(위키 원칙과 동일).

    **커밋 수를 앞세우지 않는다.** git 은 커리큘럼상 4주차에 배우므로 1~3주차
    커밋은 구조적으로 0건이다. 그 기간에 "커밋 0개"만 보이면 알림이 무의미해진다.
    1차 지표는 커밋과 무관하게 잡히는 것(바꾼 파일·폴더·작품)으로 두고,
    커밋은 실제로 있을 때만 덧붙인다.
    """
    week, students = data["week"], data["students"]
    commits = sum(len(s["commits"]) for s in students)
    touched = sum(len(s.get("touched", [])) for s in students)
    works = sum(s["pages"] for s in students)
    active = sum(1 for s in students
                 if s["commits"] or s.get("touched") or s["folders"])
    folders = sorted({f for s in students for f in s["folders"]})

    stat = [f"활동한 사람 {active}명"]
    if touched:
        stat.append(f"바꾼 파일 {touched}개")
    if commits:                      # 4주차부터 의미가 생긴다
        stat.append(f"커밋 {commits}개")
    if works:
        stat.append(f"작품 {works}개")

    lines = [f"*{week}주차 기록이 올라왔어요*", " · ".join(stat)]
    if folders:
        lines.append("이번 주 폴더: " + " ".join(f"`{f}`" for f in folders))
    # 한입 요약 — weeks/wNN.md 에서 결정적으로 뽑는다 (LLM 없음, 120 원칙).
    # 자기 전에 폰으로 훑는 용도라 3줄을 넘기지 않는다. 자세한 건 Notion 버튼.
    lines += digest(cls, week)

    wiki = (f"https://{domain}/git/{cls}/class-wiki-{cls}"
            if domain else "")
    blocks = [{"type": "section",
               "text": {"type": "mrkdwn", "text": "\n".join(lines)}}]
    buttons = []
    # Notion 발행본 링크 — publish-notion.py 가 남긴 파일에서 읽는다.
    # 파일이 없거나 주차가 어긋나면 조용히 생략 (알림은 위키만으로도 성립).
    notion = notion_link(cls, week)
    if notion:
        buttons.append({"type": "button",
                        "text": {"type": "plain_text", "text": "📖 이번 주 정리 (Notion)"},
                        "url": notion, "style": "primary"})
    if wiki:
        buttons.append({"type": "button",
                        "text": {"type": "plain_text", "text": "위키 열기"},
                        "url": wiki})
    if buttons:
        blocks.append({"type": "actions", "elements": buttons})
    return {"text": f"{week}주차 기록이 올라왔어요", "blocks": blocks}


def digest(cls, week):
    """weeks/wNN.md 에서 '### 소제목'(오늘 배운 것)과 '## 다음 주 예고' 첫 줄만 뽑는다."""
    f = WORK / cls / "weeks" / f"w{week:02d}.md"
    if not f.exists():
        return []
    topics, teaser_lines, in_teaser = [], [], False
    for line in f.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("### "):
            topics.append(re.sub(r"^\d+\.\s*", "", s[4:]).strip())
        elif s.startswith("## "):
            in_teaser = "다음 주" in s
        elif in_teaser:
            if not s or s.startswith("---"):   # 문단 끝
                if teaser_lines:
                    in_teaser = False
            else:
                teaser_lines.append(re.sub(r"[*`]", "", s))
    teaser = " ".join(teaser_lines)
    out = []
    if topics:
        out.append("📚 오늘 배운 것: " + " · ".join(topics[:6]))
    if teaser:
        out.append(f"🔮 다음 주: {teaser}")
    return out


NOTION_LINKS = Path("/var/lib/wiki-build/notion-links.json")


def notion_link(cls, week):
    """publish-notion.py 가 upsert 후 남기는 {cls: {week, url}} 파일에서 읽는다."""
    try:
        d = json.loads(NOTION_LINKS.read_text(encoding="utf-8"))
        e = d.get(cls, {})
        return e.get("url") if e.get("week") == week else None
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", type=int)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    cfg = load_env()
    domain = cfg.get("BASE_DOMAIN") or load_env(Path("/opt/scripts/hub.env")).get("DOMAIN", "")

    week = a.week
    if week is None:
        # build-wiki.py 와 같은 원칙 — 휴일 반영한 실제 수업일 목록을 먼저 본다.
        # scripts/term_calendar.py 참고.
        sys.path.insert(0, str(Path(__file__).parent))
        import term_calendar
        week = term_calendar.week_of()
        if week is None:
            if term_calendar.is_after_course():
                print("과정 종료일이 지났다 — 알림을 보내지 않는다")
                return 0
            hub = load_env(Path("/opt/scripts/hub.env")).get("COURSE_START", "")
            if hub:
                d0 = datetime.strptime(hub, "%Y-%m-%d").date()
                week = max(0, (date.today() - d0).days // 7 + 1)
            else:
                week = 0

    sent = 0
    for cls_dir in sorted(WORK.iterdir()) if WORK.exists() else []:
        if not cls_dir.is_dir() or cls_dir.name.startswith("_"):
            continue
        cls = cls_dir.name
        raw = cls_dir / "raw" / f"{TERM}-w{week:02d}.json"
        if not raw.exists():
            continue
        url = cfg.get(HOOK_KEY.get(cls, ""), "")
        if not url and not a.dry_run:
            print(f"  {LABEL.get(cls, cls)}: 웹훅 미설정({HOOK_KEY.get(cls)}) — 생략")
            continue
        data = json.loads(raw.read_text(encoding="utf-8"))
        if post(url, build(cls, data, domain), a.dry_run):
            print(f"  {LABEL.get(cls, cls)}: {week}주차 알림 전송")
            sent += 1
    if not sent and not a.dry_run:
        print("전송 없음 — 웹훅 미설정이거나 raw 자료 없음. 위키는 서버에 그대로 있다.")
    return 0          # 알림 실패가 뒷단을 멈추지 않게


if __name__ == "__main__":
    sys.exit(main())
