#!/bin/bash
# 테스트 계정을 "방금 생성된 계정"과 동일한 상태로 완전 리셋 — specs/130
#
# reset-home.sh와의 차이: reset-home.sh는 실제 학생용이라 .git·.bashrc·
# git-credentials를 일부러 보존한다(안 그러면 학생이 push를 못 함). 이 스크립트는
# 반대다 — 테스트 계정은 매번 "1주차 첫날"과 완전히 같아야 하므로 그것들까지 지우고
# 처음부터 다시 배선한다.
#
# 안전장치: 계정명이 accounts.csv 에 없거나 "test/bash/demo" 패턴이 아니면 중단한다.
# 실제 학생 계정을 실수로 밀어버리는 사고를 막기 위함이다.
#
# 사용: sudo reset-test-account.sh <계정>
set -euo pipefail
U="${1:?사용: reset-test-account.sh <테스트계정>}"
cd /opt/scripts

[[ "$U" =~ ^(test|bash|demo)[a-z0-9]*$ ]] || {
  echo "거부: '$U'는 테스트 계정 이름 규칙(test*/bash*/demo*)에 맞지 않습니다."
  echo "실제 학생 계정(mid01 등)을 이 스크립트로 지우는 사고를 막기 위한 안전장치입니다."
  exit 1
}
[ -d "/home/$U" ] || { echo "계정 없음: $U — 먼저 create-accounts.sh 로 생성하세요"; exit 1; }

echo "── 1. 실행 중인 프로세스 정리 ──"
loginctl terminate-user "$U" 2>/dev/null || true
pkill -u "$U" 2>/dev/null || true
sleep 1

echo "── 2. 홈 디렉토리 완전 초기화 (.git·.bashrc 포함) ──"
find "/home/$U" -mindepth 1 -maxdepth 1 -exec rm -rf {} +

# 셸 기본 파일을 먼저 깐다. /opt/template-home 에는 project 와 .codex 만 들어
# 있어서, 이걸 건너뛰면 .bash_profile 이 없는 홈이 만들어진다.
# 그러면 SSH 로그인이 .bashrc 를 아예 읽지 않아 **tmux 자동 진입도 PATH 도
# 죽는다** — 리셋한 계정만 실제 학생과 다르게 동작해서, 리허설이 거짓 신호를
# 준다. (2026-08-28 학원 현장에서 test01 이 이 상태로 발견됨)
rsync -a /etc/skel/ "/home/$U/"
rsync -a /opt/template-home/ "/home/$U/"
chown -R "$U": "/home/$U"
chmod 700 "/home/$U"

# tmux 자동 진입 재기입 (create-accounts.sh 의 배선을 그대로 재현)
grep -q 'tmux new' "/home/$U/.bashrc" 2>/dev/null || \
  echo '[ -z "$TMUX" ] && tmux new -A -s main' >> "/home/$U/.bashrc"
chown "$U": "/home/$U/.bashrc"

echo "── 3. 작품관 심링크 재생성 ──"
install -d -o "$U" -g "$U" -m 755 "/srv/pages/$U"
find "/srv/pages/$U" -mindepth 1 -delete   # 이전 테스트에서 올린 결과물 제거
restorecon "/srv/pages/$U" 2>/dev/null || true
ln -sfn "/srv/pages/$U" "/home/$U/project/public"
chown -h "$U": "/home/$U/project/public"

echo "── 4. 하네스 재배선 (AGENTS.md·codex 설정·스킬) ──"
./link-harness.sh "$U"

echo "── 4-1. 규칙 문서 복구 (모노레포 rules/) ──"
/home/opc/projects/AITF/scripts/push-rule.sh --sync "$U" 2>/dev/null || echo "  (push-rule 생략 — 배포된 규칙 없음)"

echo "── 5. git 신원 재설정 (Gitea 토큰이 있는 경우만) ──"
if grep -q "^${U}," gitea-tokens.csv 2>/dev/null; then
  tok=$(grep "^${U}," gitea-tokens.csv | cut -d, -f2)
  sudo -u "$U" git config --global user.name  "$U"
  sudo -u "$U" git config --global user.email "$U@class.local"
  sudo -u "$U" git config --global credential.helper store
  echo "http://$U:$tok@127.0.0.1:3000" | sudo -u "$U" tee "/home/$U/.git-credentials" > /dev/null
  sudo -u "$U" chmod 600 "/home/$U/.git-credentials"
  P="/home/$U/project"
  sudo -u "$U" git -C "$P" init -b main
  sudo -u "$U" git -C "$P" remote add origin "http://127.0.0.1:3000/$U/project.git"
  echo "  git 배선 완료"
else
  echo "  gitea-tokens.csv 에 $U 없음 — git 배선 건너뜀 (4주차 이전 테스트라면 정상)"
fi

echo "── 6. 포트 대역 재확인 ──"
if grep -q "^${U}," accounts.csv 2>/dev/null; then
  ./alloc-ports.sh accounts.csv --deploy > /dev/null
  echo "  포트 대역 재배포 완료"
else
  echo "  accounts.csv 에 $U 없음 — 포트 배선 건너뜀"
fi

echo
echo "══ 리셋 완료: $U 는 이제 '방금 생성된 계정'과 동일합니다 ══"
echo "  남는 것(의도적): 서버 로그·OpenAI API 사용량(외부 대시보드 기준이라 로컬 리셋 불가)"
