# template-home — 학생 홈 스켈레톤 (공개판)

서버의 `/opt/template-home` 원본에서 **의존성(node_modules)과 하네스 링크를 뺀** 사본.
신규 계정 생성·초기화 시 이 구조가 학생 홈으로 배포된다 ([specs/040](../specs/040-accounts.md)).

- 의존성은 서버에서 사전 설치해 둔다 — 수업 중 `npm install` 금지가 공유 서버 운영의 핵심
- `AGENTS.md`/`GEMINI.md` 심링크는 배포 시 `link-harness.sh`가 건다 ([specs/055](../specs/055-harness.md))
