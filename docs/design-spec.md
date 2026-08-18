# AITF 디자인 스펙

> 이 저장소의 모든 문서·발표자료가 따르는 시각 규칙입니다.
> 새 산출물을 만들 때는 이 문서의 토큰을 그대로 쓰고, 임의로 색·글꼴을 새로 정하지 않습니다.
>
> **적용 범위**: 문서 HTML (`curriculum/*.html`, `docs/*.html`), 발표자료 (`decks/*.html`)
> **적용 제외**: 학생용 스킬 템플릿 (`materials/skills/*/template.html`) — 학생이 직접 고쳐야 하므로 단순하게 유지합니다.

---

## 0. 원칙

1. **단일 테마 확정.** 순흑 캔버스 하나로 고정합니다. 라이트 모드를 만들지 않습니다.
   대신 **모든 색을 명시적으로 칠합니다** — 배경을 비워두면 뷰어의 테마가 비쳐 글자가 사라집니다.
2. **색은 한 곳에만 쓴다.** 강조색은 화면당 한 군데. 나머지는 전부 무채색으로 눕힙니다.
3. **그림자 대신 헤어라인.** 박스 섀도를 쓰지 않습니다. 깊이는 1px 테두리와 배경 명도차로만 만듭니다.
4. **글로우는 분위기용.** 큰 반경의 저채도 방사 그라디언트를 섹션당 최대 1개. 내용을 가리면 안 됩니다.
5. **외부 요청 0.** 폰트·이미지·스크립트를 전부 파일 안에 넣습니다 (CSP 차단 + 오프라인 열람 대응).

---

## 1. 색상

### 1-1. 토큰 정의

CSS 커스텀 프로퍼티로 `:root`에 선언합니다. **미디어 쿼리나 `[data-theme]` 안에서만 정의되는 색이 있으면 안 됩니다.**

```css
:root{
  /* 바탕 — 명도가 낮은 순서 */
  --canvas:#000000;    /* 페이지 바탕. body에 반드시 명시 */
  --sunken:#050507;    /* 카드보다 더 들어간 면 — 표 머리글, 카드 속 카드 */
  --card:#0a0a0c;      /* 기본 카드 면 */
  --elevated:#101012;  /* 떠 있는 면 — 콜아웃, 알약 버튼 */

  /* 글자 — 명도가 높은 순서 */
  --ink:#fcfdff;                    /* 제목, 강조 본문 */
  --body:rgba(252,253,255,.86);     /* 본문 기본 */
  --charcoal:rgba(252,253,255,.7);  /* 보조 설명 */
  --mute:#a1a4a5;                   /* 캡션 */
  --ash:#888e90;                    /* 라벨, 표 머리글 */
  --faint:rgba(252,253,255,.42);    /* 비활성 */

  /* 선 */
  --hair:rgba(255,255,255,.06);         /* 기본 구분선 */
  --hair-strong:rgba(255,255,255,.14);  /* 강조 테두리 */
  --divider:rgba(255,255,255,.04);      /* 섹션 구분 */

  /* 강조 — 의미가 있을 때만 */
  --blue:#3b9eff;    /* 기본 강조. 링크·라벨·번호 */
  --green:#11ff99;   /* 긍정·완료·중등반 */
  --violet:#a78bfa;  /* 고등반 */
  --orange:#ff801f;  /* 주의·불가침·우선순위 */
  --yellow:#ffc53d;  /* 경고·준비 필요 */
}
```

### 1-2. 강조색 사용 규칙

| 색 | 쓰는 곳 | 쓰지 않는 곳 |
|---|---|---|
| `--blue` | 섹션 eyebrow, 번호, 링크, 기본 글로우 | 본문 안 임의 강조 |
| `--green` | 완료 상태, 중등반 갈래 | 일반 성공 메시지 남발 |
| `--violet` | 고등반 갈래 | 그 외 |
| `--orange` | 불가침 주차, 우선순위 1·2·3 | 단순 장식 |
| `--yellow` | 강사 준비 항목, 배포 주의 | 본문 강조 |

**한 화면에 강조색 2종 이상이 동시에 눈에 띄면 과합니다.** 중등/고등 대비처럼 짝을 이루는 경우만 예외입니다.

### 1-3. 글로우

```css
/* 섹션당 최대 1개. pointer-events:none 필수 */
.hero::before{
  content:"";position:absolute;top:-280px;left:46%;transform:translateX(-50%);
  width:1000px;height:560px;pointer-events:none;
  background:radial-gradient(closest-side,rgba(0,117,255,.28),rgba(0,117,255,0) 72%);
}
```

