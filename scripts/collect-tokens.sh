#!/bin/bash
# tokscale 학생별 토큰 사용량 수집 (cron 호출) — specs/070
# cron 예시 (/etc/cron.d/tokmon, 실제 시간표로 수정):
#   * 13-17 * * 6  root /opt/scripts/collect-tokens.sh   # 수업 시간대 1분 주기
#   */15 * * * *   root /opt/scripts/collect-tokens.sh   # 평시 15분 주기
set -uo pipefail
mkdir -p /var/lib/tokmon
chmod 700 /var/lib/tokmon

cut -d, -f1 /opt/scripts/accounts.csv | while read -r u; do
  [ -z "$u" ] && continue
  sudo -u "$u" tokscale --json --today > "/var/lib/tokmon/$u.json" 2>/dev/null
done
