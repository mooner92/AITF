# 030 — P2: 접속 경로·보안 잠금

**상태**: In Progress · 터널 라우팅 구축 완료 (2026-08-16 기준 도메인 확정, 2026-08-17 적용) · 차단: **Access 정책**(운영자 대시보드 작업), 학원 고정 IP

## 목표

학생은 학원에서 **브라우저만으로** 서버 터미널에 접속하고(계정·이메일 수집 없이), 외부에서는 접속 불가.
강사는 어디서든 OTP로 관리 경로 접속. 마지막에 공인 SSH 포트를 닫아 공격면 제거.

## ⚠️ 잠금 순서 (틀리면 운영자 본인이 잠긴다)

**새 경로 3중 검증 통과 전에는 절대 포트 22를 닫지 않는다.**

## 설계

- 기존 Cloudflare 터널(로컬 관리형, config.yml)에 ingress 3개 추가 — 새 터널 만들지 않음:
  ```yaml
  # /etc/cloudflared/config.yml (기존 항목 위, 404 폴백 앞에 추가)
  - hostname: ssh.<domain>
    service: ssh://localhost:22
  - hostname: git.<domain>
    service: http://localhost:3000
  - hostname: mon.<domain>
    service: http://localhost:8080
  ```
- DNS 라우팅: `cloudflared tunnel route dns <TUNNEL_ID> ssh.<domain>` (git/mon 동일)
- Zero Trust Access 애플리케이션:
  - **학생용** (ssh/git): `Bypass` 정책 — include: 학원 고정 IP → 로그인 마찰 0, 이메일 수집 0
  - **관리자용** (mon + 원격 ssh): `Allow` — 강사 이메일 One-Time PIN
  - ssh 앱은 **브라우저 렌더링(SSH) ON**
- 인증 분기: 학원 IP가 **유동**이면 학생용도 이메일 OTP로 회귀 (학생 이메일 수집 필요 — 설계 변경이므로 이 스펙 개정)

## 구축 결과 (2026-08-17)

| 호스트명 | 서비스 | 상태 |
|---|---|---|
| `mon.<domain>` | OpenObserve 127.0.0.1:8080 | ✅ 연결·검증 완료 (HTTP 200, OpenObserve 응답 확인) |
| `git.<domain>` | Gitea 127.0.0.1:3000 | ✅ 연결·검증 완료 (HTTP 200, Gitea 응답 확인) |
| `ssh.<domain>` | sshd 22 | ⛔ **의도적으로 비활성** — config.yml에 주석 처리. Access 정책 생성 후에만 해제 |
| 기존 서비스 | (변경 없음) | ✅ 회귀 확인 10/10 정상 |

### 구축 중 발견·처리한 문제 2건

1. **고아 replica가 라우팅을 오염시키고 있었다.** 같은 터널에 replica 2개가 붙어 있었는데, 하나는 시스템 서비스(config.yml 기반), 다른 하나는 수개월 전 수동 실행된 고아 프로세스로 `--url` 플래그를 쓰고 있었다. `--url`은 **모든 호스트명을 한 서비스로 강제 라우팅**하므로, 새 호스트명을 추가해도 요청의 절반이 엉뚱한 서비스로 갔을 것이다. 고아 프로세스를 정리하고 커넥터 1개로 통일 (기존 서비스 회귀 확인 후 실행).
2. **`ssh.<domain>` DNS 레코드가 이미 존재했다.** (와일드카드 아님 — 없는 서브도메인은 응답 없음) ingress 규칙을 켜면 Access 정책 없이 SSH가 열릴 수 있어 즉시 규칙을 주석 처리했다. 확인 결과 이 호스트명은 **우리 터널이 아닌 다른 곳**을 가리키고 있어(모든 경로에 빈 200 응답, 터널 폴백 404와 불일치) 실제 노출은 없었다. 운영자가 대시보드 DNS 탭에서 이 레코드의 정체를 확인해야 하며, 우리 터널로 가져오면 기존 레코드를 덮어쓴다.

## 작업 체크리스트

- [ ] 선행: 학원 네트워크에서 `curl ifconfig.me` → 고정 IP 여부 확인 (운영자)
- [x] 도메인 결정 (운영자)
- [x] config.yml ingress 추가 + 검증(`ingress validate`, `ingress rule`) → 재시작 → 기존 서비스 회귀 확인
- [x] 고아 replica 정리 → 커넥터 1개
- [x] DNS 라우팅 2건 (mon·git) — ssh는 Access 후로 보류
- [ ] **Access 앱 생성 (운영자, Zero Trust 대시보드)** — 이게 다음 게이트
  - 학생용(git, 추후 ssh): `Bypass` — 학원 고정 IP
  - 관리자용(mon): `Allow` — 운영자 이메일 One-Time PIN
  - ⚠️ **현재 mon·git은 각 앱의 로그인 화면이 공개 노출된 상태**다. Access 정책을 얹기 전까지는 임시 상태로 취급할 것
- [ ] ssh 앱 브라우저 렌더링 ON + config.yml의 ssh 규칙 주석 해제 → 재시작
- [ ] ✅ 3중 검증: ① 학원 IP에서 브라우저 터미널 성공 ② 외부(LTE)에서 차단 ③ 관리자 OTP 경로 성공
- [ ] 3중 검증 후에만: OCI Security List에서 `0.0.0.0/0 tcp/22` 삭제, **운영자 자택 IP /32 예외는 남김** (최후 복구 경로)
- [ ] 사용하지 않는 개방 포트 정리 (firewalld + Security List 이중 확인)

## 검증 기준

- [ ] 외부에서 `nmap -p22 <SERVER_IP>` → filtered/closed
- [ ] 학생 시나리오: 학원 IP → 브라우저 → 로그인 화면 없이 터미널
- [ ] 기존 터널 서비스 무영향

## 락아웃 복구 경로 (사고 대응)

Cloudflare 관리자 ssh 경로 → 안 되면 자택 IP 직통 22 → 최후에 OCI Cloud Shell 시리얼 콘솔.

## 비공개 참조

터널 ID·실제 도메인·학원/자택 IP·기존 서비스 hostname 등 실값은 서버 내 `~/class-setup/` 노트에만.