- 불투명도 상한: 히어로 `.28`, 카드 `.16`, 그 외 `.13`
- 반드시 `closest-side` — 기본값을 쓰면 가장자리가 각지게 잘립니다
- 부모에 `overflow:hidden`, 자식 콘텐츠에 `position:relative`

---

## 2. 타이포그래피

### 2-1. 서체

**Paperlogy 단일 서체**로 한글·영문·숫자를 모두 처리합니다. 서체를 섞지 않고 **웨이트 폭으로 위계를 만듭니다.**

```css
--font:Paperlogy,-apple-system,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;
```

| 웨이트 | 파일 | 역할 |
|:--:|---|---|
| 200 | `Paperlogy-2ExtraLight.ttf` | 대형 디스플레이 — h1, h2, 큰 숫자 |
| 400 | `Paperlogy-4Regular.ttf` | 본문 |
| 600 | `Paperlogy-6SemiBold.ttf` | 소제목, 라벨, 강조 |
| 800 | `Paperlogy-8ExtraBold.ttf` | 최상위 강조 (드물게) |

**4개만 임베드합니다.** 9웨이트를 다 넣으면 파일이 무의미하게 커집니다.
원본 TTF는 저장소에 넣지 않고 (`curriculum/fonts/` — gitignore) 배포 zip에서 풉니다.

### 2-2. 임베드 방법

문서에 실제로 쓰인 글자만 서브셋해 woff2 data URI로 넣습니다. 자동화: [`curriculum/build-html.py`](../curriculum/build-html.py)

```bash
pip install "fonttools[woff]" brotli
python3 build-html.py <문서>.src.html
```

원본 664KB/웨이트 → 서브셋 후 문서당 4웨이트 합계 **87~124KB**.

### 2-3. 스케일

문서와 슬라이드가 기준 단위가 다릅니다.

**문서** — `px` + `clamp()` (읽는 매체)

| 역할 | 크기 | 웨이트 | 자간 | 행간 |
|---|---|:--:|:--:|:--:|
| h1 | `clamp(40px,7.4vw,80px)` | 200 | `-.035em` | 1.05 |
| h2 | `clamp(27px,4.2vw,42px)` | 200 | `-.03em` | 1.18 |
| h3 | 17.5–19px | 600 | `-.01em` | 1.42 |
| 본문 | 15.5–16px | 400 | — | 1.72 |
| 리드 | `clamp(16.5px,2vw,20px)` | 400 | — | 1.64 |
| eyebrow / 라벨 | 11.5–12.5px | 600 | `.17em` + `uppercase` | — |
| 캡션 | 13–13.5px | 400 | — | 1.6 |

**슬라이드** — `vmin` (화면 크기와 무관하게 비율 유지). §5 참조.

### 2-4. 규칙

- 본문 한 줄은 `max-width:74ch` 이하. 리드는 `52ch`, 카드 안 본문은 제한 없음.
- 제목에 `text-wrap:balance`.
- 숫자가 세로로 정렬되는 표·카운터에는 `font-variant-numeric:tabular-nums`.
- h1·h2의 부분 강조는 `<b>`(600) 또는 `<em>`(600 + `--blue`). `<em>`의 기울임은 해제합니다.
- 대문자 라벨은 한글에 적용되지 않으므로, 한글 라벨은 자간만 주고 `text-transform`은 영문에만 걸립니다.

---

## 3. 레이아웃

### 3-1. 폭

| 문서 유형 | `max-width` |
|---|---|
| 표·주차 카드가 많은 문서 | 1040px |
| 표준 문서 | 960px |
| 요청서·메모 등 짧은 문서 | 880px |

좌우 패딩 24px, 하단 여백 110–120px.

### 3-2. 리듬

```css
section{padding:72px 0;border-top:1px solid var(--divider)}
@media(max-width:760px){ section{padding:54px 0} }
```

- 히어로: `112px 0 68px` (모바일 `80px 0 52px`)
- 섹션 사이는 여백 + 1px 구분선. 큰 제목으로만 나누지 않습니다.
- 형제 요소 간격은 flex/grid의 `gap`으로 줍니다. 개별 `margin`으로 벌리면 상쇄되어 어긋납니다.

### 3-3. 모서리

```css
--r-sm:6px; --r-md:8px; --r-lg:12px; --r-xl:16px; --r-full:9999px;
```

