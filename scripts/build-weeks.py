#!/usr/bin/env python3
"""curriculum/detailed-plan.md → /srv/hub/weeks.json (specs/170)

관제탑의 주차별 계획을 **커리큘럼 문서에서 뽑아온다.** 손으로 옮겨 적으면
커리큘럼이 바뀔 때 관제탑이 조용히 낡는다 — 정본은 항상 detailed-plan.md 다.

추출 대상 (주차 절의 실제 형식):
    ### N주 — 제목 ★태그
    | **만들기 목표** | … |
    | **개발 역량**  | … |
    | **사용 기술**  | … |
    **진행**: …
    **강사 준비**: …

사용: build-weeks.py [--out /srv/hub/weeks.json] [--print]
"""
import argparse, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "curriculum" / "detailed-plan.md"

# 강조·링크·코드 표기를 사람이 읽는 평문으로
def plain(s: str) -> str:
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)      # 링크 → 텍스트
    s = s.replace("**", "").replace("`", "")
    return re.sub(r"\s+", " ", s).strip()


def split_steps(prose: str):
    """진행 서술을 읽기 좋은 단계로 자른다.

    원문은 '→' 로 흐름을 잇고 '①②③' 으로 블록을 나눈다. 이 둘을 경계로 쓴다.
    (문장 끝 마침표로 자르면 '3.5' 같은 숫자나 약어에서 잘못 끊긴다.)
    """
    prose = plain(prose)
    parts = re.split(r"\s*→\s*", prose)
    out = []
    for p in parts:
        p = p.strip(" ·")
        if not p:
            continue
        # ①②③ 로 시작하는 큰 블록은 그대로 살린다
        out.append(p)
    return out


def parse():
    if not SRC.exists():
        sys.exit(f"커리큘럼 문서를 찾을 수 없습니다: {SRC}")
    text = SRC.read_text(encoding="utf-8")

    # 버전 (머리말의 v8.5 등)
    mv = re.search(r"^#\s.*\(([vV][\d.]+)\)", text, re.M)
    version = mv.group(1) if mv else ""

    weeks = []
    # ### N주 — 제목 … 다음 ### 또는 --- 전까지
    for m in re.finditer(r"^### (\d+)주\s*[—-]\s*(.+?)$\n(.*?)(?=^### \d+주|^## |\Z)",
                         text, re.M | re.S):
        n, title, body = int(m.group(1)), m.group(2).strip(), m.group(3)

        # 제목 끝의 ★태그 분리
        tag = ""
        tm = re.search(r"★(.+)$", title)
        if tm:
            tag = tm.group(1).strip()
            title = title[:tm.start()].strip()

        def cell(label):
            c = re.search(rf"\|\s*\*\*{label}\*\*\s*\|(.+?)\|", body)
            return plain(c.group(1)) if c else ""

        # 필드 라벨은 부제를 달기도 한다 — "**진행 · 전반 60분**:" (8주차),
        # "**진행 · 후반 50분 — 프로젝트 프리플라이트**:" 처럼. 라벨로 시작하기만 하면
        # 뒤에 무엇이 붙든 같은 필드로 본다. 경계도 이 라벨들뿐이다 — 본문 중간의
        # 줄 첫머리 **강조**(5주차 "**well-made 하네스 해부**")를 경계로 쓰면 잘린다.
        LABEL = r"\*\*(?:진행|강사 준비)(?:[^*]*)?\*\*\s*:"

        def field(label):
            """같은 라벨의 블록이 여럿이면(8주차 전반/후반) 모두 이어 붙인다."""
            found = re.findall(
                rf"\*\*{label}(?:[^*]*)?\*\*\s*:\s*(.*?)(?=\n{LABEL}|\Z)",
                body, re.S)
            return "\n".join(x.strip() for x in found)

        prep_raw = field("강사 준비")
        weeks.append({
            "week": n,
            "title": plain(title),
            "tag": plain(tag),
            "goal": cell("만들기 목표"),
            "skill": cell("개발 역량"),
            "tech": cell("사용 기술"),
            "steps": split_steps(field("진행")),
            "prep": [plain(x) for x in re.split(r"\s*[,·]\s*(?![^(]*\))",
                                                plain(prep_raw).rstrip(".")) if plain(x)],
        })
    return {"version": version, "source": "curriculum/detailed-plan.md", "weeks": weeks}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/srv/hub/weeks.json")
    ap.add_argument("--print", dest="show", action="store_true")
    a = ap.parse_args()

    data = parse()
    if len(data["weeks"]) != 12:
        print(f"경고: 주차를 {len(data['weeks'])}개만 찾았습니다 (12개 예상). "
              "detailed-plan.md 의 '### N주 —' 형식을 확인하세요.", file=sys.stderr)

    if a.show:
        for w in data["weeks"]:
            print(f"\n[{w['week']}주] {w['title']}" + (f"  ★{w['tag']}" if w["tag"] else ""))
            print(f"  만들기: {w['goal']}")
            print(f"  역량  : {w['skill']}")
            print(f"  기술  : {w['tech']}")
            print(f"  진행  : {len(w['steps'])}단계 / 준비 {len(w['prep'])}항목")
        return

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out} — {len(data['weeks'])}주차 ({data['version']})")


if __name__ == "__main__":
    main()
