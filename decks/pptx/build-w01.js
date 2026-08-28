// AITF 1주차 — PPTX 생성. docs/design-spec.md 토큰을 PowerPoint로 옮긴다.
// 폰트는 Paperlogy 대신 Malgun Gothic — 임베드 없이 어느 Windows 에서도 그대로 보이고,
// 강사가 PowerPoint에서 직접 고칠 수 있어야 한다는 요구가 폰트 정합성보다 우선이다.
const pptxgen = require("pptxgenjs");

const C = {
  bg: "000000",
  ink: "FCFDFF",
  body: "D4D4D8",
  mute: "9CA3AF",
  ash: "77797A",
  orange: "FF801F",
  blue: "3B9EFF",
  green: "11FF99",
  violet: "A78BFA",
  card: "0A0A0C",
  cardHi: "141416",
  hair: "2A2A2D",
};
const FONT = "Malgun Gothic";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3" x 7.5"
pres.author = "AITF";
pres.title = "1주차 — AI를 처음 만나요";

const W = 13.333, H = 7.5;
const MX = 0.75; // 좌우 여백
const CW = W - MX * 2;

function bgFill(slide, accent) {
  slide.background = { color: C.bg };
  if (accent) {
    // 상단 액센트 바 — engine.css 의 글로우를 얇은 바로 단순화
    slide.addShape("rect", { x: 0, y: 0, w: W, h: 0.08, fill: { color: accent } });
  }
}

function notesOf(slide, text) {
  if (text) slide.addNotes(text);
}

function eyebrow(slide, text, color = C.blue, y = 0.55) {
  slide.addText(text.toUpperCase(), {
    x: MX, y, w: CW, h: 0.4, fontFace: FONT, fontSize: 13, color,
    charSpacing: 3, bold: true,
  });
}

function title(slide, text, y = 0.95, size = 34) {
  slide.addText(text, {
    x: MX, y, w: CW, h: 1.1, fontFace: FONT, fontSize: size, color: C.ink,
    bold: false, valign: "top",
  });
}

// ── 표지 / 마무리 ──────────────────────────────────────────────
function coverSlide({ eyebrow: eb, titleText, sub, bullets, accent = C.blue, notes }) {
  const s = pres.addSlide();
  bgFill(s, accent);
  if (eb) eyebrow(s, eb, accent, 1.3);
  s.addText(titleText, {
    x: MX, y: 1.9, w: CW, h: 2.0, fontFace: FONT, fontSize: 44, color: C.ink, valign: "top",
  });
  if (sub) s.addText(sub, {
    x: MX, y: 3.9, w: CW * 0.8, h: 0.8, fontFace: FONT, fontSize: 18, color: C.body, valign: "top",
  });
  if (bullets) s.addText(bullets.map((b, i) => ({
    text: b, options: { bullet: { code: "2022" }, breakLine: i < bullets.length - 1, color: C.mute, fontSize: 15 },
  })), { x: MX, y: 4.9, w: CW * 0.7, h: 1.6, fontFace: FONT, valign: "top" });
  notesOf(s, notes);
  return s;
}

// ── 간지 ──────────────────────────────────────────────────────
function chapterSlide({ num, titleText, accent, notes }) {
  const s = pres.addSlide();
  bgFill(s, accent);
  s.addText(String(num), {
    x: 0, y: 1.8, w: W, h: 2.0, fontFace: FONT, fontSize: 96, color: accent, align: "center", bold: false,
  });
  s.addText(titleText, {
    x: 0, y: 4.0, w: W, h: 1.0, fontFace: FONT, fontSize: 32, color: C.ink, align: "center",
  });
  notesOf(s, notes);
  return s;
}

// ── 본문 슬라이드 공통 프레임 ──────────────────────────────────
function baseSlide({ eyebrow: eb, titleText, accent = C.blue, notes }) {
  const s = pres.addSlide();
  bgFill(s, accent);
  if (eb) eyebrow(s, eb, accent);
  title(s, titleText);
  notesOf(s, notes);
  return s;
}

