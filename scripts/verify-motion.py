#!/usr/bin/env python3
"""덱 애니메이션 실기 검증 (design-spec 8-2).

실제 브라우저를 띄워 모션이 재생되는지, 차트 색이 팔레트와 맞는지 확인한다.
정적 검사(check-design.py)는 코드에 있는지까지만 본다.

    python3 scripts/verify-motion.py decks/w01-orientation.html
"""
import os, pathlib, sys
from playwright.sync_api import sync_playwright

DECK = "file://" + str(pathlib.Path(sys.argv[1]).resolve())
SHELL = os.environ.get("CHROME_SHELL", "/usr/lib64/chromium-browser/headless_shell")

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=SHELL, args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    pg.goto(DECK)
    pg.wait_for_timeout(300)

    print("=== 1) 등장 계단 — 슬라이드 진입 직후 실행 중인 애니메이션 수 ===")
    pg.keyboard.press("ArrowRight")   # 2번 장(흐름 칩)으로
    pg.wait_for_timeout(120)          # 전환 직후
    n = pg.evaluate("document.getAnimations().filter(a=>a.playState==='running').length")
    print(f"   진입 120ms 시점 실행 중: {n}개")

    print("=== 2) 막대 성장 — 11번 장 fragment 열기 전/중/후 폭 ===")
    pg.evaluate("location.hash='#11'"); pg.reload(); pg.wait_for_timeout(400)
    # fragment 2개 열면 bars 등장
    pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(80)
    pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(100)   # bars fragment on, 애니메이션 초반
    w_early = pg.evaluate("""(()=>{const i=document.querySelector('.slide.on .bar.c2 .track i');
        const r=i.getBoundingClientRect(); const m=getComputedStyle(i).transform; return {w:r.width,m};})()""")
    pg.wait_for_timeout(1400)                                    # 애니메이션 종료 후
    w_late = pg.evaluate("""(()=>{const i=document.querySelector('.slide.on .bar.c2 .track i');
        const r=i.getBoundingClientRect(); const m=getComputedStyle(i).transform; return {w:r.width,m};})()""")
    print(f"   100ms 시점 transform: {w_early['m'][:40]}")
    print(f"   1.5s  시점 transform: {w_late['m'][:40]}")
    grew = w_early["m"] != w_late["m"] or "matrix" in w_early["m"]
    print(f"   → 막대가 자랐는가: {'예' if grew else '아니오'}")

    print("=== 3) 막대 색 — c2 채움색 ===")
    c = pg.evaluate("getComputedStyle(document.querySelector('.slide.on .bar.c2 .track i')).backgroundColor")
    print(f"   c2 = {c}  (기대: rgb(46, 184, 138) = #2eb88a)")
    c1 = pg.evaluate("getComputedStyle(document.querySelector('.slide.on .bar:not(.c2) .track i')).backgroundColor")
    print(f"   c1 = {c1}  (기대: rgb(38, 98, 217) = #2662d9)")

    print("=== 4) 카운트업 — 3번 장 fragment 연 뒤 숫자 변화 ===")
    pg.evaluate("location.hash='#3'"); pg.reload(); pg.wait_for_timeout(400)
    pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(50)
    pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(120)   # 카드 fragment on, 카운트 초반
    v1 = pg.evaluate("document.querySelector('.slide.on [data-count=\"3\"]').textContent")
    pg.wait_for_timeout(1200)
    v2 = pg.evaluate("document.querySelector('.slide.on [data-count=\"3\"]').textContent")
    print(f"   120ms: '{v1}' → 1.3s: '{v2}'  (중간값→최종값이면 카운트업 동작)")

    print("=== 5) 글로우 이동 ===")
    g1 = pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--gx')")
    pg.keyboard.press("End"); pg.wait_for_timeout(1000)
    g2 = pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--gx')")
    print(f"   3번 장 --gx={g1.strip()} → 마지막 장 --gx={g2.strip()}")

    b.close()
print("검증 완료")
