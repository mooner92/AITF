#!/bin/bash
# 강사 관제탑 상태 수집 — specs/170
# 5분마다 cron 이 실행해 /srv/hub/status.json 을 갱신한다.
# OpenObserve(070)가 "지표"라면 이 파일은 "수업 운영 현황"이다 — 서비스 생존,
# 자동화 최근 실행, 학생별 적립(커밋·작품), 강사 수동 노트를 한 파일로 모은다.
#
# 도메인 등 서버 고유 값은 /opt/scripts/hub.env 에서 읽는다 (저장소에는 없음).
set -euo pipefail

OUT="/srv/hub/status.json"
ENVFILE="/opt/scripts/hub.env"
NOTES="/opt/scripts/hub-notes.md"

DOMAIN=""
COURSE_START=""
[ -f "$ENVFILE" ] && . "$ENVFILE"

now=$(date +%s)

svc() { systemctl is-active "$1" 2>/dev/null || echo "unknown"; }

# 컨테이너 상태 (docker ps 는 이름 정확 매칭)
ctr() {
  local st
  st=$(docker inspect -f '{{.State.Status}}' "$1" 2>/dev/null) || { echo "absent"; return; }
  echo "$st"
}

# 디렉토리에서 가장 최근 mtime (없으면 0)
newest() {
  local d="$1"
  [ -d "$d" ] || { echo 0; return; }
  find "$d" -mindepth 1 -printf '%T@\n' 2>/dev/null | sort -rn | head -1 | cut -d. -f1 || echo 0
}

# ── 학생 적립 현황 ──
students_json="["
first=1
for home in /home/mid* /home/high* /home/test* /home/bash* /home/demo*; do
  [ -d "$home" ] || continue
  u=$(basename "$home")
  id -u "$u" >/dev/null 2>&1 || continue

  commits=0
  if [ -d "$home/project/.git" ]; then
    commits=$(git -C "$home/project" rev-list --count HEAD 2>/dev/null || echo 0)
  fi
  pages=0
  [ -d "/srv/pages/$u" ] && pages=$(find "/srv/pages/$u" -type f 2>/dev/null | wc -l)
  # 마지막 활동: 홈 최상위+project 만 훑는다 (전체 재귀는 느림)
  last=$(find "$home" -maxdepth 2 -printf '%T@\n' 2>/dev/null | sort -rn | head -1 | cut -d. -f1 || echo 0)

  [ $first -eq 0 ] && students_json+=","
  first=0
  students_json+="{\"id\":\"$u\",\"commits\":$commits,\"pages\":$pages,\"last_activity\":$last}"
done
students_json+="]"

# ── 수동 노트 (JSON 문자열로 이스케이프) ──
notes_escaped="\"\""
if [ -f "$NOTES" ]; then
  notes_escaped=$(python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))' < "$NOTES")
fi

# ── 자동화 최근 실행 ──
tokens_last=$(newest /var/lib/tokmon)
snapshot_last=$(newest /srv/snapshots)
rehearsal_last=$(newest /opt/scripts/rehearsal-logs)
wiki_built=false
[ -x /opt/scripts/auto-wiki.sh ] && wiki_built=true

mkdir -p /srv/hub
cat > "$OUT.tmp" <<JSON
{
  "generated_at": $now,
  "domain": "$DOMAIN",
  "course_start": "$COURSE_START",
  "services": {
    "nginx": "$(svc nginx)",
    "gitea": "$(svc gitea)",
    "docker": "$(svc docker)",
    "cloudflared": "$(svc cloudflared)"
  },
  "containers": {
    "aitf_mon": "$(ctr aitf-mon)"
  },
  "automation": {
    "tokens_last": $tokens_last,
    "snapshot_last": $snapshot_last,
    "rehearsal_last": $rehearsal_last,
    "wiki_built": $wiki_built
  },
  "students": $students_json,
  "notes": $notes_escaped
}
JSON
mv "$OUT.tmp" "$OUT"
chown root:nginx "$OUT" 2>/dev/null || true
chmod 640 "$OUT"
