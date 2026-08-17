#!/bin/bash
# 학생 홈에 하네스 배포 — specs/055
# 사용: link-harness.sh <계정>
#   AGENTS.md      → 심링크 (수정 불가, 저장소에 안 딸려감)
#   config.toml    → 사본 (계정별 키가 들어갈 수 있어 심링크 아님)
set -euo pipefail
U="$1"
ln -sfn /opt/harness/AGENTS.md "/home/$U/project/AGENTS.md"
chown -h "$U": "/home/$U/project/AGENTS.md"
install -d -o "$U" -g "$U" -m 700 "/home/$U/.codex"
install -o "$U" -g "$U" -m 600 /opt/harness/codex-config.toml "/home/$U/.codex/config.toml"
echo "하네스 배포 완료: $U"