// 한 문장 슬라이드
function statementSlide({ titleText, sub, quote, accent, notes }) {
  const s = baseSlide({ titleText, accent, notes: null });
  s.addText(titleText, { x: MX, y: 0, w: 0, h: 0 }); // no-op placeholder to keep signature simple
  // 실제 제목은 baseSlide 가 이미 그렸으므로 sub/quote만 추가
  if (sub) s.addText(sub, { x: MX, y: 2.3, w: CW * 0.85, h: 1.0, fontFace: FONT, fontSize: 20, color: C.body, valign: "top" });
  if (quote) s.addText(quote, {
    x: MX, y: 3.5, w: CW * 0.85, h: 1.2, fontFace: FONT, fontSize: 17, color: accent || C.blue,
    italic: false, valign: "top",
  });
  notesOf(s, notes);
  return s;
}

// 카드 3~4칸
function cardsSlide({ eyebrow: eb, titleText, lead, cards, quote, accent, notes }) {
  const s = baseSlide({ eyebrow: eb, titleText, accent, notes: null });
  let y = 2.1;
  if (lead) { s.addText(lead, { x: MX, y, w: CW, h: 0.6, fontFace: FONT, fontSize: 17, color: C.body }); y += 0.8; }
  const n = cards.length;
  const gap = 0.25;
  const cw = (CW - gap * (n - 1)) / n;
  cards.forEach((c, i) => {
    const cx = MX + i * (cw + gap);
    const fill = c.strong ? C.cardHi : C.card;
    s.addShape("roundRect", { x: cx, y, w: cw, h: 2.1, rectRadius: 0.08, fill: { color: fill }, line: { color: C.hair, width: 1 } });
    s.addText(c.k, { x: cx + 0.2, y: y + 0.2, w: cw - 0.4, h: 0.4, fontFace: FONT, fontSize: 12, color: C.ash, bold: true });
    s.addText(c.v, { x: cx + 0.2, y: y + 0.65, w: cw - 0.4, h: 0.8, fontFace: FONT, fontSize: 22, color: c.strong ? accent : C.ink, bold: true });
    if (c.p) s.addText(c.p, { x: cx + 0.2, y: y + 1.5, w: cw - 0.4, h: 0.5, fontFace: FONT, fontSize: 12, color: C.mute });
  });
  if (quote) s.addText(quote, { x: MX, y: y + 2.35, w: CW * 0.85, h: 0.8, fontFace: FONT, fontSize: 16, color: accent || C.blue });
  notesOf(s, notes);
  return s;
}

// 흐름 (flow chips)
function flowSlide({ eyebrow: eb, titleText, chips, quote, accent, notes }) {
  const s = baseSlide({ eyebrow: eb, titleText, accent, notes: null });
  const y = 2.6;
  let x = MX;
  const h = 0.55;
  chips.forEach((c) => {
    const tw = Math.max(1.1, 0.11 * c.text.length + 0.5);
    s.addShape("roundRect", {
      x, y, w: tw, h, rectRadius: h / 2,
      fill: { color: c.hi ? C.ink : C.bg },
      line: { color: c.hi ? C.ink : C.hair, width: 1 },
    });
    s.addText(c.text, {
      x, y, w: tw, h, align: "center", valign: "middle",
      fontFace: FONT, fontSize: 13, color: c.hi ? C.bg : C.body, bold: !!c.hi,
    });
    x += tw + 0.15;
    if (x < W - MX - 0.3) {
      s.addText("→", { x, y, w: 0.3, h, align: "center", valign: "middle", fontFace: FONT, fontSize: 14, color: C.mute });
      x += 0.35;
    }
  });
  if (quote) s.addText(quote, { x: MX, y: y + 1.1, w: CW * 0.85, h: 0.8, fontFace: FONT, fontSize: 16, color: accent || C.blue });
  notesOf(s, notes);
  return s;
}

