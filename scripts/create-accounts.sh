#!/bin/bash
# CSV 기반 학생 계정 일괄 생성 — specs/040
# 입력: /opt/scripts/accounts.csv (헤더 없음, "계정ID,비밀번호") — 서버에만 존재, repo 커밋 금지
# 실행: root 권한 필요
set -euo pipefail
cd /opt/scripts

# 학생 1인당 메모리 상한 — 인원 확정 후 산정 (예산: 총24G - 기존서비스~5G - 운영자~3G = 16G / 동시 인원)
MEMORY_MAX="${MEMORY_MAX:-1300M}"
MEMORY_HIGH="${MEMORY_HIGH:-1024M}"

while IFS=, read -r u p; do
  [ -z "$u" ] && continue
  useradd -m "$u" 2>/dev/null || echo "skip: $u (이미 존재)"
  echo "$u:$p" | chpasswd
  chmod 700 "/home/$u"                       # 학생 상호 열람 차단

  # 로그인하면 tmux 자동 진입 (세션 유지 + 마우스 스크롤은 /etc/tmux.conf)
  grep -q 'tmux new' "/home/$u/.bashrc" || \
    echo '[ -z "$TMUX" ] && tmux new -A -s main' >> "/home/$u/.bashrc"

  # 메모리·프로세스 상한 — 드롭인이라 로그인 전에도 적용되고 재부팅에도 유지됨
  uid=$(id -u "$u")
  mkdir -p "/etc/systemd/system/user-${uid}.slice.d"
  printf '[Slice]\nMemoryMax=%s\nMemoryHigh=%s\nTasksMax=256\n' "$MEMORY_MAX" "$MEMORY_HIGH" \
    > "/etc/systemd/system/user-${uid}.slice.d/limit.conf"
done < accounts.csv

systemctl daemon-reload
echo "완료. 검증: 테스트 계정 로그인 → tmux 진입 / sudo 거부 / 타 계정 홈 열람 거부"
