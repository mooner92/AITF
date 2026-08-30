# 040 — P3: 학생 계정·템플릿 홈

**상태**: **Done** · 템플릿·검증 완료, 명단 확정(5명, 고등반) — 계정 생성·키 주입·`check-account.sh` 전원 통과 (2026-08-30)

## 목표

CSV 한 장으로 학생 계정을 일괄 생성/재생성. 각 계정은 tmux 자동 진입, 메모리·프로세스 상한, sudo 불가, 프로젝트 스켈레톤(의존성 사전 설치) 제공.

## 설계

- **반 편성 확정**: 일요일 **14–16 중등반 / 16–18 고등반**, 반당 ~6명. 계정 접두사 `mid` / `high` (예: `mid01`, `high03`) — 스냅샷·정리 스크립트가 접두사로 반을 구분한다.
- **명단 → CSV**: `계정ID,비밀번호` (헤더 없음). 실명 매핑은 repo 밖 스프레드시트에만.
- **메모리 예산 (24GB 유지 확정, [010](010-instance.md))**:
  총 24GB − OS·기존 서비스(~3GB) − 운영자 세션(~2GB) − 여유 ≈ 학생 몫 충분.
  동시 접속 ~6명(순차 수업): **MemoryMax=1536M / MemorySwapMax=512M** (드롭인 기준값).
- **MemoryHigh는 쓰지 않는다** — 2026-08-16 실측: High 스로틀은 폭주 프로세스를 "죽지 않고 한없이 느리게" 만들어 학생이 원인을 알 수 없다. 명확한 OOM-kill(Max)이 교육적으로 낫다. **MemorySwapMax 필수** — 이게 없으면 폭주가 swap으로 밀려나 서버 전체 I/O를 끌어내린다 (같은 실측에서 발견).
- **상한은 systemd slice 드롭인** (로그인 전에도 적용, 재부팅 유지):
  ```ini
  # /etc/systemd/system/user-<UID>.slice.d/limit.conf
  [Slice]
  MemoryMax=1024M
  MemoryHigh=800M
  TasksMax=256        ; 포크폭탄·프로세스 폭주 차단
  ```
- **템플릿 홈** `/opt/template-home`: 프로젝트 스켈레톤 + **node_modules 사전 설치**.
  수업 중 `npm install` 금지가 공유 서버 운영의 핵심 — 디스크·CPU 폭주의 최대 원인 제거.
- 스크립트: [`scripts/create-accounts.sh`](../scripts/create-accounts.sh), [`scripts/reset-home.sh`](../scripts/reset-home.sh)

## 작업 체크리스트

- [ ] 명단 스프레드시트 → `accounts.csv` → 서버 `/opt/scripts/` (700 디렉토리)
- [ ] `create-accounts.sh` 배치·실행 (useradd + chpasswd + tmux 자동 진입 + slice 드롭인)
- [ ] ❌ wheel 그룹 금지 재확인
- [ ] 홈 디렉토리 권한 700 확인 (학생 상호 열람 차단)
- [ ] 템플릿 홈 구축 (주제 확정 후 스켈레톤 확정, 의존성 설치는 디스크 확장 후)
- [ ] `reset-home.sh` 배치

## 검증 기준

- [ ] 테스트 계정 로그인 → tmux 자동 진입
- [ ] `sudo` 시도 → 거부 / `cat /opt/scripts/accounts.csv` → 거부 / `ls /home/<다른계정>` → 거부
- [ ] `npm ls` → 의존성 존재 (설치 없이)
- [ ] 메모리 폭주 시뮬레이션 → MemoryMax에서 해당 계정 프로세스만 죽고 서버·기존 서비스 무영향

## 결정 기록

- 2026-08-16 · `systemctl set-property` 대신 slice 드롭인 파일 채택 — 로그인 전 적용 + TasksMax 추가.
