<!-- class: cover -->
^ 1주차
# AI를 <em>처음</em> 만나요

오늘은 chatgpt.com 계정을 만들고, AI에게 처음으로 뭔가를 시켜봅니다.

- 중등반 {{CLASS_MID_TIME}} · 고등반 {{CLASS_HIGH_TIME}}

??? 시작 전 확인: 노트북 전원, 브라우저 열림, 구글 계정 안내 카드 배부, chatgpt.com 접속 테스트, 핸즈온 문장 준비(Gitea handson 저장소 열어두기). 첫 5분은 자리 정돈과 출석 확인만 한다.

??? 여기서 2분. 정시에 시작하고, 늦게 온 학생은 뒤에서 합류시킨다.

---
## 저는 <b>{{INTRO_NAME}}</b>입니다

![](assets/img/intro.jpg)

^^^
{{INTRO_ROLE}}

??? 여기서 3분. 사진 한 장(작업 화면·현장 사진 등 — assets/img/intro.jpg 로 넣으면 빌드에 들어간다). 이력을 읊지 말고 "무엇을 만드는 사람인가"만 말한다.

---
## 이런 걸 <b>만들어 왔습니다</b>

<div class="flow">
<span>{{INTRO_BUILT_1}}</span>
<span>{{INTRO_BUILT_2}}</span>
<span class="hi">{{INTRO_BUILT_3}}</span>
</div>

??? 여기서 2분. 에피소드 한 줄은 대본 참고 — 화면에 띄우지 않고 말로 한다. 학생이 아는 것에 빗대어 말한다. 회사 이름·기술 스택은 의미 없다 — "너희가 쓰는 그거"가 통한다. 마지막 한 줄로 긴장을 푼다.

---
## 왜 이 수업을 <b>하냐면</b>

{{INTRO_WHY}}

^^^
> 12주 뒤에 여러분은 "AI를 써봤다"가 아니라 **"AI로 뭘 만들어봤다"**고 말하게 됩니다. 그게 이 수업의 전부입니다.

??? 여기서 2분. 이 장이 첫 시간의 감정적 정점이다 — 천천히 말한다.

---
## 여러분은 <b>AI를 써본 적</b> 있나요?

<div class="grid c3">
<div class="card"><div class="k">한 번도</div><div class="v">안 써봤어요</div></div>
<div class="card"><div class="k">가끔</div><div class="v">써봤어요</div></div>
<div class="card strong"><div class="k">거의 매일</div><div class="v">써요</div></div>
</div>

??? 여기서 5분(멘트는 대본). 실제로 손을 들게 하고 숫자를 눈으로 확인한다. "한 번도"가 많으면 다음 장을 천천히, "매일"이 많으면 가입 단계를 빠르게 넘기고 실습을 늘린다. 반응을 보고 이후 시간 배분을 즉석에서 조정하는 게 이 장의 목적.

---
<!-- class: g-none -->
## AI는 <b>다음 말을 맞혀요</b>

<div class="flow">
<span>안녕하세</span><i>→</i>
<span class="hi">?</span>
</div>

^^^
누구나 "요"를 떠올려요. AI도 같은 일을 해요 — 수많은 글을 읽고, **다음에 올 말**을 맞혀요.

^^^
> 이 간단한 걸 아주 잘하게 만든 게 지금의 AI예요.

??? 여기서 5분. "안녕하세…" 하고 말을 멈추면 교실이 알아서 "요"를 외친다 — 그 순간이 개념 설명을 대신한다(대본 참고). 신경망·학습 데이터 같은 용어는 꺼내지 않는다.

---
## AI는 <b>갑자기 나온 게 아니에요</b>

<div class="flow">
<span>규칙을 직접 코딩</span><i>→</i>
<span>예시로 배우게 함</span><i>→</i>
<span>뇌를 닮은 그물로</span><i>→</i>
<span class="hi">하나가 여러 일을</span>
</div>

