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
# 주입 위치: ~/.bashrc.d/50-openai.sh (600, 학생 소유)
#   .bashrc 가 ~/.bashrc.d/* 를 읽도록 이미 배선돼 있다.
#   .bashrc 본문에 직접 쓰지 않는 이유: 학생이 .bashrc 를 고치다 키를 날리거나,
#   반대로 키가 섞인 .bashrc 를 통째로 커밋할 수 있다.
#
# ⚠ 홈을 리셋하면 키도 지워진다. reset-test-account.sh 뒤에 다시 돌릴 것.
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
  echo "  $acct: 주입"
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
