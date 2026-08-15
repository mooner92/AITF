#!/bin/bash
# 반 교대 시 이전 반 잔여 프로세스 정리 — specs/080, 100 (운영 루틴)
# 사용: cleanup-class.sh <반접두사>
set -euo pipefail
CLASS="$1"

cut -d, -f1 /opt/scripts/accounts.csv | grep "^${CLASS}" | while read -r u; do
  [ -z "$u" ] && continue
  # 해당 계정의 모든 프로세스 종료 (tmux 세션·에이전트 포함) — 메모리 회수
  loginctl terminate-user "$u" 2>/dev/null || true
  pkill -u "$u" 2>/dev/null || true
done

sleep 2
echo "정리 완료. 메모리 회수 확인:"
free -h