^^^
<div class="grid c4">
<div class="card"><div class="k">옛날</div><div class="v">규칙 코딩</div><p>"고양이는 귀가 뾰족하고…" 사람이 다 적어줌 — 금방 한계</p></div>
<div class="card"><div class="k">머신러닝</div><div class="v">예시로 학습</div><p>고양이 사진 만 장을 보여주면 스스로 특징을 찾아요</p></div>
<div class="card"><div class="k">딥러닝</div><div class="v">깊은 그물</div><p>뇌 신경망을 흉내 낸 층을 깊이 쌓았더니 훨씬 잘하게 됐어요</p></div>
<div class="card strong"><div class="k">파운데이션 모델</div><div class="v">지금</div><p>글 전체로 배운 하나가 번역·코딩·그림까지 다 해요</p></div>
</div>

??? 여기서 3분. 연도·인명은 꺼내지 않는다 — "직접 가르치다가, 예시로 배우게 했더니, 크게 만들수록 잘하더라"라는 줄기 하나만. 학생 질문("알파고는요?")이 나오면 "바둑 딥러닝 시대의 스타"로 짧게 받는다. 시간이 밀리면 이 장과 다음 장을 통째로 건너뛴다 — 자르는 순서 1번.

---
## 전부 <b>한 가족</b>이에요

<figure class="media" style="border:none;background:none">
<svg viewBox="0 0 760 300" role="img" aria-label="인공지능 안에 머신러닝, 그 안에 딥러닝이 있고, 딥러닝을 아주 크게 키운 것이 파운데이션 모델이다"
     style="width:100%;max-height:46vmin;color:#fcfdff">
  <g font-family="inherit">
    <ellipse class="draw" pathLength="1" cx="300" cy="150" rx="270" ry="135" fill="none" stroke="currentColor" stroke-opacity=".3"/>
    <text class="pop" style="--d:.2s" x="300" y="52" font-size="19" fill="currentColor" fill-opacity=".65" text-anchor="middle">인공지능 — 똑똑해 보이는 모든 프로그램</text>
    <ellipse class="draw" style="--d:.25s" pathLength="1" cx="300" cy="168" rx="195" ry="96" fill="none" stroke="currentColor" stroke-opacity=".45"/>
    <text class="pop" style="--d:.45s" x="300" y="106" font-size="19" fill="currentColor" fill-opacity=".8" text-anchor="middle">머신러닝 — 예시로 배우는 것</text>
    <ellipse class="draw" style="--d:.5s" pathLength="1" cx="300" cy="188" rx="120" ry="58" fill="none" stroke="#3b9eff" stroke-opacity=".7"/>
    <text class="pop" style="--d:.7s" x="300" y="163" font-size="19" fill="#3b9eff" text-anchor="middle">딥러닝 — 깊은 그물로</text>
    <circle class="draw" style="--d:.75s" pathLength="1" cx="300" cy="210" r="24" fill="#3b9eff" fill-opacity=".18" stroke="#3b9eff"/>
    <text class="pop" style="--d:.9s" x="300" y="216" font-size="15" fill="#3b9eff" text-anchor="middle">지금</text>
    <g stroke="#3b9eff" stroke-width="2" fill="none">
      <path class="draw" style="--d:1s" pathLength="1" d="M330,205 Q450,180 540,180"/>
    </g>
    <g class="pop" style="--d:1.25s">
      <text x="552" y="165" font-size="20" fill="#3b9eff">파운데이션 모델</text>
      <text x="552" y="192" font-size="15" fill="currentColor" fill-opacity=".65">딥러닝을 아주 크게 키워서</text>
      <text x="552" y="214" font-size="15" fill="currentColor" fill-opacity=".65">글·코드·그림을 한꺼번에 배운 것</text>
      <text x="552" y="236" font-size="15" fill="currentColor" fill-opacity=".65">ChatGPT가 바로 이거예요</text>
    </g>
  </g>
