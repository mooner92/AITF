#!/bin/bash
# 수업 후 반 단위 증분 스냅샷 + 진도 요약 — specs/080
# 사용: snapshot-class.sh <반접두사> <주차>   예: snapshot-class.sh mid 03 (반접두사: mid=중등, high=고등)
set -euo pipefail
CLASS="$1"; WEEK="$2"; DATE=$(date +%F)
SNAP="/srv/snapshots/${DATE}_${CLASS}_w${WEEK}"
PREV=$(ls -d /srv/snapshots/*_${CLASS}_* 2>/dev/null | tail -1 || true)

# 디스크 여유 사전 확인 — 10GB 미만이면 중단
AVAIL_GB=$(df --output=avail -BG /srv | tail -1 | tr -dc '0-9')
[ "$AVAIL_GB" -lt 10 ] && { echo "중단: /srv 잔여 ${AVAIL_GB}G < 10G — 오래된 스냅샷 정리 후 재시도"; exit 1; }

mkdir -p "$SNAP"/{homes,tokens}

cut -d, -f1 /opt/scripts/accounts.csv | grep "^${CLASS}" | while read -r u; do
  [ -z "$u" ] && continue
  # --link-dest: 이전 스냅샷과 하드링크 공유 → 변경분만 실용량 차지
  rsync -a --delete \
    --exclude node_modules --exclude .cache --exclude .npm \
    ${PREV:+--link-dest="$PREV/homes/$u"} \
    "/home/$u/" "$SNAP/homes/$u/"
  sudo -u "$u" tokscale --json > "$SNAP/tokens/$u.json" 2>/dev/null || true
done

# 진도 요약 — 수업 후 훑어보고 뒤처진 학생 파악
{
  echo "# ${DATE} · ${CLASS} · ${WEEK}주차"
  echo
  echo "| 학생 | 커밋 수 | 누적 토큰 | 마지막 수정 |"
  echo "|---|---|---|---|"
  cut -d, -f1 /opt/scripts/accounts.csv | grep "^${CLASS}" | while read -r u; do
    [ -z "$u" ] && continue
    C=$(sudo -u "$u" git -C "/home/$u/project" rev-list --count HEAD 2>/dev/null || echo 0)
    T=$(jq -r '.total_tokens // "-"' "$SNAP/tokens/$u.json" 2>/dev/null || echo "-")
    # 진도 지표이므로 학생 작업물만 본다 — 홈 전체를 보면 캐시·락 파일이 잡혀 의미가 없다
    L=$(find "/home/$u/project" -type f ! -path "*/node_modules/*" ! -path "*/.git/*" \
        -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2- || echo "-")
    echo "| $u | $C | $T | $(basename "${L:--}") |"
  done
} > "$SNAP/summary.md"

echo "완료: $SNAP"
du -sh "$SNAP"
