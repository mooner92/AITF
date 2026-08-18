#!/usr/bin/env python3
"""주차별 슬라이드 원고 뼈대를 상세 계획서에서 뽑아낸다.

계획서(`curriculum/detailed-plan.md`)의 주차 절을 읽어 각 주차 원고의 뼈대를 만든다.
계획이 바뀌면 다시 돌려서 아직 손대지 않은 주차만 갱신할 수 있다.

이미 있는 파일은 덮어쓰지 않는다 (`--force` 로만 덮어씀).

    python3 scaffold.py            # 없는 주차만 생성
    python3 scaffold.py --week 5   # 5주차만
    python3 scaffold.py --force    # 전부 다시
"""
import argparse, re
from pathlib import Path

HERE = Path(__file__).parent
PLAN = HERE.parent / "curriculum" / "detailed-plan.md"

TEMPLATE = """<!-- class: cover g-none -->
^ {week}주차
# {title}

{goal_make}

- 접속: {{{{ACCESS_URL}}}}
- 중등반 {{{{CLASS_MID_TIME}}}} · 고등반 {{{{CLASS_HIGH_TIME}}}}

??? 시작 전 확인: {prep}

---

<!-- class: g-none -->
## 오늘 끝나면 <b>이게 생깁니다</b>

^^^
{goal_make}

??? 완성 예시를 미리 띄워두고 시작한다.

---

## 오늘 쓰는 것

^^^
{goal_tech}

^^^
> 이 도구는 그 달의 최신 것으로 바뀔 수 있습니다. 목표는 그대로입니다.

??? 도구가 교체됐다면 이 장을 먼저 고친다 (design-spec 5절, 교체 규칙).

---

<!-- class: chapter g-orange -->
<span class="n">1</span>
## 만들기

??? 여기서부터 실습. 진행 순서는 아래 노트 참고.
??? {flow}

---

## 이렇게 <b>시작합니다</b>

TODO — 학생에게 보여줄 첫 지시문 예시를 여기에

^^^
> TODO — 흔히 막히는 지점과 대처

??? TODO — 돌아다니며 볼 것, 빨리 끝낸 학생에게 줄 과제

---

## 중등 · 고등

<div class="split">
<div class="lane mid"><span class="who">중등반</span>
<p>{mid}</p>
</div>
<div class="lane high"><span class="who">고등반</span>
<p>{high}</p>
</div>
</div>

??? 반별로 다른 장이므로, 해당 반 수업에서는 자기 쪽만 띄워도 된다.

---

<!-- class: g-green -->
## 오늘의 기록

^^^
만든 것을 작품관에 올립니다.{commit}

^^^
> 사용량 그래프에서 오늘 쓴 만큼을 각자 확인합니다. 비교 대상은 지난주의 나입니다.

??? 대시보드를 띄운다. 순위는 보여주지 않는다.

---

<!-- class: cover g-none -->
## 다음 주에는

^^^
TODO — 다음 주 예고 한 줄

^^^
- 숙제 없음
- 준비물 없음

??? 마무리 3분.
"""


def parse_weeks(text):
    """계획서에서 주차별 정보를 뽑는다."""
    weeks = {}
    # '### 1주 — 제목' 부터 다음 '### N주' 또는 '## ' 까지
    for m in re.finditer(r"^###\s*(\d+)주\s*—\s*(.+?)$(.*?)(?=^###\s*\d+주|^##\s|\Z)",
                         text, flags=re.M | re.S):
        n, title, body = int(m.group(1)), m.group(2).strip(), m.group(3)

        def cell(label):
            c = re.search(rf"\|\s*\*\*{label}\*\*\s*\|\s*(.+?)\s*\|", body)
            return c.group(1).strip() if c else ""

        def para(label):
            p = re.search(rf"\*\*{label}\*\*:\s*(.+?)(?=\n\*\*|\n---|\Z)", body, flags=re.S)
            return " ".join(p.group(1).split()) if p else ""

        title = re.sub(r"\s*★.*$", "", title).strip()
        weeks[n] = {
            "week": n,
            "title": title,
            "goal_make": cell("만들기 목표") or "TODO",
            "goal_skill": cell("개발 역량") or "TODO",
            "goal_tech": cell("사용 기술") or "TODO",
            "flow": para("진행")[:400] or "TODO",
            "prep": para("강사 준비")[:200] or "TODO",
            "high": para("고등 추가")[:220] or "TODO — 고등반 심화",
        }
    return weeks


def build(w):
    d = dict(w)
    d["mid"] = "TODO — 중등반 진행 방식 (블록을 더 잘게 쪼개고 결과물 범위를 좁힌다)"
    d["commit"] = " 6주차부터는 커밋도 함께 합니다." if w["week"] >= 6 else ""
    # 마크다운 강조 기호는 슬라이드 원고에서 그대로 쓰이므로 유지, 표 기호만 제거
    for k in ("goal_make", "goal_tech", "flow", "prep", "high"):
        d[k] = d[k].replace("|", "·")
    return TEMPLATE.format(**d)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", type=int)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    weeks = parse_weeks(PLAN.read_text(encoding="utf-8"))
    if not weeks:
        raise SystemExit("계획서에서 주차를 찾지 못했습니다 — detailed-plan.md 형식 확인")

    made, kept = [], []
    for n, w in sorted(weeks.items()):
        if a.week and n != a.week:
            continue
        slug = re.sub(r"[^\w가-힣]+", "-", w["title"]).strip("-")
        out = HERE / f"w{n:02d}-{slug}.md"
        existing = list(HERE.glob(f"w{n:02d}-*.md"))
        if existing and not a.force:
            kept.append(existing[0].name); continue
        out.write_text(build(w), encoding="utf-8")
        made.append(out.name)

    for f in made: print(f"생성  {f}")
    for f in kept: print(f"유지  {f}  (--force 로 덮어쓰기)")
    print(f"\n주차 {len(weeks)}개 인식 · 생성 {len(made)} · 유지 {len(kept)}")
