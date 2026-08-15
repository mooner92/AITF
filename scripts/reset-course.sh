#!/bin/bash
# 종강 후 아카이브 + 초기화 안내 — specs/080
# 파괴적 명령은 일부러 자동 실행하지 않는다 — 출력을 육안 확인 후 직접 실행
set -euo pipefail
STAMP=$(date +%F)
tar czf "/srv/backup/course_${STAMP}.tar.gz" /srv/snapshots /var/lib/tokmon
echo "아카이브: /srv/backup/course_${STAMP}.tar.gz"
echo
echo "학생 홈을 템플릿으로 되돌리려면:"
echo "  cut -d, -f1 /opt/scripts/accounts.csv | xargs -n1 /opt/scripts/reset-home.sh"
echo "계정까지 삭제하려면 (되돌릴 수 없음):"
echo "  cut -d, -f1 /opt/scripts/accounts.csv | xargs -n1 sudo userdel -r"
