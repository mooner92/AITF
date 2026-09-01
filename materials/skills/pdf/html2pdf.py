#!/usr/bin/env python3
"""HTML 발표자료 → PDF 변환 — aitf-pdf 스킬의 도구

왜 스크립트로 두는가: 발표자료 HTML 은 **현재 장만 보이고 나머지는 숨겨 두는**
구조라, 그냥 인쇄하면 1페이지만 나온다 (2026-09-01 실측: 7장짜리 → 1쪽).
인쇄용 CSS 를 끼워 모든 장을 펼친 뒤 한 장씩 페이지를 나눠야 한다.

사용:
    python3 html2pdf.py <입력.html> [출력.pdf]

동작:
    1. 원본을 건드리지 않고 임시 사본에 인쇄용 CSS 를 넣는다
    2. 헤드리스 브라우저로 인쇄한다 (16:9 페이지)
    3. 페이지 수가 슬라이드 수와 같은지 확인한다
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME = "/usr/lib64/chromium-browser/headless_shell"

# 16:9 (13.333in x 7.5in). 모든 슬라이드를 펼치고 한 장마다 페이지를 끊는다.
PRINT_CSS = """
<style id="aitf-print">
@page { size: 13.333in 7.5in; margin: 0; }
@media print {
  html, body { margin:0 !important; padding:0 !important; background:#fff !important; }
  /* 무대가 position:fixed 면 첫 쪽에만 찍힌다 — 흐름 안으로 되돌린다 */
  #stage, .stage, #deck, .deck {
    position: static !important; inset: auto !important;
    display: block !important; transform: none !important;
  }
  #glow, .glow { display: none !important; }
  .slide, section.slide, article.slide, body > section, body > article {
    display: flex !important; position: relative !important;
    width: 13.333in !important; height: 7.5in !important;
    box-sizing: border-box !important;
    page-break-after: always; break-after: page;
    page-break-inside: avoid; break-inside: avoid;
  }
  .slide:last-of-type, body > section:last-of-type, body > article:last-of-type {
    page-break-after: auto; break-after: auto;
  }
}
</style>
"""

CLASS_SLIDE_RE = re.compile(r"<\w+[^>]*class=\"[^\"]*\bslide\b", re.I)
TAG_SLIDE_RE = re.compile(r"<(?:section|article)\b", re.I)


def count_slides(html: str) -> int:
    """슬라이드 수 추정. class 에 slide 가 있으면 그것이 정답이고,
    없을 때만 section/article 개수로 센다 (둘을 더하면 이중 계산된다)."""
    n = len(CLASS_SLIDE_RE.findall(html))
    return n if n else len(TAG_SLIDE_RE.findall(html))


def count_pages(pdf: Path) -> int:
    data = pdf.read_bytes()
    return len(re.findall(rb"/Type\s*/Page[^s]", data))


def build(src: Path, out: Path) -> int:
    html = src.read_text(encoding="utf-8")
    n_slides = count_slides(html)

    if "</head>" in html:
        patched = html.replace("</head>", PRINT_CSS + "</head>", 1)
    else:                                   # head 가 없는 자료도 있다
        patched = PRINT_CSS + html

    with tempfile.TemporaryDirectory() as tmp:
        tmp_html = Path(tmp) / "print.html"
        # 이미지·CSS 상대경로가 살아 있도록 원본 폴더의 파일을 함께 둔다
        for f in src.parent.iterdir():
            if f.is_file() and f != src:
                shutil.copy2(f, Path(tmp) / f.name)
        tmp_html.write_text(patched, encoding="utf-8")
        tmp_pdf = Path(tmp) / "out.pdf"
        r = subprocess.run(
            [CHROME, "--headless", "--no-sandbox", "--disable-gpu",
             "--no-pdf-header-footer", f"--print-to-pdf={tmp_pdf}",
             f"file://{tmp_html}"],
            capture_output=True, text=True, timeout=120)
        if not tmp_pdf.exists():
            sys.exit(f"PDF 생성 실패:\n{r.stderr[-400:]}")
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(tmp_pdf, out)

    pages = count_pages(out)
    print(f"만들었습니다: {out} ({pages}쪽)")
    if n_slides and pages != n_slides:
        print(f"  ! 슬라이드 {n_slides}장인데 {pages}쪽입니다 — 열어서 확인하세요")
    return pages


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("사용: python3 html2pdf.py <입력.html> [출력.pdf]")
    src = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".pdf")
    build(src, out)
