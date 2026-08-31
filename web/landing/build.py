#!/usr/bin/env python3
"""메인 페이지 빌드 — index.src.html → /srv/hub-public/index.html (specs/170)

이 페이지는 **인증 없이 누구나 본다.** 그래서:
  · 학생 이름·계정·활동 수치는 절대 넣지 않는다 (관제탑은 쿠키 뒤에 있다)
  · 주차 목록은 제목·만들기 목표까지만 — 강사 준비·진행 상세는 공개하지 않는다
    (7주차 위키 공개 같은 장치가 미리 새면 수업이 김새므로)
  · 개강일·수업일 목록은 공개 정보라 그대로 넣는다

디자인(2026-08-31 전면 개정): Mobbin 분석 문서 기반 갤러리-화이트 모노크롬.
  · 서체 — 라틴/숫자는 Inter 가변(무료, Saans 대체 — 문서의 대체 권고 그대로
    300/450/650 축 사용), 한글은 Paperlogy 400·700 두 웨이트.
    셋 다 서브셋해 임베드한다 (외부 요청 0 원칙).
  · 주차 표시 — 하드코딩이 아니라 term-calendar.json 의 수업일 목록을 빌드 시
    주입하고, 현재 상태는 클라이언트가 날짜로 계산한다. 매주 재빌드 불필요.

사용: python3 web/landing/build.py [--deploy]
"""
import base64, json, os, re, subprocess, sys, tempfile
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
OUT_DIR = Path(os.environ.get("LANDING_OUT", str(HERE / "dist")))
DEPLOY_DIR = Path("/srv/hub-public")
PL_DIR = Path(os.environ.get("PAPERLOGY_DIR", REPO / "curriculum" / "fonts"))
INTER = HERE / "fonts" / "InterVariable.ttf"

# 한글 + 괘선·기호 (Paperlogy 몫)
KO_UNICODES = ("U+AC00-D7A3,U+3130-318F,U+1100-11FF,U+3000-303F")
# 라틴·숫자·문장부호·화살표 (Inter 몫)
LATIN_UNICODES = ("U+0020-007E,U+00A0-00FF,U+2013-2014,U+2018-201F,U+2022,"
                  "U+2026,U+2190-2199,U+00B7,U+2032-2033")


def _read_server_file(path: str) -> str:
    p = Path(path)
    try:
        return p.read_text(encoding="utf-8")
    except (PermissionError, FileNotFoundError):
        r = subprocess.run(["sudo", "-n", "cat", path], capture_output=True, text=True)
        return r.stdout if r.returncode == 0 else ""


def course_start() -> str:
    m = re.search(r"^COURSE_START=(.*)$", _read_server_file("/opt/scripts/hub.env"), re.M)
    return m.group(1).strip() if m else ""


def class_dates() -> list:
    """scripts/term_calendar.py 와 같은 규칙 — 명시 목록 우선, 없으면
    course_start 부터 skip_sundays 를 건너뛰며 12개."""
    txt = _read_server_file("/opt/scripts/term-calendar.json")
    if not txt:
        return []
    cfg = json.loads(txt)
    explicit = cfg.get("class_dates") or []
    if explicit:
        return explicit
    start = cfg.get("course_start") or course_start()
    if not start:
        return []
    d0 = datetime.strptime(start, "%Y-%m-%d").date()
    skip = set(cfg.get("skip_sundays", []))
    out, cur = [], d0
    while len(out) < 12:
        s = cur.isoformat()
        if s not in skip:
            out.append(s)
        cur += timedelta(days=7)
    return out


def public_weeks():
    """커리큘럼에서 공개해도 되는 필드만 추린다."""
    r = subprocess.run([sys.executable, str(REPO / "scripts" / "build-weeks.py"),
                        "--out", "/tmp/_weeks_full.json"],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"주차 추출 실패: {r.stderr.strip()}")
    d = json.loads(Path("/tmp/_weeks_full.json").read_text(encoding="utf-8"))
    return {"version": d["version"],
            "class_dates": class_dates(),
            "weeks": [{"week": w["week"], "title": w["title"], "goal": w["goal"]}
                      for w in d["weeks"]]}


def subset(src: Path, unicodes: str) -> tuple:
    from fontTools.subset import main as subset_main
    with tempfile.TemporaryDirectory() as tmp:
        wf = Path(tmp) / "f.woff2"
        subset_main([str(src), f"--output-file={wf}", "--flavor=woff2",
                     f"--unicodes={unicodes}", "--layout-features=*",
                     "--no-hinting", "--desubroutinize"])
        return base64.b64encode(wf.read_bytes()).decode(), round(wf.stat().st_size / 1024)


def main():
    for f in (INTER, PL_DIR / "Paperlogy-4Regular.ttf", PL_DIR / "Paperlogy-7Bold.ttf"):
        if not f.exists():
            sys.exit(f"폰트 없음: {f}")

    inter_b64, inter_kb = subset(INTER, LATIN_UNICODES)
    pl4_b64, pl4_kb = subset(PL_DIR / "Paperlogy-4Regular.ttf", KO_UNICODES)
    pl7_b64, pl7_kb = subset(PL_DIR / "Paperlogy-7Bold.ttf", KO_UNICODES)

    face = (
        # Inter 가변 — 라틴·숫자. 300~650 축을 그대로 쓴다 (Saans 652→650 매핑).
        "@font-face{font-family:Inter;font-style:normal;font-weight:100 900;"
        f"font-display:swap;src:url(data:font/woff2;base64,{inter_b64}) format('woff2')}}"
        # Paperlogy — 한글. 400/700 두 장이면 650 제목은 700 으로, 300 리드는 400 으로 맞는다.
        "@font-face{font-family:Paperlogy;font-style:normal;font-weight:400;"
        f"font-display:swap;src:url(data:font/woff2;base64,{pl4_b64}) format('woff2')}}"
        "@font-face{font-family:Paperlogy;font-style:normal;font-weight:700;"
        f"font-display:swap;src:url(data:font/woff2;base64,{pl7_b64}) format('woff2')}}"
    )

    html = (HERE / "index.src.html").read_text(encoding="utf-8")
    html = (html.replace("__FONT__", face)
                .replace("__COURSE_START__", course_start())
                .replace("__CLASS_DATES__", json.dumps(class_dates())))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "index.html").write_text(html, encoding="utf-8")
    (OUT_DIR / "weeks-public.json").write_text(
        json.dumps(public_weeks(), ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"{OUT_DIR}/index.html — Inter {inter_kb}KB · Paperlogy {pl4_kb}+{pl7_kb}KB · "
          f"개강일 {course_start() or '미설정'} · 수업일 {len(class_dates())}개")

    if "--deploy" in sys.argv:
        for f in ("index.html", "weeks-public.json"):
            subprocess.run(["sudo", "install", "-o", "root", "-g", "nginx", "-m", "644",
                            str(OUT_DIR / f), str(DEPLOY_DIR / f)], check=True)
            subprocess.run(["sudo", "restorecon", str(DEPLOY_DIR / f)], capture_output=True)
        print(f"배포 완료 → {DEPLOY_DIR}")


if __name__ == "__main__":
    main()
