/* AITF 발표자료 엔진 — 동작
   docs/design-spec.md 5-2·5-3 구현. 외부 의존성 없음.

   설계 원칙
   - fragment가 남아 있으면 슬라이드를 넘기지 않고 fragment부터 소진한다.
   - 위치는 location.hash에 남긴다 (새로고침·링크 공유 대응).
   - View Transition은 있으면 쓰고 없으면 그냥 넘긴다 (점진적 향상).
*/
(() => {
  const slides = [...document.querySelectorAll('.slide')];
  const bar = document.getElementById('bar');
  const num = document.getElementById('num');
  const seekEl = document.getElementById('seek');
  const overview = document.getElementById('overview');
  const help = document.getElementById('help');
  const black = document.getElementById('black');

  // 슬라이드별 fragment 목록 — 인덱스 순서대로 켜진다
  const frags = slides.map(s => [...s.querySelectorAll('.fragment')]);

  let i = 0;      // 현재 슬라이드
  let f = 0;      // 현재 슬라이드에서 켜진 fragment 수
  let seek = '';  // 숫자 입력 버퍼

  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

  function paint() {
    slides.forEach((s, k) => s.classList.toggle('on', k === i));
    frags[i].forEach((el, k) => el.classList.toggle('on', k < f));
    // 다른 슬라이드의 fragment는 되돌려 둔다 — 뒤로 갔다 오면 다시 단계별로 나와야 한다
    frags.forEach((list, k) => { if (k !== i) list.forEach(el => el.classList.remove('on')); });

    const total = slides.length;
    bar.style.width = ((i + 1) / total * 100) + '%';
    num.textContent = (i + 1) + ' / ' + total;
    if (location.hash !== '#' + (i + 1)) history.replaceState(null, '', '#' + (i + 1));
    pushNotes();
  }

  /* 전환 애니메이션을 감싸는 얇은 래퍼.
     View Transition을 지원하지 않거나 모션 저감이 켜져 있으면 즉시 실행한다. */
  function transition(dir, fn) {
    if (reduced || !document.startViewTransition) { fn(); return; }
    document.documentElement.dataset.dir = dir;
    document.startViewTransition(fn);
  }

  function go(n, dir) {
    const next = Math.max(0, Math.min(slides.length - 1, n));
    if (next === i) return;
    const d = dir || (next > i ? 'fwd' : 'back');
    transition(d, () => {
      i = next;
      // 뒤로 갈 때는 그 슬라이드의 fragment를 모두 펼친 상태로 들어간다
      f = d === 'back' ? frags[i].length : 0;
      paint();
    });
  }

  function next() {
    if (f < frags[i].length) { f++; paint(); return; }   // fragment 먼저
    go(i + 1, 'fwd');
  }

  function prev() {
    if (f > 0) { f--; paint(); return; }
    go(i - 1, 'back');
  }

  function toggle(el) {
    const on = el.classList.toggle('on');
    if (el === overview && on) buildOverview();
    return on;
  }

  function buildOverview() {
    if (overview.dataset.built) return;
    slides.forEach((s, k) => {
      const t = s.querySelector('h1, h2, h3');
      const b = document.createElement('button');
      b.innerHTML = `<span class="i">${k + 1}</span>
                     <span class="t">${t ? t.textContent.trim() : '(제목 없음)'}</span>`;
      b.onclick = () => { overview.classList.remove('on'); go(k); };
      overview.appendChild(b);
    });
    overview.dataset.built = '1';
  }

  addEventListener('keydown', e => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const k = e.key;

    // 숫자 입력 → Enter 로 점프
    if (/^[0-9]$/.test(k)) { seek += k; seekEl.textContent = '→ ' + seek; return; }
    if (k === 'Enter' && seek) { go(parseInt(seek, 10) - 1); seek = ''; seekEl.textContent = ''; return; }
    if (k === 'Escape') {
      seek = ''; seekEl.textContent = '';
      overview.classList.remove('on'); help.classList.remove('on'); black.classList.remove('on');
      return;
    }

    if ([' ', 'ArrowRight', 'ArrowDown', 'PageDown'].includes(k)) { e.preventDefault(); next(); }
    else if (['ArrowLeft', 'ArrowUp', 'PageUp'].includes(k)) { e.preventDefault(); prev(); }
    else if (k === 'Home') go(0);
    else if (k === 'End') go(slides.length - 1);
    else if (k === 'f' || k === 'F') {
      document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen();
    }
    else if (k === 'o' || k === 'O') toggle(overview);
    else if (k === '.') toggle(black);
    else if (k === '?') toggle(help);
    else if (k === 's' || k === 'S') openNotes();
  });

  // 클릭 — 화면 좌우 절반. 크롬 요소 위에서는 무시한다
  addEventListener('click', e => {
    if (e.target.closest('#overview, #help, a, button')) return;
    e.clientX > innerWidth / 2 ? next() : prev();
  });

  // 터치 스와이프
  let x0 = null;
  addEventListener('touchstart', e => { x0 = e.changedTouches[0].clientX; }, { passive: true });
  addEventListener('touchend', e => {
    if (x0 === null) return;
    const dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 40) (dx < 0 ? next() : prev());
    x0 = null;
  }, { passive: true });

  /* 발표자 노트 — 별도 창에 현재/다음 슬라이드 노트를 띄운다.
     BroadcastChannel로 본 창의 이동을 따라간다. */
  let notesWin = null;
  const chan = 'BroadcastChannel' in window ? new BroadcastChannel('aitf-deck') : null;

  function notesFor(k) {
    const n = slides[k] && slides[k].querySelector('.notes');
    return n ? n.innerHTML : '<em style="color:#888e90">노트 없음</em>';
  }
  function titleFor(k) {
    const t = slides[k] && slides[k].querySelector('h1,h2,h3');
    return t ? t.textContent.trim() : '';
  }
  function pushNotes() {
    if (!chan) return;
    chan.postMessage({
      i, total: slides.length,
      cur: notesFor(i), curT: titleFor(i),
      nxt: i + 1 < slides.length ? notesFor(i + 1) : '', nxtT: titleFor(i + 1),
    });
  }
  function openNotes() {
    if (!chan) { alert('이 브라우저는 발표자 노트 창을 지원하지 않습니다.'); return; }
    notesWin = open('', 'aitf-notes', 'width=760,height=620');
    notesWin.document.write(`<!doctype html><meta charset="utf-8"><title>발표자 노트</title>
<style>
 body{background:#000;color:rgba(252,253,255,.86);font-family:system-ui,-apple-system,sans-serif;
      margin:0;padding:28px;line-height:1.7}
 h2{font-size:13px;letter-spacing:.16em;text-transform:uppercase;color:#888e90;
    font-weight:600;margin:0 0 10px}
 section{border:1px solid rgba(255,255,255,.14);border-radius:12px;padding:22px;margin-bottom:16px;
         background:#0a0a0c}
 .t{color:#fcfdff;font-size:19px;font-weight:600;margin-bottom:12px}
 .n{font-size:11px;color:#888e90;letter-spacing:.1em}
 .nxt{opacity:.62}
</style>
<div class="n" id="p"></div>
<section><h2>현재</h2><div class="t" id="ct"></div><div id="c"></div></section>
<section class="nxt"><h2>다음</h2><div class="t" id="nt"></div><div id="n"></div></section>
<script>
 new BroadcastChannel('aitf-deck').onmessage = e => {
   const d = e.data;
   p.textContent = (d.i+1) + ' / ' + d.total;
   ct.textContent = d.curT; c.innerHTML = d.cur;
   nt.textContent = d.nxtT; n.innerHTML = d.nxt;
 };
<\/script>`);
    notesWin.document.close();
    setTimeout(pushNotes, 120);
  }

  // 해시로 시작 위치 복원
  const start = parseInt((location.hash || '').slice(1), 10);
  if (start >= 1 && start <= slides.length) i = start - 1;

  buildOverview();
  paint();
})();