// 절차 표
function tableSlide({ eyebrow: eb, titleText, headers, rows, quote, accent, notes }) {
  const s = baseSlide({ eyebrow: eb, titleText, accent, notes: null });
  const body = [
    headers.map((h) => ({ text: h, options: { fill: { color: "050507" }, color: C.ash, fontSize: 12, bold: true, fontFace: FONT } })),
    ...rows.map((r) => r.map((cell, i) => ({
      text: cell, options: { fill: { color: C.card }, color: i === 0 ? C.ink : C.body, fontSize: 14, fontFace: FONT },
    }))),
  ];
  s.addTable(body, {
    x: MX, y: 2.15, w: CW, colW: headers.length === 3 ? [1.3, CW - 1.3 - 4.5, 4.5] : undefined,
    border: { type: "solid", color: C.hair, pt: 0.5 }, autoPage: false, valign: "middle", rowH: 0.55,
  });
  if (quote) s.addText(quote, { x: MX, y: 2.15 + (rows.length + 1) * 0.55 + 0.35, w: CW * 0.85, h: 0.6, fontFace: FONT, fontSize: 15, color: accent || C.blue });
  notesOf(s, notes);
  return s;
}

// 실습 지시 (코드 블록)
function codeSlide({ eyebrow: eb, titleText, code, bullets, quote, accent, notes }) {
  const s = baseSlide({ eyebrow: eb, titleText, accent, notes: null });
  s.addShape("roundRect", { x: MX, y: 2.1, w: CW, h: 1.1 + code.split("\n").length * 0.05, rectRadius: 0.08, fill: { color: C.card }, line: { color: C.hair, width: 1 } });
  s.addText(code, { x: MX + 0.3, y: 2.3, w: CW - 0.6, h: 1.3, fontFace: "Consolas", fontSize: 16, color: C.green, valign: "top" });
  let y = 3.9;
  if (bullets) {
    s.addText(bullets.map((b, i) => ({ text: b, options: { bullet: { code: "2022" }, breakLine: i < bullets.length - 1, color: C.body, fontSize: 15 } })),
      { x: MX, y, w: CW * 0.85, h: 1.0, fontFace: FONT, valign: "top" });
    y += 1.1;
  }
  if (quote) s.addText(quote, { x: MX, y, w: CW * 0.85, h: 0.8, fontFace: FONT, fontSize: 16, color: accent || C.blue });
  notesOf(s, notes);
  return s;
}

// 목록형
function listSlide({ eyebrow: eb, titleText, bullets, quote, accent, notes }) {
  const s = baseSlide({ eyebrow: eb, titleText, accent, notes: null });
  s.addText(bullets.map((b, i) => ({ text: b, options: { bullet: { code: "2022" }, breakLine: i < bullets.length - 1, color: C.body, fontSize: 17, paraSpaceAfter: 10 } })),
    { x: MX, y: 2.2, w: CW * 0.85, h: 2.0, fontFace: FONT, valign: "top" });
  if (quote) s.addText(quote, { x: MX, y: 4.3, w: CW * 0.85, h: 0.8, fontFace: FONT, fontSize: 16, color: accent || C.blue });
  notesOf(s, notes);
  return s;
}

// ════════════════════════════════════════════════════════════
// 1. 표지
coverSlide({
  eyebrow: "1주차",
  titleText: "AI를 처음 만나요",
  sub: "오늘은 chatgpt.com 계정을 만들고, AI에게 처음으로 뭔가를 시켜봅니다.",
  bullets: ["중등반 ⟪시간⟫ · 고등반 ⟪시간⟫"],
  accent: C.blue,
  notes: "시작 전 확인: 노트북 전원, 브라우저 열림, 구글 계정 안내 카드 배부 완료, chatgpt.com 접속 테스트 완료. 첫 5분은 자리 정돈과 출석 확인만 한다.\n여기서 2분. 정시에 시작하고, 늦게 온 학생은 뒤에서 합류시킨다.",
});

