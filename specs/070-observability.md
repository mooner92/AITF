# 070 — P6: 토큰·리소스·진도 관측 (OpenObserve)

**상태**: In Progress · 수집 파이프라인 + OpenObserve 가동 (2026-08-16), 대시보드 구성 잔여

## 채택 결정: 모니터링 웹은 자작 대신 [OpenObserve](https://github.com/openobserve/openobserve)

운영자 제안으로 검토 후 채택 (2026-08-16). 근거:
- 단일 Rust 엔진, arm64 공식 이미지, 실측 **294MB RAM** — 공용 서버 예산 안에 듦 (systemd 아닌 docker `--memory=1g` 캡)
- **내장 인증이 핵심 요구를 해결**: 학생이 루프백으로 `curl` 해도 401 (실측 검증) — 자작 시 직접 만들었어야 할 부분
- JSON HTTP 인제스트 + SQL 검색 + 대시보드 빌더 내장 → 자작 UI 개발 공수 제거
- 배포는 **docker 컨테이너**(`aitf-mon`, named volume) — "Gitea는 바이너리" 원칙과 다른 선택인 이유: OpenObserve OSS는 바이너리 직배포가 없고(EE만), named volume은 SELinux 마찰이 없음

## 목표

강사가 반 전체/개인별 **토큰 사용량 + 서버 리소스 + 진도**를 준실시간으로 한 화면에서 본다.
학생별 분리 집계, 온라인 리더보드 미사용(로컬 전용). 학생에게는 어떤 관리 권한도 없다.

## 설계

- **수집 3종** (cron, 같은 주기):
  1. **토큰**: tokscale(로컬 로그 판독 CLI)을 학생별 실행 → `/var/lib/tokmon/<계정>.json`
  2. **리소스**: 학생별 systemd slice의 cgroup에서 메모리·CPU·프로세스 수 직접 판독 →
     `/sys/fs/cgroup/user.slice/user-<UID>.slice/{memory.current,cpu.stat,pids.current}` + 서버 전체 `free`/`loadavg`
     → 누가 메모리 상한에 근접했는지, 뭐가 폭주하는지 수업 중 즉시 식별
  3. **진도**: 학생별 프로젝트 커밋 수 + 마지막 파일 수정 시각 → 멈춰 있는 학생 조기 발견
  - cron 주기: **일요일 13–18시 1분 / 평시 15분** (수업: 일 14–16 중등, 16–18 고등)
    ```
    # /etc/cron.d/tokmon
    * 13-18 * * 0  root /opt/scripts/collect-tokens.sh
    */15 * * * *   root /opt/scripts/collect-tokens.sh
    ```
  - `/var/lib/tokmon`은 root 700 — 학생 상호 열람 차단. 학생 본인은 자기 계정에서 `tokscale` 직접 실행 시 본인 것만 보임.
- **대시보드**: OpenObserve — `127.0.0.1:8080`(호스트) → 컨테이너 5080. 외부는 `mon.<domain>`(강사 OTP) 경유.
  - 인증: OpenObserve 로그인 (root 계정 자격증명은 `/opt/scripts/openobserve-admin.txt`, root 600). 무인증 API 401 확인됨.
  - 수집기가 스트림 3개로 push: `tokens`(tokscale) · `resources`(cgroup) · `server`(전체 헬스)
  - 필요 뷰:
    1. **반 대시보드** (수업 중 메인): 학생별 카드 — 토큰(오늘/누적) · 메모리 게이지(상한 대비) · 마지막 활동 시각 · 커밋 수. 상한 90% 근접 시 카드 강조
    2. 개인 상세: 토큰 추이, 모델별 분포, 커밋 타임라인
    3. 서버 헬스: 전체 메모리/CPU/디스크 + 기존 서비스 상태
    4. **1차 vs 2차 스프린트 비교** (12주차용)
    5. 리그 보드: 주간 프롬프트 골프 순위 · 절감률 (커리큘럼 연동, [090](090-materials.md))
- 관리자 버튼(유저 추가·초기화)은 후순위 — 실작업은 스크립트, UI는 호출 버튼일 뿐.
- 스크립트: [`scripts/collect-tokens.sh`](../scripts/collect-tokens.sh)

## 작업 체크리스트

- [x] 수집 스크립트 + cron 배치 (일 13–18시 1분 / 평시 15분)
- [x] OpenObserve 가동 (docker `aitf-mon`, 루프백 8080, 메모리 캡 1G, restart 정책)
- [x] 인제스트 → SQL 검색 왕복 검증 (스트림 3개)
- [ ] 대시보드 구성 (UI에서 — 터널 연결 후): 반 대시보드 / 개인 상세 / 서버 헬스 / 1차vs2차 / 리그 보드
- [ ] 터널 `mon.<domain>` 연결 (030)

### 대시보드용 시작 쿼리 (UI 패널에 그대로 사용)

```sql
-- 반 대시보드: 학생별 최신 상태 (mid/high는 user 접두사)
SELECT "user", max(_timestamp) AS t, max(mem_bytes)/1048576 AS mem_mb, max(commits) AS commits
FROM resources WHERE "user" LIKE 'mid%' GROUP BY "user" ORDER BY "user"

-- 메모리 상한 근접 경고 (1536M의 90%)
SELECT "user", mem_bytes/1048576 AS mem_mb FROM resources WHERE mem_bytes > 1449551462

-- 서버 헬스 추이
SELECT _timestamp, load, mem_avail/1073741824 AS mem_avail_gb FROM server ORDER BY _timestamp
```

## 검증 기준

- [ ] 학생 계정에서 프롬프트 1회 → 1분 내 대시보드 반영 (리허설에서)
- [x] 학생이 `tokscale` 실행 → 본인 것만 보임 (계정 분리 구조)
- [x] 학생 계정에서 `curl 127.0.0.1:8080/api/...` → **401** (실측)
