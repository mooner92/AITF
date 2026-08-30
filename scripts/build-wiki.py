#!/usr/bin/env python3
"""자동 위키 — LLM Wiki 패턴 구현 (specs/180)

세 층으로 나눈다 (패턴 문서의 Architecture 그대로):

  raw/      원천 자료. 결정적 수집으로 만들고 이후 **수정하지 않는다**.
            LLM 도 읽기만 한다. 이 층은 모델이 없어도 항상 생성된다.
  wiki/     LLM 이 소유하는 층 — 엔티티 페이지(학생·스킬·도구·개념),
            index.md, log.md. **누적되고 갱신된다** (매주 새 파일이 아니라).
  AGENTS.md 스키마. LLM 에게 이 위키를 어떻게 유지하는지 알려준다.

핵심 장치 — 마커 구간:
    <!-- auto:활동 --> … <!-- /auto:활동 -->
  마커 안은 이 스크립트가 매번 덮어쓴다(결정적 사실).
  마커 밖은 LLM 이나 사람이 쓴 서술이며 **절대 건드리지 않는다**.
  덕분에 "모델 없이도 사실은 쌓이고, 모델이 붙으면 서술이 자란다"가 동시에 성립한다.

사용:
  build-wiki.py                 오늘 기준 주차, 전 반
  build-wiki.py --week 3
  build-wiki.py --class high
  build-wiki.py --dry-run
"""
import argparse, json, os, re, subprocess, sys
from datetime import date, datetime
from pathlib import Path

ROSTER = Path("/opt/scripts/roster.csv")
WORK = Path("/var/lib/wiki-build")
PUBLIC = Path("/srv/wiki")
GITEA = "127.0.0.1:3000"
TERM = os.environ.get("TERM_NAME", "2026-fall")


def sh(*args, cwd=None, check=False):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"{' '.join(args)}\n{r.stderr}")
    return r.stdout.strip()


def cred():
    return Path("/opt/scripts/gitea-admin.txt").read_text().strip()


# ── 마커 구간 치환 ────────────────────────────────────────────────
def put_section(text: str, name: str, body: str) -> str:
    """마커 구간을 body 로 교체. 없으면 문서 끝에 추가."""
    begin, end = f"<!-- auto:{name} -->", f"<!-- /auto:{name} -->"
    block = f"{begin}\n{body.rstrip()}\n{end}"
    pat = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.S)
    if pat.search(text):
        return pat.sub(lambda _: block, text)
    return (text.rstrip() + "\n\n" + block + "\n") if text.strip() else block + "\n"