</svg>
<figcaption>바깥에서 안으로 들어갈수록 최근 이야기예요</figcaption>
</figure>

^^^
> 같은 점은 하나예요 — **전부 예시로 배워요.** 달라진 건 크기예요. 크게 만들수록, 시키지 않은 일까지 잘하게 됐어요.

??? 여기서 3분. 이 그림이 이 장의 전부다 — "AI ⊃ 머신러닝 ⊃ 딥러닝, 그걸 키운 게 파운데이션 모델". 마지막 한 줄("크기가 달라지니 시키지 않은 일까지")이 다음 장(AI는 하나가 아니에요 — 회사마다 자기 파운데이션 모델)으로 이어진다. 밀리면 앞 장과 함께 건너뛴다.

---
## AI는 <b>하나가 아니에요</b>

<div class="grid c3">
<div class="card">
  <div class="k" style="color:#74aa9c">OpenAI</div>
  <div class="v">ChatGPT</div>
  <p>제일 많이 써요. 오늘 우리가 쓰는 것</p>
</div>
<div class="card">
  <div class="k" style="color:#d97757">Anthropic</div>
  <div class="v">Claude</div>
  <p>긴 글·코딩에 강해요</p>
</div>
<div class="card">
  <div class="k" style="color:#4285f4">Google</div>
  <div class="v">Gemini</div>
  <p>검색·유튜브랑 붙어 있어요</p>
</div>
</div>

^^^
> 같은 질문에 다르게 답해요. **뭘 쓰는지 고르는 것**도 실력이에요 — 그건 2주차에 해봐요.

??? 여기서 3분. 로고 없이 글자 마크로 간다(테마 통일). 오늘은 "여러 개가 있다"까지만 — 어느 게 낫냐는 질문이 나오면 "2주차에 직접 겨루게 해볼 거예요"로 받는다. 가격 얘기는 꺼내지 않는다.

---
## 12주 동안 <b>이렇게 갑니다</b>

<div class="flow">
<span>내 프로필 카드</span><i>→</i>
<span>내 웹페이지</span><i>→</i>
<span>그림·포스터</span><i>→</i>
<span class="hi">발표 슬라이드</span><i>→</i>
<span>이야기책</span><i>→</i>
<span>영상</span><i>→</i>
<span class="hi">나만의 작품관</span>
</div>

^^^
> 오늘 만드는 프로필 카드가 이 줄의 첫 칸이에요. 매주 한 칸씩 채워요.

??? 흰 칸 두 개(발표 슬라이드·작품관)가 이 과정의 두 정점. 5주차와 8주차. 여기서 3분.

---
<!-- class: g-violet -->
## 12주 뒤, <b>이렇게 달라져요</b>

<div class="grid c3">
<div class="card"><div class="k">지금</div><div class="v">AI를 써봤어요</div><p>물어보면 답해주는 정도</p></div>
<div class="card"><div class="k">12주 뒤</div><div class="v">만들 수 있어요</div><p>웹페이지·슬라이드·봇 — 만들고 싶은 걸 직접</p></div>
<div class="card strong"><div class="k">그리고</div><div class="v">스스로 찾아요</div><p>새 AI 소식을 직접 접하고, 써보는 사람</p></div>
</div>

^^^
> 만든 것들은 전부 인터넷의 내 작품관에 쌓여요.

??? 여기서 3분. 결과물 자랑이 아니라 **사람의 변화**를 말하는 장. "누구에게 보여준다"류 표현은 쓰지 않는다(부담). 작품관 실물은 3주차 첫 배포 때 자연스럽게 본다.

---
## 이렇게 <b>지내요</b>

^^^
- **막히면 3분 안에 손을 들어요** — 혼자 끙끙대는 시간이 제일 아까워요
- **옆 친구가 막히면 알려줍니다** — 설명해보면 자기가 제일 많이 배웁니다
- **AI가 한 말을 그대로 믿지 않습니다** — 12주 동안 가장 중요한 습관입니다

