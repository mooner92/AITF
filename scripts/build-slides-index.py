#!/usr/bin/env python3
"""수업자료 모음 페이지 생성 — /srv/slides/index.html

/srv/slides/wNN/*.html 을 스캔해 주차별 카드 목차를 만든다.
주차 제목은 /srv/hub/weeks.json(정본: curriculum/detailed-plan.md)에서 가져온다.

공개 페이지다 (Cloudflare Access /slides Bypass) — 학부모·원장님이 본다.
학생 개인정보 없음: 수업자료 파일 자체가 PII 없는 수업 자료다.

새 주차 수업자료 배포 절차:
    sudo cp decks/wNN-*.html /srv/slides/wNN/<이름>.html
    sudo scripts/build-slides-index.py
"""
import html
import json
import re
from pathlib import Path

SLIDES = Path("/srv/slides")
WEEKS_JSON = Path("/srv/hub/weeks.json")
LABEL = {"orientation": "수업자료", "terminal": "터미널 명령어 정리",
         "slack-manual": "Slack 사용법 (참고용)", "slack": "Slack 사용법 (슬라이드)"}


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
        files = sorted(f for f in d.glob("*.html")
                       if not f.name.endswith(".embed.html"))
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

    body = "\n".join(cards) if cards else "<p class='empty'>아직 올라온 수업자료가 없어요.</p>"
    out = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AITF 수업자료</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgdmlld0JveD0iMCAwIDEwMCAxMDAiIHJvbGU9ImltZyIgYXJpYS1sYWJlbD0iQUlURiI+PHRpdGxlPkFJVEY8L3RpdGxlPgogIDxkZWZzPjxsaW5lYXJHcmFkaWVudCBpZD0iZyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSI4IiB5MT0iNiIgeDI9IjkyIiB5Mj0iOTQiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAiIHN0b3AtY29sb3I9IiMzYjllZmYiPjwvc3RvcD48c3RvcCBvZmZzZXQ9Ii41IiBzdG9wLWNvbG9yPSIjMDA3NWZmIj48L3N0b3A+CiAgICAgIDxzdG9wIG9mZnNldD0iMSIgc3RvcC1jb2xvcj0iIzEwMTQxOCI+PC9zdG9wPgogICAgPC9saW5lYXJHcmFkaWVudD48L2RlZnM+CiAgPHBhdGggZD0iTTExLjUgNjIgNTAgMTQgODguNSA2MiIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ1cmwoI2cpIiBzdHJva2Utd2lkdGg9IjEwIiBzdHJva2UtbGluZWpvaW49Im1pdGVyIiBzdHJva2UtbGluZWNhcD0iYnV0dCI+PC9wYXRoPgogICAgPGxpbmUgeDE9IjUwIiB5MT0iMTQiIHgyPSI1MCIgeTI9Ijg4IiBzdHJva2U9InVybCgjZykiIHN0cm9rZS13aWR0aD0iMTAiIHN0cm9rZS1saW5lY2FwPSJidXR0Ij48L2xpbmU+CiAgICA8bGluZSB4MT0iMjkuNSIgeTE9IjM4IiB4Mj0iNzAuNSIgeTI9IjM4IiBzdHJva2U9InVybCgjZykiIHN0cm9rZS13aWR0aD0iMTQiIHN0cm9rZS1saW5lY2FwPSJidXR0Ij48L2xpbmU+CiAgICA8bGluZSB4MT0iNTAiIHkxPSI2MCIgeDI9IjY2IiB5Mj0iNjAiIHN0cm9rZT0idXJsKCNnKSIgc3Ryb2tlLXdpZHRoPSIxNCIgc3Ryb2tlLWxpbmVjYXA9ImJ1dHQiPjwvbGluZT4KICAgIDxsaW5lIHgxPSIzNCIgeTE9Ijg4IiB4Mj0iNjYiIHkyPSI4OCIgc3Ryb2tlPSJ1cmwoI2cpIiBzdHJva2Utd2lkdGg9IjE0IiBzdHJva2UtbGluZWNhcD0iYnV0dCI+PC9saW5lPgo8L3N2Zz4=">
