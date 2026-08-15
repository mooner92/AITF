# AITF — AI Task Force 특강

코딩학원 AI 특강의 **인프라 구축 기록 + 수업 기록** 저장소입니다.
학생들이 나중에 "이 수업 환경이 어떻게 만들어졌는지"까지 볼 수 있도록 공개로 운영합니다.

## 저장소 구조

```
specs/      # Spec-Driven Development — 단계별(P0~P9) 스펙과 진행 상태
scripts/    # 서버 운영 스크립트 (공개 가능 버전 — 민감 값은 placeholder)
classlog/   # 수업 기록 (주차별)
SECURITY.md # 공개 저장소 정보 정책 — 무엇을 절대 올리지 않는가
```

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
