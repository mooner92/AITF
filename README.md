<div align="center">

# AITF

**중고등학생 12주 AI 코딩 특강 — 인프라와 수업 기록 전부**

터미널에서 AI 에이전트에게 일을 시키고, 결과를 검증하고, 기록으로 남기는 과정.
그 수업을 굴리는 서버가 어떻게 만들어졌는지까지 공개합니다.

![스펙](https://img.shields.io/badge/specs-21%20문서-white?style=flat-square&labelColor=0a0a0a)
![커리큘럼](https://img.shields.io/badge/커리큘럼-v8.5-ff7a17?style=flat-square&labelColor=0a0a0a)
![방식](https://img.shields.io/badge/방식-Spec--Driven-a0c3ec?style=flat-square&labelColor=0a0a0a)
![서버](https://img.shields.io/badge/서버-Oracle%20A1%20aarch64-white?style=flat-square&labelColor=0a0a0a)
![라이선스](https://img.shields.io/badge/문서-CC%20BY--NC-7c3aed?style=flat-square&labelColor=0a0a0a)

</div>

---

## 무엇을 만들고 있나

중고등학생이 **웹 챗봇이 아니라 실무 개발자의 환경**에서 12주를 보내는 수업입니다.
브라우저를 열면 바로 리눅스 터미널이 뜨고, 거기서 AI 에이전트에게 일을 시킵니다.

| | |
|---|---|
| **학생이 하는 것** | 프로필 카드 → 발표자료 → 나만의 스킬 → Slack 봇 → 팀 프로젝트 |
| **매주 쌓이는 것** | 작품관 · 커밋 이력 · **AI가 자동으로 쓰는 반 위키** |
| **끝나면 남는 것** | GitHub으로 그대로 옮겨지는 12주치 포트폴리오 (잔디 포함) |
| **준비물** | 구글 계정 하나. 설치·가입 없음 |

---

## 이 저장소의 특징

**모든 결정에 근거가 남아 있습니다.** 21개 스펙 문서에 목표·설계·검증 기준과 함께
**결정 기록**이 붙어 있고, 판단이 바뀌면 지우지 않고 왜 바뀌었는지를 덧씁니다.

**문서보다 실물을 믿습니다.** "문서에 그렇게 쓰여 있다"가 근거가 되지 못한 사례들이
[`docs/verification-practice.md`](docs/verification-practice.md)에 정리돼 있습니다 —
바이너리를 뜯어 스킬 경로를 확인하고, 헤드리스 브라우저로 애니메이션이 실제로 도는지
보고, 로컬 모델 속도를 직접 재서 판단합니다.

**미검증은 미검증이라고 씁니다.** 추정치로 수업을 설계하지 않습니다.

---

## 어디부터 볼까

| 궁금한 것 | 볼 곳 |
|---|---|
| **12주에 뭘 하나** | [`curriculum/detailed-plan.html`](curriculum/detailed-plan.html) — 주차별 상세 (v8.5) |
| **서버가 어떻게 생겼나** | [`docs/architecture.html`](docs/architecture.html) — 5개 층 해부도 |
| **지금 어디까지 됐나** | [`docs/server-readiness-report.md`](docs/server-readiness-report.md) |
| **첫 수업은 어떻게 굴리나** | [`docs/day1-runbook.md`](docs/day1-runbook.md) — 분 단위 시간표·사고 대응 |
| **결정의 이유** | [`specs/README.md`](specs/README.md) — 스펙 현황판 |

HTML 문서는 내려받아 브라우저로 열면 됩니다. **글꼴이 파일에 들어 있어 오프라인에서도** 그대로 열립니다.

```bash
git clone git@github.com:mooner92/AITF.git
open AITF/docs/architecture.html
```

---

## 저장소 구조

```
specs/       스펙 21개 — 목표·설계·검증 기준·결정 기록 (P0~P11 + 확장)
curriculum/  수업 계획 — 강사용·학부모용·학원 요청용
decks/       주차별 발표자료 — 원고(.md)를 쓰면 자립 HTML 한 파일로 빌드
docs/        구조 해부도 · 운영 매뉴얼 · 검증 원칙
scripts/     서버 운영 — 계정·포트·스킬·위키·백업 (민감 값은 자리표시자)
materials/   학생 배포물 — 스킬 3종 · 규칙 문서 · 치트시트
web/         강사 관제탑 · 랜딩 페이지 · Gitea 테마
classlog/    수업 기록 (주차별)
```

---

## 어떻게 굴러가나

```
학생 브라우저
     │  Cloudflare Zero Trust 터널 (인바운드 포트 0)
     ▼
nginx ── 터미널 · 작품관 · Gitea · 관제탑 · 학생 웹서비스
     │
     ├── 학생별 리눅스 계정 (홈 700 · sudo 없음 · 메모리 상한)
     ├── Gitea — 1인 1저장소(모노레포) + 반별 위키
     └── 일요일 20시 자동 위키 → Notion 발행 → Slack 알림
```

- Oracle Cloud ap-seoul-1 · Ampere A1 (aarch64) 4 OCPU / 24GB · Oracle Linux 9
- **인바운드 포트를 열지 않습니다.** 모든 외부 접근은 터널을 통과합니다
- SELinux Enforcing 유지. 막히면 끄지 않고 `restorecon`/`semanage`로 해결합니다

---

## 자동 위키 — 이 저장소에서 제일 재미있는 부분

매주 일요일 밤, 서버가 그날 학생 활동을 모아 **위키를 스스로 씁니다.**

```
raw/         결정적 수집 — 커밋·폴더·작품·스킬. 불변, LLM 도 읽기만
students/    학생별 페이지가 12주간 자란다
skills/      스킬 엔티티 — 누가 언제 썼나. 링크 그래프의 허브
projects/    프로젝트 엔티티
```

`<!-- auto:활동 -->` 마커 **안쪽은 스크립트가 매주 덮어쓰고, 바깥은 LLM 이 쓴 서술**이라
서로 침범하지 않습니다. **모델이 없어도 사실은 쌓이고, 모델이 붙으면 서술이 자랍니다.**

7주차에 이 위키를 처음 공개합니다 — "이걸 매주 AI가 써왔습니다"가 그 주 주제
(에이전틱)의 실물 예시가 됩니다.

---

## 진행 방식

1. 각 단계는 `specs/NNN-*.md` 로 시작합니다 — 목표 / 설계 / 작업 / 검증 기준 / 결정 기록
2. 스펙이 정해진 뒤에 서버 작업을 합니다
3. 작업이 끝나면 **검증 기준을 실제로 통과시키고** 상태를 올립니다
4. 판단이 바뀌면 **지우지 않고 왜 바뀌었는지를 덧씁니다**

## 기여자용

```bash
git config core.hooksPath .githooks   # 민감정보 커밋 차단 훅
```

무엇을 올리지 않는지는 [`SECURITY.md`](SECURITY.md)에 있습니다 —
실제 IP·키·학생 개인정보는 서버에만 두고 저장소에는 자리표시자만 둡니다.
