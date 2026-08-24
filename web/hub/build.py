#!/usr/bin/env python3
"""index.src.html → index.html — Paperlogy 임베드 (외부 요청 0 원칙)

관제탑은 텍스트가 JS로 동적 생성되므로 curriculum/build-html.py 처럼
"보이는 글자만 서브셋" 하는 방식을 쓸 수 없다. 한글 음절 전체를 넣는데,
Paperlogy Regular 기준 woff2 135KB 라 그대로 임베드해도 부담이 없다.

웨이트는 400 하나만 쓴다 (DESIGN.md — 볼드 금지).

사용: python3 web/hub/build.py
"""
import base64, os, pathlib, sys, tempfile
from fontTools.subset import main as subset_main

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
FONT = pathlib.Path(os.environ.get(
    "PAPERLOGY_DIR", REPO / "curriculum" / "fonts")) / "Paperlogy-4Regular.ttf"

# 라틴 + 문장부호 + 통화 + 화살표 + 수학기호 + 괘선 + 한글(음절/자모)
UNICODES = ("U+0020-007E,U+00A0-00FF,U+2000-206F,U+20A0-20BF,U+2190-21FF,"
            "U+2200-22FF,U+2500-257F,U+25A0-25FF,U+2600-26FF,"
            "U+AC00-D7A3,U+3130-318F,U+1100-11FF")

def main():
    if not FONT.exists():
        sys.exit(f"폰트 없음: {FONT}\n  PAPERLOGY_DIR 환경변수로 경로를 지정하세요.")

    with tempfile.TemporaryDirectory() as tmp:
        out = pathlib.Path(tmp) / "pl.woff2"
        subset_main([str(FONT), f"--output-file={out}", "--flavor=woff2",
                     f"--unicodes={UNICODES}", "--layout-features=*",
                     "--no-hinting", "--desubroutinize"])
        b64 = base64.b64encode(out.read_bytes()).decode()
        kb = round(out.stat().st_size / 1024)

    face = ("@font-face{font-family:Paperlogy;font-style:normal;font-weight:400;"
            f"font-display:swap;src:url(data:font/woff2;base64,{b64}) format('woff2')}}")

    src = (HERE / "index.src.html").read_text(encoding="utf-8")
    if "__FONT__" not in src:
        sys.exit("index.src.html 에 __FONT__ 자리표시자가 없습니다.")
    (HERE / "index.html").write_text(src.replace("__FONT__", face), encoding="utf-8")
    print(f"index.html 생성 — 폰트 {kb}KB 임베드")

if __name__ == "__main__":
    main()
