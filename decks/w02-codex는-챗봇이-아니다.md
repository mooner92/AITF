<!-- class: cover -->
^ 2주차
# 오늘, <em>Codex</em>를 만나요

지난주엔 고칠 때마다 복사, 저장, 새로고침을 직접 했어요. 오늘부터 그 일은 도구가 해요.

??? 시작 전 확인: 학생 서버 계정 로그인 가능(faillock 주의), codex 동작 확인(강사 계정에서 1회 실행), 수업자료 모음 페이지 열어두기, 예시 주제 자료 2종 준비, Class 1용 Gitea 5단계 표. 여기서 2분.

---
## 지난주에 <b>이걸 했어요</b>

<div class="flow">
<span>프로필 카드</span><i>→</i>
<span>서버 접속</span><i>→</i>
<span>명령어 여섯 개</span><i>→</i>
<span class="hi">저장소에 올리기</span>
</div>

^^^
> 마지막 칸은 오늘 전원이 채워요 — 지난주에 못 올린 사람도 오늘 같이 올려요.

??? 여기서 3분. Class 1은 마지막 칸이 아직 비어 있다는 걸 자연스럽게 말한다("오늘 같이 채워요"). 지난주 결석생도 이 장에서 흐름을 잡는다.

---
## 기록이 <b>쌓이고 있어요</b>

^^^
- 노션 **수업 기록** 페이지에 매주 일요일 저녁, 그 주 정리가 자동으로 올라와요
- Slack에서 `/thisweek` 를 치면 이번 주 정리 링크가 나에게만 와요

^^^
> 오늘 수업도 저녁이면 자동으로 정리돼 있을 거예요. 누가 정리하는지는 나중에 알려드릴게요.

??? 여기서 3분. 프로젝터로 노션 1주차 페이지를 30초만 보여준다. "누가 정리하냐"는 7주차 위키 공개의 떡밥 — 답하지 않는다.

---
<!-- class: g-orange -->
## 그 바퀴, <b>기억나요?</b>

<figure class="media" style="border:none;background:none">
<svg viewBox="0 0 640 400" role="img" aria-label="바꿔달라고 할 때마다 사람이 복사하고 저장하고 새로고침하는 바퀴를 돌렸다"
     style="width:100%;max-height:42vmin;color:#fcfdff">
  <defs>
    <marker id="w2arw" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#ff801f"/>
    </marker>
  </defs>
  <g fill="none" stroke="#ff801f" stroke-width="2.5">
    <path class="march" pathLength="1" marker-end="url(#w2arw)" d="M 155,150 A 168,168 0 0,1 262,44"/>
    <path class="march" pathLength="1" marker-end="url(#w2arw)" d="M 378,44 A 168,168 0 0,1 485,150"/>
    <path class="march" pathLength="1" marker-end="url(#w2arw)" d="M 485,250 A 168,168 0 0,1 378,356"/>
    <path class="march" pathLength="1" marker-end="url(#w2arw)" d="M 262,356 A 168,168 0 0,1 155,250"/>
  </g>
  <g font-size="19" fill="currentColor" text-anchor="middle" font-family="inherit">
    <text class="pop" x="150" y="207">"바꿔줘"</text>
    <text class="pop" style="--d:.15s" x="320" y="40">코드 다시 받기</text>
    <text class="pop" style="--d:.3s" x="492" y="207">다운로드</text>
    <text class="pop" style="--d:.45s" x="320" y="382">새로고침</text>
  </g>
  <g class="pop" style="--d:.7s" font-family="inherit" text-anchor="middle">
    <text x="320" y="192" font-size="18" fill="#ff801f">한 번 고칠 때마다</text>
    <text x="320" y="218" font-size="18" fill="#ff801f">사람이 세 칸을 돌았어요</text>
  </g>
</svg>
<figcaption>지난주, 색 하나 바꾸는 데 우리가 한 일이에요</figcaption>
</figure>

??? 여기서 2분. 지난주 마지막 그림 재등장 — "이거 계속 해야 돼요?"라는 질문이 있었다면 그 학생을 호명해 공을 돌린다.

---
## 이 반복 작업을 <b>대신 실행하는 도구</b>가 있어요

^^^
> 이름은 **Codex**예요. 앞으로 10주 동안 우리 옆에 있을 도구예요.

??? 한 문장 슬라이드. 여기서 1분 — 이름을 처음 말하는 순간이라 또박또박.

---
<!-- class: chapter g-orange -->
<span class="n">1</span>

## Codex가 뭐예요

??? 간지. 여기서부터 도구 설명 블록 — 총 30분 안에 22장(6~22)을 지난다. 시연 2회 포함이라 슬라이드당 오래 머물지 않는다.

---
## ChatGPT 만든 회사가 만든 <b>일 시키는 도구</b>예요

<div class="grid c3">
<div class="card"><div class="k">만든 곳</div><div class="v">OpenAI</div><p>ChatGPT랑 같은 회사예요</p></div>
<div class="card"><div class="k">쓰는 곳</div><div class="v">터미널</div><p>지난주 배운 그 검은 화면이요</p></div>
<div class="card strong"><div class="k">하는 일</div><div class="v">일을 대신 해요</div><p>답만 하는 게 아니라 파일을 만들고 고쳐요</p></div>
</div>

^^^
> 대화하는 건 ChatGPT랑 똑같아요. 다른 건 **대화가 끝난 뒤에 하는 일**이에요.

??? 여기서 2분. "챗봇과 뭐가 다른가"를 3축으로 나눠 다음 장부터 그림으로 하나씩 본다.

---
<!-- class: g-none -->
## 다름 하나. 채팅은 <b>지나가요</b>