<style>
  /* Mobbin 라이트 — 랜딩(web/landing)과 같은 토큰 (2026-08-31 라이트 전환) */
  :root{{--bg:#ffffff;--card:#ffffff;--soft:#f3f3f3;--line:#e0e0e0;--line-soft:#f0f0f0;
    --ink:#141414;--mute:#707070;--accent:#0075ff}}
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{background:var(--bg);color:var(--ink);
    font:400 16px/1.6 "Apple SD Gothic Neo","Malgun Gothic",-apple-system,sans-serif;
    padding:clamp(24px,6vw,72px) 20px}}
  main{{max-width:680px;margin:0 auto}}
  h1{{font-size:clamp(28px,5vw,40px);font-weight:800;letter-spacing:-.02em;margin-bottom:6px;
    display:flex;align-items:center;gap:12px}}
  h1 .mark{{display:block}}
  .brandfoot{{display:flex;align-items:center;gap:20px;margin-top:18px}}
  .brandfoot img{{display:block;height:28px;width:auto}}
  .brandfoot .sep{{width:1px;height:22px;background:var(--line)}}
  .lede{{color:var(--mute);margin-bottom:40px;font-size:15px}}
  article{{background:var(--card);border:1px solid var(--line-soft);border-radius:24px;
    padding:22px 24px;margin-bottom:14px}}
  header{{display:flex;align-items:baseline;gap:14px;margin-bottom:14px}}
  .wk{{color:var(--accent);font-weight:700;font-size:14px;white-space:nowrap}}
  h2{{font-size:18px;font-weight:700}}
  nav{{display:flex;flex-direction:column;gap:8px}}
  nav a{{display:flex;justify-content:space-between;align-items:center;
    padding:12px 16px;background:var(--soft);border:1px solid transparent;border-radius:9999px;
    color:var(--ink);text-decoration:none;font-size:15px;transition:border-color .15s}}
  nav a:hover{{border-color:var(--ink)}}
  nav a span{{color:var(--mute)}}
  .empty{{color:var(--mute)}}
  footer{{margin-top:44px;color:var(--mute);font-size:13px}}
</style>
</head>
<body>
<main>
  <h1><img class="mark" src="brand/aitf-mark-64.svg" alt="" width="34" height="34">AITF 수업자료</h1>
  <p class="lede">매주 수업에서 쓴 슬라이드를 모아두는 곳이에요. 슬라이드는 ← → 키로 넘겨요.</p>
  {body}
  <footer>AITF · AI 코딩 특강 — 매주 수업 후 업데이트됩니다
    <div class="brandfoot">
      <img src="brand/aitf-lockup-240.svg" alt="AITF">
      <span class="sep" aria-hidden="true"></span>
      <img src="brand/jr-lockup-240.png" alt="JR 아카데미">
    </div>
  </footer>
</main>
</body>
</html>
"""
    (SLIDES / "index.html").write_text(out, encoding="utf-8")
    (SLIDES / "embed.html").write_text(EMBED, encoding="utf-8")
    n_embed = write_deck_embeds()
    print(f"index.html 생성 — {len(cards)}주차 (+embed.html, 덱 래퍼 {n_embed}개)")


BASE_URL = "https://aitf.excusa.uk/slides"


def write_deck_embeds():
    """덱마다 정적 메타데이터 래퍼(wNN/<이름>.embed.html)와 oEmbed JSON을 만든다.

    노션은 임베드 블록 크기를 API 로 못 정하고, 대신 iframely 가 URL 의
    oEmbed/player 메타데이터를 읽어 크기·비율을 정한다(유튜브가 처음부터
    큰 16:9 로 나오는 경로). 쿼리 파라미터 방식(embed.html?src=)은 정적
    메타에 개별 덱 정보를 못 실어서, 덱마다 래퍼 파일을 생성한다.
    사람이 직접 열면 16:9 프레임 + 전체 화면 링크가 보인다."""
    n = 0
    oembed_dir = SLIDES / "oembed"
    oembed_dir.mkdir(exist_ok=True)
    for d in sorted(SLIDES.glob("w[0-9][0-9]")):
        for f in sorted(d.glob("*.html")):
            if f.name.endswith(".embed.html"):
                continue
            title = LABEL.get(f.stem, f.stem)
            deck_url = f"{BASE_URL}/{d.name}/{f.name}"
            oembed_name = f"{d.name}-{f.stem}.json"
            oembed_url = f"{BASE_URL}/oembed/{oembed_name}"
            (oembed_dir / oembed_name).write_text(json.dumps({
                "version": "1.0", "type": "video",
                "provider_name": "AITF",
                "title": title,
                "html": (f'<iframe src="{deck_url}" width="1280" height="720" '
                         f'frameborder="0" allowfullscreen></iframe>'),
                "width": 1280, "height": 720,
            }, ensure_ascii=False), encoding="utf-8")
            (d / f"{f.stem}.embed.html").write_text(f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="alternate" type="application/json+oembed" href="{oembed_url}" title="{html.escape(title)}">
<meta name="twitter:card" content="player">
<meta name="twitter:player" content="{deck_url}">
<meta name="twitter:player:width" content="1280">
<meta name="twitter:player:height" content="720">
<meta property="og:type" content="video.other">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:video" content="{deck_url}">
<meta property="og:video:width" content="1280">
<meta property="og:video:height" content="720">
<style>
  body{{margin:0;background:#ffffff;font:13px/1.5 "Apple SD Gothic Neo",sans-serif}}
  .frame{{width:100%;aspect-ratio:16/9;border:0;display:block;background:#000;border-radius:8px}}
  .bar{{display:flex;justify-content:flex-end;padding:6px 2px}}
  .bar a{{color:#707070;text-decoration:none}}
  .bar a:hover{{color:#141414}}
</style>
</head>
<body>
<iframe class="frame" src="{f.name}" allowfullscreen></iframe>
<div class="bar"><a href="{f.name}" target="_blank" rel="noopener">전체 화면으로 보기 ↗</a></div>
</body>
</html>
""", encoding="utf-8")
            n += 1
    return n


