# AITF — AI Task Force 특강

코딩학원 AI 특강의 **인프라 구축 기록 + 수업 기록** 저장소입니다.
학생들이 나중에 "이 수업 환경이 어떻게 만들어졌는지"까지 볼 수 있도록 공개로 운영합니다.

## 저장소 구조

```
docs/       # 구조 설명 문서 (architecture.html — 브라우저로 열어보는 해부도)
specs/      # Spec-Driven Development — 단계별(P0~P9) 스펙과 진행 상태
scripts/    # 서버 운영 스크립트 (공개 가능 버전 — 민감 값은 placeholder)
curriculum/ # 수업 계획 문서 (상세·학부모용·학원 요청 — md + 조판된 html)
classlog/   # 수업 기록 (주차별)
SECURITY.md # 공개 저장소 정보 정책 — 무엇을 절대 올리지 않는가
```

## 수업 계획이 궁금하면

[`curriculum/`](curriculum/README.md)에 독자별로 정리돼 있습니다.

| 문서 | 독자 |
|---|---|
| [`detailed-plan.html`](curriculum/detailed-plan.html) | 강사·원장 — 12주 주차별 상세, 중등/고등 갈래 |
| [`parent-guide.html`](curriculum/parent-guide.html) | 학부모 — 배포용 요약 |
| [`academy-request.html`](curriculum/academy-request.html) | 원장 — 개강 전 협조 요청 |

HTML은 내려받아 브라우저로 열면 됩니다 (글꼴 내장, 오프라인 열람 가능).
같은 내용의 `.md` 버전이 나란히 있습니다.

## 서버 구조가 궁금하면

[`docs/architecture.html`](docs/architecture.html)를 내려받아 브라우저로 열면 됩니다.
5개 층이 왜 그렇게 쌓였는지, 요청이 어떤 경로로 들어오는지 그림으로 정리돼 있습니다.

```bash
git clone git@github.com:mooner92/AITF.git && open AITF/docs/architecture.html
```

## 검증 원칙

문서보다 실물을 믿습니다 — [`docs/verification-practice.md`](docs/verification-practice.md).
"문서에 그렇게 쓰여 있다"가 근거가 되지 못한 사례들과, 그래서 세운 규칙이 정리돼 있습니다.

## 진행 방식 (Spec-Driven)

1. 각 단계는 `specs/NNN-*.md` 스펙 문서로 시작한다 — 목표 / 설계 / 작업 / 검증 기준 / 결정 기록.
2. 스펙이 `Approved`가 된 뒤에 실제 서버 작업을 한다.
3. 작업이 끝나면 검증 기준을 통과시키고 스펙 상태를 `Done`으로 올린다.
4. 전체 현황판은 [`specs/README.md`](specs/README.md).

## 환경 개요

- Oracle Cloud (ap-seoul-1) · Ampere A1 (aarch64) 4 OCPU / 24GB · Oracle Linux 9
- 학생별 리눅스 계정 + tmux + AI CLI(Codex/Gemini) + 자체 Gitea + 토큰 사용량 모니터링
- 접속은 Cloudflare Zero Trust 터널 경유 (브라우저 터미널)

## 클론 후 첫 설정 (기여자용)

```bash
git config core.hooksPath .githooks   # 민감정보 커밋 차단 훅 활성화
```
