#!/usr/bin/env python3
"""빌드된 슬라이드 HTML → Artifact 게시용 조각으로 변환.

Artifact 툴은 자체 <!doctype>...<head>...<body> 뼈대를 씌우므로, build-deck.py가
만든 완전한 문서(자체 <head><style> + <body><script>)를 그대로 넘기면 head/body가
이중으로 겹친다. <style> 블록과 <body> 내용만 뽑아 이어 붙인다 — <style>은 문서
어디에 있어도 브라우저가 그대로 적용하므로 안전하다.

사용: python3 to-artifact.py w01-orientation.html [출력.html]
기본 출력: 스크래치패드/artifact/<이름>.html
"""
import os, re, sys
from pathlib import Path

# 세션마다 스크래치패드 경로가 달라진다 — 하드코딩하지 않고 환경에서 받는다.
# 없으면 저장소 옆 임시 폴더로 폴백(스크래치패드가 없는 환경에서도 동작하게).
SCRATCH = Path(os.environ.get("CLAUDE_SCRATCHPAD", Path(__file__).parent / ".artifact-scratch"))


def convert(src_path, out_path=None):
    html = Path(src_path).read_text(encoding="utf-8")
    style = re.search(r"<style>.*?</style>", html, re.S).group(0)
    body = re.search(r"<body>(.*)</body>", html, re.S).group(1)
    title = re.search(r"<title>(.*?)</title>", html)
    out = style + "\n" + body
    out_path = Path(out_path) if out_path else SCRATCH / Path(src_path).name
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out, encoding="utf-8")
    print(str(out_path))
    return out_path, (title.group(1) if title else Path(src_path).stem)


if __name__ == "__main__":
    convert(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