<figure class="media" style="border:none;background:none">
<svg viewBox="0 0 720 300" role="img" aria-label="채팅창의 대화는 창을 닫으면 옆에 없고, 길어지면 앞부분을 잊는다"
     style="width:100%;max-height:40vmin;color:#fcfdff">
  <g font-family="inherit">
    <rect class="draw" pathLength="1" x="30" y="30" width="300" height="240" rx="14" fill="none" stroke="currentColor" stroke-opacity=".3"/>
    <text class="pop" style="--d:.1s" x="180" y="66" font-size="17" fill="currentColor" fill-opacity=".7" text-anchor="middle">어제의 대화</text>
    <g class="pop" style="--d:.2s">
      <rect x="55" y="88" width="170" height="34" rx="12" fill="currentColor" fill-opacity=".12"/>
      <text x="70" y="110" font-size="14" fill="currentColor" fill-opacity=".8">카드 만들어줘</text>
    </g>
    <g class="pop" style="--d:.35s">
      <rect x="120" y="132" width="185" height="34" rx="12" fill="#3b9eff" fill-opacity=".16"/>
      <text x="135" y="154" font-size="14" fill="currentColor" fill-opacity=".8">네, 만들었어요</text>
    </g>
    <g class="pop" style="--d:.5s">
      <rect x="55" y="176" width="150" height="34" rx="12" fill="currentColor" fill-opacity=".12"/>
      <text x="70" y="198" font-size="14" fill="currentColor" fill-opacity=".8">파랗게 바꿔줘</text>
    </g>
    <text class="pop" style="--d:.65s" x="180" y="248" font-size="14" fill="currentColor" fill-opacity=".5" text-anchor="middle">…이 흐름은 이 창 안에만 있어요</text>
    <path class="draw" style="--d:.8s" pathLength="1" d="M 350,150 L 400,150" stroke="currentColor" stroke-opacity=".5" stroke-width="2" fill="none"/>
    <rect class="draw" style="--d:.9s" pathLength="1" x="420" y="30" width="270" height="240" rx="14" fill="none" stroke="#ff801f" stroke-opacity=".55" stroke-dasharray="7 5"/>
    <text class="pop" style="--d:1.1s" x="555" y="140" font-size="18" fill="#ff801f" text-anchor="middle">오늘 새 창을 열면</text>
    <text class="pop" style="--d:1.2s" x="555" y="168" font-size="18" fill="#ff801f" text-anchor="middle">처음부터 다시 설명해요</text>
  </g>
</svg>
<figcaption>대화가 길어지면 앞부분부터 잊기도 해요</figcaption>
</figure>

??? 여기서 2분. 학생 경험에 연결 — "ChatGPT로 코드 만들다가 다음 날 이어서 하려면 어땠어요?" 한 명에게 물으면 "다시 설명했어요"가 나온다.

---
## 파일도 <b>매번 줘야 해요</b>

<div class="grid c3">
<div class="card"><div class="k">채팅에서는</div><div class="v">파일을 첨부해요</div><p>보여주고 싶은 파일을 매번 올려요</p></div>
<div class="card"><div class="k">파일이 많아지면</div><div class="v">다 못 올려요</div><p>어제 것, 지난주 것… 어디 갔죠?</p></div>
<div class="card strong"><div class="k">결과물도</div><div class="v">복사해서 옮겨요</div><p>받은 코드를 내가 저장해야 해요</p></div>
</div>

??? 여기서 2분. 학생 다수가 이미 ChatGPT 복붙 개발을 해봤다 — "해본 사람?" 손들게 하면 공감대가 만들어진다.

---
<!-- class: g-green -->
## Codex는 <b>폴더 안에서 일해요</b>

<figure class="media" style="border:none;background:none">
<svg viewBox="0 0 720 310" role="img" aria-label="Codex는 project 폴더의 파일을 읽어 오고, 고친 결과를 다시 폴더에 쓴다"
     style="width:100%;max-height:40vmin;color:#fcfdff">
  <defs>
    <marker id="w2fold" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#a1a4a5"/>
    </marker>
  </defs>
  <g font-family="inherit">
    <path class="draw" pathLength="1" d="M 140,60 h120 l22,22 h218 a14,14 0 0 1 14,14 v160 a14,14 0 0 1 -14,14 H 140 a14,14 0 0 1 -14,-14 V 74 a14,14 0 0 1 14,-14 z" fill="none" stroke="#11ff99" stroke-opacity=".6" stroke-width="2"/>
    <text class="pop" style="--d:.2s" x="150" y="112" font-size="17" fill="#11ff99">~/project</text>
    <g class="pop" style="--d:.4s" font-size="15" fill="currentColor" fill-opacity=".85">
      <text x="170" y="152">📄 me.html</text>
      <text x="170" y="184">📄 notes.md</text>
      <text x="170" y="216">📁 w01/</text>
    </g>
    <g class="pop" style="--d:.6s">
      <circle cx="470" cy="150" r="34" fill="#11ff99" fill-opacity=".14" stroke="#11ff99" stroke-opacity=".7"/>
      <text x="470" y="157" font-size="15" fill="#11ff99" text-anchor="middle">Codex</text>
    </g>
    <g stroke="#a1a4a5" stroke-opacity=".75" stroke-width="2.5" fill="none">
      <path class="march" pathLength="1" marker-end="url(#w2fold)" d="M 290,146 Q 350,120 428,138"/>
      <path class="march" pathLength="1" marker-end="url(#w2fold)" d="M 436,166 Q 350,214 298,192"/>
    </g>
    <text class="pop" style="--d:1.1s" x="352" y="108" font-size="14" fill="#a1a4a5" text-anchor="middle">읽기</text>
    <text class="pop" style="--d:1.2s" x="352" y="240" font-size="14" fill="#a1a4a5" text-anchor="middle">쓰기</text>
  </g>
</svg>
<figcaption>어제 만든 파일이 그대로 있으니, 설명을 다시 할 필요가 없어요</figcaption>
</figure>

^^^
> 지난주에 폴더 여섯 개 명령어를 배운 이유가 오늘 나와요 — **Codex의 작업장이 바로 그 폴더**예요.

??? 여기서 2분. "지난주에 왜 터미널부터 배웠나"가 여기서 회수된다 — 이 연결을 놓치지 말 것.

---
## 다름 둘. 채팅은 보여주고, <b>Codex는 만들어요</b>

<div class="split">
<div class="lane"><div class="who" style="color:#a1a4a5;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);display:inline-block;padding:.5vmin 2vmin;border-radius:9999px;font-size:2.4vmin">ChatGPT</div>
<p>코드를 <b>화면에 보여줘요</b></p>
<p>저장은 내가 해요 — 복사, 붙여넣기, 저장</p>
</div>
<div class="lane"><div class="who" style="color:#11ff99;background:rgba(17,255,153,.09);border:1px solid rgba(17,255,153,.26);display:inline-block;padding:.5vmin 2vmin;border-radius:9999px;font-size:2.4vmin">Codex</div>
<p>파일을 <b>직접 만들어요</b></p>
<p>고치는 것도 파일에 바로 — 복사가 없어요</p>
</div>
</div>