// 2. 저는 OOO입니다
cardsSlide({
  titleText: "저는 ⟪강사 이름⟫입니다",
  lead: "⟪강사 소개 한 줄⟫",
  cards: [
    { k: "개발 경력", v: "⟪N⟫년" },
    { k: "앞으로 만날 시간", v: "24시간", p: "12주 × 2시간" },
    { k: "여러분이 만들 것", v: "12개", p: "매주 하나씩", strong: true },
  ],
  accent: C.blue,
  notes: "여기서 3분. 이력을 읊지 말고 \"무엇을 만드는 사람인가\"만 말한다. 숫자 세 개가 뜨는 동안 말하면 딱 맞는다.",
});

// 3. 이런 걸 만들어왔습니다
flowSlide({
  titleText: "이런 걸 만들어 왔습니다",
  chips: [{ text: "⟪만든 것 1⟫" }, { text: "⟪만든 것 2⟫" }, { text: "⟪만든 것 3⟫", hi: true }],
  quote: "⟪가벼운 에피소드 한 줄⟫",
  accent: C.blue,
  notes: "여기서 2분. 학생이 아는 것에 빗대어 말한다. 회사 이름·기술 스택은 의미 없다 — \"너희가 쓰는 그거\"가 통한다. 마지막 한 줄로 긴장을 푼다.",
});

// 4. 왜 이 수업을 하냐면
statementSlide({
  titleText: "왜 이 수업을 하냐면",
  sub: "⟪강사가 이 수업을 하는 이유⟫",
  quote: "12주 뒤에 여러분은 \"AI를 써봤다\"가 아니라 \"AI로 뭘 만들어봤다\"고 말하게 됩니다. 그게 이 수업의 전부입니다.",
  accent: C.blue,
  notes: "여기서 2분. 이 장이 첫 시간의 감정적 정점이다 — 천천히 말한다.",
});

// 5. 여러분은 AI를 써본 적 있나요?
cardsSlide({
  titleText: "여러분은 AI를 써본 적 있나요?",
  cards: [
    { k: "한 번도", v: "안 써봤어요" },
    { k: "가끔", v: "써봤어요" },
    { k: "거의 매일", v: "써요", strong: true },
  ],
  quote: "손을 들어볼까요? 오늘 속도를 여기 맞춰요.",
  accent: C.blue,
  notes: "여기서 5분. 실제로 손을 들게 하고 숫자를 눈으로 확인한다. \"한 번도\"가 많으면 다음 슬라이드(AI가 뭔지)를 천천히, \"매일\"이 많으면 가입 단계를 빠르게 넘기고 프로필 카드 실습을 늘린다. 정답은 없다 — 반응을 보고 이후 시간 배분을 즉석에서 조정하는 게 이 슬라이드의 목적이다.",
});

// 6. AI는 무엇을 하는 걸까요
statementSlide({
  titleText: "AI는 무엇을 하는 걸까요",
  sub: "여러분이 쓰는 AI는, 다음에 올 말을 아주 잘 맞히는 프로그램이에요.",
  quote: "\"옛날 옛적에\" 다음엔 뭐가 올까요? 대부분 \"한\" 이 나오죠. AI도 이렇게, 수많은 글을 보고 다음 말을 맞혀요.",
  accent: C.blue,
  notes: "여기서 5분. 어렵게 설명하지 않는다. \"다음 말 맞히기\"라는 직관 하나만 남기면 충분하다. 신경망·학습 데이터 같은 용어는 꺼내지 않는다 — 오늘은 개념보다 경험이 먼저다.",
});