^^^
> 세 번째가 이 수업의 핵심입니다. 나머지 둘은 그걸 배우기 위한 준비입니다.

??? 특히 첫 번째 — 조용한 교실일수록 손 드는 문턱을 낮춰 두어야 한다. "3분"이라는 숫자가 허락의 근거가 된다. 12주 내내 이 세 줄로 돌아온다. 여기서 3분.

---
## 오늘 끝나면 <b>이게 생겨요</b>

<div class="card" style="max-width:62vmin;margin:2vmin auto 0;text-align:left">
<div class="k" style="color:#3b9eff">MY PROFILE</div>
<div class="v">민콩</div>
<p>좋아하는 팀 · LG 트윈스</p>
<p>오늘 순위 · 2위 (68승 51패)</p>
<p>오늘 서울 날씨 · 26°C 흐림</p>
</div>

^^^
> 내용은 AI가 방금 웹에서 찾아와요 — 순위도, 날씨도 오늘 것이에요.

??? 여기서 2분. 화면의 카드는 예시 목업. 강사가 미리 자기 것을 ChatGPT 웹에서 만들어(핸즈온 01 문장 그대로, 10분) 브라우저 실물로 보여주면 더 좋다. "숙제 없음, 준비물 없음"도 여기서 말한다.

---
<!-- class: chapter g-orange -->
<span class="n">1</span>

## 가입하기

??? 여기서부터 전원이 같이 움직인다. 한 명이라도 막히면 다음으로 안 넘어간다. 간지 1분.

---
## <b>다섯 단계</b>면 끝나요

| 단계 | 무엇을 | 확인 |
|:--:|---|---|
| 1 | 브라우저를 연다 | 크롬 또는 엣지 |
| 2 | chatgpt.com 을 친다 | 주소창에 직접 입력 |
| 3 | "Google로 계속하기"를 누른다 | 학교 gmail 사용 |
| 4 | 이름과 생년월일을 입력한다 | 처음 가입할 때만 |
| 5 | 대화창이 뜬다 | 이게 오늘 쓸 화면입니다 |

^^^
> 이미 계정이 있으면 3~4단계는 건너뛰어요.

??? 여기서 20분 — 오늘의 최대 변수. 3~4명씩 확인하며 진행. 15분 지나면 안 된 학생은 옆자리 화면 공유로 진도를 뺀다. 계정 문제는 쉬는 시간에. 보호자 동의는 사전 완료 상태.

---
## 여기서 <b>막히면</b>

^^^
- 전화번호를 묻는다 → 학생 폰 번호로 인증(선택인 경우가 많아요)
- "이미 있는 계정" 이라고 뜬다 → 예전에 만든 계정을 그대로 쓰면 됩니다
- 화면이 영어로 뜬다 → 오른쪽 아래 설정에서 한국어로 바꿀 수 있어요

^^^
> 막히면 손을 드세요. 넘어가지 않고 같이 봅니다.

??? 별도 시간 배정 없음 — 앞 장의 20분 블록 안에서 처리한다.

---
<!-- class: chapter g-orange -->
<span class="n">2</span>

## 프로필 카드 만들기

??? 간지 1분. 여기서부터 핸즈온 문장은 Gitea handson 저장소(w01 폴더)에서 복사해 쓴다 — 프로젝터에 띄우고 학생은 눈으로 보고 따라 친다.

---
## 이렇게 <b>시켜보세요</b>

```
내 프로필 카드를 HTML로 만들어줘.
내가 좋아하는 OOO 정보를 웹에서 찾아서 넣어줘.
```

^^^
게임, 아이돌, 유튜버, 팀, 캐릭터 — 뭐든 좋아하는 거 아무거나요.

^^^
> AI가 인터넷에서 직접 찾아와요. 내가 알려주지 않았는데도요.

