# 공개 저장소 정보 정책 (허들)

이 저장소는 **공개**다. 아래 항목은 어떤 형태로도(코드·문서·커밋 메시지·이슈) 올리지 않는다.

## 절대 금지 목록

| 분류 | 예시 | 대신 쓰는 표기 |
|---|---|---|
| 자격증명 | API 키, 비밀번호, 토큰, `.git-credentials`, 터널 credentials | `<OPENAI_KEY>`, `<GITEA_TOKEN>` |
| 신원정보 | 학생 실명, `accounts.csv`, 이메일 | `student01` 같은 계정ID만 |
| 네트워크 | 서버 공인 IP, 학원 IP, 자택 IP, Cloudflare 터널 ID | `<SERVER_IP>`, `<ACADEMY_IP>`, `<TUNNEL_ID>` |
| 운영 세부 | 이 서버에서 함께 도는 **다른 서비스**의 이름·포트·구성 | "기존 운영 서비스" 로만 언급 |
| 보안 상태 | 열려 있는 포트 목록, 취약점 메모, 침투 테스트 결과 | 서버 내 비공개 노트에만 기록 |
| 수업 스포일러 | 하네스 실제 내용(리빌 주차 전), 스킬 해부 대상 | 리빌 후 커밋 |

## 민감 정보의 실제 위치 (repo 밖, 서버 내부)

- `~/class-setup/` — 내부 운영 노트 (실제 값이 들어간 계획·실사 기록)
- `/opt/scripts/` — 실제 값이 들어간 운영 스크립트, `accounts.csv` (root 700)

이 repo의 `scripts/`는 위 스크립트의 **placeholder 버전**이다. 서버 배포 시 실제 값을 채운다.

## 기술적 방어선

1. `.gitignore` — `.env`, `*.key`, `*.csv`, `*credentials*` 등 원천 차단
2. `.githooks/pre-commit` — 스테이징된 내용에서 키 패턴·IP·금지 파일명을 스캔, 발견 시 커밋 거부
   - 활성화: `git config core.hooksPath .githooks`
   - 오탐 시에만 `git commit --no-verify` (사용 전 반드시 diff 육안 확인)
3. 커밋 전 습관: `git diff --cached` 를 훑고 커밋한다

## 사고 대응

민감 정보가 push된 경우: ① 해당 자격증명 **즉시 폐기·재발급**(히스토리 세탁보다 먼저) ② `git filter-repo`로 히스토리 제거 ③ force push ④ 이 문서에 사후 기록.