// 7. 12주 동안 이렇게 갑니다
flowSlide({
  titleText: "12주 동안 이렇게 갑니다",
  chips: [
    { text: "내 프로필 카드" }, { text: "내 웹페이지" }, { text: "그림·포스터" },
    { text: "발표 슬라이드", hi: true }, { text: "이야기책" }, { text: "영상" }, { text: "나만의 작품관", hi: true },
  ],
  quote: "오늘 만드는 프로필 카드가 이 줄의 첫 칸이에요. 매주 한 칸씩 채워요.",
  accent: C.blue,
  notes: "흰 칸 두 개(발표 슬라이드·작품관)가 이 과정의 두 정점. 5주차와 8주차. 여기서 3분.",
});

// 8. 12주 뒤 여러분의 화면
statementSlide({
  titleText: "12주 뒤 여러분의 화면",
  sub: "완성된 작품관을 띄워둔 채로 설명합니다",
  quote: "이 주소를 가족에게 보내면, 여러분이 12주 동안 만든 걸 그대로 봅니다.",
  accent: C.violet,
  notes: "말 대신 화면. 미리 만들어 둔 완성 작품관을 실제로 띄우고 천천히 스크롤한다. 설명은 짧게 — 화면이 알아서 말한다. 여기서 3분. 첫 시간 동기의 대부분이 이 장에서 나온다.",
});

// 9. 이렇게 지내요
listSlide({
  titleText: "이렇게 지내요",
  bullets: [
    "막히면 3분 안에 손을 들어요 — 혼자 끙끙대는 시간이 제일 아까워요",
    "옆 친구가 막히면 알려줍니다 — 설명해보면 자기가 제일 많이 배웁니다",
    "AI가 한 말을 그대로 믿지 않습니다 — 12주 동안 가장 중요한 습관입니다",
  ],
  quote: "세 번째가 이 수업의 핵심입니다. 나머지 둘은 그걸 배우기 위한 준비입니다.",
  accent: C.blue,
  notes: "특히 첫 번째 — 조용한 교실일수록 손 드는 문턱을 낮춰 두어야 한다. \"3분\"이라는 숫자가 허락의 근거가 된다. 12주 내내 이 세 줄로 돌아온다. 여기서 3분.",
});

// 10. 오늘 끝나면 이게 생겨요
cardsSlide({
  titleText: "오늘 끝나면 이게 생겨요",
  lead: "내 프로필 카드. 내가 좋아하는 것을 AI가 직접 찾아서 만들어요.",
  cards: [
    { k: "오늘 만들 것", v: "HTML 카드", p: "내 컴퓨터에 저장돼요" },
    { k: "오늘 배울 말", v: "1개", p: "프롬프트 — AI에게 시키는 말" },
    { k: "숙제", v: "0개", p: "12주 내내 안 변해요", strong: true },
  ],
  accent: C.blue,
  notes: "완성 예시(강사 프로필 카드)를 미리 만들어 화면에 띄워둔다. \"12주 뒤 여러분의 작품관\"과 이어서 보여주면 좋다. 여기서 3분.",
});

// 11. 챕터 1 — 가입하기
chapterSlide({ num: 1, titleText: "가입하기", accent: C.orange, notes: "여기서부터 전원이 같이 움직인다. 한 명이라도 막히면 다음으로 안 넘어간다. 간지 1분." });

// 12. 다섯 단계면 끝나요
tableSlide({
  titleText: "다섯 단계면 끝나요",
  headers: ["단계", "무엇을", "확인"],
  rows: [
    ["1", "브라우저를 연다", "크롬 또는 엣지"],
    ["2", "chatgpt.com 을 친다", "주소창에 직접 입력"],
    ["3", "\"Google로 계속하기\"를 누른다", "학교 gmail 사용"],
    ["4", "이름과 생년월일을 입력한다", "처음 가입할 때만"],
    ["5", "대화창이 뜬다", "이게 오늘 쓸 화면입니다"],
  ],
  quote: "이미 계정이 있으면 3~4단계는 건너뛰어요.",
  accent: C.orange,
  notes: "학원 IP·네트워크는 이미 확인됐다 — ChatGPT 는 일반 웹사이트라 서버 접속과 달리 IP 인증이 필요 없다. 여기서 20분 — 오늘의 최대 변수. 계정 만드는 속도는 학생마다 크게 갈린다. 20분이 지났는데 못 만든 학생은 옆자리 화면 공유로 진도를 뺀다. 보호자 동의는 사전에 완료된 상태.",
});