??? 여기서 2분. 왼쪽/오른쪽을 손으로 가리키며 대비. "보여주다"와 "만들다"의 차이가 오늘 실습에서 몸으로 확인된다.

---
<!-- class: g-green -->
## 다름 셋. 실행까지 <b>직접 해요</b>

<figure class="media" style="border:none;background:none">
<svg viewBox="0 0 640 400" role="img" aria-label="바꿔달라고 말하면 코드 수정, 저장, 확인을 Codex가 돌고 사람은 말만 한다"
     style="width:100%;max-height:42vmin;color:#fcfdff">
  <defs>
    <marker id="w2garw" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#11ff99"/>
    </marker>
  </defs>
  <g fill="none" stroke="#11ff99" stroke-width="2.5">
    <path class="march" pathLength="1" marker-end="url(#w2garw)" d="M 155,150 A 168,168 0 0,1 262,44"/>
    <path class="march" pathLength="1" marker-end="url(#w2garw)" d="M 378,44 A 168,168 0 0,1 485,150"/>
    <path class="march" pathLength="1" marker-end="url(#w2garw)" d="M 485,250 A 168,168 0 0,1 378,356"/>
    <path class="march" pathLength="1" marker-end="url(#w2garw)" d="M 262,356 A 168,168 0 0,1 155,250"/>
  </g>
  <g font-size="19" fill="currentColor" text-anchor="middle" font-family="inherit">
    <text class="pop" x="150" y="207">파일 읽기</text>
    <text class="pop" style="--d:.15s" x="320" y="40">코드 고치기</text>
    <text class="pop" style="--d:.3s" x="492" y="207">저장하기</text>
    <text class="pop" style="--d:.45s" x="320" y="382">확인하기</text>
  </g>
  <g class="pop" style="--d:.7s">
    <circle cx="320" cy="200" r="46" fill="#11ff99" fill-opacity=".13" stroke="#11ff99" stroke-opacity=".7"/>
    <text x="320" y="207" font-size="17" fill="#11ff99" text-anchor="middle" font-family="inherit">Codex</text>
  </g>
  <text class="pop" style="--d:.95s" x="320" y="285" font-size="15" fill="currentColor" fill-opacity=".6" text-anchor="middle" font-family="inherit">나는 "바꿔줘"라고 말만 해요</text>
</svg>
<figcaption>같은 과정이에요 — 실행하는 쪽이 바뀌었어요</figcaption>
</figure>

??? 여기서 2분. 4장과 같은 구도, 색과 중심만 바뀐 그림 — "같은 과정인데 실행하는 쪽이 바뀌었다"가 시각적으로 전달된다.

---
## 세 가지 다름, <b>정리하면</b>

<div class="grid c3">
<div class="card"><div class="k">기억</div><div class="v">폴더에 남아요</div><p>대화가 아니라 파일로 쌓여요</p></div>
<div class="card"><div class="k">파일</div><div class="v">직접 만들어요</div><p>복사·붙여넣기가 없어요</p></div>
<div class="card strong"><div class="k">실행</div><div class="v">직접 해요</div><p>고치고 저장하고 확인까지 한 번에</p></div>
</div>

^^^
> 이런 식으로 일하는 프로그램을 부르는 이름이 따로 있어요. 그 이름은 **직접 써본 다음에** 알려드릴게요.

??? 여기서 2분. "에이전트"라는 단어는 여기서도 아직 안 쓴다 — 마지막 문장이 그 자리의 예약이다.

---
<!-- class: g-orange -->
## 진짜인지 <b>지금 확인해봐요</b>

<div class="foot">강사 화면으로 같이 봐요</div>

같은 부탁을 두 곳에 동시에 시켜볼게요 — "이 카드의 배경을 밤하늘색으로 바꿔줘"

^^^
- 관찰 1 · **저장을 누가 했나요?**
- 관찰 2 · **복사·붙여넣기를 몇 번 했나요?**

??? 여기서 6분 — 오늘 설명 블록의 핵심 시연. 왼쪽 창 ChatGPT 웹, 오른쪽 창 서버 codex를 나란히 띄우고 같은 문장을 입력한다. ChatGPT 쪽은 코드가 화면에 나오고 강사가 복사→저장→새로고침을 일부러 천천히 한다. Codex 쪽은 파일이 바로 바뀐다. 미리 me.html을 양쪽에 준비해 둘 것.

---
## 방금 본 것, <b>숫자로 남겨요</b>

| | ChatGPT | Codex |
|---|---|---|
| 저장한 사람 | 나 | Codex |
| 복사·붙여넣기 | 2~3번 | 0번 |
| 내가 한 일 | 말하고, 나르고, 저장하고 | **말하기만** |

??? 여기서 2분. 시연 결과를 표로 못박는다. 실제 시연에서 숫자가 다르게 나오면 그 숫자로 고쳐 말한다 — 표는 예상값이다.

---
## 이런 도구, <b>Codex만 있는 게 아니에요</b>

^^^
> AI 회사마다 하나씩 만들고 있어요. 지난주에 "AI는 하나가 아니에요"라고 했죠 — 도구도 하나가 아니에요.

??? 여기서 1분. 지형도 2장 진입 예고 — "표가 두 장 나오는데, 외우라는 게 아니라 지도 구경이에요"라고 먼저 말해 부담을 낮춘다.

---
## 세 도구 지도 <b>① 누가 만들었나</b>

<div class="grid c3">
<div class="card" style="text-align:center">
<svg viewBox="0 0 24 24" role="img" aria-label="OpenAI 로고" style="width:10vmin;height:10vmin;fill:#fcfdff">
<path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1686a.071.071 0 0 1 .038.052v5.5826a4.504 4.504 0 0 1-4.4945 4.4944zm-9.6607-4.1254a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1408-1.6464zM2.3408 7.8956a4.485 4.485 0 0 1 2.3655-1.9728V11.6a.7664.7664 0 0 0 .3879.6765l5.8144 3.3543-2.0201 1.1685a.0757.0757 0 0 1-.071 0l-4.8303-2.7865A4.504 4.504 0 0 1 2.3408 7.872zm16.5963 3.8558L13.1038 8.364 15.1192 7.2a.0757.0757 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6772a.79.79 0 0 0-.407-.667zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.7759.7759 0 0 0-.7854 0L9.409 9.2297V6.8974a.0662.0662 0 0 1 .0284-.0615l4.8303-2.7866a4.4992 4.4992 0 0 1 6.6802 4.66zM8.3065 12.863l-2.02-1.1638a.0804.0804 0 0 1-.038-.0567V6.0742a4.4992 4.4992 0 0 1 7.3757-3.4537l-.142.0805L8.704 5.459a.7948.7948 0 0 0-.3927.6813zm1.0976-2.3654l2.602-1.4998 2.6069 1.4998v2.9994l-2.5974 1.4997-2.6067-1.4997Z"/>
</svg>

