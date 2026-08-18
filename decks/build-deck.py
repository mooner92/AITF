#!/usr/bin/env python3
"""마크다운 슬라이드 원고 → 자립 실행 HTML 발표자료.

산출물은 파일 하나다. 폰트·CSS·JS가 전부 안에 들어가므로 인터넷 없이,
USB로 옮겨서도 열린다 (docs/design-spec.md 0절 5항).

원고 문법
---------
    ---                     슬라이드 구분
    <!-- class: cover -->   그 슬라이드의 class (cover | chapter | g-green ...)
    # 제목                  h1
    ## 제목                 h2
    ### 제목                h3
    ^^^                     여기부터 아래는 fragment (한 단계씩 노출)
    ??? 노트                발표자 노트 (화면에 안 나옴, S키로 봄)
    표·목록·코드블록·인용    마크다운 그대로

치환
----
`{{KEY}}` 형태는 class-config.json 값으로 바뀐다. 값이 없으면 눈에 띄게
`⟪KEY 미설정⟫`으로 남아서, 빈칸인 채로 발표장에 들고 가는 사고를 막는다.

사용
----
    python3 build-deck.py <원고.md> [-o 출력.html] [-c class-config.json]
"""
import argparse, base64, html, io, json, os, re, sys, unicodedata
from pathlib import Path

HERE = Path(__file__).parent
FONT_DIR = Path(os.environ.get("PAPERLOGY_DIR", HERE.parent / "curriculum" / "fonts"))
WEIGHTS = {200: "Paperlogy-2ExtraLight.ttf", 400: "Paperlogy-4Regular.ttf",
           600: "Paperlogy-6SemiBold.ttf", 800: "Paperlogy-8ExtraBold.ttf"}


# ── 치환 ──────────────────────────────────────────────────────────
def load_config(path):
    if not path or not Path(path).exists():
        return {}
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    flat = {}

    def walk(prefix, node):
        for k, v in node.items():
            key = f"{prefix}{k}".upper()
            if isinstance(v, dict):
                walk(f"{key}_", v)
            elif isinstance(v, list):
                flat[key] = v
            else:
                flat[key] = str(v)
    walk("", raw)
    return flat


def substitute(text, cfg):
    """{{KEY}} → 값. 리스트 값은 {{KEY:table}} / {{KEY:list}} 로 형태를 고를 수 있다."""
    missing = set()

    def one(m):
        key, _, fmt = m.group(1).partition(":")
        key = key.strip().upper()
        v = cfg.get(key)
        # example 파일의 <설명> 형태는 아직 안 채운 것으로 본다 — 조용히 통과시키면
        # 빈칸인 채로 발표장에 들고 가게 된다
        if v is None or (isinstance(v, str) and re.fullmatch(r"\s*<.*>\s*", v)):
            missing.add(key)
            return f"⟪{key} 미설정⟫"
        if isinstance(v, list):
            if fmt == "list":
                return "\n".join(f"- {x}" for x in v)
            if fmt == "table":
                rows = "\n".join(f"| {x} |" for x in v)
                return f"| 계정 |\n|---|\n{rows}"
            return ", ".join(str(x) for x in v)
        return v

    return re.sub(r"\{\{([^}]+)\}\}", one, text), missing


# ── 마크다운 (필요한 만큼만) ──────────────────────────────────────
def inline(s):
    s = html.escape(s, quote=False)
    # 원고에 직접 쓴 인라인 태그는 살린다 — <b> <em> <span class="..."> 등.
    # 이걸 빼먹으면 제목의 <b>가 화면에 글자 그대로 나온다.
    s = re.sub(r"&lt;(/?(?:b|i|u|em|strong|small|code|br)|"
               r"span(?:\s+[\w-]+=&quot;[^&]*&quot;|\s+[\w-]+=\"[^\"]*\")*|/span)&gt;",
               r"<\1>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"<em>\1</em>", s)
    return s


def render_block(lines):
    """블록 단위 마크다운 → HTML. 표·목록·코드·인용·문단만 다룬다."""
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]

        if not ln.strip():
            i += 1
            continue

        # 코드블록
        if ln.strip().startswith("```"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            out.append("<pre><code>" + html.escape("\n".join(buf)) + "</code></pre>")
            continue

        # 표
        if ln.lstrip().startswith("|") and i + 1 < len(lines) and set(lines[i+1].strip()) <= set("|-: "):
            head = [c.strip() for c in ln.strip().strip("|").split("|")]
            i += 2
            body = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                body.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in head)
            tr = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
            out.append(f'<div class="tw"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>')
            continue

        # 목록
        if re.match(r"^\s*[-*]\s+", ln):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(inline(re.sub(r"^\s*[-*]\s+", "", lines[i]))); i += 1
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>")
            continue

        # 인용 → 콜아웃
        if ln.lstrip().startswith(">"):
            buf = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i])); i += 1
            out.append(f'<div class="point"><p>{inline(" ".join(buf))}</p></div>')
            continue

        # 제목
        m = re.match(r"^(#{1,3})\s+(.*)", ln)
        if m:
            lv = len(m.group(1))
            out.append(f"<h{lv}>{inline(m.group(2))}</h{lv}>"); i += 1
            continue

        # eyebrow
        if ln.startswith("^ "):
            out.append(f'<p class="eyebrow">{inline(ln[2:])}</p>'); i += 1
            continue

        # '<' 로 시작하는 줄은 원본 HTML로 본다.
        # 태그 조합을 부분적으로만 인식하려 들면 여는 쪽만 통과해 문서가 깨진다.
        if ln.lstrip().startswith("<"):
            out.append(ln.strip()); i += 1
            continue

        # 문단
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(
                r"^\s*([-*]\s|>|#{1,3}\s|\||```|\^\s)", lines[i]):
            buf.append(lines[i].strip()); i += 1
        if buf:
            out.append(f"<p>{inline(' '.join(buf))}</p>")
    return "\n".join(out)


