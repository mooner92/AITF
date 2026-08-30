# scripts — 서버 운영 스크립트 (공개 버전)

서버 실배치 위치는 `/opt/scripts`(root 700). 여기 있는 것은 **민감 값이 없는 공개 버전**이며,
`accounts.csv`(계정·비밀번호)와 토큰류는 서버에만 존재한다. `<...>` 표기는 배포 시 실값으로 치환.

| 스크립트 | 용도 | 관련 스펙 |
|---|---|---|
| `create-accounts.sh` | CSV 기반 학생 계정 일괄 생성 + 메모리 상한 | [040](../specs/040-accounts.md) |
| `reset-home.sh` | 학생 홈을 템플릿으로 초기화 | 040 |
| `check-account.sh` | 계정별 상태 점검(셸·하네스·키·sudo 없음 확인) — 개강일 아침 1줄 점검용 | 040/160 |
| `make-cards.py` | 학생 계정 카드(타이핑 가능한 8자 비밀번호) 생성 | 040/160 |
| `push-key.sh` | 학생별 OpenAI 키 주입 — env var + `codex login --with-api-key`(`~/.codex/auth.json`) 둘 다 필요 | [050](../specs/050-ai-layer.md) |
| `deploy-skills.sh` | 교육용 하네스(스킬 3종) 배포·연결 상태 확인(`--check`) | [055](../specs/055-harness.md) |
| `link-harness.sh` | 학생 홈에 하네스 심링크 연결 | 055 |
| `setup-git-students.sh` | 학생 git 신원·인증·remote 사전 주입 | [060](../specs/060-git.md) |
| `collect-tokens.sh` | tokscale 학생별 수집 (cron) | [070](../specs/070-observability.md) |
| `snapshot-class.sh` | 수업 후 반 단위 증분 스냅샷 + 진도 요약 | [080](../specs/080-snapshot.md) |
| `restore-student.sh` | 학생 단위 복구 | 080 |
| `cleanup-class.sh` | 반 교대 시 잔여 프로세스 정리 | 080/100 |
| `reset-course.sh` | 종강 아카이브 + 초기화 안내 | 080 |
| `reset-test-account.sh` | 리허설용 시험 계정(`test01`~) 초기 상태로 복원 | [100](../specs/100-rehearsal.md) |
| `test-pipeline.sh` | 주차별 리허설 체크리스트를 순서대로 진행·기록 (정본은 `docs/friday-test-pipeline.md`) | 100 |
| `alloc-ports.sh` | 학생별 포트 대역 배정·배포(`--deploy`) | [110](../specs/110-student-services.md) |
| `push-rule.sh` | nginx/방화벽 규칙 배포 — **운영자 승인 후에만 실행** | [030](../specs/030-access.md)/110 |
| `notify-slack.py` | 반별 웹훅으로 위키 발행 알림 | [120](../specs/120-integrations.md) |
| `publish-notion.py` | 위키 → Notion 주간 페이지 발행(반별 업서트, 멱등) | 120 |
| `compare-bot.py` | Slack `/compare`(블라인드 A/B) · `/qwentest`(강사 전용) 봇 — systemd `aitf-compare-bot` | 120/[150](../specs/150-model-bots.md) |
| `build-wiki.py` | 학생 활동(홈 워킹카피 + Gitea bare 저장소 양쪽) 수집 → 위키 md 생성 | [180](../specs/180-wiki.md) |
| `enrich-wiki.py` | 위키 md에 LLM(gpt-5.6-luna) 서술 추가 — 마커 밖만, 결정적 수집과 분리 | 180 |
| `term_calendar.py` | 공휴일 반영 주차 계산(`class_dates`/`week_of`) — 2026 추석(09-27) 등 휴강일 처리 | 180 |
| `hub-status.sh` | 강사 관제탑용 상태 스냅샷 생성 | [170](../specs/170-instructor-hub.md) |
| `check-design.py` | 발표자료/문서 HTML 정적 검사 — 폰트·테마·태그·민감정보 | `docs/design-spec.md` §8-1 |
| `verify-motion.py` | 발표자료 모션 실기 검사(헤드리스 브라우저, reduced-motion 양방향) | `docs/design-spec.md` §8-2 |
| `build-weeks.py` | 주차별 산출물 일괄 빌드 | — |