// 13. 여기서 막히면
listSlide({
  titleText: "여기서 막히면",
  bullets: [
    "전화번호를 묻는다 → 학생 폰 번호로 인증(선택인 경우가 많아요)",
    "\"이미 있는 계정\" 이라고 뜬다 → 예전에 만든 계정을 그대로 쓰면 됩니다",
    "화면이 영어로 뜬다 → 오른쪽 아래 설정에서 한국어로 바꿀 수 있어요",
  ],
  quote: "막히면 손을 드세요. 넘어가지 않고 같이 봅니다.",
  accent: C.orange,
  notes: "별도 시간 배정 없음 — 앞 슬라이드의 20분 블록 안에서 처리한다. 흔한 세 가지만 미리 알아둔다.",
});

// 14. 챕터 2 — 프로필 카드 만들기
chapterSlide({ num: 2, titleText: "프로필 카드 만들기", accent: C.orange, notes: "간지 1분." });

// 15. 이렇게 시켜보세요
codeSlide({
  titleText: "이렇게 시켜보세요",
  code: "내 프로필 카드를 HTML로 만들어줘.\n내가 좋아하는 OOO 정보를 웹에서 찾아서 넣어줘.",
  bullets: ["게임, 아이돌, 유튜버, 팀, 캐릭터 — 뭐든 좋아하는 거 아무거나요."],
  quote: "AI가 인터넷에서 직접 찾아와요. 내가 알려주지 않았는데도요.",
  accent: C.orange,
  notes: "여기서 15분. 돌아다니며 막힌 학생부터 본다. 검색이 잘 안 걸리면 \"웹에서 찾아봐줘\"를 덧붙이게 한다. ChatGPT 가 코드를 화면에 통째로 보여준다 — 아직 파일이 아니라는 걸 짚어준다.",
});

// 16. 받은 걸 파일로 만들어요
tableSlide({
  titleText: "받은 걸 파일로 만들어요",
  headers: ["단계", "무엇을"],
  rows: [
    ["1", "코드를 전부 복사한다"],
    ["2", "메모장을 연다"],
    ["3", "붙여넣고, 이름을 me.html 로 저장한다"],
    ["4", "저장한 파일을 더블클릭한다"],
  ],
  quote: "짜잔! 방금 만든 카드가 화면에 떴어요.",
  accent: C.orange,
  notes: "여기서 5분. 메모장 저장 시 \"파일 형식\"을 \"모든 파일\"로, 확장자를 .html 로 정확히 쓰게 한다 — 흔한 실수 지점이다. 이 순간이 오늘의 첫 정점이다.",
});

// 17. 마음에 안 들면 다시 시키면 돼요
listSlide({
  titleText: "마음에 안 들면 다시 시키면 돼요",
  bullets: ["\"색을 파란색으로 바꿔줘\"", "\"테두리를 둥글게 해줘\"", "\"글씨를 더 크게 해줘\""],
  quote: "그런데 이번엔… 코드를 통째로 다시 받아요. 복사하고, 저장하고, 다시 열어야 해요.",
  accent: C.orange,
  notes: "여기서 10분. 실제로 2~3번 반복시킨다. 매번 전체 코드 복사 → 메모장 붙여넣기 → 저장 → 새로고침을 그대로 겪게 한다. 이 번거로움이 다음 슬라이드의 재료다 — 강사가 미리 불편하다고 말하지 않는다.",
});

