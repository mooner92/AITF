#!/usr/bin/env python3
"""`/compare` 블라인드 테스트 봇 — 2주차 (specs/120 §3, specs/150)

학생이 `/compare <질문>` 을 치면, 같은 질문을 두 모델에 동시에 던지고
**이름을 가린 채(A/B)** 나란히 보여준다. 정답 공개는 봇이 하지 않는다 —
강사가 서버 로그를 보고 수업 중에 말로 공개한다(2주차 슬라이드 설계 그대로).

2026-08-30: GPT 두 티어(luna·terra) 비교는 같은 회사 모델끼리라 실습으로서
의미가 부족하다고 판단해 폐기. **luna(OpenAI) vs qwen3.8-27b(회사 서버)**로
교체했다 — "AI는 하나가 아니다"가 실제로 성립하는 조합이다.

qwen 은 회사 GPU 서버를 Cloudflare Access **Service Token**으로 통과해
호출한다. 회사 쪽 회신에서 확인된 제약 셋을 그대로 반영했다:
  · 비스트리밍 + `chat_template_kwargs.enable_thinking=false` + `max_tokens≤900`
    만 안전하다 — 스트리밍+thinking끔은 본문이 빈 문자열로 오는 vLLM 버그가
    있고, thinking 을 켜면 100초(Cloudflare 프록시 타임아웃) 벽에 걸린다.
  · 서버 쪽에 동시 실행 상한이 없어(`--max-num-seqs` 미지정) **봇 쪽에서
    반드시 큐잉**해야 한다 — LOCAL_MODEL_SEM 이 그 역할.
  · Access 정책엔 요일/시각 조건이 없어(신원·IP 기준만 지원) **봉 쪽에서
    스스로 시간대를 지킨다** — ALLOWED_HOURS.
    일요일 13~19시(수업 시간, 여유 포함)에만 qwen 을 부른다. 원래 요청서에는
    14~18시로 적어 보냈으나, 2026-08-30 1시간씩 여유를 더해 넓혔다 — 통보
    수준(1시간 확대)이라 회사에 별도 재협의는 안 함.

동작 원리 — ack-fast / work-slow (150 §1 ⓑ):
    1. 슬래시 커맨드 수신 → 3초 안에 ack (Bolt 가 자동)
    2. "생각 중…" 메시지를 채널에 올림 (ts 확보)
    3. 백그라운드 스레드에서 두 모델 동시 호출
    4. 끝나는 대로 그 메시지를 A/B 결과로 덮어씀 (chat_update)

Socket Mode 를 쓴다 — 인바운드 포트를 열지 않는다(110·150 원칙과 동일).

설정: /opt/scripts/.env (600)
    SLACK_BOT_TOKEN=xoxb-...            OAuth 봇 토큰
    SLACK_APP_TOKEN=xapp-...            앱 레벨 토큰 (connections:write 스코프)
    COMPARE_BOT_OPENAI_KEY=sk-...       OpenAI 쪽 전용 키 (학생 키와 분리)
    CF_ACCESS_CLIENT_ID=...access       회사 서버용 Service Token
    CF_ACCESS_CLIENT_SECRET=cfast_...
    LOCAL_LLM_BASE_URL=https://llm.excusa.uk/v1
    LOCAL_LLM_MODEL=qwen3.8-27b
    QWEN_TESTER_SLACK_IDS=U0XXXXXXX          강사 전용 /qwentest 허용 목록(콤마 구분)

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
from datetime import datetime
from pathlib import Path

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

ENV = Path("/opt/scripts/.env")
LOG = Path("/var/log/aitf-compare.jsonl")

# 서버 쪽에 동시 실행 상한이 없다 — 여기서 반드시 걸어야 한다 (회사 회신 필수 조건).
# openai 쪽은 이 제한이 필요 없다(우리 프로젝트 예산으로만 제한됨).
LOCAL_MODEL_SEM = threading.Semaphore(2)

# 일요일(weekday()==6) 13~19시. 요청서엔 14~18시로 적어 보냈으나
# 2026-08-30 여유 확보차 앞뒤 1시간씩 넓혔다(회사 재협의 불필요 — Sean 확인).
ALLOWED_WEEKDAY = 6
ALLOWED_HOURS = range(13, 19)


def in_allowed_window(now=None) -> bool:
    now = now or datetime.now()
    return now.weekday() == ALLOWED_WEEKDAY and now.hour in ALLOWED_HOURS


# label 은 출처 표시용. [com] = 회사 서버, 나중에 다른 소스가 붙으면
# 같은 규칙으로 접두어만 바꾼다 (예: [hf] 허깅페이스 자체 호스팅 등).
# API 호출에는 반드시 name(서버가 실제로 아는 모델 id)을 쓴다 — label 은
# 화면 표시 전용이라 오타가 있어도 호출은 깨지지 않지만, 헷갈릴 수 있어 분리했다.
# 두 모델 다 이 지시를 받는다 — /compare 가 "블라인드" 테스트가 되려면
# 서식 스타일 자체가 힌트가 되면 안 된다(헤더·표·이모지로 도배하는 쪽이
# 한눈에 다른 모델임을 드러내면 블라인드가 깨진다). 2026-08-30 실측:
# 지시 없이 물었더니 qwen 이 보고서 스타일로 900토큰을 다 채워 답이
# 중간에 잘렸다 — 짧게 답하라는 지시가 없어서 생긴 문제였다.
SYSTEM_PROMPT = (
    "중고등학생 채팅방에서 짧게 답한다. 한국어로, 2~4문장. "
    "마크다운 제목(#)·표·이모지·볼드 남발 없이 평범한 대화체로 쓴다. "
    "모르는 용어가 나오면 모른다고 짧게 말하고 넘어간다."
)

MODELS = [
    {"name": "gpt-5.6-luna", "label": "[openai]gpt-5.6-luna", "provider": "openai", "in": 0.20, "out": 1.20},
    {"name": "qwen3.8-27b", "label": "[com]qwen3.8-27b", "provider": "local", "in": 0.0, "out": 0.0},
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


def call_openai(cfg, model, prompt, timeout=45):
    t0 = time.time()
    body = json.dumps({
        "model": model["name"],
        "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                     {"role": "user", "content": prompt}],
        "max_completion_tokens": 400,
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions", data=body, method="POST",
        headers={"Authorization": f"Bearer {cfg['COMPARE_BOT_OPENAI_KEY']}",
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
        elapsed = time.time() - t0
        text = data["choices"][0]["message"]["content"].strip()
        usage = data.get("usage", {})
        cost = (usage.get("prompt_tokens", 0) * model["in"]
                + usage.get("completion_tokens", 0) * model["out"]) / 1_000_000
        return True, text, elapsed, f"약 ${cost:.4f}", None
    except urllib.error.HTTPError as e:
        return False, None, time.time() - t0, None, f"HTTP {e.code}"
    except Exception as e:
        return False, None, time.time() - t0, None, str(e)[:80]


def call_local(cfg, model, prompt, timeout=90, bypass_window=False):
    """회사 서버 qwen. 회신에서 확인된 유일한 안전 조합만 쓴다 —
    비스트리밍 + thinking 끔 + max_tokens 900. 다른 조합(스트리밍+thinking끔)은
    본문이 빈 문자열로 오는 vLLM 버그가 있어 쓰지 않는다.

    bypass_window: 강사 개인 테스트 전용(/qwentest)에서만 True 로 넘긴다.
    학생이 쓰는 /compare 경로는 이 인자를 절대 안 넘긴다 — 그래서 시간대
    보호가 학생 트래픽에는 항상 걸린다. 세마포어(동시성 제한)는 두 경로
    모두 그대로 적용된다 — 이건 "누가 부르냐"가 아니라 "GPU가 몇 개를
    동시에 버티냐"의 문제라 예외를 두면 안 된다."""
    if not bypass_window and not in_allowed_window():
        return False, None, 0.0, None, "지금은 로컬 모델 사용 시간이 아니에요 (일요일 13~19시만)"

    base = cfg.get("LOCAL_LLM_BASE_URL", "").rstrip("/")
    cid = cfg.get("CF_ACCESS_CLIENT_ID")
    csec = cfg.get("CF_ACCESS_CLIENT_SECRET")
    if not (base and cid and csec):
        return False, None, 0.0, None, "로컬 모델 설정 미완료"

    t0 = time.time()
    body = json.dumps({
        "model": model["name"],
        "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                     {"role": "user", "content": prompt}],
        "max_tokens": 900,
        "chat_template_kwargs": {"enable_thinking": False},
    }).encode()
    req = urllib.request.Request(
        f"{base}/chat/completions", data=body, method="POST",
        headers={"CF-Access-Client-Id": cid, "CF-Access-Client-Secret": csec,
                 "Content-Type": "application/json",
                 # Cloudflare 가 Python urllib 기본 UA("Python-urllib/3.x")를
                 # 봇으로 인식해 403(에러 1010)으로 차단한다 — curl 은 통과하는데
                 # urllib 만 막히는 걸로 실측 확인(2026-08-30). UA만 바꾸면 뚫린다.
                 "User-Agent": "curl/8.5.0"})

    # 서버 쪽 동시 실행 상한이 없다 — 여기서 큐잉한다(회사 합의 조건).
    with LOCAL_MODEL_SEM:
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = json.loads(r.read())
            elapsed = time.time() - t0
            text = data["choices"][0]["message"]["content"].strip()
            return True, text, elapsed, "무료 (사내 GPU)", None
        except urllib.error.HTTPError as e:
            return False, None, time.time() - t0, None, f"HTTP {e.code}"
        except Exception as e:
            return False, None, time.time() - t0, None, str(e)[:80]


