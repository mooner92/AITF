#!/bin/bash
# 학생 홈을 템플릿으로 초기화 — specs/040
# 사용: reset-home.sh <계정>
set -euo pipefail
U="$1"
rsync -a --delete /opt/template-home/ "/home/$U/"
chown -R "$U": "/home/$U"
chmod 700 "/home/$U"
echo "초기화 완료: $U"
