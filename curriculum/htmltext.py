#!/usr/bin/env python3
"""*.src.html의 산문 텍스트 노드만 빼내고 되돌려 넣는다 (윤문 파이프라인용).

윤문기는 평문만 다루므로, HTML을 통째로 넘기면 태그·CSS까지 고쳐버린다.
그래서 텍스트 노드만 번호를 붙여 뽑아내고, 윤문된 결과를 같은 번호 자리에 되꽂는다.

제외 대상:
  style / title  — 코드와 메타데이터
  svg 내부       — 좌표가 고정된 라벨이라 길이가 바뀌면 그림이 깨진다
  짧은 라벨      — 버튼·태그·표 머리글 등 (MIN_LEN 미만)

사용:
  htmltext.py extract <src.html> <out.txt>
  htmltext.py apply   <src.html> <edited.txt> <out.html>
"""
import re, sys
from html.parser import HTMLParser

SKIP_TAGS = {"style", "title", "svg"}
MIN_LEN = 12          # 이보다 짧으면 라벨로 보고 건드리지 않는다
HANGUL = re.compile(r"[가-힣]")


class Collector(HTMLParser):
    """텍스트 노드의 원문 위치(offset, length)를 모은다."""

    def __init__(self, raw):
        super().__init__(convert_charrefs=False)
        self.raw = raw
        self.lines = [0]
        for line in raw.splitlines(keepends=True):
            self.lines.append(self.lines[-1] + len(line))
        self.depth = 0          # SKIP_TAGS 안에 있으면 > 0
        self.spans = []

    def _off(self):
        ln, col = self.getpos()
        return self.lines[ln - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.depth += 1

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if self.depth:
            return
        if len(data.strip()) < MIN_LEN or not HANGUL.search(data):
            return
        self.spans.append((self._off(), len(data)))


def collect(path):
    raw = open(path, encoding="utf-8").read()
    c = Collector(raw)
    c.feed(raw)
    return raw, c.spans


def extract(src, out):
    raw, spans = collect(src)
    blocks = []
    for i, (off, length) in enumerate(spans, 1):
        # 앞뒤 공백·들여쓰기는 원문에 남기고 알맹이만 넘긴다
        text = " ".join(raw[off:off + length].split())
        blocks.append(f"[{i}] {text}")
    open(out, "w", encoding="utf-8").write("\n\n".join(blocks) + "\n")
    print(f"{src}: 텍스트 노드 {len(spans)}개 · {sum(len(b) for b in blocks)}자")


def rewrap(text, lead, width=96):
    """원문 들여쓰기를 유지하며 소스를 읽기 좋게 접는다 (렌더링에는 영향 없음)."""
    indent = lead.rsplit("\n", 1)[-1] if "\n" in lead else ""
    if not indent or len(text) + len(indent) <= width:
        return text
    lines, cur = [], ""
    for word in text.split(" "):
        if cur and len(indent) + len(cur) + 1 + len(word) > width:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}" if cur else word
    lines.append(cur)
    return ("\n" + indent).join(lines)


def apply(src, edited, out):
    raw, spans = collect(src)
    text = open(edited, encoding="utf-8").read()
    # 윤문기가 붙이는 메타데이터 블록은 본문이 아니다 — 놔두면 마지막 노드에 딸려 들어간다
    text = re.split(r"<!--\s*HUMANIZE-SUMMARY", text)[0]
    found = dict(re.findall(r"^\[(\d+)\][ \t]*(.*?)(?=\n\[\d+\]|\Z)",
                            text, flags=re.S | re.M))
    if len(found) != len(spans):
        sys.exit(f"블록 수 불일치: 원본 {len(spans)} vs 윤문본 {len(found)} — 중단")

    pieces, prev = [], 0
    for i, (off, length) in enumerate(spans, 1):
        original = raw[off:off + length]
        lead = original[:len(original) - len(original.lstrip())]
        tail = original[len(original.rstrip()):]
        pieces.append(raw[prev:off])
        pieces.append(lead + rewrap(" ".join(found[str(i)].split()), lead) + tail)
        prev = off + length
    pieces.append(raw[prev:])
    open(out, "w", encoding="utf-8").write("".join(pieces))
    print(f"{out}: {len(spans)}개 노드 반영")


if __name__ == "__main__":
    cmd, *rest = sys.argv[1:]
    {"extract": extract, "apply": apply}[cmd](*rest)