??? 여기서 15분. 이 문장은 handson/w01/01-프로필카드.txt 에 있다. 돌아다니며 막힌 학생부터 본다. 검색이 안 걸리면 "웹에서 찾아봐줘"를 덧붙이게 한다. ChatGPT가 코드를 화면에 통째로 보여준다 — 아직 파일이 아니라는 걸 짚어준다.

---
## 받은 걸 <b>파일로 만들어요</b>

| 단계 | 무엇을 |
|:--:|---|
| 1 | 코드를 전부 복사한다 |
| 2 | 메모장을 연다 |
| 3 | 붙여넣고, 이름을 `me.html` 로 저장한다 |
| 4 | 저장한 파일을 더블클릭한다 |

^^^
> 저장한 파일을 열면, 방금 만든 카드가 브라우저에 떠요.

??? 여기서 5분. 메모장 저장 시 "파일 형식"을 "모든 파일"로, 확장자를 .html 로 정확히 — 흔한 실수 지점. 이 순간이 오늘의 첫 정점이다.

---
## 마음에 안 들면 <b>다시 시키면 돼요</b>

^^^
- "색을 파란색으로 바꿔줘"
- "테두리를 둥글게 해줘"
- "글씨를 더 크게 해줘"

^^^
> 바꿀 때마다… 복사하고, 저장하고, 다시 열어요.

??? 여기서 10분. 실제로 2~3번 반복시킨다(문장은 handson/w01/02-고치기.txt). 매번 전체 코드 복사 → 메모장 붙여넣기 → 저장 → 새로고침을 그대로 겪게 한다. 강사가 미리 "번거롭죠"라고 말하지 않는다 — 다음 장의 그림이 대신 말한다.

---
<!-- class: g-orange -->
## 방금 우리가 <b>한 일이에요</b>

<figure class="media" style="border:none;background:none">
<svg viewBox="0 0 760 300" role="img" aria-label="고칠 때마다 사람이 복사, 저장, 새로고침을 반복하는 순환 구조"
     style="width:100%;max-height:46vmin;color:#fcfdff">
  <defs>
    <marker id="clArw" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#ff801f"/>
    </marker>
  </defs>
  <g fill="none" stroke="currentColor" stroke-opacity=".25">
    <rect class="draw" pathLength="1" x="40"  y="110" width="150" height="80" rx="14"/>
    <rect class="draw" pathLength="1" style="--d:.15s" x="290" y="30"  width="180" height="70" rx="14"/>
    <rect class="draw" pathLength="1" style="--d:.3s" x="560" y="110" width="160" height="80" rx="14"/>
    <rect class="draw" pathLength="1" style="--d:.45s" x="290" y="200" width="180" height="70" rx="14"/>
  </g>
  <g font-size="21" fill="currentColor" text-anchor="middle" font-family="inherit">
    <g class="pop" style="--d:.1s"><text x="115" y="143">AI에게</text><text x="115" y="170">"바꿔줘"</text></g>
    <g class="pop" style="--d:.25s"><text x="380" y="58">코드 전체를</text><text x="380" y="84">다시 받음</text></g>
    <g class="pop" style="--d:.4s"><text x="640" y="143">복사해서</text><text x="640" y="170">메모장에 저장</text></g>
    <g class="pop" style="--d:.55s"><text x="380" y="228">브라우저</text><text x="380" y="254">새로고침</text></g>
  </g>
  <g fill="none" stroke="#ff801f" stroke-width="2.5" marker-end="url(#clArw)">
    <path class="march" pathLength="1" d="M190,130 Q230,80 285,68"/>
    <path class="march" pathLength="1" d="M470,68 Q530,80 575,110"/>
    <path class="march" pathLength="1" d="M615,190 Q530,225 475,232"/>
    <path class="march" pathLength="1" d="M285,232 Q200,225 130,190"/>
  </g>
  <text class="pop" style="--d:.8s" x="380" y="158" font-size="19" fill="#ff801f" text-anchor="middle" font-family="inherit">고칠 때마다 한 바퀴</text>
