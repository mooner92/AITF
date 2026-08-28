#!/bin/bash
# 학생 홈에 하네스 배포 — specs/055
# 사용: link-harness.sh <계정>
#   AGENTS.md      → 심링크 (수정 불가, 저장소에 안 딸려감)
#   config.toml    → 사본 (계정별 키가 들어갈 수 있어 심링크 아님)
#   skills/*       → 심링크 (공용 스킬. 학생 자작 스킬은 같은 폴더에 실제 디렉토리로 공존)
#
# 스킬 경로 근거: Codex는 $CODEX_HOME/skills 를 스캔하고, CODEX_HOME 미설정 시
# ~/.codex/skills 로 폴백한다 (codex 0.147.0 바이너리 확인).
# /opt/harness/skills 는 탐색 경로가 아니므로 반드시 여기로 링크해야 인식된다.
set -euo pipefail
U="$1"
H="/home/$U"

# 하네스 지시서
ln -sfn /opt/harness/AGENTS.md "$H/project/AGENTS.md"
chown -h "$U": "$H/project/AGENTS.md"

# Codex 설정
install -d -o "$U" -g "$U" -m 700 "$H/.codex"
install -o "$U" -g "$U" -m 600 /opt/harness/codex-config.toml "$H/.codex/config.toml"

# 공용 스킬 — 학생별로 심링크. 원본은 root 소유라 학생이 고칠 수 없고,
# 서버에서 스킬을 고치면 전원에게 즉시 반영된다.
install -d -o "$U" -g "$U" -m 755 "$H/.codex/skills"
for s in /opt/harness/skills/*/; do
  [ -d "$s" ] || continue
  name=$(basename "$s")
  ln -sfn "$s" "$H/.codex/skills/$name"
  chown -h "$U": "$H/.codex/skills/$name"
done

echo "하네스 배포 완료: $U (스킬 $(ls -1 /opt/harness/skills 2>/dev/null | wc -l)개 연결)"

# 작품관 발행 경로 — project/public 에 넣으면 바로 인터넷에 뜬다 (3주차)
# 2026-08-28: 학생 계정 5개 전부 이 링크가 없는 채로 발견됐다. check-account.sh 가 잡았다.
install -d -o "$U" -g "$U" -m 755 "/srv/pages/$U"
ln -sfn "/srv/pages/$U" "$H/project/public"
chown -h "$U": "$H/project/public"
