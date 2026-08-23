#!/bin/bash
# 금요일 현장 리허설용 — 여러 주차를 쉬지 않고 이어서 시험한다 — specs/130
#
# 실제 수업은 주 1회, 이 리허설은 한 시간에 2~3주를 통과한다. 그래서 이 스크립트는
# 주차 사이에 자동으로 리셋하지 않는다 — 실제 학생처럼 상태가 이어지는 채로 다음
# 주차로 넘어가야 "2주차에 만든 위키가 3주차에도 남아있나" 같은 이어달리기 문제를
# 잡을 수 있다. 리셋이 필요하면 reset-test-account.sh 를 따로, 원하는 시점에 돌린다.
#
# 각 주차 체크리스트는 docs/friday-test-pipeline.md 가 정본이다. 이 스크립트는 그
# 항목들을 순서대로 띄우고, 강사가 하나씩 확인하며 Enter로 넘기게 하고, 결과와
# 걸린 시간을 로그 파일에 남긴다. 항목의 실제 내용을 고치고 싶으면 그 문서를 고치고
# 이 스크립트의 WEEK_* 배열을 맞춰 갱신한다(정본은 문서, 배열은 그 요약).
#
# 사용: test-pipeline.sh <계정> <시작주차> [끝주차]
#   예:  test-pipeline.sh test1 1 3
set -euo pipefail

U="${1:?사용: test-pipeline.sh <계정> <시작주차> [끝주차]}"
WSTART="${2:?시작 주차 번호를 입력하세요 (예: 1)}"
WEND="${3:-$WSTART}"

LOGDIR="/opt/scripts/rehearsal-logs"
mkdir -p "$LOGDIR"
LOGFILE="$LOGDIR/${U}-$(date +%Y%m%d-%H%M%S).log"

log() { echo "$@" | tee -a "$LOGFILE"; }
ts() { date +%H:%M:%S; }

# ── 주차별 체크리스트 (docs/friday-test-pipeline.md 요약본) ──
# 형식: "설명|solo|classroom" — solo=혼자 시험 가능, classroom=실 학생 필요(리허설에서 건너뜀)

WEEK_1=(
  "서버 계정 카드로 브라우저 터미널 접속 (5단계, 25분 가정 실측)|solo"
  "tmux 3키 — 스크롤/중단/재입력|solo"
  "Codex CLI 첫 대화 — 세션 유지 확인|solo"
  "프로필 카드 — 웹 검색으로 정보 조사 후 터미널 카드 생성|solo"
  "할루시네이션 시연 — 검색 없이 인물 질문|solo"
  "사용량 그래프 확인 (12주차 비교 기준점)|solo"
  "짝과 이름 나누기, 반응 관찰|classroom"
)

WEEK_2=(
  "같은 요청을 ChatGPT 웹과 Codex CLI에 동시 실행 — 차이 확인|solo"
  "/compare 블라인드 테스트 3라운드 (요약/창작/코드) 동작 확인|solo"
  "정답 공개 시 속도·비용 병기 표시 확인|solo"
  "Gitea 위키 최초 개설 — '우리 반 모델 가이드' 문서 생성|solo"
  "인터넷에 올리면 안 되는 것 안내 문구 노출 확인|solo"
  "블라인드 라운드 반 전체 투표 반응|classroom"
)

WEEK_3=(
  "단체 디자인 세션 — Claude로 로고 생성 (강사 진행 시연이라 혼자 재현 가능)|solo"
  "개요→생성→design.md 적용 흐름 — 발표자료 1건 완주|solo"
  "public/ 배포 후 30초 내 실제 URL 접속 확인|solo"
  "위키에 결과물 기록 확인|solo"
  "발표자료 스킬(deck) 공개 시나리오 — example.md/html 비교 열람|solo"
  "AI 활용 표기 안내 문구 노출 확인|solo"
  "반 전체 앞에서 서로 결과물 비교|classroom"
)

week_array_name() { echo "WEEK_$1"; }

run_week() {
  local wk="$1"
  local arrname
  arrname=$(week_array_name "$wk")
  if ! declare -p "$arrname" >/dev/null 2>&1; then
    log "  [건너뜀] ${wk}주차 체크리스트가 아직 스크립트에 없습니다 — docs/friday-test-pipeline.md 참고해 추가하세요."
    return
  fi
  local -n items="$arrname"

  log ""
  log "════════════════════════════════════════"
  log "  ${wk}주차 시험 시작 — $(ts)"
  log "════════════════════════════════════════"

  local i=0
  for entry in "${items[@]}"; do
    i=$((i+1))
    local desc="${entry%%|*}"
    local kind="${entry##*|}"
    if [ "$kind" = "classroom" ]; then
      log "  [$i] (실학생 필요 — 리허설 건너뜀) $desc"
      continue
    fi
    log "  [$i] $desc"
    read -r -p "        확인했으면 Enter, 문제 있으면 'x' 입력 후 Enter: " ans
    if [ "${ans:-}" = "x" ]; then
      read -r -p "        무슨 문제였나요 (한 줄): " note
      log "        ⚠ 문제 기록 — $(ts) — $note"
    else
      log "        ✅ 통과 — $(ts)"
    fi
  done

  log "  ${wk}주차 시험 종료 — $(ts)"
}

log "══ 리허설 시작 — 계정: $U / 주차: ${WSTART}~${WEND} / $(date '+%Y-%m-%d %H:%M') ══"
log "로그 파일: $LOGFILE"
log ""
log "안내: 주차 사이에 자동 리셋하지 않습니다(실제 학생처럼 상태가 이어집니다)."
log "      계정을 처음 상태로 되돌리려면 별도로 reset-test-account.sh $U 를 실행하세요."

for ((wk=WSTART; wk<=WEND; wk++)); do
  run_week "$wk"
done

log ""
log "══ 리허설 종료 — $(date '+%H:%M') ══"
log "문제로 기록된 항목은 위 로그의 '⚠'로 검색: grep '⚠' $LOGFILE"