</svg>
<figcaption>"색만 바꿔줘"인데, 사람이 하는 일이 세 가지예요</figcaption>
</figure>

??? 여기서 4분. 그림을 띄워두고 잠깐 조용히 있는다 — 학생이 "계속 이렇게 해요?"라고 먼저 말하게 기다린다(대본 참고). 나오면 "맞아요"로만 받고 답은 마지막 장에서 준다.

---
## 대화는 <b>사라지지 않아요</b>

^^^
컴퓨터를 끄거나 창을 닫아도, 왼쪽 목록에 오늘 대화가 그대로 남아 있어요.

^^^
> 그래서 다음에 들어와도, 오늘 만든 카드 얘기를 이어서 할 수 있어요.

??? 실제로 창을 닫았다 다시 열어 왼쪽 대화 목록에서 오늘 대화를 찾아 들어가는 걸 시연한다. 30초면 된다. 여기서 3분.

---
<!-- class: g-orange -->
## 이 답, <b>믿어도 될까요</b>

<div class="foot">강사 화면으로 같이 봐요</div>

```
{{INTRO_NAME}}이 누구야?
```

^^^
> 그럴듯한 답이 나와요. 그런데 **맞는 답일까요?**

??? 말 대신 시연(핸즈온 03). 최신 모델은 자동 검색·되묻기를 해서 "완전한 헛소리"는 드물다 — 대신 **동명이인을 자신 있게 설명**하거나 근거 없는 세부를 섞는 경우가 많다. 어느 쪽이 나와도 교훈은 같다: 그럴듯함 ≠ 맞음. **반드시 전날 실측**해서 실제 출력을 확인해 둘 것 — 결과에 따라 멘트를 맞춘다(대본에 세 갈래 준비). 여기서 5분.

---
## 오늘 <b>제일 중요한 그림</b>이에요

