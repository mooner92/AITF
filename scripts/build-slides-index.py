#!/usr/bin/env python3
"""발표자료 모음 페이지 생성 — /srv/slides/index.html

/srv/slides/wNN/*.html 을 스캔해 주차별 카드 목차를 만든다.
주차 제목은 /srv/hub/weeks.json(정본: curriculum/detailed-plan.md)에서 가져온다.

공개 페이지다 (Cloudflare Access /slides Bypass) — 학부모·원장님이 본다.
학생 개인정보 없음: 발표자료 파일 자체가 PII 없는 수업 자료다.

새 주차 발표자료 배포 절차:
    sudo cp decks/wNN-*.html /srv/slides/wNN/<이름>.html
    sudo scripts/build-slides-index.py
"""
import html
import json
import re
from pathlib import Path

SLIDES = Path("/srv/slides")
WEEKS_JSON = Path("/srv/hub/weeks.json")
LABEL = {"orientation": "수업 발표자료", "terminal": "터미널 명령어 정리",
         "slack-manual": "Slack 사용법"}


def week_titles():
    try:
        d = json.loads(WEEKS_JSON.read_text(encoding="utf-8"))
        return {w["week"]: re.sub(r"\s*\(.*진행 기록\)\s*", "", w["title"])
                for w in d["weeks"]}
    except Exception:
        return {}


def main():
    titles = week_titles()
    cards = []
    for d in sorted(SLIDES.glob("w[0-9][0-9]")):
        n = int(d.name[1:])
        files = sorted(d.glob("*.html"))
        if not files:
            continue
        links = "".join(
            f'<a href="{d.name}/{f.name}">{html.escape(LABEL.get(f.stem, f.stem))}'
            f'<span aria-hidden="true">→</span></a>'
            for f in files)
        title = html.escape(titles.get(n, ""))
        cards.append(
            f'<article><header><span class="wk">{n}주차</span>'
            f'<h2>{title or f"{n}주차 수업"}</h2></header>'
            f'<nav>{links}</nav></article>')

    body = "\n".join(cards) if cards else "<p class='empty'>아직 올라온 발표자료가 없어요.</p>"
    out = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AITF 발표자료</title>
<style>
  :root{{--bg:#0a0a0a;--card:#161618;--line:#26282c;--ink:#f5f6f8;--mute:#9aa0a8;--accent:#3b9eff}}
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{background:var(--bg);color:var(--ink);
    font:400 16px/1.6 "Apple SD Gothic Neo","Malgun Gothic",-apple-system,sans-serif;
    padding:clamp(24px,6vw,72px) 20px}}
  main{{max-width:680px;margin:0 auto}}
  h1{{font-size:clamp(28px,5vw,40px);font-weight:800;letter-spacing:-.02em;margin-bottom:6px}}
  .lede{{color:var(--mute);margin-bottom:40px;font-size:15px}}
  article{{background:var(--card);border:1px solid var(--line);border-radius:14px;
    padding:22px 24px;margin-bottom:14px}}
  header{{display:flex;align-items:baseline;gap:14px;margin-bottom:14px}}
  .wk{{color:var(--accent);font-weight:700;font-size:14px;white-space:nowrap}}
  h2{{font-size:18px;font-weight:700}}
  nav{{display:flex;flex-direction:column;gap:8px}}
  nav a{{display:flex;justify-content:space-between;align-items:center;
    padding:12px 16px;border:1px solid var(--line);border-radius:10px;
    color:var(--ink);text-decoration:none;font-size:15px;transition:border-color .15s}}
  nav a:hover{{border-color:var(--accent)}}
  nav a span{{color:var(--mute)}}
  .empty{{color:var(--mute)}}
  footer{{margin-top:44px;color:var(--mute);font-size:13px}}
</style>
</head>
<body>
<main>
  <h1>AITF 발표자료</h1>
  <p class="lede">매주 수업에서 쓴 슬라이드를 모아두는 곳이에요. 슬라이드는 ← → 키로 넘겨요.</p>
  {body}
  <footer>AITF · AI 코딩 특강 — 매주 수업 후 업데이트됩니다</footer>
</main>
</body>
</html>
"""
    (SLIDES / "index.html").write_text(out, encoding="utf-8")
    print(f"index.html 생성 — {len(cards)}주차")


if __name__ == "__main__":
    main()
