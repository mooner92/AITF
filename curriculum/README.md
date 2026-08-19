# curriculum — 수업 계획 문서

각 문서는 **누가 읽는가**로 나뉩니다. HTML은 같은 내용을 읽기 좋게 조판한 것으로,
페이퍼로지 글꼴이 파일 안에 내장되어 있어 인터넷 없이 열어도 그대로 보입니다.

| 문서 | 독자 | HTML |
|---|---|---|
| [`detailed-plan.md`](detailed-plan.md) | **강사·원장 (내부)** — 주차별 상세, 중등/고등 갈래 분리 | [`detailed-plan.html`](detailed-plan.html) |
| [`parent-guide.md`](parent-guide.md) | **학부모** — 배포용 요약 | [`parent-guide.html`](parent-guide.html) |
| — | **학생** — 12주 지도 (스택·스포일러 없음) | [`student-guide.html`](student-guide.html) |
| [`academy-request.md`](academy-request.md) | **원장** — 개강 전 협조 요청 (계정·IP·명단) | [`academy-request.html`](academy-request.html) |
| [`class-plan.md`](class-plan.md) | 학원 제출용 요약 계획서 | — |
| [`overview.md`](overview.md) | 공개용 과정 개요 | — |
| [`season2-concept.md`](season2-concept.md) | 시즌 2 구상 (대부분 본 과정에 흡수됨) | — |

> **배포 주의** — `detailed-plan`은 10주차 진행에 서프라이즈 구성이 있어
> 학생에게 배포하지 않습니다. 학생·학부모에게는 `parent-guide`를 씁니다.

## HTML 다시 만들기

`*.src.html`이 원본이고, `build-html.py`가 문서에 실제로 쓰인 글자만 남긴
서브셋 글꼴을 넣어 `*.html`로 뽑습니다. 본문을 고칠 때는 `.src.html`을 고친 뒤 다시 빌드하세요.

```bash
# 1. Paperlogy 배포 zip을 풀어 TTF 9종을 curriculum/fonts/ 에 둔다 (저장소에 포함하지 않음)
# 2. 의존성
pip install "fonttools[woff]" brotli
# 3. 빌드
python3 build-html.py detailed-plan.src.html parent-guide.src.html academy-request.src.html
```

글꼴 위치를 바꾸려면 `PAPERLOGY_DIR` 환경변수를 쓰면 됩니다.
원본 9웨이트는 각 664KB지만, 서브셋 후에는 문서당 4웨이트 86~122KB로 들어갑니다.