<div class="k" style="color:#74aa9c">OpenAI · ChatGPT의 회사</div>
<div class="v">Codex</div>
<p>터미널 · GPT 계열 모델</p>
</div>
<div class="card" style="text-align:center">

<svg viewBox="0 0 24 24" role="img" aria-label="Claude 로고" style="width:10vmin;height:10vmin;fill:#d97757">
<path d="m4.7144 15.9555 4.7174-2.6471.079-.2307-.079-.1275h-.2307l-.7893-.0486-2.6956-.0729-2.3375-.0971-2.2646-.1214-.5707-.1215-.5343-.7042.0546-.3522.4797-.3218.686.0608 1.5179.1032 2.2767.1578 1.6514.0972 2.4468.255h.3886l.0546-.1579-.1336-.0971-.1032-.0972L6.973 9.8356l-2.55-1.6879-1.3356-.9714-.7225-.4918-.3643-.4614-.1578-1.0078.6557-.7225.8803.0607.2246.0607.8925.686 1.9064 1.4754 2.4893 1.8336.3643.3035.1457-.1032.0182-.0728-.164-.2733-1.3539-2.4467-1.445-2.4893-.6435-1.032-.17-.6194c-.0607-.255-.1032-.4674-.1032-.7285L6.287.1335 6.6997 0l.9957.1336.419.3642.6192 1.4147 1.0018 2.2282 1.5543 3.0296.4553.8985.2429.8318.091.255h.1579v-.1457l.1275-1.706.2368-2.0947.2307-2.6957.0789-.7589.3764-.9107.7468-.4918.5828.2793.4797.686-.0668.4433-.2853 1.8517-.5586 2.9021-.3643 1.9429h.2125l.2429-.2429.9835-1.3053 1.6514-2.0643.7286-.8196.85-.9046.5464-.4311h1.0321l.759 1.1293-.34 1.1657-1.0625 1.3478-.8804 1.1414-1.2628 1.7-.7893 1.36.0729.1093.1882-.0183 2.8535-.607 1.5421-.2794 1.8396-.3157.8318.3886.091.3946-.3278.8075-1.967.4857-2.3072.4614-3.4364.8136-.0425.0304.0486.0607 1.5482.1457.6618.0364h1.621l3.0175.2247.7892.522.4736.6376-.079.4857-1.2142.6193-1.6393-.3886-3.825-.9107-1.3113-.3279h-.1822v.1093l1.0929 1.0686 2.0035 1.8092 2.5075 2.3314.1275.5768-.3218.4554-.34-.0486-2.2039-1.6575-.85-.7468-1.9246-1.621h-.1275v.17l.4432.6496 2.3436 3.5214.1214 1.0807-.17.3521-.6071.2125-.6679-.1214-1.3721-1.9246L14.38 17.959l-1.1414-1.9428-.1397.079-.674 7.2552-.3156.3703-.7286.2793-.6071-.4614-.3218-.7468.3218-1.4753.3886-1.9246.3157-1.53.2853-1.9004.17-.6314-.0121-.0425-.1397.0182-1.4328 1.9672-2.1796 2.9446-1.7243 1.8456-.4128.164-.7164-.3704.0667-.6618.4008-.5889 2.386-3.0357 1.4389-1.882.929-1.0868-.0062-.1579h-.0546l-6.3385 4.1164-1.1293.1457-.4857-.4554.0608-.7467.2307-.2429 1.9064-1.3114Z"/>
</svg>

<div class="k" style="color:#d97757">Anthropic · Claude의 회사</div>
<div class="v">Claude Code</div>
<p>터미널 + 데스크탑 앱 · Claude 계열 모델</p>
</div>
<div class="card" style="text-align:center">

<svg viewBox="0 0 24 24" role="img" aria-label="Google Gemini 로고" style="width:10vmin;height:10vmin">
<defs><linearGradient id="gem" x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="#4285f4"/><stop offset=".5" stop-color="#9b72cb"/><stop offset="1" stop-color="#d96570"/>
</linearGradient></defs>
<path fill="url(#gem)" d="M11.04 19.32Q12 21.51 12 24q0-2.49.93-4.68.96-2.19 2.58-3.81t3.81-2.55Q21.51 12 24 12q-2.49 0-4.68-.93a12.3 12.3 0 0 1-3.81-2.58 12.3 12.3 0 0 1-2.58-3.81Q12 2.49 12 0q0 2.49-.96 4.68-.93 2.19-2.55 3.81a12.3 12.3 0 0 1-3.81 2.58Q2.49 12 0 12q2.49 0 4.68.96 2.19.93 3.81 2.55t2.55 3.81"/>
</svg>

<div class="k" style="color:#4285f4">Google · Gemini의 회사</div>
<div class="v">Antigravity</div>
<p>코드 편집기 · Gemini 계열 모델</p>
</div>
</div>

??? 여기서 3분. 문양은 단순화한 근사 — 로고를 눈에 익혀 두면 나중에 어디서 봐도 소속을 안다. 각 사 형제 챗봇을 아는 학생이 있으면 반응이 온다.

---
## 세 도구 지도 <b>② 무엇이 다른가</b>

| | Codex | Claude Code | Antigravity |
|---|---|---|---|
| 쓰는 법 | 구독 또는 API 열쇠 | 구독 또는 API 열쇠 | Google 계정으로 로그인 |
| 잘하는 것 | 코딩 · 일 위임 | 긴 작업 · 꼼꼼한 계획 | 편집기 안에서 한 번에 |
| 우리 수업 | **이걸 써요** | 강사가 수업 준비에 써요 | 구경만 해둬요 |

^^^
> 셋 다 하는 일은 같아요 — **말로 시키면 파일로 해내는 것.** 하나를 제대로 배우면 나머지는 금방이에요.

