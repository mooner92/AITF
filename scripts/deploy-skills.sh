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
students() {
  [ -f "$ROSTER" ] || return 0
  awk -F, 'NR>1 && $2!="" {print $2}' "$ROSTER" | while read -r u; do
    id -u "$u" >/dev/null 2>&1 && echo "$u"
  done
}

if [ "$MODE" = "--check" ]; then
  echo "원본(저장소): $REPO_SKILLS"
  ls -1 "$REPO_SKILLS" | sed 's/^/  /'
  echo "보관소(서버): $STORE"
  ls -1 "$STORE" 2>/dev/null | sed 's/^/  /' || echo "  (없음)"
  echo "학생 연결 상태:"
  for u in $(students); do
    n=$(ls -1 "/home/$u/.codex/skills" 2>/dev/null | wc -l)
    echo "  $u: $n개"
  done
  [ -z "$(students)" ] && echo "  (학생 계정 없음 — 명단 대기)"
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
