#!/usr/bin/env python3
"""HTML 문서에 Paperlogy 서브셋 폰트를 인라인 임베드한다.

원본 TTF는 9웨이트 × 664KB. 문서에 실제로 쓰인 글자만 남긴 뒤 woff2로 변환해
data URI로 넣는다 (외부 요청 0 — Artifact CSP 및 오프라인 열람 대응).

준비: Paperlogy 배포 zip을 풀어 TTF 9종을 ./fonts/ 에 둔다 (또는 PAPERLOGY_DIR 지정).
      pip install "fonttools[woff]" brotli
사용: python3 build-html.py <src.html> [<src.html> ...]
      각 파일의 __FONT_FACES__ 를 @font-face 블록으로 치환해 <name>.html 로 저장.
"""
import base64, io, os, re, sys, unicodedata
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options

FONT_DIR = Path(os.environ.get("PAPERLOGY_DIR", Path(__file__).parent / "fonts"))
WEIGHTS = {  # css weight -> 파일명
    200: "Paperlogy-2ExtraLight.ttf",
    400: "Paperlogy-4Regular.ttf",
    600: "Paperlogy-6SemiBold.ttf",
    800: "Paperlogy-8ExtraBold.ttf",
}

def visible_text(html: str) -> str:
    """스타일·스크립트를 뺀 나머지에서 화면에 나올 문자 수집."""
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)          # 태그 제거
    s = re.sub(r"&[a-zA-Z]+;|&#\d+;", " ", s)  # 엔티티 제거
    return s

def subset_woff2(ttf_path: Path, chars: set) -> bytes:
    font = TTFont(str(ttf_path))
    opts = Options()
    opts.layout_features = ["*"]
    opts.notdef_outline = True
    opts.desubroutinize = True
    sub = Subsetter(options=opts)
    sub.populate(text="".join(sorted(chars)))
    sub.subset(font)
    font.flavor = "woff2"
    buf = io.BytesIO()
    font.save(buf)
    return buf.getvalue()

def build(src: Path) -> Path:
    html = src.read_text(encoding="utf-8")

    # 문서에 실제로 등장하는 글자 + 항상 필요한 기본 문자
    chars = set(visible_text(html))
    chars |= set(
        "0123456789"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        " .,·:;!?()[]{}<>/\\|-–—_=+*&%@#'\"“”‘’…→←↑↓✓✔●○★☆⚡"
    )
    chars = {c for c in chars if not unicodedata.category(c).startswith("C")}

    faces = []
    total = 0
    for weight, fname in WEIGHTS.items():
        data = subset_woff2(FONT_DIR / fname, chars)
        total += len(data)
        b64 = base64.b64encode(data).decode()
        faces.append(
            "@font-face{font-family:Paperlogy;font-style:normal;"
            f"font-weight:{weight};font-display:swap;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}"
        )
    css = "\n".join(faces)

    out = src.with_name(src.name.replace(".src.html", ".html"))
    out.write_text(html.replace("__FONT_FACES__", css), encoding="utf-8")
    print(f"{out.name}: 글자 {len(chars)}자 · 폰트 {total/1024:.0f}KB · 문서 {out.stat().st_size/1024:.0f}KB")
    return out

if __name__ == "__main__":
    for a in sys.argv[1:]:
        build(Path(a))
