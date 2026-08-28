#!/usr/bin/env python3
"""계정 카드 생성 — 학생에게 인쇄해 나눠줄 접속 정보 (specs/130)

첫 수업의 최대 변수는 접속이고, 그 병목은 **비밀번호를 눈으로 확인할 수
없다는 것**이다. 터미널은 입력한 글자를 별표조차 찍지 않으므로, 오타가 나도
어디서 틀렸는지 알 수 없어 처음부터 다시 쳐야 한다. 그래서 카드는 비밀번호를
**한 글자씩 떨어뜨려** 보여준다 — 학생이 손가락으로 짚어가며 칠 수 있게.

출력은 /opt/scripts/account-cards.txt (600). 저장소에는 올리지 않는다
(SECURITY.md — accounts.csv 계열은 서버에만 둔다).

사용:
    sudo ./make-cards.py                 전체
    sudo ./make-cards.py --class high    특정 반만
"""
import argparse
import csv
import pathlib
import unicodedata

ROSTER = pathlib.Path("/opt/scripts/roster.csv")
ACCOUNTS = pathlib.Path("/opt/scripts/accounts.csv")
HUBENV = pathlib.Path("/opt/scripts/hub.env")
OUT = pathlib.Path("/opt/scripts/account-cards.txt")

LABEL = {"mid": "중등부", "high": "고등부"}
INNER = 46          # 테두리 안쪽 폭(칸 기준)


def width(s: str) -> int:
    """터미널·고정폭 인쇄에서 차지하는 칸 수.

    한글은 두 칸을 차지하는데 len() 은 한 칸으로 세기 때문에, 이걸 쓰지 않으면
    이름 길이에 따라 카드 오른쪽 테두리가 제각각 어긋난다.
    """
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in s)


def pad(s: str, n: int) -> str:
    return s + " " * max(0, n - width(s))


def row(left: str, right: str = "") -> str:
    gap = INNER - width(left) - width(right)
    return f"│ {left}{' ' * max(1, gap)}{right} │"


def server_ip() -> str:
    """카드에 박을 접속 주소. hub.env 에 있으면 그걸 쓰고, 없으면 자리표시자."""
    if HUBENV.exists():
        for ln in HUBENV.read_text(encoding="utf-8").splitlines():
            if ln.startswith("SSH_HOST="):
                return ln.split("=", 1)[1].strip()
    return "⟪서버주소⟫"


def spaced(pw: str) -> str:
    """비밀번호를 한 글자씩 띄운다. 눈으로 짚으며 칠 수 있게."""
    return " ".join(pw)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--class", dest="cls", help="mid 또는 high")
    a = ap.parse_args()

    pw = dict(r for r in csv.reader(ACCOUNTS.open(encoding="utf-8")) if r)
    host = server_ip()

    cards = []
    for r in csv.DictReader(ROSTER.open(encoding="utf-8")):
        acct = r["계정ID"].strip()
        if a.cls and r["반"].strip() != a.cls:
            continue
        if acct not in pw:
            print(f"  ! {acct}: 비밀번호 기록 없음 — 건너뜀")
            continue
        cards.append([
            "╭" + "─" * (INNER + 2) + "╮",
            row(f"{r['이름'].strip()}", LABEL.get(r["반"].strip(), r["반"].strip())),
            "├" + "─" * (INNER + 2) + "┤",
            row("아이디", acct),
            row("비밀번호", spaced(pw[acct])),
            "├" + "─" * (INNER + 2) + "┤",
            row(f"ssh {acct}@{host}"),
            "╰" + "─" * (INNER + 2) + "╯",
            "",
            "  · 비밀번호는 쳐도 화면에 안 나와요. 그대로 치고 Enter!",
            "  · 처음 한 번만 yes 를 묻습니다 → yes 입력",
            "",
            "",
        ])

    if not cards:
        print("만들 카드가 없다 — roster.csv 와 accounts.csv 를 확인할 것")
        return 1

    text = "\n".join("\n".join(c) for c in cards)
    OUT.write_text(text, encoding="utf-8")
    OUT.chmod(0o600)
    print(f"{len(cards)}장 생성 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