카드 12px, 큰 카드 16px, 콜아웃·표 셀 8px, 알약 `--r-full`.

### 3-4. 가로 스크롤

표·코드·다이어그램은 **자기 컨테이너 안에서만** 가로 스크롤합니다. 페이지 본문은 절대 가로로 밀리면 안 됩니다.

```css
.tw{overflow-x:auto;border:1px solid var(--hair-strong);border-radius:var(--r-lg)}
table{min-width:520px}
```

---

## 4. 컴포넌트

### 4-1. 표

```css
th{font-size:11.5px;font-weight:600;letter-spacing:.11em;text-transform:uppercase;
   color:var(--ash);background:var(--sunken);white-space:nowrap}
td{color:var(--charcoal);line-height:1.58}
td:first-child{color:var(--ink)}      /* 첫 열은 항목명이므로 밝게 */
tr:last-child td{border-bottom:none}
```

### 4-2. 콜아웃 (`.point`)

라벨 + 본문 2단 구조. 라벨 색으로 종류를 구분합니다.

```css
.point{background:var(--elevated);border:1px solid var(--hair-strong);
       border-radius:var(--r-md);padding:16px 18px}
.point .k{font-size:10.5px;font-weight:600;letter-spacing:.13em;
          text-transform:uppercase;color:var(--blue);margin-bottom:7px}
.point.prep .k{color:var(--yellow)}   /* 강사 준비 */
```

### 4-3. 갈래 (`.split` / `.lane`)

중등·고등처럼 **대등한 두 갈래**를 나란히 놓을 때 씁니다. 좁은 화면에서는 1열로 떨어집니다.

```css
.split{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:760px){ .split{grid-template-columns:1fr} }
.lane.mid .who{color:var(--green);background:rgba(17,255,153,.09);
               border:1px solid rgba(17,255,153,.26)}
.lane.high .who{color:var(--violet);background:rgba(167,139,250,.1);
                border:1px solid rgba(167,139,250,.3)}
```

### 4-4. 다이어그램

인라인 SVG만 씁니다. 라이브러리·외부 이미지 금지.

- `viewBox`로 크기를 정하고 CSS로 `width:100%;height:auto`
- 선·글자는 `currentColor` — 의미를 가진 요소 하나만 실제 색을 씁니다
- 화살표는 `<defs><marker>` 또는 작은 `<polygon>`
- 글자 11~13px, 설명 문장은 그림이 아니라 `<figcaption>`에
- `role="img"` + `aria-label`에 그림이 말하는 바를 한 문장으로

### 4-5. 접근성

```css
a:focus-visible{outline:2px solid var(--blue);outline-offset:2px}
@media(prefers-reduced-motion:reduce){ html{scroll-behavior:auto} }
```

---

## 5. 발표자료 확장 규칙

문서와 같은 색·서체를 쓰되, **단위와 동작이 다릅니다.**

### 5-1. 무대

- 고정 비율 **16:9**. 슬라이드는 뷰포트를 꽉 채우고 내용은 `vmin` 기준으로 잡습니다.
- 한 슬라이드 = 한 메시지. 본문 6줄 이하.
- 슬라이드 패딩 `7vmin 9vmin`.

| 역할 | 크기 (vmin) | 웨이트 |
|---|:--:|:--:|
| 표지 제목 | 9 | 200 |
| 슬라이드 제목 | 6.4 | 200 |
| 소제목 | 3.6 | 600 |
| 본문·항목 | 3.0 | 400 |
| eyebrow | 1.9 | 600 |
| 각주·출처 | 1.7 | 400 |

### 5-2. 조작

| 키 | 동작 |
|---|---|
| `→` `↓` `Space` `PageDown` | 다음 단계 (fragment가 남아 있으면 fragment 먼저) |
| `←` `↑` `PageUp` | 이전 단계 |
| `Home` / `End` | 처음 / 마지막 |
| `F` | 전체화면 |
| `O` | 전체 슬라이드 개요 (그리드) |
| `.` | 화면 가리기 (검은 화면) |
| 숫자 + `Enter` | 해당 번호로 이동 |

클릭/탭도 좌우 절반으로 동작합니다. 현재 위치는 `location.hash`에 기록해 새로고침·링크 공유가 됩니다.

### 5-3. 모션

**네 층으로 나눕니다.**

1. **슬라이드 전환** — 같은 문서 안 View Transition API. Chrome·Edge·Safari 18·Firefox 144에서 동작하고,
   미지원 브라우저는 전환 없이 즉시 교체되어 아무 문제가 없습니다 (점진적 향상).
