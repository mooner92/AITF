#!/bin/bash
# 자동 위키 생성 — specs/180
#
# 수집은 한 번, 출력은 세 갈래(학생별·반별·전체). 반 저장소 하나 안에서 3층을 만든다.
#   students/<계정>/wNN.md   그 주 그 학생
#   weeks/wNN.md             그 주 반 전체
#   → archive 저장소에 반 요약 사본
#
# 원칙 (180):
#   · 계정 ID만 기록한다. 실명·메일은 넣지 않는다
#   · 다른 학생 파일의 "내용"은 담지 않는다 — 무엇을 했다는 사실만
#   · LLM 에 의존하지 않는다. 총평 문장은 나중에 선택적으로 붙인다
#   · 멱등: 같은 주를 두 번 돌려도 결과가 같다
#
# 사용:
#   build-wiki.sh              # 오늘 기준 주차, 전 반
#   build-wiki.sh --week 3     # 주차 지정
#   build-wiki.sh --class high # 반 지정
#   build-wiki.sh --dry-run    # 생성만 하고 push 하지 않음
set -euo pipefail

ROSTER=/opt/scripts/roster.csv
WORK=/var/lib/wiki-build
PUBLIC=/srv/wiki                      # 학생이 읽는 사본
GITEA=http://127.0.0.1:3000
CRED=$(cat /opt/scripts/gitea-admin.txt)
. /opt/scripts/hub.env 2>/dev/null || true
COURSE_START="${COURSE_START:-}"

WEEK=""; ONLY_CLASS=""; DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --week) WEEK="$2"; shift 2 ;;
    --class) ONLY_CLASS="$2"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    *) echo "알 수 없는 인자: $1"; exit 1 ;;
  esac
done

# 주차 계산 (개강일 기준). 개강 전이면 0 주차로 둔다.
if [ -z "$WEEK" ]; then
  if [ -n "$COURSE_START" ]; then
    s=$(date -d "$COURSE_START" +%s); n=$(date +%s)
    WEEK=$(( (n - s) / 604800 + 1 ))
    [ "$WEEK" -lt 1 ] && WEEK=0
  else
    WEEK=0
  fi
fi
WNN=$(printf 'w%02d' "$WEEK")
TODAY=$(date +%Y-%m-%d)
SINCE="${WIKI_SINCE:-24 hours ago}"      # 그날 활동 범위

md_escape() { sed 's/[<>]//g'; }

# ── 반 목록 ──
classes() {
  awk -F, 'NR>1 && $1!="" && $1!~/^⟪/ {print $1}' "$ROSTER" | sort -u
}
students_of() {
  awk -F, -v c="$1" 'NR>1 && $1==c && $2!="" {print $2}' "$ROSTER"
}

