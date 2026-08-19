#!/usr/bin/env bash
# 학생 계정 → 포트 대역 · 호스트명 · nginx 블록 생성 (specs/110)
#
# 공식: 중등 11000 + N×100 / 고등 12000 + N×100  (N = 계정 번호)
# 대역 100개 중 외부에 열리는 것은 첫 포트 하나뿐이다.
#
#   ./alloc-ports.sh accounts.csv                 # 배정표만 출력 (기본)
#   ./alloc-ports.sh accounts.csv --nginx         # nginx 조각까지 생성
#   BASE_DOMAIN=aitf.example.uk ./alloc-ports.sh ...
#
# accounts.csv 형식: 계정,비밀번호  (040-accounts.md 와 동일)
set -euo pipefail

CSV="${1:?사용: alloc-ports.sh <accounts.csv> [--nginx]}"
MODE="${2:-}"
DOMAIN="${BASE_DOMAIN:-<BASE_DOMAIN 미설정>}"
OUTDIR="${NGINX_OUT:-/etc/nginx/conf.d/students}"
TABLE="${PORTS_CSV:-/opt/scripts/ports.csv}"

port_of() {                      # 계정명 → 공개 포트
  local acct="$1" num base
  num=$(printf '%s' "$acct" | sed 's/[^0-9]//g')
  num=$((10#${num:-0}))
  case "$acct" in
    mid*)  base=11000 ;;
    high*) base=12000 ;;
    *)     echo "알 수 없는 계정 접두사: $acct" >&2; return 1 ;;
  esac
  echo $(( base + num * 100 ))
}

echo "계정,공개포트,대역시작,대역끝,주소"
: > "$TABLE.tmp"

while IFS=, read -r acct _pw; do
  [ -z "${acct// }" ] && continue
  case "$acct" in \#*) continue ;; esac

  p=$(port_of "$acct")
  host="${acct}.${DOMAIN}"
  echo "${acct},${p},${p},$((p + 99)),https://${host}"
  echo "${acct},${p},$((p + 99)),${host}" >> "$TABLE.tmp"

  [ "$MODE" = "--nginx" ] || continue

  mkdir -p "$OUTDIR"
  cat > "${OUTDIR}/${acct}.conf" <<EOF
# 생성됨 — alloc-ports.sh. 직접 고치지 말 것 (다시 생성하면 덮어씀)
server {
    listen 127.0.0.1:8081;
    server_name ${host};

    access_log /var/log/nginx/student-${acct}.log;

    location / {
        proxy_pass http://127.0.0.1:${p};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;        # 핫리로드 웹소켓
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        client_max_body_size 20m;

        # 학생이 서버를 안 켰을 때 502 대신 안내 페이지
        proxy_intercept_errors on;
        error_page 502 503 504 = @offline;
    }

    location @offline {
        root /srv/fallback;
        try_files /offline.html =503;
        internal;
    }
}
EOF
done < "$CSV"

mv "$TABLE.tmp" "$TABLE" 2>/dev/null || rm -f "$TABLE.tmp"

if [ "$MODE" = "--nginx" ]; then
  echo >&2
  echo "nginx 조각 생성: ${OUTDIR}/" >&2
  echo "적용 전 반드시: sudo nginx -t && sudo systemctl reload nginx" >&2
  echo "터널 ingress와 DNS 레코드는 별도 (운영자 작업 — specs/110)" >&2
fi
