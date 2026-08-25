#!/usr/bin/env python3
"""메인 페이지 빌드 — index.src.html → /srv/hub-public/index.html (specs/170)

이 페이지는 **인증 없이 누구나 본다.** 그래서:
  · 학생 이름·계정·활동 수치는 절대 넣지 않는다 (관제탑은 쿠키 뒤에 있다)
  · 주차 목록은 제목·만들기 목표까지만 — 강사 준비·진행 상세는 공개하지 않는다
    (7주차 위키 공개 같은 장치가 미리 새면 수업이 김새므로)
  · 개강일은 공개 정보라 그대로 넣는다

사용: python3 web/landing/build.py [--deploy]
"""
import base64, json, os, re, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
# 기본은 저장소 안에 만들고, --deploy 일 때만 서버 경로로 설치한다.
# (fontTools 가 사용자 설치본이라 sudo 로 빌드하면 모듈을 못 찾는다)
OUT_DIR = Path(os.environ.get("LANDING_OUT", str(HERE / "dist")))
DEPLOY_DIR = Path("/srv/hub-public")
FONT = Path(os.environ.get("PAPERLOGY_DIR", REPO / "curriculum" / "fonts")) / "Paperlogy-4Regular.ttf"
UNICODES = ("U+0020-007E,U+00A0-00FF,U+2000-206F,U+20A0-20BF,U+2190-21FF,"
            "U+2200-22FF,U+2500-257F,U+25A0-25FF,U+2600-26FF,"
            "U+AC00-D7A3,U+3130-318F,U+1100-11FF")


def course_start():
    """개강일. hub.env 는 root 600 이라 일반 권한이면 sudo 로 한 번 더 시도한다."""
    txt = ""
    env = Path("/opt/scripts/hub.env")
    try:
        txt = env.read_text(encoding="utf-8")
    except (PermissionError, FileNotFoundError):
        r = subprocess.run(["sudo", "-n", "cat", str(env)], capture_output=True, text=True)
        txt = r.stdout if r.returncode == 0 else ""
    m = re.search(r"^COURSE_START=(.*)$", txt, re.M)
    return m.group(1).strip() if m else ""


def public_weeks():
    """커리큘럼에서 공개해도 되는 필드만 추린다."""
    r = subprocess.run([sys.executable, str(REPO / "scripts" / "build-weeks.py"),
                        "--out", "/tmp/_weeks_full.json"],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"주차 추출 실패: {r.stderr.strip()}")
    d = json.loads(Path("/tmp/_weeks_full.json").read_text(encoding="utf-8"))
    return {"version": d["version"],
            "weeks": [{"week": w["week"], "title": w["title"], "goal": w["goal"]}
                      for w in d["weeks"]]}


def main():
    from fontTools.subset import main as subset_main
    if not FONT.exists():
        sys.exit(f"폰트 없음: {FONT}")

    with tempfile.TemporaryDirectory() as tmp:
        wf = Path(tmp) / "pl.woff2"
        subset_main([str(FONT), f"--output-file={wf}", "--flavor=woff2",
                     f"--unicodes={UNICODES}", "--layout-features=*",
                     "--no-hinting", "--desubroutinize"])
        b64 = base64.b64encode(wf.read_bytes()).decode()
        kb = round(wf.stat().st_size / 1024)

    face = ("@font-face{font-family:Paperlogy;font-style:normal;font-weight:400;"
            f"font-display:swap;src:url(data:font/woff2;base64,{b64}) format('woff2')}}")

    html = (HERE / "index.src.html").read_text(encoding="utf-8")
    html = html.replace("__FONT__", face).replace("__COURSE_START__", course_start())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "index.html").write_text(html, encoding="utf-8")
    (OUT_DIR / "weeks-public.json").write_text(
        json.dumps(public_weeks(), ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"{OUT_DIR}/index.html — 폰트 {kb}KB, 개강일 {course_start() or '미설정'}")

    if "--deploy" in sys.argv:
        for f in ("index.html", "weeks-public.json"):
            subprocess.run(["sudo", "install", "-o", "root", "-g", "nginx", "-m", "644",
                            str(OUT_DIR / f), str(DEPLOY_DIR / f)], check=True)
            subprocess.run(["sudo", "restorecon", str(DEPLOY_DIR / f)], capture_output=True)
        print(f"배포 완료 → {DEPLOY_DIR}")


if __name__ == "__main__":
    main()
