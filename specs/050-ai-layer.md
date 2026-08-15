# 050 — P4: AI CLI·API 키

**상태**: Draft · 차단: 040

## 목표

모든 학생 계정에서 Codex CLI / Gemini CLI가 즉시 동작. 키는 학생별 분리, 비용은 hard cap으로 상한.

## 설계

- **설치는 반드시 root 전역** (`sudo npm i -g`) — 운영자 계정의 npm prefix는 자기 홈(700) 아래라서 거기 설치하면 학생이 실행 불가:
  ```bash
  sudo npm i -g @openai/codex @google/gemini-cli tokscale
  which codex   # /usr/bin 또는 /usr/local/bin 이어야 정상. /home/** 이면 잘못 설치된 것
  ```
- **키 발급**: OpenAI Platform에서 인원수만큼 개별 키 + **hard cap**(예: $30) / Google AI Studio 결제 연결(분당 요청 제한 해제) + 예산 상한·알림
- **키 주입**: 각 학생 `~/.bashrc`에 export, `chmod 600`. 계정 분리(홈 700)로 상호 열람 불가.
- 전역 gitignore(060)가 `.codex/` `.gemini/` `.env`를 커밋에서 차단.

## 작업 체크리스트

- [ ] CLI 3종 root 전역 설치 + `which`로 경로 검증
- [ ] 키 발급 (운영자, 인원 확정 후) + cap 설정
- [ ] 키 주입 스크립트 실행 (실키는 서버에서만 다룸 — repo에는 절대 없음)

## 검증 기준

- [ ] 학생 계정에서 `codex` 실행 → 정상 응답
- [ ] 학생 A 계정에서 학생 B의 `~/.bashrc` 읽기 시도 → 거부
- [ ] hard cap 실동작은 리허설(100)에서 소액 실측

## 결정 기록

- 2026-08-16 · tokscale도 이 단계에서 함께 root 전역 설치 (070에서 사용).
