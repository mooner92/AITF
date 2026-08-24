# rules/ — 학생 저장소에 배포하는 규칙 문서

**내부 문서입니다** (학생 배포 대상 아님 — 이 README 는 배포에서 제외됩니다).

## 구조

학생마다 저장소는 하나(모노레포)입니다. 프로젝트가 늘 때마다 저장소를 만들지 않고
폴더가 늘어납니다. 규칙 문서는 저장소 안 `rules/` 폴더로 들어갑니다:

```
project/                    ← 학생 저장소 (1인 1개, 12주 내내 이것 하나)
  README.md                 ← 저장소 안내 (materials/student-repo/README.md)
  MY-SERVER.md              ← 포트·주소 (alloc-ports.sh 가 개인화 생성)
  rules/                    ← 이 폴더의 문서들이 배포되는 곳
  use_skills/  make_bot/ …  ← 주차별 프로젝트 폴더 (naming.md 규칙)
  public/                   ← 작품관 (심링크)
```

## 배포 방법

```bash
./scripts/push-rule.sh naming          # 규칙 1개를 전 학생에게
./scripts/push-rule.sh sdd make_sdd    # 여러 개 동시
./scripts/push-rule.sh --sync          # 배포된 전체를 재배포 (신규·리셋 계정 복구)
./scripts/push-rule.sh --sync ⟪계정⟫    # 한 계정만
./scripts/push-rule.sh --list          # 배포 가능/배포됨 목록
```

- 심링크가 아니라 **복사**입니다 — 학생의 다음 `git add .` 에 자연스럽게 포함되고,
  수료 후 GitHub 이전 때도 규칙 문서가 함께 갑니다 (심링크는 깨집니다).
- 같은 이름을 다시 배포하면 **덮어씁니다** — 규칙 문서는 강사 소유이고,
  학생 수정분을 보존하지 않습니다 (문서 머리말에 명시돼 있습니다).

## 배포 시점 (커리큘럼 연동)

| 문서 | 시점 | 계기 |
|---|---|---|
| `naming.md` | 1주차 (계정 생성 시) | 첫 폴더를 만들기 전에 |
| `commit.md` | 4주차 | git 3동작을 배우는 주 |
| `sdd.md` | 10주차 | 스펙을 쓰고 맡기는(SDD) 주 |
| `make_sdd.md` | 10주차+ | 기존 프로젝트를 스펙 구조로 재정리할 때 |

수업 중 "지금 이 규칙을 떨어뜨린다" 자체가 장면입니다 — 배포 직후 학생이
`ls rules/` 로 새 파일을 발견하고, 열어 보고, 커밋해서 자기 것으로 만듭니다.
