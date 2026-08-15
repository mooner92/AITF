# 030 — P2: 접속 경로·보안 잠금

**상태**: Draft · 차단: 학원 고정 IP 확인, 도메인 결정

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

## 작업 체크리스트

- [ ] 선행: 학원 네트워크에서 `curl ifconfig.me` → 고정 IP 여부 확인 (운영자)
- [ ] 도메인 결정 (운영자)
- [ ] config.yml ingress 추가 → `sudo systemctl restart cloudflared` → **기존 터널 hostname 정상 동작 회귀 확인**
- [ ] DNS 라우팅 3건 + Access 앱 2건 + 브라우저 렌더링 ON
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
