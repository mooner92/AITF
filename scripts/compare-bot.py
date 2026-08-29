#!/usr/bin/env python3
"""`/compare` 블라인드 테스트 봇 — 2주차 (specs/120 §3, specs/150)

학생이 `/compare <질문>` 을 치면, 같은 질문을 두 모델에 동시에 던지고
**이름을 가린 채(A/B)** 나란히 보여준다. 정답 공개는 봇이 하지 않는다 —
강사가 서버 로그를 보고 수업 중에 말로 공개한다(2주차 슬라이드 설계 그대로).

강등 경로 (specs/150 "⚠ 확인 필요"): 회사 서버 로컬 모델 사용은 아직
미승인이라, 지금은 **GPT 두 티어(luna·terra) 비교**로 돈다. 승인이 나면
로컬 모델 엔드포인트를 MODELS 에 추가하기만 하면 된다 — 채널·학생 습관은
그대로 두고 뒤의 모델만 바꾸는 게 애초 설계 원칙(150 "0. 확정 사항").

동작 원리 — ack-fast / work-slow (150 §1 ⓑ):
    1. 슬래시 커맨드 수신 → 3초 안에 ack (Bolt 가 자동)
    2. "생각 중…" 메시지를 채널에 올림 (ts 확보)
    3. 백그라운드 스레드에서 두 모델 동시 호출
    4. 끝나는 대로 그 메시지를 A/B 결과로 덮어씀 (chat_update)

Socket Mode 를 쓴다 — 인바운드 포트를 열지 않는다(110·150 원칙과 동일).

설정: /opt/scripts/.env (600)
    SLACK_BOT_TOKEN=xoxb-...        OAuth 봇 토큰
    SLACK_APP_TOKEN=xapp-...        앱 레벨 토큰 (connections:write 스코프)
    COMPARE_BOT_OPENAI_KEY=sk-...   전용 키 (학생 키와 분리 — specs 결정)

로그: /var/log/aitf-compare.jsonl — 어느 라벨(A/B)이 어느 모델이었는지.
      **Slack에는 절대 안 올라간다.** 강사가 공개할 때 눈으로 보는 용도.

사용:
    python3 compare-bot.py            # 포그라운드 실행 (systemd 가 이 방식으로 돌림)
"""
import json
import os
import random
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

ENV = Path("/opt/scripts/.env")
LOG = Path("/var/log/aitf-compare.jsonl")

# 강등 경로 — 회사 서버 승인 나면 여기에 로컬 모델을 추가한다.
# key 는 라벨이 아니라 "고를 때 참고할 이름"일 뿐, 학생에게는 절대 노출 안 함.
MODELS = [
    {"name": "gpt-5.6-luna", "in": 0.20, "out": 1.20},
    {"name": "gpt-5.6-terra", "in": 2.00, "out": 12.00},
]


def load_env():
    cfg = {}
    if ENV.exists():
        for ln in ENV.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1)
                cfg[k.strip()] = v.strip()
    return cfg


def call_model(api_key, model, prompt, timeout=45):
    """모델 하나 호출. (성공여부, 답, 걸린시간, 예상비용, 에러메시지) 반환.
    실패해도 예외를 밖으로 던지지 않는다 — 한 모델이 죽어도 나머지는 보여줘야 한다."""
    t0 = time.time()
    body = json.dumps({
        "model": model["name"],
        "messages": [{"role": "user", "content": prompt}],
        "max_completion_tokens": 400,
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions", data=body, method="POST",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
        elapsed = time.time() - t0
        text = data["choices"][0]["message"]["content"].strip()
        usage = data.get("usage", {})
        cost = (usage.get("prompt_tokens", 0) * model["in"]
                + usage.get("completion_tokens", 0) * model["out"]) / 1_000_000
        return True, text, elapsed, cost, None
    except urllib.error.HTTPError as e:
        return False, None, time.time() - t0, 0.0, f"HTTP {e.code}"
    except Exception as e:
        return False, None, time.time() - t0, 0.0, str(e)[:80]


def log_reveal(channel, ts, prompt, mapping):
    """A/B 매핑을 서버에만 남긴다. Slack 에는 절대 쓰지 않는다."""
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "channel": channel, "ts": ts, "prompt": prompt, "mapping": mapping,
        }, ensure_ascii=False) + "\n")


def main():
    cfg = load_env()
    bot_token = cfg.get("SLACK_BOT_TOKEN")
    app_token = cfg.get("SLACK_APP_TOKEN")
    api_key = cfg.get("COMPARE_BOT_OPENAI_KEY")
    missing = [k for k, v in [("SLACK_BOT_TOKEN", bot_token), ("SLACK_APP_TOKEN", app_token),
                               ("COMPARE_BOT_OPENAI_KEY", api_key)] if not v]
    if missing:
        print(f"설정 누락: {', '.join(missing)} — /opt/scripts/.env 확인")
        raise SystemExit(1)

    app = App(token=bot_token)

    @app.command("/compare")
    def handle_compare(ack, body, client):
        ack()  # 3초 규칙 — 제일 먼저
        prompt = (body.get("text") or "").strip()
        channel = body["channel_id"]
        if not prompt:
            client.chat_postEphemeral(channel=channel, user=body["user_id"],
                                       text="`/compare 질문 내용` 처럼 뒤에 질문을 붙여주세요.")
            return

        placeholder = client.chat_postMessage(channel=channel, text="🤔 두 모델이 생각 중…")
        ts = placeholder["ts"]

        def work():
            order = MODELS[:]
            random.shuffle(order)  # 매번 A/B 순서를 섞는다 — 패턴으로 유추 못 하게
            results = [None, None]

            def run(i, m):
                results[i] = call_model(api_key, m, prompt)

            threads = [threading.Thread(target=run, args=(i, m)) for i, m in enumerate(order)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            lines = [f"*질문:* {prompt}\n"]
            mapping = {}
            for label, m, (ok, text, elapsed, cost, err) in zip("AB", order, results):
                mapping[label] = m["name"]
                if ok:
                    lines.append(f"*{label}* — {elapsed:.1f}초 · 약 ${cost:.4f}\n> {text}")
                else:
                    lines.append(f"*{label}* — 응답 실패 ({err})")
            client.chat_update(channel=channel, ts=ts, text="\n\n".join(lines))
            log_reveal(channel, ts, prompt, mapping)

        threading.Thread(target=work, daemon=True).start()

    print("compare-bot: Socket Mode 연결 시작")
    SocketModeHandler(app, app_token).start()


if __name__ == "__main__":
    main()
