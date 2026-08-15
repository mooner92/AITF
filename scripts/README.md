# scripts — 서버 운영 스크립트 (공개 버전)

서버 실배치 위치는 `/opt/scripts`(root 700). 여기 있는 것은 **민감 값이 없는 공개 버전**이며,
`accounts.csv`(계정·비밀번호)와 토큰류는 서버에만 존재한다. `<...>` 표기는 배포 시 실값으로 치환.

| 스크립트 | 용도 | 관련 스펙 |
|---|---|---|
| `create-accounts.sh` | CSV 기반 학생 계정 일괄 생성 + 메모리 상한 | [040](../specs/040-accounts.md) |
| `reset-home.sh` | 학생 홈을 템플릿으로 초기화 | 040 |
| `setup-git-students.sh` | 학생 git 신원·인증·remote 사전 주입 | [060](../specs/060-git.md) |
| `collect-tokens.sh` | tokscale 학생별 수집 (cron) | [070](../specs/070-observability.md) |
| `snapshot-class.sh` | 수업 후 반 단위 증분 스냅샷 + 진도 요약 | [080](../specs/080-snapshot.md) |
| `restore-student.sh` | 학생 단위 복구 | 080 |
| `cleanup-class.sh` | 반 교대 시 잔여 프로세스 정리 | 080/100 |
| `reset-course.sh` | 종강 아카이브 + 초기화 안내 | 080 |