build_class() {
  local cls="$1"
  local repo="class-wiki-${cls}"
  local dir="$WORK/$cls"
  local wrote_any=0

  echo "── ${cls} 반 (${WNN}) ──"

  # 저장소 준비 (없으면 클론, 있으면 갱신)
  if [ ! -d "$dir/.git" ]; then
    rm -rf "$dir"; mkdir -p "$(dirname "$dir")"
    git clone -q "http://${CRED}@127.0.0.1:3000/${cls}/${repo}.git" "$dir" 2>/dev/null || {
      echo "  ! 저장소를 못 열었습니다: ${cls}/${repo}"; return 0; }
  else
    git -C "$dir" pull -q --ff-only 2>/dev/null || true
  fi
  git -C "$dir" config user.name  "AITF 위키봇"
  git -C "$dir" config user.email "wiki@class.local"

  mkdir -p "$dir/students" "$dir/weeks" "$dir/skills"

  local week_lines=""

  for u in $(students_of "$cls"); do
    id -u "$u" >/dev/null 2>&1 || continue
    local proj="/home/$u/project"
    local sdir="$dir/students/$u"
    mkdir -p "$sdir"

    # ── 수집 ──
    local commits="" ncommit=0 folders="" nfile=0
    if [ -d "$proj/.git" ]; then
      commits=$(git -C "$proj" log --since="$SINCE" --pretty='%s' 2>/dev/null | md_escape || true)
      ncommit=$(printf '%s' "$commits" | grep -c . || true)
    fi
    # 프로젝트 폴더 = 모노레포 최상위 디렉토리 (rules·public·.git 제외)
    if [ -d "$proj" ]; then
      folders=$(find "$proj" -maxdepth 1 -mindepth 1 -type d \
        ! -name '.git' ! -name 'rules' ! -name 'public' -printf '%f\n' 2>/dev/null | sort || true)
    fi
    [ -d "/srv/pages/$u" ] && nfile=$(find "/srv/pages/$u" -type f 2>/dev/null | wc -l)

    # ── 학생별 문서 ──
    {
      echo "# ${u} — ${WEEK}주차"
      echo
      echo "> ${TODAY} 자동 생성. 계정 ID만 기록합니다."
      echo
      echo "## 이번 주 커밋 (${ncommit}건)"
      echo
      if [ "$ncommit" -gt 0 ]; then printf '%s\n' "$commits" | sed 's/^/- /'
      else echo "- (없음)"; fi
      echo
      echo "## 내 프로젝트 폴더"
      echo
      if [ -n "$folders" ]; then printf '%s\n' "$folders" | sed 's/^/- `/;s/$/`/'
      else echo "- (아직 없음)"; fi
      echo
      echo "## 작품관"
      echo
      echo "- 공개 파일 ${nfile}개"
      echo
      echo "---"
      echo "[반 인덱스](../../README.md) · [내 기록 전체](index.md)"
    } > "$sdir/${WNN}.md"

    # ── 학생 누적 인덱스 ──
    {
      echo "# ${u} — 전체 기록"
      echo
      for f in $(ls "$sdir" | grep -E '^w[0-9]+\.md$' | sort); do
        echo "- [${f%.md}](${f})"
      done
    } > "$sdir/index.md"

    week_lines+="| \`${u}\` | ${ncommit} | $(printf '%s' "$folders" | tr '\n' ' ') | ${nfile} |"$'\n'
    wrote_any=1
  done

  # ── 반별 주차 문서 ──
  {
    echo "# ${WEEK}주차 — ${cls} 반"
    echo
    echo "> ${TODAY} 자동 생성"
    echo
    echo "| 계정 | 커밋 | 프로젝트 폴더 | 작품 |"
    echo "|---|---|---|---|"
    if [ -n "$week_lines" ]; then printf '%s' "$week_lines"
    else echo "| (활동 없음) | | | |"; fi
    echo
    echo "---"
    echo "[반 인덱스](../README.md)"
  } > "$dir/weeks/${WNN}.md"

  # ── 반 인덱스 ──
  {
    echo "# ${cls} 반 위키"
    echo
    echo "우리 반이 12주 동안 한 일이 매주 자동으로 쌓입니다."
    echo "**프로젝트를 하다 막히면 여기서 먼저 찾아보세요** — 같은 걸 먼저 해본 친구가 있을 수 있어요."
    echo
    echo "## 주차별"
    echo
    for f in $(ls "$dir/weeks" 2>/dev/null | sort); do echo "- [${f%.md}](weeks/${f})"; done
    echo
    echo "## 학생별"
    echo
    for s in $(ls "$dir/students" 2>/dev/null | sort); do echo "- [${s}](students/${s}/index.md)"; done
    echo
    echo "---"
    echo "> 계정 ID만 기록합니다. 실명·연락처는 들어가지 않습니다."
  } > "$dir/README.md"

  # ── 커밋 ──
  if [ "$DRY" -eq 1 ]; then
    echo "  (dry-run — push 안 함)"; git -C "$dir" status --short | head -5; return 0
  fi
  git -C "$dir" add -A
  if git -C "$dir" diff --cached --quiet; then
    echo "  변경 없음"
  else
    git -C "$dir" commit -q -m "${WEEK}주차 자동 기록 (${TODAY})"
    git -C "$dir" push -q origin HEAD 2>/dev/null && echo "  push 완료" || echo "  ! push 실패"
  fi

  # ── 학생이 읽는 사본 (Codex 가 직접 읽는다) ──
  install -d -o root -g "cls-${cls}" -m 750 "$PUBLIC/$cls"
  rsync -a --delete --exclude '.git' "$dir/" "$PUBLIC/$cls/"
  chgrp -R "cls-${cls}" "$PUBLIC/$cls"; chmod -R g+rX,o-rwx "$PUBLIC/$cls"
  # 학생 홈에 심링크
  for u in $(students_of "$cls"); do
    [ -d "/home/$u" ] || continue
    ln -sfn "$PUBLIC/$cls" "/home/$u/class-wiki"
    chown -h "$u": "/home/$u/class-wiki"
  done
  echo "  학생 읽기 경로 갱신: ~/class-wiki"
}

mkdir -p "$WORK"
for c in $(classes); do
  [ -n "$ONLY_CLASS" ] && [ "$c" != "$ONLY_CLASS" ] && continue
  build_class "$c"
done
echo "완료 — ${WNN}"
