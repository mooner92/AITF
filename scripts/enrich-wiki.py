#!/usr/bin/env python3
"""위키 서술 보강 — LLM 통합 패스 (specs/180)

build-wiki.py 가 만든 `raw/` 사실을 읽고, 엔티티 페이지의 **마커 밖 서술**을
로컬 모델로 채운다. 마커 안(자동 생성 사실)은 절대 건드리지 않는다.

설계 원칙:
  · 이 스크립트가 실패해도 위키는 이미 완성돼 있다 (build-wiki.py 가 사실을 다 씀).
    LLM 은 "덤"이지 의존 대상이 아니다.
  · 모델이 지어낸 내용이 학생에게 사실처럼 보이면 안 되므로, 서술은
    **raw 에 실제로 있는 항목만** 근거로 쓰게 하고 출처를 함께 남긴다.
  · 이미 사람이 쓴 서술이 있으면 덮어쓰지 않는다 (--force 로만).

설정: /opt/scripts/wiki-llm.env
    LLM_URL=https://⟪모델서버⟫/v1        OpenAI 호환 엔드포인트
    LLM_MODEL=qwen3.6-27b
    LLM_KEY=⟪키⟫                        (없으면 헤더 생략)

사용:
    enrich-wiki.py --class high            비어 있는 서술만 채움
    enrich-wiki.py --class high --force    이미 있는 서술도 갱신
    enrich-wiki.py --class high --dry-run  호출만 하고 저장 안 함
"""
import argparse, json, os, re, subprocess, sys, urllib.request
from pathlib import Path

WORK = Path("/var/lib/wiki-build")
ENV = Path("/opt/scripts/wiki-llm.env")
PLACEHOLDER = "(아직 기록 없음)"
TIMEOUT = 60


def load_env():
    cfg = {}
    if ENV.exists():
        for line in ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip()
    return cfg


def ask(cfg, system, user):
    """OpenAI 호환 /chat/completions 호출. 실패하면 None (위키는 그대로 둔다)."""
    url = cfg.get("LLM_URL", "").rstrip("/") + "/chat/completions"
    body = json.dumps({
        "model": cfg.get("LLM_MODEL", "qwen"),
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "temperature": 0.3, "max_tokens": 400,
    }).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    if cfg.get("LLM_KEY"):
        req.add_header("Authorization", f"Bearer {cfg['LLM_KEY']}")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            d = json.loads(r.read())
        return d["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"  ! 모델 호출 실패: {e}")
        return None


SYSTEM = """너는 중고등학생 코딩 수업의 반 위키를 관리한다. 한국어 해요체로 쓴다.

반드시 지킨다:
- 주어진 '사실' 목록에 **없는 내용은 절대 쓰지 않는다.** 모르면 모른다고 쓴다.
- 학생을 비교하거나 평가하지 않는다. 순위·우열·칭찬·질책 모두 금지.
  "누가 더 잘한다"가 아니라 "누가 무엇을 해봤다"로만 쓴다.
- 계정 ID만 쓴다. 실명·이메일은 쓰지 않는다.
- 2~4문장. 짧게."""


def has_prose(text, heading):
    """해당 소제목 아래에 사람이 쓴 서술이 이미 있나."""
    m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        return False
    return PLACEHOLDER not in m.group(1) and bool(m.group(1).strip())


def put_prose(text, heading, prose):
    def repl(m):
        return f"## {heading}\n\n{prose}\n\n"
    return re.sub(rf"^## {re.escape(heading)}\s*$.*?(?=^## |\Z)", repl,
                  text, count=1, flags=re.S | re.M)


def facts_for_skill(raws, skill):
    users = [s["account"] for w in raws for s in w["students"] if skill in s["skills"]]
    folders = sorted({f for w in raws for s in w["students"]
                      if skill in s["skills"] for f in s["folders"]})
    return (f"스킬 이름: {skill}\n"
            f"이 스킬이 설치된 계정 수: {len(set(users))}\n"
            f"이 학생들이 만든 폴더: {', '.join(folders) or '없음'}")


def facts_for_project(raws, proj):
    makers = sorted({s["account"] for w in raws for s in w["students"]
                     if proj in s["folders"]})
    files = sorted({t for w in raws for s in w["students"]
                    if proj in s["folders"] for t in s.get("touched", [])
                    if t.startswith(proj + "/")})
    return (f"폴더 이름: {proj}\n"
            f"만든 계정 수: {len(makers)}\n"
            f"그 안의 파일: {', '.join(files[:12]) or '아직 없음'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--class", dest="cls", required=True)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    cfg = load_env()
    if not cfg.get("LLM_URL"):
        print(f"모델 미설정 — {ENV} 에 LLM_URL 을 넣으세요. 위키는 그대로 둡니다.")
        return 0

    dir_ = WORK / a.cls
    if not dir_.is_dir():
        print(f"반 작업본이 없습니다: {dir_} (먼저 build-wiki.py 실행)")
        return 1

    raws = []
    for rf in sorted((dir_ / "raw").glob("*.json")):
        try:
            raws.append(json.loads(rf.read_text(encoding="utf-8")))
        except Exception:
            pass
    if not raws:
        print("raw 자료가 없습니다.")
        return 1

    changed = 0
    targets = ([(p, "뭘 하는 스킬인가", facts_for_skill(raws, p.stem))
                for p in sorted((dir_ / "skills").glob("*.md"))]
               + [(p, "무엇을 만드는 폴더인가", facts_for_project(raws, p.stem))
                  for p in sorted((dir_ / "projects").glob("*.md"))])

    for path, heading, facts in targets:
        text = path.read_text(encoding="utf-8")
        if has_prose(text, heading) and not a.force:
            print(f"  · {path.name} (이미 서술 있음 — 건너뜀)")
            continue
        prose = ask(cfg, SYSTEM,
                    f"아래 사실만 근거로 '{heading}'를 2~4문장으로 써 주세요.\n\n{facts}")
        if not prose:
            continue
        print(f"  ✓ {path.relative_to(dir_)} — {prose.splitlines()[0][:50]}…")
        if not a.dry_run:
            path.write_text(put_prose(text, heading, prose), encoding="utf-8")
            changed += 1

    if changed and not a.dry_run:
        subprocess.run(["git", "-C", str(dir_), "add", "-A"], capture_output=True)
        subprocess.run(["git", "-C", str(dir_), "commit", "-q", "-m",
                        f"서술 보강 (LLM) — {changed}개 페이지"], capture_output=True)
        ok = subprocess.run(["git", "-C", str(dir_), "push", "-q", "origin", "HEAD"],
                            capture_output=True).returncode == 0
        print("push 완료" if ok else "! push 실패")
        # 학생 읽기 사본 갱신
        subprocess.run(["rsync", "-a", "--delete", "--exclude", ".git",
                        f"{dir_}/", f"/srv/wiki/{a.cls}/"], capture_output=True)
        subprocess.run(["chgrp", "-R", f"cls-{a.cls}", f"/srv/wiki/{a.cls}"],
                       capture_output=True)
        subprocess.run(["chmod", "-R", "g+rX,o-rwx", f"/srv/wiki/{a.cls}"],
                       capture_output=True)
    print(f"완료 — {changed}개 갱신")
    return 0


if __name__ == "__main__":
    sys.exit(main())
