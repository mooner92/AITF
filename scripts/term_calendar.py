#!/usr/bin/env python3
"""12주 학사 달력 — 학원 방학(추석 등)으로 건너뛰는 일요일을 반영한다.

지금까지 위키·알림 스크립트는 "COURSE_START 로부터 며칠 지났나 ÷ 7"로 주차를
계산했다. 이 방식은 **학원이 쉬는 일요일이 하나라도 생기면 그 뒤 모든 주차 번호가
밀린다** — 12주가 12번의 연속 일요일이 아니기 때문이다(2026-08-29 설계 검토).

이 파일은 "몇 번째 주차인가"를 날짜 뺄셈이 아니라 **명시적 날짜 목록**으로 답한다.
목록이 비어 있으면(아직 확정 전) 기존 방식(연속 계산)으로 자동 폴백한다 —
안 채워도 지금 동작이 갑자기 바뀌지 않는다.

설정: /opt/scripts/term-calendar.json (서버 전용, git 미포함)
    {
      "course_start": "2026-08-30",
      "skip_sundays": ["2026-09-27"],   // 학원이 쉬는 일요일 — 확정되는 대로 추가
      "class_dates": []                  // 채우면 이게 최우선 — 12개를 직접 나열해도 됨
    }
"""
from __future__ import annotations  # 서버 Python 3.9 — `date | None` 타입 힌트에 필요

import json
from datetime import date, datetime, timedelta
from pathlib import Path

CONF = Path("/opt/scripts/term-calendar.json")


def _load():
    if not CONF.exists():
        return {}
    return json.loads(CONF.read_text(encoding="utf-8"))


def class_dates(n_weeks: int = 12) -> list[date]:
    """12번의 실제 수업일 목록. class_dates 를 직접 채웠으면 그걸 쓰고,
    아니면 course_start 부터 skip_sundays 를 건너뛰며 계산한다."""
    cfg = _load()
    explicit = cfg.get("class_dates") or []
    if explicit:
        return [datetime.strptime(d, "%Y-%m-%d").date() for d in explicit]

    start = cfg.get("course_start")
    if not start:
        return []
    d0 = datetime.strptime(start, "%Y-%m-%d").date()
    skip = {datetime.strptime(x, "%Y-%m-%d").date() for x in cfg.get("skip_sundays", [])}

    dates, cur = [], d0
    while len(dates) < n_weeks:
        if cur not in skip:
            dates.append(cur)
        cur += timedelta(days=7)
    return dates


def week_of(today: date | None = None) -> int | None:
    """오늘이 몇 주차 수업일인지. 수업일이 아니면 None(휴일 포함)."""
    today = today or date.today()
    cd = class_dates()
    if not cd:
        return None
    for i, d in enumerate(cd, 1):
        if d == today:
            return i
    return None


def is_after_course(today: date | None = None) -> bool:
    """마지막 주차(보통 12주차)가 지났는지 — 크론이 스스로 멈추는 기준."""
    today = today or date.today()
    cd = class_dates()
    if not cd:
        return False
    return today > cd[-1]


if __name__ == "__main__":
    import sys
    cd = class_dates()
    if not cd:
        print("term-calendar.json 이 없거나 course_start 가 비어 있다 — 폴백 없음")
        sys.exit(1)
    for i, d in enumerate(cd, 1):
        mark = " ← 오늘" if d == date.today() else ""
        print(f"{i:2}주차  {d.isoformat()} ({'월화수목금토일'[d.weekday()]}){mark}")
    print(f"\n오늘 주차: {week_of()}")
    print(f"과정 종료 지남: {is_after_course()}")