??? 여기서 3분. "강사가 수업 준비에 Claude Code를 쓴다"는 사실은 학생 호기심 포인트 — 수업자료가 어떻게 만들어지는지는 나중에(스킬 공개 장면) 이어진다. 세부 요금은 말하지 않는다.

---
## 같은 기능인데 <b>이름만 달라요</b>

| | Codex | Claude Code | Antigravity |
|---|---|---|---|
| 지시서 파일 | AGENTS.md | CLAUDE.md | GEMINI.md |
| 켜는 명령 | `codex` | `claude` | 앱을 실행 |
| 위험한 일 전에 | 물어봐요 | 물어봐요 | 물어봐요 |

^^^
> **하나를 배우면 셋 다 읽을 수 있어요.** 나중에 도구를 고를 일이 생기면, 이 표가 그대로 통역사가 돼요.

??? 여기서 2분. 지시서 파일(AGENTS.md)은 오늘 실습에서 실물로 본다(뒤 실습 2 마지막 장) — "이따 직접 열어봐요"로 연결. 확실한 사실만 실었다 — 요금·버전 같은 바뀌는 정보는 넣지 않는다.

---
## 지금 다 못 외워도 <b>괜찮아요</b>

^^^
오늘 수업자료는 인터넷에 공개돼 있어요 — 집에서 폰으로도 볼 수 있어요.

```
aitf.excusa.uk/slides
```

??? 여기서 1분. 공개 페이지를 실제로 한 번 띄워 보여준다(1주차 자료가 이미 있다). 학부모에게도 보여줄 수 있다는 말은 굳이 안 한다 — 주소만.

---
## 그래서 우리는 <b>Codex를 써요</b>

<div class="grid c3">
<div class="card"><div class="k">이미 준비됨</div><div class="v">서버에 설치</div><p>지난주 접속한 그 서버에 있어요</p></div>
<div class="card"><div class="k">각자 열쇠</div><div class="v">내 API 키</div><p>한 사람씩 따로 발급했어요</p></div>
<div class="card strong"><div class="k">안심 한도</div><div class="v">쓰는 만큼 과금, 상한 있음</div><p>실수로 많이 써도 멈추게 돼 있어요</p></div>
</div>

??? 여기서 2분. "API 키 = AI를 쓰는 열쇠, 잃어버리면 다른 사람이 내 몫을 쓴다" 정도만. 금액은 말하지 않는다.

---
## Codex가 가끔 <b>물어볼 거예요</b>

^^^
- "이 파일을 지워도 될까요?" — 되돌리기 어려운 일 전에는 **먼저 물어봐요**
- 그때는 읽고, 맞으면 **y** 를 눌러요

^^^
> 왜 물어볼까요? 이 질문은 마음에 담아두세요 — 몇 주 뒤에 크게 다뤄요.

??? 여기서 2분. 승인 개념의 첫 노출 — 7주차 승인 경계 실습의 씨앗. "무조건 y"가 아니라 "읽고 y"를 지금부터 습관으로.

---
## 오늘 <b>이 순서로 가요</b>

<div class="flow">
<span>손 풀기</span><i>→</i>
<span>Codex 인사</span><i>→</i>
<span class="hi">발표자료 1</span><i>→</i>
<span>내 규칙 만들기</span><i>→</i>
<span class="hi">발표자료 2</span>
</div>

^^^
> 발표자료를 **두 개** 만들어요. 왜 두 개인지는 만들다 보면 알게 돼요.

??? 여기서 1분. 설명 블록 끝 — 시계 확인. 여기까지 약 32분이 정상 페이스. 밀렸으면 실습 1을 8분으로 줄인다.

---
<!-- class: chapter g-orange -->
<span class="n">2</span>

## 손 풀기

??? 간지. 실습 블록 시작 — 여기서부터는 학생 손이 움직인다.

---
## 지난주 실수, <b>복습하고 가요</b>

| 친 것 | 결과 | 바른 것 |
|---|---|---|
| `cd..` | 안 됨 | `cd ..` 한 칸 띄우기 |
| `cd projsct` | No such file | `cd pro` + **Tab 키** |
| `cat Agent.md` | 안 됨 | 대소문자 정확히 |

^^^
> 오늘의 무기는 **Tab** — 이름을 반쯤 치고 Tab을 누르면 나머지를 완성해줘요.

??? 여기서 3분. 지난주 실제 사례라고 말해주되 누가 했는지는 말하지 않는다. Tab 완성은 오늘 전원이 실제로 써보게 한다.

---
## 미션. <b>서버에 들어가서 확인해요</b>

```
ssh 내아이디@서버주소
cd project
ls
```

^^^
- 체크포인트 · 폴더 목록이 보이면 성공
- 심화 · `ls -a` 로 숨은 파일 이름 세 개 적어보기

??? 여기서 8분. 계정 카드 배부 확인. 접속 주소는 카드에 있다. 막히는 학생 순회 — 대부분 비밀번호 입력(화면에 안 보임)에서 멈춘다.

---
## 비밀번호를 다섯 번 틀리면 <b>3분 쉬어야 해요</b>

^^^
- 서버가 잠깐 문을 잠가요 — 지난주에 실제로 있었던 일이에요
- 그럴 땐 당황하지 말고 **3분 기다렸다가** 다시 하면 돼요

^^^
> 다섯 번 틀리기 전에 손을 드는 게 더 빨라요.

??? 여기서 1분. faillock 3분 정책. 잠긴 학생이 나오면 이 장을 다시 띄우고 시간을 재준다 — 강사가 서버에서 즉시 풀 수도 있다(faillock --user 계정 --reset).

---
## Class 1은 <b>지난주 카드부터 올려요</b>

| 단계 | 무엇을 |
|:--:|---|
| 1 | `aitf.excusa.uk/git/` 접속 |
| 2 | 계정 카드의 아이디·비밀번호로 로그인 |
| 3 | `project` 저장소 열기 |
| 4 | **Upload file** 에 `me.html` 끌어다 놓기 |
| 5 | **Commit Changes** 누르기 |

^^^
> Class 2는 지난주에 했어요 — 옆에서 도와주면 두 배로 배워요.

??? 여기서 7분(Class 1만, Class 2는 2분 확인 후 다음으로). me.html이 집 컴퓨터에 있는 학생은 ChatGPT 대화 목록에서 다시 다운로드 — 지난주 "대화는 사라지지 않아요"의 실전 회수.

