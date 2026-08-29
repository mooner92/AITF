#!/usr/bin/env bash
# OpenAI API 키 주입 — 학생 계정별 (specs/050)
#
# 키는 학생마다 다르다. 이유는 보안이 아니라 **격리**다 —
# 한 학생이 예산을 다 태워도 나머지 넷은 계속 수업할 수 있어야 한다.
# (OpenAI 는 프로젝트 단위로 월 예산 상한을 걸 수 있다. 키 단위로는 못 건다.
#  그래서 학생 1명 = 프로젝트 1개 = 키 1개 로 잡는다.)
#
# 키 목록: /opt/scripts/openai-keys.csv  (600, git 에 절대 올리지 않는다)
#     계정ID,sk-...
#
# 주입 위치 — **두 곳에 같은 키를 넣는다. 하나만 넣으면 Codex 가 실제로는 인증하지 못한다.**
#
#   ① ~/.bashrc.d/50-openai.sh (600, 학생 소유) — 환경변수. `codex doctor` 는 이것만
#      보고 "auth is provided by environment" 라고 통과시키지만, 이 문서 작성 시점
#      (codex-cli 0.147.0) 기준 **기본 openai 프로바이더는 실제 요청에 이 값을 안 쓴다** —
#      알려진 문제(OPENAI_API_KEY exported 인데도 401 Missing bearer). doctor 의 초록
#      체크만 보고 "됐다"고 판단하면 안 된다 — 2026-08-29 실제 학생 계정 5개에서
#      전부 재현·확인했다.
#   ② ~/.codex/auth.json — `codex login --with-api-key` 가 쓰는 실제 인증 파일.
#      Codex 요청은 이걸 읽는다. `printenv OPENAI_API_KEY | codex login --with-api-key`
#      로 만든다 — 학생 계정으로 실행해야 그 계정 소유 파일이 된다.
#
#   .bashrc 본문에 직접 쓰지 않는 이유(①): 학생이 .bashrc 를 고치다 키를 날리거나,
#   반대로 키가 섞인 .bashrc 를 통째로 커밋할 수 있다.
#
# ⚠ 홈을 리셋하면 둘 다 지워진다. reset-test-account.sh 뒤에 다시 돌릴 것.
#
# 사용:
#   sudo ./push-key.sh                 전원
#   sudo ./push-key.sh high01          한 명만
#   sudo ./push-key.sh --verify        주입 후 실제 API 호출로 확인
set -euo pipefail

KEYS=/opt/scripts/openai-keys.csv
VERIFY=0
ONLY=""

for a in "$@"; do
  case "$a" in
    --verify) VERIFY=1 ;;
    -*) echo "모르는 옵션: $a"; exit 2 ;;
    *) ONLY="$a" ;;
  esac
done

[[ $EUID -eq 0 ]] || { echo "root 로 실행할 것 (sudo)"; exit 1; }
[[ -f "$KEYS" ]] || { echo "키 파일이 없다: $KEYS"; exit 1; }

n=0
while IFS=, read -r acct key; do
  acct="${acct//[[:space:]]/}"; key="${key//[[:space:]]/}"
  [[ -z "$acct" || "$acct" == \#* ]] && continue
  [[ -n "$ONLY" && "$acct" != "$ONLY" ]] && continue

  if ! id "$acct" &>/dev/null; then
    echo "  ! $acct: 계정 없음 — 건너뜀"; continue
  fi
  if [[ "$key" != sk-* ]]; then
    echo "  ! $acct: 키 형식이 sk- 로 시작하지 않는다 — 건너뜀"; continue
  fi

  d="/home/$acct/.bashrc.d"
  install -d -o "$acct" -g "$acct" -m 700 "$d"
  f="$d/50-openai.sh"
  printf 'export OPENAI_API_KEY=%s\n' "$key" > "$f"
  chown "$acct:$acct" "$f"
  chmod 600 "$f"

  # 진짜 필요한 쪽 — auth.json. 이게 없으면 codex exec 이 401 로 죽는다.
  if printf '%s' "$key" | su -s /bin/bash -l "$acct" -c 'codex login --with-api-key' >/dev/null 2>&1; then
    echo "  $acct: 주입 (env + auth.json)"
  else
    echo "  $acct: 주입 (env만 — auth.json 쓰기 실패, codex exec 이 여전히 401 날 수 있다)"
  fi
  n=$((n+1))

  if [[ $VERIFY -eq 1 ]]; then
    # 파일을 읽어 "있다"고 확인하지 않는다. 실제로 인증이 되는지 물어본다.
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 \
             -H "Authorization: Bearer $key" https://api.openai.com/v1/models || echo 000)
    case "$code" in
      200) echo "      확인: 인증 성공" ;;
      401) echo "      ✗ 401 — 키가 잘못됐거나 폐기됨" ;;
      429) echo "      ✗ 429 — 예산 소진 또는 요청 한도" ;;
      000) echo "      ? 서버에서 api.openai.com 에 못 나감 (네트워크)" ;;
      *)   echo "      ? HTTP $code" ;;
    esac
  fi
done < "$KEYS"

echo "── $n 개 계정 주입 완료 ──"
[[ $VERIFY -eq 0 ]] && echo "실제 인증까지 확인하려면: sudo $0 --verify"
exit 0