2. **등장 계단** — 슬라이드에 들어올 때 직계 자식들이 위로 1.4vmin 떠오르며 60ms 간격으로
   차례로 나타납니다 (0.5s). 전환이 끝나갈 때쯤 시작해 이어집니다. 모든 슬라이드 공통 —
   슬라이드마다 다른 등장 효과를 만들지 않습니다.
3. **fragment 등장** — 발표자가 진행하는 단계 노출. CSS `transition`만 씁니다.
4. **수치 모션** — 카운트업·막대 성장. 슬라이드에 들어올 때마다 재생하고,
   같은 슬라이드 안에서는 반복하지 않습니다 (fragment를 오가도 숫자가 요동하지 않게).

```css
/* 전환: 방향에 따라 밀어내기 */
::view-transition-old(slide){animation:slide-out .28s cubic-bezier(.4,0,.2,1) both}
::view-transition-new(slide){animation:slide-in .28s cubic-bezier(.4,0,.2,1) both}

/* fragment: 6px 올라오며 페이드 */
.fragment{opacity:0;transform:translateY(6px);
          transition:opacity .32s ease,transform .32s ease}
.fragment.on{opacity:1;transform:none}
```

**금지**: 튀거나 회전하는 전환, 0.4초를 넘는 전환, 슬라이드마다 다른 전환 효과,
같은 수치 모션의 반복 재생 (뒤로 갔다 와도 숫자가 다시 오르지 않습니다).
모션은 "다음으로 넘어갔다"를 알리는 용도이지 볼거리가 아닙니다.

### 5-3-1. 글로우 — 덱 전체에 하나, 진행과 함께 이동

문서의 글로우는 섹션마다 고정이지만, **발표자료의 글로우는 덱 전체에 하나**입니다.
첫 장에서 화면 왼쪽에 있다가 장이 넘어갈수록 오른쪽으로 옮겨 가서, 마지막 장에서
오른쪽 끝에 도착합니다. 청중은 의식하지 못해도 "얼마나 왔는지"가 빛의 위치로 전달됩니다.

```css
#glow{
  position:fixed;top:-34vmin;height:86vmin;width:130vmin;
  left:calc(14vw + var(--gx,0) * 72vw);transform:translateX(-50%);
  background:radial-gradient(closest-side,var(--glow-c,rgba(0,117,255,.34)),transparent 72%);
  transition:left .8s cubic-bezier(.4,0,.2,1),background .5s ease;
}
```

- `--gx` = 현재 장 / (전체 장 − 1). 엔진이 계산합니다.
- 이동 범위는 14vw~86vw — 빛의 중심이 화면 밖으로 나가지 않습니다.
- 불투명도는 문서(.28)보다 진한 **.34** — 발표장 프로젝터는 명암비가 낮아 옅으면 사라집니다.
- 색은 슬라이드 class로 바꿉니다: `g-green`(.24) `g-violet`(.28) `g-orange`(.26) `g-none`(끔).
  기본은 파랑이며, 색 변경도 이동과 같은 easing으로 부드럽게 넘어갑니다.

### 5-3-2. 수치 컴포넌트

수치를 보여줄 때는 문장이 아니라 전용 컴포넌트를 씁니다. 외부 라이브러리는 쓰지 않습니다 —
shadcn/ui의 **디자인 언어와 차트 팔레트는 가져오되, npm 패키지는 가져오지 않습니다.**
발표자료는 자립 실행 파일이라 React 런타임이 들어갈 자리가 없고, CSP가 외부 요청을 차단합니다.
필요한 요소는 아래처럼 CSS/SVG로 직접 만듭니다.

