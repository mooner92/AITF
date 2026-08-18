#!/usr/bin/env python3
"""슬라이드 원고에서 산문만 빼내고 되돌려 넣는다 (윤문 파이프라인 ②·④단계).

윤문기는 평문만 다룬다. 원고를 통째로 넘기면 `^^^`·`{{ }}`·표 기호까지 고쳐버리므로,
산문 줄만 번호를 붙여 뽑아내고 윤문된 결과를 같은 번호 자리에 되꽂는다.

윤문에서 제외하는 줄
  ??? 로 시작       발표자 노트 — 강사만 보는 메모라 문체를 다듬을 이유가 없다
  <!-- --> / < 시작 지시자와 원본 HTML
  ``` 블록 안        코드는 그대로여야 한다
  | 로 시작          표 — 셀을 늘리면 화면을 넘친다
  ^^^ / --- / ^      구조 표시
  {{...}} 만 있는 줄  치환자
  TODO 포함          아직 안 쓴 자리

사용
    prep.py extract <원고.md> <out.txt>
    prep.py apply   <원고.md> <윤문된.txt> [출력.md]   # 출력 생략 시 원고 덮어씀
"""
import re, sys
from pathlib import Path

SKIP = re.compile(r"^\s*(\?\?\?|<|```|\||\^\^\^|---\s*$|\^\s|>\s*$|$)")


def prose_lines(text):
    """윤문 대상 줄의 인덱스를 고른다."""
    lines = text.split("\n")
    picked, in_code = [], False
    for n, ln in enumerate(lines):
        if ln.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code or SKIP.match(ln):
            continue
        s = ln.strip()
        if not s or "TODO" in s:
            continue
        # 치환자만 있는 줄은 건드릴 게 없다
        if re.fullmatch(r"[-\s]*\{\{[^}]+\}\}[\s·:]*(\{\{[^}]+\}\})?[\s]*", s):
            continue
        if len(s) < 6:
            continue
        picked.append(n)
    return lines, picked


def extract(src, out):
    lines, picked = prose_lines(Path(src).read_text(encoding="utf-8"))
    blocks = [f"[{k+1}] {lines[n].strip()}" for k, n in enumerate(picked)]
    Path(out).write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
    print(f"{Path(src).name}: 산문 {len(picked)}줄 추출 → {out}")


def apply(src, edited, out=None):
    raw = Path(src).read_text(encoding="utf-8")
    lines, picked = prose_lines(raw)
    text = re.split(r"<!--\s*HUMANIZE-SUMMARY", Path(edited).read_text(encoding="utf-8"))[0]
    found = dict(re.findall(r"^\[(\d+)\][ \t]*(.*?)(?=\n\[\d+\]|\Z)", text, flags=re.S | re.M))

    if len(found) != len(picked):
        sys.exit(f"블록 수 불일치: 원본 {len(picked)} vs 윤문본 {len(found)} — 중단")

    for k, n in enumerate(picked):
        original = lines[n]
        indent = original[:len(original) - len(original.lstrip())]
        lines[n] = indent + " ".join(found[str(k + 1)].split())

    Path(out or src).write_text("\n".join(lines), encoding="utf-8")
    print(f"{out or src}: {len(picked)}줄 반영")


if __name__ == "__main__":
    cmd, *rest = sys.argv[1:]
    {"extract": extract, "apply": apply}[cmd](*rest)