<figure class="media" style="border:none;background:none">
<svg viewBox="0 0 760 270" role="img" aria-label="근거를 찾아 답하면 믿을 수 있고, 근거 없이 답하면 그럴듯해도 확인이 필요하다"
     style="width:100%;max-height:44vmin;color:#fcfdff">
  <defs>
    <marker id="svArw" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="currentColor" fill-opacity=".55"/>
    </marker>
  </defs>
  <g font-family="inherit" text-anchor="middle">
    <rect class="draw" pathLength="1" x="20" y="26" width="350" height="216" rx="18" fill="none" stroke="#11ff99" stroke-opacity=".5" stroke-width="1.5"/>
    <text class="pop" x="195" y="66" font-size="21" fill="#11ff99">찾아보고 답하면</text>
    <g class="pop" style="--d:.25s">
      <text x="82" y="140" font-size="20" fill="currentColor">질문</text>
      <g fill="none" stroke="currentColor" stroke-opacity=".8" stroke-width="2">
        <circle cx="192" cy="130" r="14"/>
        <line x1="202" y1="140" x2="216" y2="154"/>
      </g>
      <text x="195" y="180" font-size="14" fill="currentColor" fill-opacity=".55">웹에서 확인</text>
      <text x="303" y="140" font-size="20" fill="#11ff99">근거 있음</text>
    </g>
    <line class="draw" style="--d:.2s" pathLength="1" x1="110" y1="133" x2="162" y2="133" stroke="currentColor" stroke-opacity=".5" stroke-width="2" marker-end="url(#svArw)"/>
    <line class="draw" style="--d:.35s" pathLength="1" x1="226" y1="133" x2="256" y2="133" stroke="currentColor" stroke-opacity=".5" stroke-width="2" marker-end="url(#svArw)"/>
    <text class="pop" style="--d:.5s" x="195" y="220" font-size="16" fill="currentColor" fill-opacity=".65">방금 찾은 정보로 답해요</text>
    <rect class="draw" style="--d:.15s" pathLength="1" x="390" y="26" width="350" height="216" rx="18" fill="none" stroke="#ff801f" stroke-opacity=".5" stroke-width="1.5"/>
    <text class="pop" style="--d:.15s" x="565" y="66" font-size="21" fill="#ff801f">기억만으로 답하면</text>
    <g class="pop" style="--d:.4s">
      <text x="452" y="140" font-size="20" fill="currentColor">질문</text>
      <g fill="none" stroke="currentColor" stroke-opacity=".8" stroke-width="2">
        <path d="M542,116 h44 a9,9 0 0 1 9,9 v16 a9,9 0 0 1 -9,9 h-26 l-11,11 v-11 h-7 a9,9 0 0 1 -9,-9 v-16 a9,9 0 0 1 9,-9 z"/>
        <text x="564" y="137" font-size="15" fill="currentColor" stroke="none">…?</text>
      </g>
      <text x="565" y="180" font-size="14" fill="currentColor" fill-opacity=".55">떠오르는 대로</text>
      <text x="673" y="140" font-size="20" fill="#ff801f">근거 없음</text>
    </g>
    <line class="draw" style="--d:.35s" pathLength="1" x1="480" y1="133" x2="528" y2="133" stroke="currentColor" stroke-opacity=".5" stroke-width="2" marker-end="url(#svArw)"/>
    <line class="draw" style="--d:.5s" pathLength="1" x1="600" y1="133" x2="630" y2="133" stroke="currentColor" stroke-opacity=".5" stroke-width="2" marker-end="url(#svArw)"/>
    <text class="pop" style="--d:.65s" x="565" y="220" font-size="16" fill="currentColor" fill-opacity=".65">그럴듯해도 확인이 필요해요</text>
  </g>
</svg>
<figcaption>근거가 있는 답인지 보는 습관 — 오늘 가져갈 한 가지예요</figcaption>
</figure>

^^^
> AI의 답은 **확인하고 써요.** 12주 내내 지킬 습관이에요.

??? 여기서 3분. 방금 겪은 두 장면(카드=웹에서 찾음, 강사 이름=근거가 불분명)을 이 그림 하나로 정리한다. "이렇게 지내요"의 세 번째 줄과 연결.

---
<!-- class: chapter g-green -->
<span class="n">3</span>

## 오늘을 남기기

??? 간지 1분.

---
## 마지막으로 <b>이렇게 시켜요</b>

```
오늘 내가 뭘 만들었는지,
다음에 이어서 할 수 있게 정리해줘.
```

^^^
> 이걸 매주 마지막에 해요. 12주 뒤엔 나만의 기록이 쌓여 있을 거예요.

??? 여기서 8분(문장은 handson/w01/04-오늘정리.txt). 실제로 시키고 결과를 같이 읽는다. 오늘부터 12주 내내 반복되는 의식이라고 알려준다. 7주차 자동 위키와 같은 원리라는 건 지금 말하지 않는다(7주차 공개 장면).

---
<!-- class: cover -->
## 다음 주, <em>Codex</em>를 만나요

^^^
말하면 **파일을 직접 만들고 고쳐주는** 도구예요. 오늘 돌린 그 바퀴 — 복사, 저장, 새로고침 — 가 통째로 사라져요.

^^^
- 숙제 없음 · 준비물 없음
- 오늘 만든 ChatGPT 계정은 계속 써요 — 아이디·비밀번호 기억하기

??? 마무리 3분(대본 참고). Codex 예고는 이 장 한 곳에서만 한다 — "에이전트" 용어는 여전히 쓰지 않고, "바퀴가 사라진다"는 오늘의 경험 언어로만 설명한다. 다음 주엔 서버 접속용 계정 카드를 나눠준다고 예고.