**차트 색은 UI 강조색과 분리합니다.** `--green`(#11ff99) 같은 UI 강조색은 라벨·태그용
쨍한 색이라 데이터에 부으면 싸구려 대시보드가 됩니다. 차트에는 shadcn 기본 팔레트의
눅은 색만 씁니다:

```css
--chart-1:#2662d9;  /* 파랑 — 기본값, 첫 계열 */
--chart-2:#2eb88a;  /* 청록 — 개선·비교 대상 */
--chart-3:#e88c30;  /* 주황 */
--chart-4:#af57db;  /* 보라 */
--chart-5:#e23670;  /* 분홍 */
```

한 차트에 3색을 넘기지 않습니다. 색이 더 필요하면 차트가 아니라 표로 갈 데이터입니다.

**카운트업** — 큰 수 하나를 각인시킬 때:

```html
<div class="card"><div class="k">12주 전체 예상</div>
  <div class="v" data-count="250" data-prefix="$"></div></div>
```

슬라이드에 들어올 때 0부터 ease-out으로 차오릅니다(0.9초). 소수점 자릿수는
`data-count` 값의 표기를 따르고, `data-prefix`/`data-suffix`로 단위를 붙입니다.

**가로 막대** — 두세 값을 비교할 때:

```html
<div class="bars">
  <div class="bar"><span class="t">1주차</span>
    <span class="track"><i style="--w:100%"></i></span><span class="n">45분</span></div>
  <div class="bar c2"><span class="t">12주차</span>
    <span class="track"><i style="--w:38%"></i></span><span class="n">17분</span></div>
</div>
```

기본은 `--chart-1`, `c2`~`c5`로 계열을 바꿉니다. 왼쪽에서 자라나며(0.9초, ease-out-expo),
막대가 여럿이면 위에서부터 120ms 시차를 두고 차례로 자랍니다.
fragment 안에 넣으면 그 단계에서 재생됩니다. 모서리는 살짝만 둥글게(0.6vmin) —
알약형 막대는 끝점 위치를 흐립니다.

**흐름** — 단계·여정을 보여줄 때:

```html
<div class="flow"><span>웹페이지</span><i>→</i><span>그림</span><i>→</i>
  <span class="hi">발표 슬라이드</span><i>→</i><span>작품관</span></div>
```

강조할 한 칸만 `hi`(흰 배경 반전). 두 칸 이상 반전하면 강조가 아닙니다.

**쓰지 않는 것**: 원형 차트(각도 비교는 눈이 못 합니다), 3D, 그라디언트 채움,
축이 잘린 막대. 수치가 4개를 넘으면 슬라이드가 아니라 표로 갑니다.

### 5-4. 모션 접근성 (필수)

```css
@media(prefers-reduced-motion:reduce){
  ::view-transition-old(slide),::view-transition-new(slide){animation:none}
  .fragment{transition:none}
}
```

이 블록이 없으면 전정기관 질환이 있는 청중에게 실제로 해롭습니다. **빠뜨리지 않습니다.**

### 5-5. 발표자 노트

`<aside class="notes">`에 적습니다. 화면에는 나오지 않고, `S` 키를 누르면 별도 창에 현재/다음 슬라이드와 함께 뜹니다.

---

## 6. 하지 않는 것

이 목록은 흔한 AI 생성 디자인의 특징이자, 우리가 피하는 것입니다.

- 크림색(#F4F1EA) 바탕 + 세리프 + 테라코타 강조
- 보라→파랑 그라디언트 히어로
- Inter·Space Grotesk 기본 사용
- 섹션 제목 앞 이모지
- 모든 것을 가운데 정렬
- 카드마다 왼쪽 강조 막대
- 내용이 순서가 아닌데 붙이는 01 / 02 / 03 번호
  → **번호는 실제로 순서·단계일 때만** 씁니다 (주차, 우선순위, 절차)
- 박스 섀도로 만드는 깊이감
- 슬라이드마다 다른 전환 효과

---

## 7. 검증

산출물을 내기 전에 통과시킵니다.

```bash
python3 scripts/check-design.py <파일.html>
```

검사 항목:

1. `__FONT_FACES__` 플레이스홀더 잔존 여부
2. `@font-face` 4개 임베드 + 본문 글리프 누락 0
3. `body`에 `background` 명시
4. 미디어 쿼리·`[data-theme]` 안에서만 정의된 색 (테마 붕괴 원인)
5. 태그 짝 맞음
6. 외부 리소스 참조 (`http://`, `https://`, `//cdn`) — 폰트·이미지·스크립트
7. 발표자료: `prefers-reduced-motion` 블록 존재
8. 민감정보 (공인 IP, 도메인, 키 패턴)

---

## 참고

- 원본 디자인 레퍼런스: Resend 디자인 시스템 분석 (순흑 캔버스, 헤어라인, 무채색 + 단일 강조)
- 적용 사례: [`curriculum/detailed-plan.html`](../curriculum/detailed-plan.html), [`curriculum/parent-guide.html`](../curriculum/parent-guide.html), [`curriculum/academy-request.html`](../curriculum/academy-request.html)
- 서체: [Paperlogy](https://www.paperlogy.co.kr/) — 무료 배포, 상업적 이용 가능
