#!/usr/bin/env bash
# 학생 계정 → 포트 대역 · 호스트명 · nginx 블록 생성 (specs/110)
#
# 공식: 중등 11000 + N×100 / 고등 12000 + N×100
#   반(mid/high)과 N 은 계정명이 아니라 roster.csv 에서 온다 — 계정명을 학생 메일
#   앞부분으로 쓰기로 하면서(2026-08-25) 이름에서 번호를 뽑을 수 없게 됐다.
#   N = 같은 반 안에서 roster.csv 에 적힌 순서(1부터). 행 순서를 바꾸면 포트가 바뀐다.
# 대역 100개 중 외부에 열리는 것은 첫 포트 하나뿐이다.
#
#   ./alloc-ports.sh accounts.csv                 # 배정표만 출력 (기본)
#   ./alloc-ports.sh accounts.csv --nginx         # nginx 조각까지 생성
#   ./alloc-ports.sh accounts.csv --deploy        # nginx + 학생 MY-SERVER.md 배포
#   BASE_DOMAIN=aitf.example.uk ./alloc-ports.sh ...
#
# accounts.csv 형식: 계정,비밀번호  (040-accounts.md 와 동일)
set -euo pipefail

CSV="${1:?사용: alloc-ports.sh <accounts.csv> [--nginx]}"
MODE="${2:-}"
DOMAIN="${BASE_DOMAIN:-<BASE_DOMAIN 미설정>}"
OUTDIR="${NGINX_OUT:-/etc/nginx/conf.d/students}"
TABLE="${PORTS_CSV:-/opt/scripts/ports.csv}"

ROSTER="${ROSTER_CSV:-/opt/scripts/roster.csv}"

port_of() {                      # 계정명 → 공개 포트 (roster.csv 기준)
  local acct="$1"
  awk -F, -v want="$acct" '
    NR==1 { next }                                  # 헤더
    $1=="" || $2=="" { next }
    { n[$1]++; if ($2==want) { cls=$1; idx=n[$1] } }
    END {
      if (cls=="")  { print "roster.csv 에 없는 계정: " want > "/dev/stderr"; exit 1 }
      if (cls=="class2")    base=11000
      else if (cls=="class1") base=12000
      else { print "알 수 없는 반: " cls > "/dev/stderr"; exit 1 }
      print base + idx*100
    }' "$ROSTER"
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

  # 학생 홈에 내 포트·주소를 적어 둔다. AI 에이전트도 이 파일을 읽는다 (server-rules.md)
  if [ "$MODE" = "--deploy" ] && [ -d "/home/$acct" ]; then
    install -d -o "$acct" -g "$acct" -m 755 "/home/$acct/project"
    cat > "/home/$acct/project/MY-SERVER.md" <<EOF
# 내 서버 정보 — ${acct}

> 자동 생성 파일입니다. 고치지 마세요 (다시 만들어집니다).
> 사용 규칙은 옆의 \`SERVER-RULES.md\` 를 보세요.

| | |
|---|---|
| 내 계정 | \`${acct}\` |
| **밖에서 보이는 포트** | **${p}** |
| 내 포트 대역 | ${p} – $((p + 99)) |
| 내 주소 | https://${host} |

## 웹페이지를 남에게 보여주려면

\`\`\`bash
# 반드시 ${p} 번 포트에 띄웁니다
npm run dev -- --port ${p}
\`\`\`

띄운 다음 https://${host} 를 열어보세요.

백엔드나 데이터베이스는 $((p + 1)) ~ $((p + 99)) 중 아무거나 쓰면 됩니다.
그건 나만 볼 수 있고, 내 웹페이지에서는 부를 수 있습니다.
EOF
    chown "$acct":"$acct" "/home/$acct/project/MY-SERVER.md"
    chmod 644 "/home/$acct/project/MY-SERVER.md"
    ln -sfn /opt/harness/server-rules.md "/home/$acct/project/SERVER-RULES.md"
    chown -h "$acct":"$acct" "/home/$acct/project/SERVER-RULES.md"
  fi

  case "$MODE" in --nginx|--deploy) ;; *) continue ;; esac

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

if [ "$MODE" = "--nginx" ] || [ "$MODE" = "--deploy" ]; then
  echo >&2
  echo "nginx 조각 생성: ${OUTDIR}/" >&2
  echo "적용 전 반드시: sudo nginx -t && sudo systemctl reload nginx" >&2
  echo "터널 ingress와 DNS 레코드는 별도 (운영자 작업 — specs/110)" >&2
fi