---
<!-- class: chapter g-green -->
<span class="n">3</span>

## Codex 첫 만남

??? 간지. 여기서부터 약 15분.

---
## 켜는 법은 한 단어, <b>켜는 곳은 project</b>

```
pwd
cd ~/project
codex
```

^^^
- Codex는 **켠 폴더 안에서** 일해요 — 지시서(AGENTS.md)가 있는 project에서 켜야 규칙이 적용돼요
- 체크포인트 · `codex` 치기 전 프롬프트에 `project` 가 보이고, 대화 입력창이 뜨면 성공
- 어디 있는지 모르겠으면 언제든 `pwd` · 나가고 싶을 땐 `/quit`

??? 여기서 3분. tmux가 지난 접속의 위치를 기억하고 있어서 학생마다 시작 위치가 다르다 — cd ~/project를 반드시 먼저. 처음 실행 시 안내 문구가 나올 수 있다 — 화면이 다르게 보여도 입력창만 뜨면 성공이라고 말해준다.

---
## 첫 인사를 <b>해보세요</b>

```
안녕? 너는 뭘 할 수 있어?
```

^^^
- 관찰 · ChatGPT랑 말투가 비슷한가요, 다른가요?
- 심화 · "지금 이 폴더에 뭐가 있어?" 라고 물어보기

??? 여기서 3분. 심화 질문이 포인트 — Codex가 ls를 직접 돌려 답하는 걸 처음 목격하는 순간. 빠른 학생이 이걸 발견하면 전체에 공유시킨다.

---
## 먼저, 지난주 파일을 <b>서버로 가져와요</b>

지난주에 브라우저로 올린 파일은 **저장소에만** 있어요. 서버로 한 번 내려받아야 만질 수 있어요.

```
cd ~/project
git pull
```

^^^
- 체크포인트 · `ls` 를 쳤을 때 지난주 파일 이름이 보이면 성공
- 아무것도 안 내려와도 괜찮아요 — 다음 장은 그대로 진행해요

??? 여기서 3분. **이 장이 없으면 다음 위임이 전원 헛돈다** — 브라우저 업로드는 Gitea 베어 저장소에만 들어가고 학생 홈에는 닿지 않는다(2026-09-01 감사에서 13명 전원 확인). git 은 4주차 정식 주제라 여기서는 "저장소에서 내 서버로 가져오는 명령" 한 줄로만 소개하고 넘어간다. Class 1 은 방금 보충 업로드한 파일이, Class 2 는 지난주 파일이 내려온다.

---
## 첫 위임. <b>지난주 파일을 정리시켜요</b>

```
지난주에 올린 파일들을 w01 폴더로 정리해줘
```

^^^
- 지켜보세요 · Codex가 **뭘 하는지 화면에 다 보여줘요**
- 물어보면 · 읽고, 맞으면 **y**

??? 여기서 5분. 첫 실전 위임 — 파일 이동을 마우스가 아니라 말로 한다. Codex가 폴더 생성·이동 계획을 보여주고 승인을 구하는 흐름을 관찰시킨다. 앞 장에서 아무것도 안 내려온 학생은 "지금 폴더를 w01 로 정리해줘"로 대체 — 템플릿 파일이라도 대상이 된다.

---
## 진짜 됐는지 <b>내 눈으로 확인해요</b>

```
ls
ls w01
```

^^^
- 체크포인트 · `w01` 폴더가 생기고, 그 안에 파일이 들어가 있으면 성공
- 심화 · `cat w01/me.html` 로 내용이 그대로인지 보기

^^^
> AI가 "했어요"라고 말해도 **확인은 내가 해요** — 1주차 세 번째 습관, 여기서도 그대로예요.

??? 여기서 3분. 검증 습관을 도구 위임에도 적용하는 첫 장면. "AI 말을 그대로 믿지 않는다"가 명령어 두 개로 실행된다.

---
## 방금, 마우스 없이 <b>파일이 움직였어요</b>

<div class="grid c3">
<div class="card"><div class="k">지난주</div><div class="v">마우스로 끌었어요</div><p>브라우저에서 한 파일씩</p></div>
<div class="card strong"><div class="k">방금</div><div class="v">말 한 문장</div><p>폴더 만들고 옮기는 걸 통째로</p></div>
<div class="card"><div class="k">그리고</div><div class="v">확인은 내가</div><p>ls 두 번이면 끝</p></div>
</div>

??? 여기서 1분. 조용히 대비만 보여주고 넘어간다 — 감탄사는 학생 몫.

---
## 그런데 Codex는 <b>w01을 어떻게 알았을까요</b>

```
cat AGENTS.md
```

^^^
- project 폴더 안에 **지시서 파일**이 있어요 — Codex는 일 시작 전에 이걸 읽어요
- "주차 폴더에 정리한다"는 규칙이 여기 적혀 있어요

^^^
> 누가 썼는지, 왜 이렇게 쓰는지는 **몇 주 뒤에** 우리가 직접 다뤄요.

??? 여기서 3분. AGENTS.md 첫 관찰 — 읽기만 하고 설명은 아낀다(4주차 해부의 예고편). "하네스" 단어는 쓰지 않는다.

---
<!-- class: chapter g-violet -->
<span class="n">4</span>

## 첫 발표자료

??? 간지. 휴식 8분을 이 앞뒤 중 자연스러운 타이밍에 넣는다 — 권장은 이 간지 직전.

---
## 가져온 발표자료 <b>1번을 꺼내세요</b>

^^^
- 최근 발표에 실제로 썼던 그 자료요 — 오늘은 그걸 **재료**로 써요
- 못 가져왔어도 괜찮아요 — 강사가 나눠주는 예시 자료 중 하나를 재료로 쓰면 돼요

<div class="grid c2">
<div class="card"><div class="k">예시 자료 A</div><div class="v">강사가 만든 완성본</div><p>수업 때 나눠드려요 · 20장 분량</p></div>
<div class="card"><div class="k">예시 자료 B</div><div class="v">강사가 만든 완성본</div><p>A와 완전히 다른 주제·스타일이에요</p></div>
</div>

??? 여기서 2분. 주제를 그 자리에서 정하게 하지 않는다 — 고민 시간이 실습을 통째로 잡아먹는다(강사 판단). 예시 자료 2종은 강사가 별도 제작(재밌는 주제, 서로 완전 다른 주제·스타일, 각 ~20장) — 확정되면 카드에 실제 제목을 넣는다. 자료를 1개만 가져온 학생은 두 번째 검증 때 남은 예시 자료를 쓴다.

