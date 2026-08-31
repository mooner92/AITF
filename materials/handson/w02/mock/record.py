#!/usr/bin/env python3
"""모의 장면 → GIF 녹화 파이프라인.

Playwright 로 각 scene-*.html 을 녹화(webm)하고 ffmpeg 팔레트 2패스로 GIF 변환.
실제 Slack 은 헤드리스로 몰 수 없어(로그인) 모의 화면을 쓴다 — 재생성은 이 스크립트 하나.

사용: python3 materials/handson/w02/mock/record.py
"""
import subprocess
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
GIF = HERE.parent / "gif"
SHELL = "/usr/lib64/chromium-browser/headless_shell"

SCENES = [  # (파일, 녹화 초, gif fps)
    ("scene-compare.html", 9.5, 10),
    ("scene-thisweek.html", 6.5, 10),
    ("scene-thread.html", 10.0, 10),
]


def main():
    GIF.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=SHELL)
            for name, secs, fps in SCENES:
                ctx = browser.new_context(
                    viewport={"width": 640, "height": 400},
                    record_video_dir=tmp,
                    record_video_size={"width": 640, "height": 400})
                page = ctx.new_page()
                page.goto((HERE / name).as_uri())
                page.wait_for_timeout(int(secs * 1000))
                page.close()
                ctx.close()
                webm = page.video.path()
                out = GIF / (name.replace("scene-", "").replace(".html", "") + ".gif")
                palette = Path(tmp) / "pal.png"
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", webm,
                                "-vf", f"fps={fps},scale=640:-1:flags=lanczos,palettegen=max_colors=64"
                                , str(palette)], check=True)
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", webm,
                                "-i", str(palette),
                                "-lavfi", f"fps={fps},scale=640:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3",
                                "-loop", "0", str(out)], check=True)
                print(f"{out.name}: {out.stat().st_size // 1024}KB")
            browser.close()


if __name__ == "__main__":
    main()