def render_slide(src):
    """슬라이드 하나 → <section>. fragment(^^^)와 노트(???)를 분리한다."""
    cls, notes, body = [], [], []
    for ln in src.split("\n"):
        m = re.match(r"^<!--\s*class:\s*(.+?)\s*-->$", ln.strip())
        if m:
            cls += m.group(1).split()
            continue
        if ln.strip().startswith("???"):
            notes.append(ln.strip()[3:].strip())
            continue
        body.append(ln)

    # ^^^ 로 나뉜 뒤쪽 덩어리들은 fragment
    chunks = re.split(r"^\^\^\^\s*$", "\n".join(body), flags=re.M)
    parts = [render_block(chunks[0].split("\n"))]
    for c in chunks[1:]:
        inner = render_block(c.split("\n"))
        if inner.strip():
            parts.append(f'<div class="fragment">{inner}</div>')

    note_html = f'<aside class="notes">{inline(" ".join(notes))}</aside>' if notes else ""
    klass = " ".join(["slide"] + cls)
    return f'<section class="{klass}">\n{chr(10).join(parts)}\n{note_html}\n</section>'


# ── 폰트 ──────────────────────────────────────────────────────────
def font_faces(text):
    from fontTools.ttLib import TTFont
    from fontTools.subset import Subsetter, Options

    chars = {c for c in text if not unicodedata.category(c).startswith("C")}
    chars |= set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
                 " .,·:;!?()[]{}<>/\\|-–—_=+*&%@#'\"“”‘’…→←↑↓✓✔●○★☆⚡⟪⟫")
    faces, total = [], 0
    for w, fname in WEIGHTS.items():
        font = TTFont(str(FONT_DIR / fname))
        opts = Options(); opts.layout_features = ["*"]; opts.desubroutinize = True
        sub = Subsetter(options=opts)
        sub.populate(text="".join(sorted(chars)))
        sub.subset(font)
        font.flavor = "woff2"
        buf = io.BytesIO(); font.save(buf)
        total += buf.tell()
        b64 = base64.b64encode(buf.getvalue()).decode()
        faces.append(f"@font-face{{font-family:Paperlogy;font-style:normal;font-weight:{w};"
                     f"font-display:swap;src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
    return "\n".join(faces), total


# ── 조립 ──────────────────────────────────────────────────────────
SHELL = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
{faces}
{css}
</style>
</head>
<body>
<div id="glow"></div>
<div id="bar"></div>
<div id="stage">
{slides}
</div>
<div id="num"></div>
<div id="seek"></div>
<div id="overview"></div>
<div id="black"></div>
<div id="help"><div>
  <kbd>→</kbd> 다음 &nbsp; <kbd>←</kbd> 이전<br>
  <kbd>F</kbd> 전체화면 &nbsp; <kbd>O</kbd> 전체 목록<br>
  <kbd>S</kbd> 발표자 노트 &nbsp; <kbd>.</kbd> 화면 가리기<br>
  숫자 입력 후 <kbd>Enter</kbd> 로 해당 장 이동<br>
  <kbd>Esc</kbd> 닫기
</div></div>
<script>
{js}
</script>
</body>
</html>
"""


def build(src_path, out_path, cfg_path):
    raw = Path(src_path).read_text(encoding="utf-8")
    cfg = load_config(cfg_path)
    raw, missing = substitute(raw, cfg)

    # 첫 h1을 제목으로
    m = re.search(r"^#\s+(.+)$", raw, flags=re.M)
    title = re.sub(r"<[^>]+>|[*`]", "", m.group(1)).strip() if m else Path(src_path).stem

    blocks = [b for b in re.split(r"^---\s*$", raw, flags=re.M) if b.strip()]
    slides = "\n".join(render_slide(b) for b in blocks)

    css = (HERE / "engine.css").read_text(encoding="utf-8")
    js = (HERE / "engine.js").read_text(encoding="utf-8")

    # 폰트는 화면에 실제로 나오는 글자만
    visible = re.sub(r"<[^>]+>", " ", slides) + title + "다음 이전 전체화면 전체 목록 발표자 노트 화면 가리기 숫자 입력 후 로 해당 장 이동 닫기"
    faces, fsize = font_faces(visible)

    out = SHELL.format(title=html.escape(title), faces=faces, css=css, js=js, slides=slides)
    Path(out_path).write_text(out, encoding="utf-8")

    n = len(blocks)
    print(f"{Path(out_path).name}: {n}장 · 폰트 {fsize//1024}KB · 전체 {len(out.encode())//1024}KB")
    if missing:
        print(f"  ⚠ 미설정 치환값 {len(missing)}개: {', '.join(sorted(missing))}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("-o", "--out")
    ap.add_argument("-c", "--config", default=str(HERE / "class-config.json"))
    a = ap.parse_args()
    sys.exit(build(a.src, a.out or str(Path(a.src).with_suffix(".html")), a.config))