---
## 그 내용으로 <b>만들어달라고 해보세요</b>

```
발표자료를 만들 거야. 제목은 "OOO"이고,
목차는 1) … 2) … 3) … 야.
이 내용으로 HTML 발표자료를 만들어서 w02 폴더에 저장해줘.
```

^^^
- 제목과 목차는 **가져온 자료에서 그대로 옮겨 적어요** — 새로 생각할 필요 없어요
- 체크포인트 · `ls w02` 에 파일이 생기면 성공
- 심화 · 원래 자료의 핵심 문장 두세 개도 불러줘서 그대로 넣게 하기

??? 여기서 5분. 내용 창작이 아니라 이관이라 빠르다 — 제목·목차를 자기 자료(또는 예시 자료)에서 옮겨 적는 것까지가 학생 몫. 파일 이름은 Codex가 정해도 된다. 생성이 오래 걸리는 학생은 그 사이 옆 학생 화면을 구경시킨다.

---
## 눈으로 <b>봐야죠</b>

```
방금 만든 발표자료를 public 폴더에도 복사해줘
```

^^^
- 그 다음, 브라우저에서 **내 작품관 주소**를 열어요 (화면에 띄워드려요)
- 체크포인트 · 내 발표자료가 브라우저에 뜨면 성공

??? 여기서 4분. 작품관 주소는 aitf.excusa.uk/pages/계정/파일명 — 프로젝터에 패턴을 띄워준다. 사전에 학원에서 /pages 접속이 되는지 반드시 확인해 둘 것(인증 정책). 안 되면 대체 경로: Gitea에 올리고 다운로드해 열기.

---
## 이제 <b>바꿔달라고 하는 시간이에요</b>

<div class="grid c4">
<div class="card"><div class="k">1번</div><div class="v">색</div><p>"배경을 어두운 남색으로"</p></div>
<div class="card"><div class="k">2번</div><div class="v">글꼴</div><p>"제목을 더 크고 굵게"</p></div>
<div class="card"><div class="k">3번</div><div class="v">배치</div><p>"제목을 왼쪽 정렬로"</p></div>
<div class="card"><div class="k">4번</div><div class="v">구성</div><p>"목차 장을 앞에 추가해줘"</p></div>
</div>

^^^
> **최소 네 번** 바꿔요. 바꿀 때마다 작품관을 새로고침해서 확인해요.

??? 여기서 10분 — 오늘 가장 긴 자유 실습. 네 방향은 예시일 뿐, 자기 취향대로 시키게 한다. 순회하며 "지난주엔 이거 한 번에 바퀴 한 바퀴였다"를 개별적으로 상기시킨다.

---
## 더 바꿀 게 <b>생각 안 나면</b>

^^^
- "말투를 초등학생도 알아듣게 바꿔줘"
- "각 장에 어울리는 이모티콘을 하나씩 넣어줘"
- "마지막 장에 퀴즈를 하나 넣어줘"

^^^
> 이상하게 나와도 괜찮아요 — "방금 건 취소하고 원래대로 해줘"도 말로 돼요.

??? 여기서 2분(앞 10분 안에 포함해도 됨). 되돌리기도 위임이 된다는 걸 슬쩍 심는다.

---
<!-- class: g-violet -->
## 잠깐. 지금까지 시킨 게 <b>쌓이고 있어요</b>

<figure class="media" style="border:none;background:none">
<svg viewBox="0 0 700 300" role="img" aria-label="바꿔달라고 한 요구사항들이 차곡차곡 쌓여 목록이 된다"
     style="width:100%;max-height:38vmin;color:#fcfdff">
  <rect class="march" pathLength="1" x="164" y="56" width="372" height="230" rx="14" fill="none" stroke="#a78bfa" stroke-opacity=".45" stroke-width="2"/>
  <g font-family="inherit" font-size="16">
    <g class="pop">
      <rect x="180" y="228" width="340" height="44" rx="10" fill="#a78bfa" fill-opacity=".14" stroke="#a78bfa" stroke-opacity=".5"/>
      <text x="350" y="256" fill="currentColor" fill-opacity=".9" text-anchor="middle">배경은 어두운 남색</text>
    </g>
    <g class="pop" style="--d:.25s">
      <rect x="180" y="176" width="340" height="44" rx="10" fill="#a78bfa" fill-opacity=".14" stroke="#a78bfa" stroke-opacity=".5"/>
      <text x="350" y="204" fill="currentColor" fill-opacity=".9" text-anchor="middle">제목은 크고 굵게</text>
    </g>
    <g class="pop" style="--d:.5s">
      <rect x="180" y="124" width="340" height="44" rx="10" fill="#a78bfa" fill-opacity=".14" stroke="#a78bfa" stroke-opacity=".5"/>
      <text x="350" y="152" fill="currentColor" fill-opacity=".9" text-anchor="middle">제목은 왼쪽 정렬</text>
    </g>
    <g class="pop" style="--d:.75s">
      <rect x="180" y="72" width="340" height="44" rx="10" fill="#a78bfa" fill-opacity=".14" stroke="#a78bfa" stroke-opacity=".5"/>
      <text x="350" y="100" fill="currentColor" fill-opacity=".9" text-anchor="middle">목차 장은 맨 앞에</text>
    </g>
    <text class="pop" style="--d:1s" x="350" y="46" fill="#a78bfa" font-size="18" text-anchor="middle">이게 전부 내 취향이에요</text>
  </g>
</svg>
<figcaption>이 목록, 그냥 흘려보내기 아깝지 않나요?</figcaption>
</figure>

??? 여기서 2분. 다음 블록으로 넘어가는 다리 — 질문을 던져두고 간지로 넘어간다.

---
<!-- class: chapter g-violet -->
<span class="n">5</span>

## 내 규칙 만들기

??? 간지. 여기서부터 오늘의 핵심 20분.

---
## 정리도 <b>시키면 돼요</b>

```
지금까지 내가 시킨 수정사항들을
slide-rule.md 파일로 정리해줘
```

^^^
- 매주 마지막에 하던 "오늘 정리해줘"와 **같은 방법**이에요 — 이번엔 내 취향을 정리시키는 거예요
- 체크포인트 · `ls` 에 slide-rule.md 가 보이면 성공