def call_model(cfg, model, prompt):
    """모델 하나 호출. (성공여부, 답, 걸린시간, 비용표시, 에러메시지) 반환.
    실패해도 예외를 밖으로 던지지 않는다 — 한 모델이 죽어도 나머지는 보여줘야 한다."""
    if model["provider"] == "local":
        return call_local(cfg, model, prompt)
    return call_openai(cfg, model, prompt)


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
    missing = [k for k in ("SLACK_BOT_TOKEN", "SLACK_APP_TOKEN", "COMPARE_BOT_OPENAI_KEY")
               if not cfg.get(k)]
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
                results[i] = call_model(cfg, m, prompt)

            threads = [threading.Thread(target=run, args=(i, m)) for i, m in enumerate(order)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            lines = [f"*질문:* {prompt}\n"]
            mapping = {}
            for label, m, (ok, text, elapsed, cost, err) in zip("AB", order, results):
                mapping[label] = m["label"]
                if ok:
                    lines.append(f"*{label}* — {elapsed:.1f}초 · {cost}\n> {text}")
                else:
                    lines.append(f"*{label}* — 응답 실패 ({err})")
            client.chat_update(channel=channel, ts=ts, text="\n\n".join(lines))
            log_reveal(channel, ts, prompt, mapping)

        threading.Thread(target=work, daemon=True).start()

    tester_ids = {u.strip() for u in cfg.get("QWEN_TESTER_SLACK_IDS", "").split(",") if u.strip()}
    local_model = next(m for m in MODELS if m["provider"] == "local")

    @app.command("/qwentest")
    def handle_qwentest(ack, body, client):
        """강사 개인 테스트용 — 시간대 제한 없이 qwen 에 바로 묻는다.
        A/B 로 가리지 않고 어느 모델인지 그대로 보여준다(학생용 /compare 와 반대).
        허용 목록(QWEN_TESTER_SLACK_IDS)에 없는 사용자는 거절한다 — 이게 없으면
        /compare 의 시간대 제한이 사실상 무의미해진다(아무나 이 명령으로 우회 가능)."""
        ack()
        user = body["user_id"]
        channel = body["channel_id"]
        if user not in tester_ids:
            client.chat_postEphemeral(channel=channel, user=user,
                                       text="이 명령은 강사 전용이에요.")
            return
        prompt = (body.get("text") or "").strip()
        if not prompt:
            client.chat_postEphemeral(channel=channel, user=user,
                                       text="`/qwentest 질문 내용` 처럼 뒤에 질문을 붙여주세요.")
            return

        placeholder = client.chat_postMessage(channel=channel,
                                               text=f"🤔 {local_model['label']} 생각 중…")
        ts = placeholder["ts"]

        def work():
            ok, text, elapsed, cost, err = call_local(cfg, local_model, prompt, bypass_window=True)
            if ok:
                msg = f"*{local_model['label']}* — {elapsed:.1f}초 · {cost}\n\n{text}"
            else:
                msg = f"*{local_model['label']}* — 실패 ({err})"
            client.chat_update(channel=channel, ts=ts, text=msg)

        threading.Thread(target=work, daemon=True).start()

    @app.command("/thisweek")
    def handle_thisweek(ack, body, client):
        """이번 주 수업 정리(Notion) 링크 — publish-notion.py 가 남긴
        /var/lib/wiki-build/notion-links.json 에서 읽는다.

        어느 반 링크를 줄지는 **슬래시 커맨드 페이로드의 channel_name** 으로
        정한다 — 봇 스코프에 channels:read 가 없어 API 로 채널 이름을 조회할
        수 없지만, 슬래시 커맨드에는 이름이 실려 온다. 채널 이름에 high/mid 가
        없으면(DM 등) 양쪽 다 보여준다. 답은 ephemeral — 채널을 어지럽히지 않는다."""
        ack()
        user = body["user_id"]
        channel = body["channel_id"]
        cname = (body.get("channel_name") or "").lower()
        try:
            links = json.loads(Path("/var/lib/wiki-build/notion-links.json")
                               .read_text(encoding="utf-8"))
        except Exception:
            links = {}
        if not links:
            client.chat_postEphemeral(channel=channel, user=user,
                                       text="아직 이번 주 정리가 발행되지 않았어요. 일요일 저녁에 올라와요!")
            return
        # class1/class2 가 정식 이름. high/mid 는 옛 채널명 호환(개강 첫 주 채널).
        if "class1" in cname or "class-1" in cname or "high" in cname:
            wanted = ["class1"]
        elif "class2" in cname or "class-2" in cname or "mid" in cname:
            wanted = ["class2"]
        else:
            wanted = [c for c in ("class1", "class2") if c in links]
        lines = []
        for c in wanted:
            e = links.get(c)
            if e:
                lines.append(f"*{e.get('label', c)} {e.get('week')}주차 정리* → {e['url']}")
        client.chat_postEphemeral(channel=channel, user=user,
                                   text="\n".join(lines) if lines
                                   else "이번 주 정리를 찾지 못했어요.")

    print("compare-bot: Socket Mode 연결 시작")
    SocketModeHandler(app, app_token).start()


if __name__ == "__main__":
    main()
