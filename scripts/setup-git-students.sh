#!/bin/bash
# 학생 git 신원·인증·remote 사전 주입 — specs/060
# 선행: Gitea에 학생 계정·저장소 생성 완료, 학생별 토큰 발급 완료
# 토큰은 /opt/scripts/gitea-tokens.csv (계정ID,토큰) — 서버에만 존재, repo 커밋 금지
set -euo pipefail
cd /opt/scripts

while IFS=, read -r u tok; do
  [ -z "$u" ] && continue
  sudo -u "$u" git config --global user.name  "$u"
  sudo -u "$u" git config --global user.email "$u@class.local"
  sudo -u "$u" git config --global credential.helper store
  echo "http://$u:$tok@127.0.0.1:3000" | sudo -u "$u" tee "/home/$u/.git-credentials" > /dev/null
  sudo -u "$u" chmod 600 "/home/$u/.git-credentials"

  # 프로젝트 폴더 git init + remote — 학생은 add/commit/push 3줄만 치면 됨
  P="/home/$u/project"
  if [ -d "$P" ] && [ ! -d "$P/.git" ]; then
    sudo -u "$u" git -C "$P" init -b main
    sudo -u "$u" git -C "$P" remote add origin "http://127.0.0.1:3000/$u/project.git"
  fi
done < gitea-tokens.csv

echo "완료. 검증: 학생 계정에서 push 시 비밀번호 안 묻는지 / .env가 status에 안 뜨는지"