def read_or_seed(path: Path, seed: str) -> str:
    """페이지가 없으면 씨앗(제목 + LLM 이 채울 자리)을 만든다."""
    if path.exists():
        return path.read_text(encoding="utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    return seed


# ── 수집 (결정적) ────────────────────────────────────────────────
GITEA_REPOS = Path("/var/lib/gitea/data/gitea-repositories")


def collect(acct: str, since: str, days: int = 7) -> dict:
    """활동 수집. **커밋에 의존하지 않는다** — git 은 4주차에 배우므로
    1~3주차에는 커밋이 구조적으로 0건이다. 파일 변경이 1차 신호이고
    커밋은 그 위에 얹히는 부가 정보다.

    커밋은 **두 곳**에서 온다. SSH/Codex 로 만든 커밋은 학생 홈의 워킹 카피
    (`/home/<acct>/project/.git`)에 남고, 1주차처럼 서버 접속 없이 Gitea
    웹 업로드로만 만든 커밋은 그 워킹 카피에 전혀 반영되지 않는다 — Gitea의
    베어 저장소에만 존재한다. 홈 디렉터리만 보면 1주차 활동이 통째로
    0건으로 잡힌다(2026-08-29 설계 검토 중 발견). 그래서 베어 저장소도
    반드시 같이 본다."""
    home = Path("/home") / acct
    proj = home / "project"
    out = {"account": acct, "commits": [], "folders": [], "pages": 0,
           "skills": [], "touched": [], "uncommitted": 0}
    seen = set()

    def add_commits(log: str):
        for l in log.splitlines():
            l = l.strip()
            if l and l not in seen:
                seen.add(l)
                out["commits"].append(l)

    if (proj / ".git").is_dir():
        # root 가 학생 소유 저장소를 읽으면 git 이 dubious ownership 으로 거부한다.
        # 소유자로 실행해 우회한다 (읽기 전용이므로 안전).
        add_commits(sh("sudo", "-u", acct, "-H", "git", "-C", str(proj),
                       "log", f"--since={since}", "--pretty=%s"))
    bare = GITEA_REPOS / acct / "project.git"
    if bare.is_dir():
        # 베어 저장소는 gitea 시스템 계정 소유 — 같은 계정으로 읽는다.
        add_commits(sh("sudo", "-u", "gitea", "git", "-C", str(bare),
                       "log", f"--since={since}", "--pretty=%s"))
    if proj.is_dir():
        out["folders"] = sorted(
            p.name for p in proj.iterdir()
            if p.is_dir() and p.name not in {".git", "rules", "public"})
    pages = Path("/srv/pages") / acct
    if pages.is_dir():
        out["pages"] = sum(1 for _ in pages.rglob("*") if _.is_file())
    sk = home / ".codex" / "skills"
    if sk.is_dir():
        out["skills"] = sorted(p.name for p in sk.iterdir())

    # 최근 바뀐 파일 — 커밋 여부와 무관하게 "무엇을 만졌나"를 잡는다
    if proj.is_dir():
        found = sh("find", str(proj), "-type", "f", "-mtime", f"-{days}",
                   "-not", "-path", "*/.git/*", "-not", "-name", "MY-SERVER.md",
                   "-not", "-name", "SERVER-RULES.md", "-not", "-path", "*/rules/*",
                   "-printf", "%P\n")
        out["touched"] = sorted(f for f in found.splitlines() if f.strip())[:40]
    # 아직 커밋 안 한 변경 — 4주차 이후 "커밋 습관" 지표가 된다
    if (proj / ".git").is_dir():
        st = sh("sudo", "-u", acct, "-H", "git", "-C", str(proj), "status", "--short")
        out["uncommitted"] = len([l for l in st.splitlines() if l.strip()])
    return out


def roster(cls=None):
    rows = []
    if not ROSTER.exists():
        return rows
    for i, line in enumerate(ROSTER.read_text(encoding="utf-8").splitlines()):
        if i == 0 or not line.strip():
            continue
        f = line.split(",")
        if len(f) < 3 or not f[1].strip() or f[0].startswith("⟪"):
            continue
        if cls and f[0].strip() != cls:
            continue
        rows.append({"class": f[0].strip(), "account": f[1].strip()})
    return rows


def classes():
    return sorted({r["class"] for r in roster()})


# ── 반 위키 빌드 ─────────────────────────────────────────────────
def build_class(cls: str, week: int, today: str, since: str, dry: bool):
    repo = f"class-wiki-{cls}"
    dir_ = WORK / cls
    print(f"── {cls} 반 (w{week:02d}) ──")

    url = f"http://{cred()}@{GITEA}/{cls}/{repo}.git"
    if not (dir_ / ".git").is_dir():
        if dir_.exists():
            sh("rm", "-rf", str(dir_))
        dir_.parent.mkdir(parents=True, exist_ok=True)
        if subprocess.run(["git", "clone", "-q", url, str(dir_)],
                          capture_output=True).returncode:
            print(f"  ! 저장소를 못 열었습니다: {cls}/{repo}")
            return
    else:
        sh("git", "-C", str(dir_), "pull", "-q", "--ff-only", url, "main")
    sh("git", "-C", str(dir_), "config", "user.name", "AITF 위키봇")
    sh("git", "-C", str(dir_), "config", "user.email", "wiki@class.local")

    # ── 1. raw 층 — 사실. 한 번 쓰면 고치지 않는다 ──
    raws = [collect(r["account"], since) for r in roster(cls)]
    raw_dir = dir_ / "raw"
    raw_dir.mkdir(exist_ok=True)
    (raw_dir / f"{TERM}-w{week:02d}.json").write_text(
        json.dumps({"week": week, "date": today, "class": cls, "students": raws},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    # ── 2. wiki 층 — 누적·갱신 ──
    skill_use: dict[str, list[str]] = {}
    folder_use: dict[str, list[str]] = {}

    for r in raws:
        a = r["account"]
        p = dir_ / "students" / f"{a}.md"
        seed = (f"# {a}\n\n"
                f"<!-- 이 아래 문단은 사람·LLM 이 씁니다. 자동 생성이 건드리지 않습니다. -->\n"
                f"## 어떤 학생인가\n\n(아직 기록 없음)\n\n")
        text = read_or_seed(p, seed)

        # 활동 표는 **raw/ 에서 재생성한다.** 이전 마크다운을 파싱하면 형식이 바뀔 때
        # 구 형식 행이 남는다. raw 가 불변 원천이므로 여기서만 읽는다.
        rows = []
        for rf in sorted((dir_ / "raw").glob(f"{TERM}-w*.json")):
            try:
                d = json.loads(rf.read_text(encoding="utf-8"))
            except Exception:
                continue
            me = next((x for x in d.get("students", []) if x["account"] == a), None)
            if not me:
                continue
            rows.append(
                f"| {d['week']} | {len(me.get('touched', []))} | {len(me['commits'])} | "
                f"{' '.join(f'`{f}`' for f in me['folders']) or '—'} | {me['pages']} |")
        body = ("### 주차별 활동\n\n"
                "| 주 | 바꾼 파일 | 커밋 | 폴더 | 작품 |\n|---|---|---|---|---|\n"
                + "\n".join(rows))
        if r["touched"]:
            body += ("\n\n### 이번 주 만진 파일\n\n"
                     + "\n".join(f"- `{t}`" for t in r["touched"][:15]))
            if len(r["touched"]) > 15:
                body += f"\n- … 외 {len(r['touched'])-15}개"
        if r["commits"]:
            body += "\n\n### 이번 주 커밋\n\n" + "\n".join(f"- {c}" for c in r["commits"])
        if r["uncommitted"]:
            body += f"\n\n> 아직 커밋하지 않은 변경 {r['uncommitted']}건이 있어요."
        if r["skills"]:
            body += "\n\n### 쓰는 스킬\n\n" + " · ".join(
                f"[{sk}](../skills/{sk}.md)" for sk in r["skills"])
        p.write_text(put_section(text, "활동", body), encoding="utf-8")

        for s in r["skills"]:
            skill_use.setdefault(s, []).append(a)
        for f in r["folders"]:
            folder_use.setdefault(f, []).append(a)

    # 스킬 엔티티 페이지 — 링크 그래프의 간선이 여기서 생긴다
    for s, users in skill_use.items():
        p = dir_ / "skills" / f"{s}.md"
        seed = (f"# {s}\n\n"
                f"<!-- 이 아래는 사람·LLM 이 씁니다. -->\n"
                f"## 뭘 하는 스킬인가\n\n(아직 기록 없음)\n\n"
                f"## 쓸 때 팁\n\n(아직 기록 없음)\n\n")
        text = read_or_seed(p, seed)
        body = ("### 우리 반에서 쓰는 사람\n\n"
                + "\n".join(f"- [{u}](../students/{u}.md)" for u in sorted(users)))
        p.write_text(put_section(text, "사용", body), encoding="utf-8")

    # 프로젝트(폴더) 엔티티 페이지
    for f, users in folder_use.items():
        p = dir_ / "projects" / f"{f}.md"
        seed = (f"# {f}\n\n<!-- 이 아래는 사람·LLM 이 씁니다. -->\n"
                f"## 무엇을 만드는 폴더인가\n\n(아직 기록 없음)\n\n")
        text = read_or_seed(p, seed)
        body = ("### 만든 사람\n\n"
                + "\n".join(f"- [{u}](../students/{u}.md)" for u in sorted(users)))
        p.write_text(put_section(text, "만든이", body), encoding="utf-8")

    # index.md — 카탈로그
    def listing(sub, label):
        d = dir_ / sub
        if not d.is_dir():
            return ""
        items = sorted(p.name for p in d.glob("*.md"))
        if not items:
            return ""
        return f"\n### {label}\n\n" + "\n".join(
            f"- [{i[:-3]}]({sub}/{i})" for i in items)

    idx = read_or_seed(dir_ / "index.md", f"# {cls} 반 위키 — 목차\n\n")
    (dir_ / "index.md").write_text(put_section(
        idx, "목차",
        (listing("students", "학생") + listing("skills", "스킬")
         + listing("projects", "프로젝트") + listing("concepts", "개념")).strip()
        or "(아직 페이지 없음)"), encoding="utf-8")

    # log.md — 시간순 append (grep 가능한 접두사)
    logp = dir_ / "log.md"
    log = logp.read_text(encoding="utf-8") if logp.exists() else "# 기록\n\n"
    entry = (f"## [{today}] ingest | {week}주차 — "
             f"학생 {len(raws)}명, 커밋 {sum(len(r['commits']) for r in raws)}건")
    # 같은 주차 줄만 교체한다 (날짜로 판정하면 같은 날 여러 주차가 누락된다)
    keep = [l for l in log.splitlines()
            if not re.match(rf"^## \[.*\] ingest \| {week}주차 ", l)]
    log = "\n".join(keep).rstrip() + "\n\n" + entry + "\n"
    logp.write_text(log, encoding="utf-8")

    # AGENTS.md — 스키마 (LLM 을 위키 관리자로 만드는 설정 파일)
    schema = Path("/opt/harness/wiki-AGENTS.md")
    if schema.exists():
        (dir_ / "AGENTS.md").write_text(schema.read_text(encoding="utf-8"), encoding="utf-8")

    # README — 입구
    (dir_ / "README.md").write_text(
        f"# {cls} 반 위키\n\n"
        "우리 반이 배우고 만든 것이 여기 쌓입니다. **프로젝트를 하다 막히면 여기서 먼저 찾아보세요** — "
        "같은 걸 먼저 해본 친구가 있을 수 있어요.\n\n"
        "- [목차](index.md) — 모든 페이지\n"
        "- [기록](log.md) — 언제 무엇이 쌓였나\n"
        "- `raw/` — 원천 자료(자동 수집). 위키 페이지는 이걸 바탕으로 자랍니다\n\n"
        "> 계정 ID만 기록합니다. 실명·연락처는 들어가지 않습니다.\n",
        encoding="utf-8")

    # ── 커밋 ──
    if dry:
        print("  (dry-run)")
        print(sh("git", "-C", str(dir_), "status", "--short"))
        return
    sh("git", "-C", str(dir_), "add", "-A")
    if subprocess.run(["git", "-C", str(dir_), "diff", "--cached", "--quiet"]).returncode:
        sh("git", "-C", str(dir_), "commit", "-q", "-m", f"{week}주차 자동 기록 ({today})")
        # origin 이 아니라 매번 cred() 로 만든 url 로 민다 — clone 시점의 origin 에는
        # 그때의 관리자 비밀번호가 박혀 있어, 비밀번호를 바꾸면 조용히 push 만 실패한다
        # (2026-08-30 실측: 비밀번호 변경 후 high·archive 만 실패, 당일 재클론된 mid 만 성공).
        ok = subprocess.run(["git", "-C", str(dir_), "push", "-q", url, "HEAD:main"],
                            capture_output=True).returncode == 0
        print("  push 완료" if ok else "  ! push 실패")
    else:
        print("  변경 없음")

    # ── 학생 읽기 사본 ──
    pub = PUBLIC / cls
    sh("install", "-d", "-o", "root", "-g", f"cls-{cls}", "-m", "750", str(pub))
    sh("rsync", "-a", "--delete", "--exclude", ".git", f"{dir_}/", f"{pub}/")
    sh("chgrp", "-R", f"cls-{cls}", str(pub))
    sh("chmod", "-R", "g+rX,o-rwx", str(pub))
    for r in roster(cls):
        h = Path("/home") / r["account"]
        if h.is_dir():
            sh("ln", "-sfn", str(pub), str(h / "class-wiki"))
            sh("chown", "-h", f"{r['account']}:", str(h / "class-wiki"))
    print("  학생 읽기 경로 갱신: ~/class-wiki")


def build_archive(week: int, today: str, dry: bool):
    print("── 통합 아카이브 ──")
    dir_ = WORK / "_archive"
    url = f"http://{cred()}@{GITEA}/archive/class-archive.git"
    if not (dir_ / ".git").is_dir():
        if dir_.exists():
            sh("rm", "-rf", str(dir_))
        if subprocess.run(["git", "clone", "-q", url, str(dir_)],
                          capture_output=True).returncode:
            print("  ! 저장소를 못 열었습니다")
            return
    else:
        sh("git", "-C", str(dir_), "pull", "-q", "--ff-only", url, "main")
    sh("git", "-C", str(dir_), "config", "user.name", "AITF 위키봇")
    sh("git", "-C", str(dir_), "config", "user.email", "wiki@class.local")

    lines = []
    for c in classes():
        src = WORK / c / "raw" / f"{TERM}-w{week:02d}.json"
        if not src.exists():
            continue
        d = json.loads(src.read_text(encoding="utf-8"))
        dst = dir_ / TERM / c
        dst.mkdir(parents=True, exist_ok=True)
        (dst / f"w{week:02d}.md").write_text(
            f"# {week}주차 — {c} 반\n\n> {today} 자동 생성 · 계정 ID만\n\n"
            "| 계정 | 바꾼 파일 | 커밋 | 폴더 | 작품 |\n|---|---|---|---|---|\n"
            + "\n".join(f"| `{s['account']}` | {len(s.get('touched', []))} | "
                        f"{len(s['commits'])} | "
                        f"{' '.join(s['folders']) or '—'} | {s['pages']} |"
                        for s in d["students"]) + "\n",
            encoding="utf-8")
        lines.append(f"- [{c} {week}주차]({TERM}/{c}/w{week:02d}.md) — "
                     f"학생 {len(d['students'])}명")

    idx = read_or_seed(dir_ / "README.md", "# 수업 아카이브\n\n기수별·반별 기록입니다.\n\n")
    prev = re.search(r"<!-- auto:목록 -->(.*?)<!-- /auto:목록 -->", idx, re.S)
    keep = [l for l in (prev.group(1).splitlines() if prev else []) if l.startswith("- [")]
    for l in lines:
        key = l.split("]")[0]
        keep = [k for k in keep if not k.startswith(key)]
        keep.append(l)
    (dir_ / "README.md").write_text(
        put_section(idx, "목록", "\n".join(sorted(set(keep)))), encoding="utf-8")

    if dry:
        print("  (dry-run)")
        return
    sh("git", "-C", str(dir_), "add", "-A")
    if subprocess.run(["git", "-C", str(dir_), "diff", "--cached", "--quiet"]).returncode:
        sh("git", "-C", str(dir_), "commit", "-q", "-m", f"{week}주차 아카이브 ({today})")
        # origin 이 아니라 매번 cred() 로 만든 url 로 민다 — clone 시점의 origin 에는
        # 그때의 관리자 비밀번호가 박혀 있어, 비밀번호를 바꾸면 조용히 push 만 실패한다
        # (2026-08-30 실측: 비밀번호 변경 후 high·archive 만 실패, 당일 재클론된 mid 만 성공).
        ok = subprocess.run(["git", "-C", str(dir_), "push", "-q", url, "HEAD:main"],
                            capture_output=True).returncode == 0
        print("  push 완료" if ok else "  ! push 실패")
    else:
        print("  변경 없음")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", type=int)
    ap.add_argument("--class", dest="cls")
    ap.add_argument("--since", default="24 hours ago")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    week = a.week
    if week is None:
        # term_calendar 가 확정된 주차만 안다 — 휴일이 아닌 12번의 실제 수업일로
        # 계산한다(연속 날짜 나누기가 아니라). 아직 미설정이면 기존 방식으로 폴백.
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import term_calendar
        week = term_calendar.week_of()
        if week is None:
            if term_calendar.is_after_course():
                print("과정 종료일이 지났다 — 위키를 만들지 않는다 (term-calendar.json 참고)")
                return 0
            start = ""
            env = Path("/opt/scripts/hub.env")
            if env.exists():
                m = re.search(r"^COURSE_START=(.*)$", env.read_text(), re.M)
                start = (m.group(1).strip() if m else "")
            if start:
                d0 = datetime.strptime(start, "%Y-%m-%d").date()
                week = max(0, (date.today() - d0).days // 7 + 1)
            else:
                week = 0

    today = date.today().isoformat()
    WORK.mkdir(parents=True, exist_ok=True)
    for c in classes():
        if a.cls and c != a.cls:
            continue
        build_class(c, week, today, a.since, a.dry_run)
    build_archive(week, today, a.dry_run)
    print(f"완료 — w{week:02d}")


if __name__ == "__main__":
    main()
