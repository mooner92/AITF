#!/usr/bin/env python3
"""디자인 스펙 준수 검사 (docs/design-spec.md 7절).

문서 HTML과 발표자료 HTML 모두에 쓴다. 발표자료는 모션 저감 블록을 추가로 요구한다.

    python3 scripts/check-design.py curriculum/*.html decks/*.html

종료 코드: 0 통과 / 1 위반
"""
import base64, io, re, sys
from pathlib import Path

# 문서에 실제로 쓰이는 공인 IP가 아닌 대역
PRIVATE = re.compile(r"^(127\.|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|169\.254\.|0\.0\.0\.0|255\.)")


def strip_code(h):
    return re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S | re.I)


def check(path):
    h = Path(path).read_text(encoding="utf-8")
    is_deck = "id=\"stage\"" in h or "/decks/" in str(path) or Path(path).parent.name == "decks"
    bad = []

    # 1. 플레이스홀더 잔존
    for ph in ("__FONT_FACES__", "⟪"):
        if ph in h:
            bad.append(f"치환되지 않은 자리표시자 '{ph}'")

    # 2. 폰트 임베드 + 글리프
    faces = re.findall(r"base64,([A-Za-z0-9+/=]+)\)", h)
    if len(faces) != 4:
        bad.append(f"@font-face {len(faces)}개 (4개여야 함)")
    else:
        try:
            from fontTools.ttLib import TTFont
            cmap = TTFont(io.BytesIO(base64.b64decode(faces[0]))).getBestCmap()
            body = re.sub(r"<[^>]+>", " ", strip_code(h))
            miss = {c for c in body if ("가" <= c <= "힣" or c.isalnum()) and ord(c) not in cmap}
            if miss:
                bad.append(f"글리프 누락 {len(miss)}자: {''.join(sorted(miss)[:12])}")
        except ImportError:
            pass

    # 3. body 배경 명시 — 없으면 뷰어 테마가 비쳐 글자가 사라진다
    if not re.search(r"body\s*\{[^}]*background\s*:", h, flags=re.S):
        bad.append("body에 background 미지정 (호스트 테마가 비침)")

    # 4. 미디어쿼리/[data-theme] 안에서만 정의된 색
    guarded = re.findall(r"@media[^{]*\{(.*?)\n\}", h, flags=re.S)
    root_block = "\n".join(re.findall(r":root\s*\{([^}]*)\}", h, flags=re.S))
    root_vars = set(re.findall(r"(--[\w-]+)\s*:", root_block))
    for g in guarded:
        for v in set(re.findall(r"(--[\w-]+)\s*:", g)):
            if v not in root_vars:
                bad.append(f"{v} 가 미디어쿼리 안에서만 정의됨")

    # 5. 태그 짝
    from html.parser import HTMLParser
    VOID = {"br", "img", "meta", "link", "hr", "input", "source", "track", "wbr", "col"}

    class P(HTMLParser):
        def __init__(s):
            super().__init__(convert_charrefs=True); s.st = []; s.err = 0
        def handle_starttag(s, t, a):
            if t not in VOID: s.st.append(t)
        def handle_endtag(s, t):
            if t in VOID: return
            if not s.st or s.st[-1] != t: s.err += 1; return
            s.st.pop()
    p = P(); p.feed(h)
    if p.err or p.st:
        bad.append(f"태그 불일치 {p.err}건 · 미닫힘 {p.st[:3]}")

    # 6. 외부 리소스
    ext = re.findall(r'(?:src|href)\s*=\s*"(https?:)?//[^"]+', h)
    ext = [e for e in re.findall(r'(?:src|href)\s*=\s*"((?:https?:)?//[^"]+)"', h)]
    if ext:
        bad.append(f"외부 리소스 참조 {len(ext)}건: {ext[:2]}")

    # 7. 발표자료 전용 — 모션 저감
    if is_deck and "prefers-reduced-motion" not in h:
        bad.append("prefers-reduced-motion 블록 없음 (접근성 필수)")

    # 8. 민감정보
    for ip in set(re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", strip_code(h))):
        if not PRIVATE.match(ip):
            bad.append(f"공인 IP로 보이는 값: {ip}")
    for pat, name in [(r"sk-[A-Za-z0-9_-]{20}", "OpenAI 키"),
                      (r"AIza[A-Za-z0-9_-]{30}", "Google 키"),
                      (r"ghp_[A-Za-z0-9]{30}", "GitHub 토큰")]:
        if re.search(pat, h):
            bad.append(f"{name} 패턴 감지")

    return bad


if __name__ == "__main__":
    files = sys.argv[1:]
    if not files:
        print("사용: check-design.py <파일.html> ...", file=sys.stderr); sys.exit(2)
    fail = 0
    for f in files:
        # *.src.html 은 빌드 전 원본이라 폰트가 아직 없다 — 검사 대상은 산출물이다
        if f.endswith(".src.html"):
            continue
        bad = check(f)
        if bad:
            fail = 1
            print(f"✗ {f}")
            for b in bad:
                print(f"    {b}")
        else:
            print(f"✓ {f}")
    sys.exit(fail)