??? 여기서 4분. 핸드오프 의식과 연결하는 게 포인트 — "우리가 매주 하던 그 마무리, 오늘은 수업 중간에 써먹는다".

---
## 뭐라고 정리했는지 <b>읽어보세요</b>

```
cat slide-rule.md
```

^^^
- 체크포인트 · 내가 시킨 것들이 문장으로 정리돼 있으면 성공
- 심화 · 빠진 게 있나 찾아보기 — 있으면 "OO도 추가해줘"

??? 여기서 3분. 학생 한 명의 slide-rule.md를 프로젝터에 띄워 같이 읽으면 좋다(본인 동의 받고). "내가 말한 게 글이 됐다"는 감각.

---
## 이제 <b>진짜 실험이에요</b>

```
두 번째 발표자료를 만들 거야. 제목은 "OOO", 목차는 … 야.
slide-rule.md 를 지키면서 만들어줘.
w02 폴더에 저장해줘.
```

^^^
- 재료는 **가져온 발표자료 2번** — 없으면 남은 예시 자료를 써요
- 이번엔 바꿔달라는 말을 **한 번도 안 하고** 만들어볼 거예요

??? 여기서 5분. 두 번째 재료 투입(가져온 자료 2번 또는 남은 예시 자료). 첫 번째와 달리 수정 지시 없이 규칙 파일 하나로 승부한다는 점을 강조해 둔다.

---
## 판정. <b>한 번에 비슷하게 나왔나요?</b>

<div class="split">
<div class="lane"><div class="who" style="color:#11ff99;background:rgba(17,255,153,.09);border:1px solid rgba(17,255,153,.26);display:inline-block;padding:.5vmin 2vmin;border-radius:9999px;font-size:2.4vmin">비슷하게 나왔다</div>
<p><b>성공이에요.</b> 내 취향이 파일 하나로 옮겨진 거예요</p>
</div>
<div class="lane"><div class="who" style="color:#ffc53d;background:rgba(255,197,61,.1);border:1px solid rgba(255,197,61,.3);display:inline-block;padding:.5vmin 2vmin;border-radius:9999px;font-size:2.4vmin">어딘가 다르다</div>
<p><b>더 좋은 일이에요.</b> 규칙에 빠진 걸 방금 찾은 거예요</p>
</div>
</div>

??? 여기서 3분. 실패를 실패라고 부르지 않는 게 이 장의 전부 — 오른쪽 결과가 나온 학생이 다음 장의 주인공이 된다.

---
## 다르면, <b>규칙을 고치고 다시</b>

<div class="flow">
<span>두 개를 비교</span><i>→</i>
<span>빠진 규칙 찾기</span><i>→</i>
<span class="hi">rule에 추가</span><i>→</i>
<span>다시 만들어줘</span>
</div>

^^^
- "slide-rule.md 에 'OO' 규칙을 추가하고, 다시 만들어줘"
- 체크포인트 · 비슷해질 때까지 — 보통 한두 바퀴면 돼요

??? 여기서 5분. 이 보강 루프가 오늘 가장 배우는 게 많은 구간. 순회하며 "뭐가 빠졌었어요?"라고 물으면 학생이 자기 언어로 규칙을 말하게 된다.

---
## 심화. <b>하지 말라는 것도 규칙이에요</b>

^^^
- "slide-rule.md 에 '절대 하지 말 것' 부분을 만들어줘"
- 예: "3D 효과 금지", "한 장에 글 여덟 줄 넘기지 않기"

^^^
> 좋은 규칙집엔 **금지 조항**이 꼭 있어요 — 원하는 것만큼, 원하지 않는 것도 분명하게.

??? 빨리 끝낸 학생용. 여기서 2분. 금지 조항은 4주차 지시문 4요소(금지)의 씨앗이기도 하다.

---
## 오늘 만든 건 <b>파일이 된 내 취향이에요</b>

^^^
> 다음에 발표자료를 또 만들 때, 이 파일 하나면 **처음부터 내 스타일로** 나와요. 설명을 다시 할 필요가 없어요.

??? 여기서 1분. 한 문장 슬라이드 — 오늘의 결론. "채팅은 지나가고, 파일은 남는다"(8장)와 수미상관.

---
## 오늘 만든 걸 <b>저장소에 올려요</b>

```
오늘 만든 발표자료 두 개랑 slide-rule.md 를
저장소에 올려줘
```

^^^
- 체크포인트 · `aitf.excusa.uk/git/` 내 project 저장소에 파일이 보이면 성공
- 지난주엔 마우스로 끌어서 올렸죠 — **이것도 말로 돼요**

??? 여기서 4분. git이라는 단어는 아직 설명하지 않는다(4주차) — "저장소에 올려줘"로 충분히 동작한다. 브라우저에서 결과 확인까지가 체크포인트.

---
## 마지막으로 <b>오늘도 정리시켜요</b>

```
오늘 내가 뭘 만들었는지,
다음에 이어서 할 수 있게 정리해줘.
```

^^^
> 매주 하는 마무리예요. 오늘은 이 정리가 **파일로 남는다**는 게 지난주와 달라요.

??? 여기서 3분. 핸드오프 의식 2회차 — ChatGPT에선 대화에 남았지만 Codex에선 파일로 남는다는 차이를 짚는다.

---
<!-- class: cover -->
## 다음 주, <em>진짜 발표</em>를 만들어요

^^^
학교에서 실제 발표했던 주제로 처음부터 끝까지 만들고, **인터넷에 공개**해요.
오늘 만든 slide-rule.md 를 그대로 다시 써요.

^^^
- 오늘 만든 slide-rule.md 같은 파일, 세상 개발자들도 만들어 써요 — **이름이 따로 있는데, 다음에 알려드릴게요**
- 숙제 없음 · 준비물 없음 — 발표했던 주제 하나만 떠올려 오세요

??? 마무리 3분. 스킬 티저는 여기 한 번만 — 단어는 끝까지 아낀다. 시간 합계: 도입 11 + 설명 34 + 손풀기 19 + 첫만남 15 + 휴식 8 + 발표자료1 23 + 규칙 20 + 마무리 10 ≈ 140분에서 각 블록 여유분을 당겨 120분에 맞춘다 — 밀리면 자르는 순서: 35장(AGENTS.md 관찰) → 27장(faillock, 언급만) → 지형도·용어표 3장을 2장으로.
