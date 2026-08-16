#!/bin/bash
# 학생별 관측 데이터 수집 (cron 호출) — specs/070
# 수집 3종: ① 토큰(tokscale) ② 리소스(cgroup) ③ 진도(커밋·최근 활동)
# cron (/etc/cron.d/tokmon):
#   * 13-18 * * 0  root /opt/scripts/collect-tokens.sh   # 일요일 수업 시간대 1분 주기
#   */15 * * * *   root /opt/scripts/collect-tokens.sh   # 평시 15분 주기
set -uo pipefail
OUT=/var/lib/tokmon
mkdir -p "$OUT"
chmod 700 "$OUT"

# OpenObserve 인제스트 설정 (specs/070) — 자격증명은 root 전용 파일에서
O2_URL="http://127.0.0.1:8080/api/default"
O2_CRED=$(cat /opt/scripts/openobserve-admin.txt 2>/dev/null || true)
NOW=$(date +%s%6N)   # OpenObserve _timestamp는 마이크로초
push() {  # push <stream> <json-record>
  [ -n "$O2_CRED" ] && curl -s -o /dev/null -u "$O2_CRED" \
    -H 'Content-Type: application/json' -d "[$2]" "$O2_URL/$1/_json"
}

cut -d, -f1 /opt/scripts/accounts.csv | while read -r u; do
  [ -z "$u" ] && continue
  uid=$(id -u "$u" 2>/dev/null) || continue

  # ① 토큰
  sudo -u "$u" tokscale --json --today > "$OUT/$u.json" 2>/dev/null

  # ② 리소스 — 학생 slice의 cgroup 직접 판독 (로그아웃 상태면 slice가 없어 0 처리)
  CG="/sys/fs/cgroup/user.slice/user-${uid}.slice"
  MEM=$(cat "$CG/memory.current" 2>/dev/null || echo 0)
  PIDS=$(cat "$CG/pids.current" 2>/dev/null || echo 0)
  CPU=$(awk '/^usage_usec/{print $2}' "$CG/cpu.stat" 2>/dev/null || echo 0)

  # ③ 진도
  COMMITS=$(sudo -u "$u" git -C "/home/$u/project" rev-list --count HEAD 2>/dev/null || echo 0)
  LAST=$(find "/home/$u" -type f ! -path "*/node_modules/*" ! -path "*/.git/*" \
         -newermt "-1 day" -printf '%T@\n' 2>/dev/null | sort -rn | head -1 || true)

  jq -n --arg u "$u" --argjson mem "$MEM" --argjson pids "$PIDS" \
        --argjson cpu_usec "$CPU" --argjson commits "$COMMITS" --arg last "${LAST:-}" \
        '{user:$u, mem_bytes:$mem, pids:$pids, cpu_usec:$cpu_usec, commits:$commits, last_activity:$last}' \
        > "$OUT/$u.sys.json" 2>/dev/null

  # OpenObserve로 전송 — resources 스트림 + tokens 스트림
  push resources "$(jq -c --argjson t "$NOW" '. + {_timestamp:$t}' "$OUT/$u.sys.json")"
  TOKREC=$(jq -c --arg u "$u" --argjson t "$NOW" '{user:$u, _timestamp:$t} + .' "$OUT/$u.json" 2>/dev/null)
  [ -n "$TOKREC" ] && push tokens "$TOKREC"
done

# 서버 전체 헬스 (모니터링 웹의 헬스 뷰용)
jq -n --argjson load "$(cut -d' ' -f1 /proc/loadavg)" \
      --argjson mem_avail "$(awk '/MemAvailable/{print $2*1024}' /proc/meminfo)" \
      --argjson disk_avail "$(df --output=avail -B1 / | tail -1 | tr -d ' ')" \
      '{load:$load, mem_avail:$mem_avail, disk_avail:$disk_avail}' > "$OUT/_server.json"
push server "$(jq -c --argjson t "$NOW" '. + {_timestamp:$t}' "$OUT/_server.json")"
