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
# roster.csv 의 학생 + 테스트 계정. 계정명이 자유 형식이라 글로브로는 못 찾는다.
_accounts() {
  [ -f /opt/scripts/roster.csv ] && awk -F, 'NR>1 && $2!="" {print $2}' /opt/scripts/roster.csv
  for h in /home/test* /home/bash* /home/demo*; do [ -d "$h" ] && basename "$h"; done
}
for u in $(_accounts | sort -u); do
  home="/home/$u"
  [ -d "$home" ] || continue
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

# ── 명단 (roster.csv: 반,계정ID,이름,gmail) ──
# gmail 은 넣지 않는다 — 노출 시 영향이 큰 연락처는 서버에만 둔다(specs/170 보안).
# 이름·반·계정ID 는 강사 전용 페이지에서 필요하므로 포함한다.
roster_json="[]"
if [ -f /opt/scripts/roster.csv ]; then
  roster_json=$(python3 - <<'PY'
import csv, json
rows=[]
with open("/opt/scripts/roster.csv", encoding="utf-8") as f:
    r=csv.reader(f)
    next(r, None)                     # 헤더
    for row in r:
        if len(row) < 3 or not row[2].strip():
            continue
        cls=row[0].strip()
        rows.append({
            "class": "" if cls.startswith("⟪") else cls,   # ⟪mid|high⟫ = 미배정
            "account": row[1].strip(),
            "name": row[2].strip(),
            "has_mail": bool(len(row) > 3 and row[3].strip()),
        })
print(json.dumps(rows, ensure_ascii=False))
PY
)
fi

# ── 수동 노트 (JSON 문자열로 이스케이프) ──
notes_escaped="\"\""
if [ -f "$NOTES" ]; then
  notes_escaped=$(python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))' < "$NOTES")
fi

# ── 자동화 최근 실행 ──
tokens_last=$(newest /var/lib/tokmon)
snapshot_last=$(newest /srv/snapshots)
rehearsal_last=$(newest /opt/scripts/rehearsal-logs)
# 자동 위키: 구축 여부가 아니라 "마지막으로 언제 돌았나"를 본다 (specs/180)
wiki_built=false
[ -x /opt/scripts/build-wiki.sh ] && wiki_built=true
wiki_last=$(newest /srv/wiki)

mkdir -p /srv/hub
cat > "$OUT.tmp" <<JSON
{
  "generated_at": $now,
  "domain": "$DOMAIN",
  "course_start": "$COURSE_START",
  "openobserve_user": "$(cut -d: -f1 /opt/scripts/openobserve-admin.txt 2>/dev/null || echo '')",
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
    "wiki_built": $wiki_built,
    "wiki_last": $wiki_last
  },
  "students": $students_json,
  "roster": $roster_json,
  "notes": $notes_escaped
}
JSON
mv "$OUT.tmp" "$OUT"
chown root:nginx "$OUT" 2>/dev/null || true
chmod 640 "$OUT"
