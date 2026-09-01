#!/usr/bin/env bash
# 서버 밖으로 들고 나갈 백업 묶음 — 암호화 tar (specs/080)
#
# 왜 이것만 담나: OS·설치물은 이 저장소의 스펙·스크립트로 재구축된다.
# 서버에만 있고 다른 사본이 없는 것 = 학생 작업물(Gitea) + 운영 시크릿뿐이고,
# 그 둘을 합쳐도 10MB 미만이라 매주 통째로 들고 나가는 게 가장 단순하다.
#
# OCI 부트 볼륨 백업을 쓰지 않는 이유: Always Free 한도(블록 200GB)를 이미
# 부트 볼륨이 차지해 백업분은 유료 구간이 된다. 우리가 잃으면 안 되는 건
# 볼륨 전체가 아니라 이 8MB 라서 비용 0인 이 방식을 쓴다 (2026-09-01 결정).
#
# 사용:
#   sudo ./make-backup.sh                 → /tmp/aitf-backup-<날짜>.tar.gz.gpg
#   sudo ./make-backup.sh --pass '암호'    → 암호 직접 지정 (미지정 시 자동 생성해 출력)
#
# 복구: gpg -d 파일 | tar xz -C /복구위치
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "root 로 실행할 것 (sudo)"; exit 1; }

PASS=""
[[ "${1:-}" == "--pass" ]] && PASS="${2:-}"
[[ -z "$PASS" ]] && PASS=$(head -c 18 /dev/urandom | base64 | tr -d '/+=' | head -c 20)

DATE=$(date +%Y-%m-%d)
OUT="/tmp/aitf-backup-${DATE}.tar.gz.gpg"
STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT

# ① 운영 시크릿·명단 (서버에만 존재)
install -d -m 700 "$STAGE/opt-scripts"
for f in roster.csv accounts.csv openai-keys.csv gitea-tokens.csv \
         .env wiki-llm.env gitea-admin.txt term-calendar.json hub.env; do
  [[ -f "/opt/scripts/$f" ]] && cp -p "/opt/scripts/$f" "$STAGE/opt-scripts/"
done

# ② Gitea 전체 — 학생 작업물·반별 위키·아카이브. 실행 중 정합성을 위해
#    저장소와 DB 를 함께 담는다 (sqlite 는 파일 복사로 충분한 규모).
install -d -m 700 "$STAGE/gitea"
cp -a /var/lib/gitea/data/gitea-repositories "$STAGE/gitea/"
cp -p /var/lib/gitea/data/gitea.db "$STAGE/gitea/"
cp -p /etc/gitea/app.ini "$STAGE/gitea/"

# ③ 위키 작업본 (Gitea 에 push 된 사본이 정본이지만, 미푸시분 보호)
cp -a /var/lib/wiki-build "$STAGE/" 2>/dev/null || true

# ④ 복구 안내 — 압축 안에 같이 넣는다 (몇 달 뒤의 나를 위해)
cat > "$STAGE/복구방법.txt" << 'INNER'
AITF 백업 — 복구 방법

1) 풀기
   gpg -d aitf-backup-<날짜>.tar.gz.gpg | tar xz

2) 무엇이 들어 있나
   opt-scripts/   운영 시크릿·명단 → /opt/scripts/ 로 (권한 600, root 소유)
   gitea/         학생 작업물·위키 전체 + gitea.db + app.ini
                  → /var/lib/gitea/data/ 로 복사 후 chown -R gitea:gitea
   wiki-build/    위키 작업본 → /var/lib/wiki-build/

3) 서버 자체는 저장소(github.com/mooner92/AITF)의 specs/ 로 재구축한다.
   OS·패키지·설정은 전부 문서화돼 있고, 이 백업은 "문서로 못 만드는 것"만 담는다.
INNER

tar czf - -C "$STAGE" . | gpg --batch --yes --symmetric --cipher-algo AES256 \
  --passphrase "$PASS" -o "$OUT"
chmod 600 "$OUT"

echo "백업 생성: $OUT ($(du -h "$OUT" | cut -f1))"
echo "암호: $PASS"
echo "→ 이 파일을 서버 밖(구글 드라이브 등)에 보관하세요. 암호는 따로 보관."