// 18. 어? 이거 계속 이렇게 해야 돼요?
statementSlide({
  titleText: "어? 이거 계속 이렇게 해야 돼요?",
  sub: "맞아요, 좀 번거롭죠.",
  quote: "이 번거로움을 없애는 방법이 있어요. 다음 주에 만나요.",
  accent: C.orange,
  notes: "여기가 오늘의 숨은 정점이다. 학생이 먼저 이 말을 하게 만드는 게 목표다 — 강사가 설명하지 않는다. 실제로 나오면 \"맞아요, 좋은 질문이에요\"로 받고, 답은 주지 않는다. 다음 주(Codex)의 필요성을 학생 스스로 느끼게 하는 것이 이 장의 전부다. \"에이전트\"라는 말은 오늘 꺼내지 않는다. 여기서 3분.",
});

// 19. 대화는 사라지지 않아요
statementSlide({
  titleText: "대화는 사라지지 않아요",
  sub: "컴퓨터를 끄거나 창을 닫아도, 왼쪽 목록에 오늘 대화가 그대로 남아 있어요.",
  quote: "그래서 다음에 들어와도, 오늘 만든 카드 얘기를 이어서 할 수 있어요.",
  accent: C.blue,
  notes: "실제로 창을 닫았다 다시 열어 왼쪽 대화 목록에서 오늘 대화를 찾아 들어가는 걸 시연한다. 30초면 된다. 여기서 3분.",
});

// 20. 그런데 검색을 안 하면 어떨까요
codeSlide({
  titleText: "그런데 검색을 안 하면 어떨까요",
  code: "⟪강사 이름⟫이 누구야?",
  bullets: ["오늘 배운 것 중 이게 제일 중요해요", "AI가 한 말은 확인하고 써요"],
  quote: "방금은 찾아봐서 맞혔죠. 이번엔 그냥 물어볼게요 — 모른다고 하지 않고, 그럴듯하게 지어내요.",
  accent: C.orange,
  notes: "말 대신 시연. 강사 이름으로 먼저 한다 — 유명인이 아니면 거의 100% 지어낸다. 미리 한 번 돌려서 결과를 확인해 둘 것. 여기서 5분. 앞의 프로필 카드(검색 O)와 이 장(검색 X)의 대비가 핵심이다 — \"찾아보면 맞히고, 안 찾으면 지어낸다\".",
});

// 21. 챕터 3 — 오늘을 남기기
chapterSlide({ num: 3, titleText: "오늘을 남기기", accent: C.green, notes: "간지 1분." });

// 22. 마지막으로 이렇게 시켜요
codeSlide({
  titleText: "마지막으로 이렇게 시켜요",
  code: "오늘 내가 뭘 만들었는지,\n다음에 이어서 할 수 있게 정리해줘.",
  quote: "이걸 매주 마지막에 해요. 12주 뒤엔 나만의 기록이 쌓여 있을 거예요.",
  accent: C.green,
  notes: "여기서 8분. 실제로 시키고 결과를 같이 읽어본다. 오늘부터 12주 내내 반복되는 의식이라고 알려준다 — 다음 주에도, 그다음 주에도 수업 끝엔 항상 이걸 한다. 7주차에 공개할 \"AI가 매주 쓰는 기록\"과 같은 원리라는 건 지금 말하지 않는다(7주차 공개 장면을 위해 감춘다).",
});

// 23. 다음 주에는
coverSlide({
  titleText: "다음 주에는",
  sub: "오늘 느낀 그 번거로움을 없애는 도구를 만나요. Codex 라는 이름이에요.",
  bullets: ["숙제 없음", "준비물 없음", "다음 주에 그냥 오면 돼요"],
  accent: C.blue,
  notes: "마무리 3분. 다음 주엔 새 계정 카드(서버 접속용)를 나눠준다고 예고한다. 오늘 만든 ChatGPT 계정도 계속 쓰니 아이디·비밀번호를 잊지 말라고 한 번 더 강조한다.",
});

pres.writeFile({ fileName: "w01-orientation.pptx" }).then(() => {
  console.log("done");
});
