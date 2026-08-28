#!/usr/bin/env bash
# 계정 상태 점검 — "이 계정이 개강일에 쓸 수 있는 상태인가" (specs/040·160)
#
# 왜 만들었나: 개강 이틀 전 학원 현장에서 같은 종류의 문제가 세 번 나왔다.
#   · test01 에 .bash_profile 이 없어 SSH 로그인이 .bashrc 를 안 읽었다
#   · test03~06 에 tmux 자동 진입 줄이 없었다
#   · 홈을 리셋하면 OpenAI 키가 조용히 사라진다
# 셋 다 "로그인해 보기 전에는 모른다"는 공통점이 있다. 계정마다 눈으로 확인하는
# 대신, 개강일 아침에 한 줄로 전원을 확인할 수 있어야 한다.
#
# 사용:
#   ./check-account.sh                 로스터의 학생 전원
#   ./check-account.sh test01          한 계정만
#   ./check-account.sh --all           학생 + 시험 계정 전부
set -uo pipefail

ROSTER=/opt/scripts/roster.csv
ACADEMY_IP=$(sudo grep -oE '^Match Address .*' /etc/ssh/sshd_config.d/60-aitf.conf 2>/dev/null | awk '{print $3}')

pass=0; fail=0
ok()   { printf '    \033[32m✓\033[0m %s\n' "$1"; pass=$((pass+1)); }
no()   { printf '    \033[31m✗\033[0m %s\n' "$1"; fail=$((fail+1)); }

check() {
  local u="$1" h="/home/$1"
  printf '\n\033[1m%s\033[0m\n' "$u"

  id "$u" &>/dev/null || { no "계정이 없다"; return; }
  [[ "$(getent passwd "$u" | cut -d: -f7)" == */bash ]] && ok "로그인 셸 bash" || no "로그인 셸이 bash 가 아니다"

  # 홈 700 — 다른 학생이 남의 작업을 못 본다
  [[ "$(stat -c %a "$h" 2>/dev/null)" == 700 ]] && ok "홈 권한 700" || no "홈 권한이 700 이 아니다"

  # SSH 로그인은 .bash_profile 을 거쳐야 .bashrc 에 닿는다.
  # 이게 없으면 tmux 도 PATH 도 조용히 죽는다.
  sudo test -f "$h/.bash_profile" && ok ".bash_profile 있음" || no ".bash_profile 없음 → tmux·PATH 죽음"
  sudo grep -q 'bashrc' "$h/.bash_profile" 2>/dev/null && ok ".bash_profile 이 .bashrc 를 읽음" \
    || no ".bash_profile 이 .bashrc 를 안 읽는다"
  sudo grep -q 'tmux new' "$h/.bashrc" 2>/dev/null && ok "tmux 자동 진입" || no "tmux 자동 진입 줄 없음"

  # 하네스 — 학생이 첫 명령을 치기 전에 있어야 하는 것들
  sudo test -f "$h/project/AGENTS.md" && ok "project/AGENTS.md" || no "project/AGENTS.md 없음"
  sudo test -f "$h/.codex/config.toml" && ok ".codex/config.toml" || no ".codex/config.toml 없음"
  sudo test -d "$h/project/public" && ok "project/public (작품관 배포용)" || no "project/public 없음"

  # 키 — 없으면 codex 가 인증 오류를 낸다
  if sudo test -f "$h/.bashrc.d/50-openai.sh"; then
    [[ "$(sudo stat -c %a "$h/.bashrc.d/50-openai.sh")" == 600 ]] \
      && ok "OpenAI 키 주입 (600)" || no "OpenAI 키 파일 권한이 600 이 아니다"
  else
    no "OpenAI 키 미주입 → codex 인증 오류"
  fi

  # sudo 가 붙으면 계정 격리가 통째로 무너진다. 매번 확인한다.
  if sudo -l -U "$u" 2>&1 | grep -qiE 'not allowed|는 .* 실행할 수 없습니다'; then
    ok "sudo 없음"
  else
    no "⚠ sudo 권한이 있다 — 즉시 회수할 것"
  fi

  sudo test -d "/srv/pages/$u" && ok "작품관 경로" || no "/srv/pages/$u 없음"
}

# 학원 IP 에서 비밀번호 로그인이 실제로 열려 있는지 — 계정과 무관한 전역 조건
printf '\033[1m공통\033[0m\n'
if [[ -n "$ACADEMY_IP" ]]; then
  r=$(sudo sshd -T -C "addr=$ACADEMY_IP,user=root,host=x" 2>/dev/null | grep -i '^passwordauthentication' | awk '{print $2}')
  [[ "$r" == yes ]] && ok "학원 IP($ACADEMY_IP) 비밀번호 로그인 열림" || no "학원 IP 에서 비밀번호 로그인이 안 열려 있다"
  # 학원이 아닌 주소를 하나 만들어 대조한다. 저장소에 공인 IP 를 적지 않으려고
  # 학원 IP 의 마지막 옥텟만 바꿔 쓴다 (SECURITY.md — 실제 IP 는 서버에만).
  OUTSIDE_IP="${ACADEMY_IP%.*}.$(( ${ACADEMY_IP##*.} == 1 ? 2 : 1 ))"
  r=$(sudo sshd -T -C "addr=$OUTSIDE_IP,user=root,host=x" 2>/dev/null | grep -i '^passwordauthentication' | awk '{print $2}')
  [[ "$r" == no ]] && ok "학원 밖은 공개키만" || no "⚠ 학원 밖에서도 비밀번호가 열려 있다"
else
  no "60-aitf.conf 에 학원 IP 가 없다"
fi

if [[ "${1:-}" == "--all" ]]; then
  targets=$( (awk -F, 'NR>1 && $2 {print $2}' <(sudo cat "$ROSTER"); echo test01 test02 test03 test04 test05 test06 | tr ' ' '\n') )
elif [[ -n "${1:-}" ]]; then
  targets="$1"
else
  targets=$(awk -F, 'NR>1 && $2 {print $2}' <(sudo cat "$ROSTER"))
fi

for u in $targets; do check "$u"; done

printf '\n── 통과 %d · 실패 %d ──\n' "$pass" "$fail"
[[ $fail -eq 0 ]] || exit 1