# Notion 임베드용 16:9 래퍼 — 노션 iframe은 높이를 우리가 못 정하므로,
# 래퍼가 자기 폭 기준 16:9 안쪽 iframe에 덱을 담고 남는 공간은 흰색으로 둔다.
# 덱은 설계된 비율 그대로 렌더되고(엔진 무수정), 여백이 노션 흰 바탕과 이어진다.
EMBED = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>수업자료</title>
<style>
  body{margin:0;background:#ffffff;font:13px/1.5 "Apple SD Gothic Neo",sans-serif}
  .frame{width:100%;aspect-ratio:16/9;border:0;display:block;background:#000;border-radius:8px}
  .bar{display:flex;justify-content:flex-end;padding:6px 2px}
  .bar a{color:#707070;text-decoration:none}
  .bar a:hover{color:#141414}
  .err{color:#707070;padding:24px;text-align:center}
</style>
</head>
<body>
<div id="root"></div>
<script>
(function(){
  var src = new URLSearchParams(location.search).get("src") || "";
  var root = document.getElementById("root");
  // 같은 폴더 구조(wNN/파일.html)만 허용 — 외부 URL 임베드 통로가 되지 않게
  if (!/^w\\d{2}\\/[A-Za-z0-9._-]+\\.html$/.test(src)) {
    root.innerHTML = '<p class="err">잘못된 주소예요.</p>';
    return;
  }
  var full = "./" + src;
  root.innerHTML =
    '<iframe class="frame" src="' + full + '" allowfullscreen></iframe>' +
    '<div class="bar"><a href="' + full + '" target="_blank" rel="noopener">전체 화면으로 보기 ↗</a></div>';
})();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
