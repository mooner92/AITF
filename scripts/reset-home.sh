#!/bin/bash
# 학생 홈을 템플릿으로 초기화 — specs/040
# 사용: reset-home.sh <계정>
#
# --delete 를 쓰면서도 아래는 반드시 보존한다. 안 그러면 초기화 후 학생이 push를 못 한다:
#   .git/            학생 작업 히스토리 (원격에 있어도 로컬 remote 설정이 날아감)
#   .git-credentials Gitea 토큰 (사전 주입해 둔 것 — 날아가면 비밀번호를 묻는다)
#   .gitconfig       git 신원
#   .bashrc          tmux 자동 진입 + API 키 export
set -euo pipefail
U="$1"
[ -d "/home/$U" ] || { echo "계정 홈 없음: $U"; exit 1; }

rsync -a --delete \
  --exclude '.git/' \
  --exclude '.git-credentials' \
  --exclude '.gitconfig' \
  --exclude '.bashrc' \
  --exclude '.bash_history' \
  /opt/template-home/ "/home/$U/"

chown -R "$U": "/home/$U"
chmod 700 "/home/$U"
/opt/scripts/link-harness.sh "$U"
echo "초기화 완료: $U (git 설정·자격증명 보존)"
