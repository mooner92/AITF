# decks/pptx — PowerPoint로 만드는 발표자료

2026-08-29부터 새 주차는 여기서 만듭니다. 기존 `../*.md` + `build-deck.py`(HTML) 경로는
1주차까지의 결과물을 유지하는 용도로 남아 있지만, **더 이상 새 주차에 쓰지 않습니다.**

## 왜 바꿨나

HTML 경로는 Paperlogy 폰트 임베드·글로우 이동·카운트업 애니메이션이 들어 있어 보기엔 좋지만,
**수정하려면 매번 원고를 고치고 다시 빌드해야 합니다.** 수업 하루 전날처럼 급하게 문구 하나
고칠 때 이 왕복이 병목이 됩니다. PowerPoint는 강사가 직접 열어 클릭 몇 번으로 고칠 수 있습니다.

**대신 잃는 것도 있습니다** — 이건 트레이드오프지 무료 업그레이드가 아닙니다:

- **폰트**: Paperlogy 임베드 대신 Windows 기본 서체(맑은 고딕)를 씁니다. 임베드하려면
  PowerPoint의 "글꼴 포함 저장"을 파일 열 때마다 수동으로 켜야 하는데, 그러면 다음 사람이
  또 PowerPoint에서 편집할 때 임베드가 깨지기 쉽습니다. 브랜드 통일성보다 편집 용이성을 택했습니다.
- **모션**: 글로우 이동·카운트업·fragment 단계 노출이 없습니다. 정적 슬라이드입니다.
- **발표자 노트**: PowerPoint 표준 노트 창을 씁니다 (`docs/design-spec.md`의 `S` 키 방식과 다름 —
  PowerPoint 자체 노트 보기를 씁니다. 오히려 더 표준적입니다).

## 사용법

```bash
npm install                 # 최초 1회 — pptxgenjs
node build-w0N.js           # 산출물: ../w0N-orientation.pptx (repo 루트 decks/)
```

## 만드는 법 — 새 주차

1. `build-w01.js` 를 복사해 `build-w0N.js` 로 이름을 바꿉니다
2. 슬라이드 헬퍼(`coverSlide`·`chapterSlide`·`cardsSlide`·`flowSlide`·`tableSlide`·`codeSlide`·
   `listSlide`·`statementSlide`)를 그대로 씁니다 — `docs/design-spec.md` §6 슬라이드 콘텐츠
   패턴과 1:1 대응합니다
3. `curriculum/detailed-plan.md` 의 해당 주차 절(만들기 목표·진행·강사 준비)을 슬라이드로 옮깁니다
4. `node build-w0N.js` 로 생성
5. **PowerPoint에서 직접 열어 검수합니다.** 이 서버엔 LibreOffice가 없어 헤드리스 렌더링 검사를
   못 합니다 — `python3 ../../scripts/pptx-check.py <파일>` 로 구조(슬라이드 수·발표자 노트 존재)만
   확인하고, 실제 레이아웃은 PowerPoint에서 눈으로 봅니다

## 생성 후에는 손으로 고칩니다

**한 번 만든 `.pptx`를 스크립트로 다시 생성해 덮어쓰지 않습니다.** 강사가 PowerPoint에서
직접 고친 내용이 스크립트 재실행으로 사라집니다. 스크립트는 **첫 뼈대를 만드는 용도**이고,
그 이후 진짜 원본은 `.pptx` 파일 자체입니다 — 그래서 HTML 산출물과 달리 `.pptx`는
`.gitignore` 대상이 아니라 **커밋합니다.**

내용을 크게 갈아엎어야 하면(예: 커리큘럼 자체가 바뀜) 스크립트를 고치고 새로 생성하되,
그 전에 기존 `.pptx`에서 강사가 손으로 추가한 내용이 있는지 먼저 확인합니다.

## 색·타이포 대응표

`docs/design-spec.md` 토큰을 pptxgenjs 헥스 색으로 옮긴 값입니다 (`build-w0N.js` 상단 `C` 객체).

| 토큰 | HTML | PPTX |
|---|---|---|
| 배경 | `--canvas` #000000 | 동일 |
| 제목 | `--ink` #fcfdff | 동일 |
| 본문 | `--body` rgba(252,253,255,.86) | #d4d4d8 (알파 없는 근사값) |
| 기본 강조 | `--blue` #3b9eff | 동일 |
| 주의·챕터 | `--orange` #ff801f | 동일 |
| 완료·핸드오프 | `--green` #11ff99 | 동일 |
| 고등반 | `--violet` #a78bfa | 동일 |

PPTX 텍스트 채우기는 알파(반투명)를 지원하지 않아 `rgba` 계열 토큰은 불투명 근사값으로 옮겼습니다.

## 참고

- 스킬 출처: [`anthropics/skills` — pptx](https://github.com/anthropics/skills/tree/main/skills/pptx)
  (Proprietary 라이선스 — 저장소에는 그 스킬 코드를 커밋하지 않습니다. 우리가 직접 쓴
  `build-w0N.js`만 커밋합니다)
- `pptxgenjs` 문법·함정: 위 스킬의 `SKILL.md` "Creating with pptxgenjs — gotchas" 절 참고
  (색은 `#` 없이 6자리 헥스만, `shadow` 옵션 객체 재사용 금지 등)
