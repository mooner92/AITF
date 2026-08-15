#!/bin/bash
# 학생 단위 복구 (사고 대응) — specs/080
# 사용: restore-student.sh <계정> <스냅샷디렉토리명>
set -euo pipefail
U="$1"; SNAP="/srv/snapshots/$2"
[ -d "$SNAP/homes/$U" ] || { echo "스냅샷 없음: $SNAP/homes/$U"; exit 1; }
rsync -a --delete "$SNAP/homes/$U/" "/home/$U/"
rsync -a --ignore-existing /opt/template-home/ "/home/$U/"   # 스냅샷에서 제외된 node_modules 재충전
chown -R "$U": "/home/$U"
chmod 700 "/home/$U"
echo "복구 완료: $U ← $2"
