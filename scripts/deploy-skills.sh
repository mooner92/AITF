#!/bin/bash
# 저장소의 스킬을 서버에 배포하고 전 학생 계정에 연결한다.
#
# 경로 근거 (codex 0.147.0 바이너리 확인, 2026-08-20):
#   Codex는 $CODEX_HOME/skills 를 스캔하고, CODEX_HOME 미설정 시 ~/.codex/skills 로 폴백한다.
#   바이너리에 ".agents/skills" 문자열은 존재하지 않는다 — 일부 문서의 그 경로는 이 버전에 해당 없음.
#   따라서 /opt/harness/skills 는 "원본 보관소"일 뿐 탐색 경로가 아니며,
#   학생별 ~/.codex/skills/<name> 심링크가 있어야 실제로 인식된다.
#
# 사용:
#   ./deploy-skills.sh            # 배포 + 전 학생 연결
#   ./deploy-skills.sh --check    # 상태만 점검 (변경 없음)
set -euo pipefail

REPO_SKILLS="$(cd "$(dirname "$0")/.." && pwd)/materials/skills"
STORE=/opt/harness/skills
MODE="${1:-}"

# 학생 계정 목록 — roster.csv 가 정본이다. 계정명이 학생 메일 앞부분이라
# 이름 패턴(^(mid|high)[0-9]+$)으로는 더 이상 찾을 수 없다 (2026-08-25).
ROSTER="${ROSTER_CSV:-/opt/scripts/roster.csv}"
# roster 는 /opt/scripts(root 700) 안에 있어 일반 사용자는 못 읽는다.
# 예전에는 그 실패를 "학생 계정이 아직 없습니다"로 잘못 보고해 학생 연결을
# 조용히 건너뛰었다 (2026-09-01 발견 — 13명이 있는데 0명으로 출력).
# 읽기는 sudo 로 하고, 정말 못 읽으면 침묵하지 않고 멈춘다.
# 파이프 대신 프로세스 치환을 쓴다 — `set -e` 아래에서 `... | while read` 는
# 서브셸이 첫 실패에 통째로 죽어 목록이 조용히 비어 버린다 (2026-09-01 실측).
students() {
  sudo test -r "$ROSTER" || { echo "  ! roster 를 읽을 수 없습니다: $ROSTER" >&2; return 1; }
  local u
  while IFS=, read -r _cls u _rest; do
    if [ -n "$u" ] && id -u "$u" >/dev/null 2>&1; then echo "$u"; fi
  done < <(sudo tail -n +2 "$ROSTER")
}

if [ "$MODE" = "--check" ]; then
  echo "원본(저장소): $REPO_SKILLS"
  ls -1 "$REPO_SKILLS" | sed 's/^/  /'
  echo "보관소(서버): $STORE"
  ls -1 "$STORE" 2>/dev/null | sed 's/^/  /' || echo "  (없음)"
  echo "학생 연결 상태:"
  for u in $(students); do
    # 학생 홈은 700 이라 일반 사용자는 못 읽는다. sudo 로 세고, 실패해도
    # 스크립트가 죽지 않게 한다 (pipefail 아래에서 ls 실패가 전체를 멈춘다).
    n=$(sudo ls -1 "/home/$u/.codex/skills" 2>/dev/null | wc -l || echo 0)
    echo "  $u: $n개"
  done
  if [ -z "$(students)" ]; then echo "  (학생 계정 없음 — 명단 대기)"; fi
  exit 0
fi

# 1. 저장소 → 서버 보관소 (root 소유, 학생 읽기 전용)
sudo mkdir -p "$STORE"
for d in "$REPO_SKILLS"/*/; do
  name=$(basename "$d")
  sudo rm -rf "${STORE:?}/$name"
  sudo cp -r "$d" "$STORE/$name"
done
sudo chown -R root:root "$STORE"
sudo find "$STORE" -type d -exec chmod 755 {} \;
sudo find "$STORE" -type f -exec chmod 644 {} \;
echo "보관소 갱신: $(ls -1 "$STORE" | tr '\n' ' ')"

# 2. 각 학생의 탐색 경로에 심링크
cnt=0
for u in $(students); do
  sudo install -d -o "$u" -g "$u" -m 755 "/home/$u/.codex/skills"
  for d in "$STORE"/*/; do
    name=$(basename "$d")
    sudo ln -sfn "$d" "/home/$u/.codex/skills/$name"
    sudo chown -h "$u": "/home/$u/.codex/skills/$name"
  done
  cnt=$((cnt+1))
done
echo "학생 연결: ${cnt}명"
[ "$cnt" -eq 0 ] && echo "  (학생 계정이 아직 없습니다 — 계정 생성 후 link-harness.sh 가 자동 연결합니다)"

# 3. 강사(운영자) 계정에도 동일하게 — 수업 준비·시연용
install -d -m 755 "$HOME/.codex/skills"
for d in "$STORE"/*/; do ln -sfn "$d" "$HOME/.codex/skills/$(basename "$d")"; done
echo "강사 계정 연결 완료: $HOME/.codex/skills"
