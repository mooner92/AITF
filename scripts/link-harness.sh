#!/bin/bash
# 학생 홈에 하네스 심볼릭 링크 걸기 — specs/055
# 사용: link-harness.sh <계정>
set -euo pipefail
U="$1"
ln -sfn /opt/harness/AGENTS.md "/home/$U/project/AGENTS.md"
ln -sfn /opt/harness/GEMINI.md "/home/$U/project/GEMINI.md"
chown -h "$U": "/home/$U/project/AGENTS.md" "/home/$U/project/GEMINI.md"
echo "하네스 링크 완료: $U"
