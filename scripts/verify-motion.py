#!/usr/bin/env python3
"""덱 애니메이션 실기 검증 (design-spec 8-2).

실제 브라우저를 띄워 모션이 재생되는지, 차트 색이 팔레트와 맞는지 확인한다.
정적 검사(check-design.py)는 "코드에 있는지"까지만 본다 — 재생 여부는 여기서 본다.

    python3 scripts/verify-motion.py decks/w01-orientation.html

준비:
    sudo dnf install -y oracle-epel-release-el9
    sudo dnf --enablerepo=ol9_developer_EPEL install -y chromium-headless
    pip install --user playwright
"""
import os, pathlib, sys
from playwright.sync_api import sync_playwright

DECK = "file://" + str(pathlib.Path(sys.argv[1]).resolve())
SHELL = os.environ.get("CHROME_SHELL", "/usr/lib64/chromium-browser/headless_shell")
PALETTE = {"chart-1": "rgb(38, 98, 217)", "chart-2": "rgb(46, 184, 138)"}

fails = []


def check(label, ok, detail=""):
    print(f"  {'✓' if ok else '✗'} {label}{'  ' + detail if detail else ''}")
    if not ok:
        fails.append(label)


def open_until(pg, selector, max_steps=80):
    """해당 요소가 실제로 드러날 때까지 오른쪽 키를 누른다.
    슬라이드 번호를 고정하면 장이 늘어날 때마다 깨지므로 내용으로 찾는다.
    요소가 fragment 안에 있으면 그 fragment가 열린 뒤라야 '드러났다'고 본다 —
    존재만 보면 아직 숨어 있는 요소를 붙잡고 '모션 없음'이라 오판한다."""
    probe = f"""(()=>{{
      const e = document.querySelector('.slide.on {selector}');
      if (!e) return false;
      const fr = e.closest('.fragment');
      return !fr || fr.classList.contains('on');
    }})()"""
    for _ in range(max_steps):
        if pg.evaluate(probe):
            return True
        pg.keyboard.press("ArrowRight")
        pg.wait_for_timeout(70)
    return False


def run(reduced):
    mode = "reduce" if reduced else "no-preference"
    print(f"\n── 모션 저감 {'켬' if reduced else '끔'} ({mode}) ──")
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=SHELL, args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": 1280, "height": 720}, reduced_motion=mode)
        pg.goto(DECK)
        pg.wait_for_timeout(500)

        # 1) 등장 계단
        pg.keyboard.press("ArrowRight")
        pg.wait_for_timeout(120)
        n = pg.evaluate("document.getAnimations().filter(a=>a.playState==='running').length")
        check("등장 계단", (n == 0) if reduced else (n >= 5), f"실행 중 {n}개")

        # 2) 막대 — 있으면 검사
        pg.goto(DECK); pg.wait_for_timeout(400)
        if open_until(pg, ".bar .track i"):
            pg.wait_for_timeout(60)
            early = pg.evaluate("getComputedStyle(document.querySelector('.slide.on .bar .track i')).transform")
            pg.wait_for_timeout(1800)
            late = pg.evaluate("getComputedStyle(document.querySelector('.slide.on .bar .track i')).transform")
            grew = early != late
            check("막대 성장", (not grew) if reduced else grew, f"{early[:24]} → {late[:24]}")

            for cls, want in PALETTE.items():
                sel = ".bar.c2 .track i" if cls == "chart-2" else ".bar:not(.c2) .track i"
                got = pg.evaluate(
                    f"(()=>{{const e=document.querySelector('.slide.on {sel}');"
                    f"return e?getComputedStyle(e).backgroundColor:'없음'}})()")
                if got != "없음":
                    check(f"차트 색 {cls}", got == want, f"{got}")
        else:
            print("  – 막대 없음 (건너뜀)")

        # 3) 카운트업
        pg.goto(DECK); pg.wait_for_timeout(400)
        if open_until(pg, "[data-count]"):
            pg.wait_for_timeout(100)
            v1 = pg.evaluate("document.querySelector('.slide.on [data-count]').textContent")
            pg.wait_for_timeout(1500)
            v2 = pg.evaluate("document.querySelector('.slide.on [data-count]').textContent")
            moved = v1 != v2
            check("카운트업", (not moved) if reduced else moved, f"'{v1}' → '{v2}'")
        else:
            print("  – 카운트업 없음 (건너뜀)")

        # 4) 글로우 이동 — 저감과 무관하게 위치는 바뀐다 (전환만 없어짐)
        pg.goto(DECK); pg.wait_for_timeout(400)
        g1 = pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--gx')").strip()
        pg.keyboard.press("End"); pg.wait_for_timeout(1200)
        g2 = pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--gx')").strip()
        check("글로우 이동", float(g1 or 0) < 0.1 and abs(float(g2 or 0) - 1) < .01, f"{g1} → {g2}")

        b.close()


if __name__ == "__main__":
    print(f"검증: {sys.argv[1]}")
    run(reduced=False)
    run(reduced=True)      # 저감 설정에서 실제로 멈추는지 — 접근성 대응의 실효 확인
    print()
    if fails:
        print(f"실패 {len(fails)}건: {', '.join(fails)}")
        sys.exit(1)
    print("전 항목 통과")
