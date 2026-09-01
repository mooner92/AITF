#!/usr/bin/env python3
"""HTML 발표자료 → PowerPoint(.pptx) 변환 — aitf-pptx 스킬의 도구

왜 스크립트로 두는가: pptx 는 zip 안에 XML 여러 장이 규격대로 들어 있는 형식이다.
직접 XML 을 써서 만들면 파일은 생기지만 PowerPoint 가 "복구가 필요합니다"를 띄우거나,
배경을 빠뜨려 **흰 배경에 흰 글씨**가 되는 사고가 난다 (2026-09-01 실측).
python-pptx 가 규격을 지켜 주므로 그 위에서 내용만 채운다.

사용:
    python3 html2pptx.py <입력.html> [출력.pptx]

동작:
    1. HTML 에서 슬라이드 단위(.slide / section / article)를 찾는다
    2. 각 슬라이드의 제목(h1~h3)과 본문(li, p)을 뽑는다
    3. 첫 장은 표지, 나머지는 제목+글머리 슬라이드로 만든다

색·글꼴은 아래 상수에서만 바꾼다. 개별 도형에 색을 직접 쓰지 않는다.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Emu, Inches, Pt

# ── 테마 — 학교 제출용 밝은 배경 (인쇄해도 잉크가 덜 든다) ──────────────
BG = RGBColor(0xFF, 0xFF, 0xFF)      # 배경: 흰색
INK = RGBColor(0x14, 0x14, 0x14)     # 본문: 근검정
ACCENT = RGBColor(0x00, 0x75, 0xFF)  # 제목: AITF 파랑
MUTE = RGBColor(0x70, 0x70, 0x70)    # 부제·설명
FONT = "맑은 고딕"                    # 윈도우에 기본 설치된 한글 글꼴

TITLE_PT, BODY_PT, SUB_PT = 32, 18, 16
MAX_BULLETS = 7                       # 넘으면 잘라내고 경고 (한 장 = 한 메시지)


class SlideExtractor(HTMLParser):
    """슬라이드 경계를 찾아 제목·본문을 모은다.

    학생 자료는 형태가 제각각이라 특정 구조를 가정하지 않는다.
    슬라이드 후보: class 에 slide/page 가 들어간 요소, 또는 <section>·<article>.
    """

    SLIDE_TAGS = {"section", "article"}
    TITLE_TAGS = {"h1", "h2", "h3"}
    TEXT_TAGS = {"li", "p"}

    def __init__(self):
        super().__init__()
        self.slides = []
        self._depth = 0          # 현재 슬라이드 안의 태그 깊이
        self._cur = None
        self._buf = None
        self._kind = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "")
        is_slide = tag in self.SLIDE_TAGS or re.search(r"\b(slide|page)\b", cls)
        if is_slide and self._cur is None:
            self._cur = {"title": "", "sub": "", "items": []}
            self._depth = 0
            return
        if self._cur is not None:
            self._depth += 1
            if tag in self.TITLE_TAGS and not self._cur["title"]:
                self._buf, self._kind = [], "title"
            elif tag in self.TEXT_TAGS:
                self._buf, self._kind = [], "text"

    def handle_data(self, data):
        if self._buf is not None:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if self._cur is None:
            return
        if self._buf is not None and (tag in self.TITLE_TAGS or tag in self.TEXT_TAGS):
            text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            if text:
                if self._kind == "title":
                    self._cur["title"] = text
                elif not self._cur["title"]:
                    self._cur["sub"] = text          # 제목 전 문단 = 부제
                else:
                    self._cur["items"].append(text)
            self._buf, self._kind = None, None
        if tag in self.SLIDE_TAGS or self._depth == 0:
            if self._cur and (self._cur["title"] or self._cur["items"] or self._cur["sub"]):
                self.slides.append(self._cur)
            self._cur = None
        else:
            self._depth -= 1


def _box(slide, text, left, top, width, height, size, color, bold=False):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = FONT
    return box


def _paint_background(slide, prs):
    """배경을 **명시적으로** 칠한다.

    이 한 줄이 없으면 배경이 비고, 글자색을 흰색으로 두었을 때
    흰 배경에 흰 글씨가 되어 아무것도 안 보인다. 실제로 났던 사고다.
    """
    rect = slide.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)  # 1 = 사각형
    rect.fill.solid()
    rect.fill.fore_color.rgb = BG
    rect.line.fill.background()
    rect.shadow.inherit = False
    slide.shapes._spTree.remove(rect._element)
    slide.shapes._spTree.insert(2, rect._element)   # 맨 뒤로 보낸다


def build(src: Path, out: Path) -> int:
    parser = SlideExtractor()
    parser.feed(src.read_text(encoding="utf-8"))
    slides = parser.slides
    if not slides:
        sys.exit("슬라이드를 못 찾았습니다. HTML 안에 .slide 나 <section> 이 있는지 확인하세요.")

    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)   # 16:9
    blank = prs.slide_layouts[6]
    warnings = []

    for i, s in enumerate(slides):
        slide = prs.slides.add_slide(blank)
        _paint_background(slide, prs)
        M = Inches(1.0)
        W = prs.slide_width - M * 2

        if i == 0:                                    # 표지
            _box(slide, s["title"] or "제목 없음", M, Inches(2.6), W,
                 Inches(1.4), TITLE_PT + 8, INK, bold=True)
            sub = s["sub"] or (s["items"][0] if s["items"] else "")
            if sub:
                _box(slide, sub, M, Inches(4.1), W, Inches(0.8), SUB_PT, MUTE)
            continue

        _box(slide, s["title"] or "", M, Inches(0.8), W, Inches(1.0),
             TITLE_PT, ACCENT, bold=True)
        items = s["items"]
        if len(items) > MAX_BULLETS:
            warnings.append(f"{i + 1}장: 항목 {len(items)}개 → {MAX_BULLETS}개만 넣었습니다")
            items = items[:MAX_BULLETS]
        top = Inches(2.1)
        for it in items:
            _box(slide, "• " + it, Inches(1.3), top, W - Inches(0.3),
                 Inches(0.6), BODY_PT, INK)
            top += Inches(0.78)

    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out)
    print(f"만들었습니다: {out} ({len(slides)}장)")
    for w in warnings:
        print("  ! " + w)
    return len(slides)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("사용: python3 html2pptx.py <입력.html> [출력.pptx]")
    src = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".pptx")
    build(src, out)
