# 020 — P1: OS 기본 세팅

**상태**: In Progress (대부분 완료, 잔여 소량) · 2026-08-16

## 목표

수업 인프라가 올라갈 OS 기반: 필수 패키지, swap, 수업 편의 설정(tmux 마우스), 디렉토리 골격과 권한.

## 완료 확인됨

- Claude Code CLI 설치·인증 (운영자 계정), 운영자 홈 700 권한
- swap 5GB (fstab 등록) / Node.js v22 / git·tmux·rsync·jq·htop용 EPEL·SELinux 도구
- 타임존 Asia/Seoul / SELinux **Enforcing** 유지

## 작업 체크리스트 (잔여)

- [ ] `sudo dnf -y install htop`
- [ ] 전체 업데이트는 **보류** — 기존 서비스 재시작 위험. 백업(010) 후 보안 업데이트만: `sudo dnf -y update --security` → 직후 서비스 헬스 확인
- [ ] tmux 전역 설정 — **마우스 모드는 넣지 않는다** (키보드 사용법을 수업에서 직접 가르치기로 결정). 스크롤 버퍼만 넉넉히:
  ```bash
  echo 'set -g history-limit 10000' | sudo tee /etc/tmux.conf
  ```
  → 대신 tmux 키보드 치트시트를 수업 자료로 준비 ([090](090-materials.md))
- [ ] 디렉토리 골격 + 권한:
  ```bash
  sudo mkdir -p /opt/scripts /opt/harness /opt/template-home /srv/snapshots /srv/backup /var/lib/tokmon
  sudo chmod 700 /opt/scripts /srv/snapshots /srv/backup /var/lib/tokmon
  # 700 이유: 계정 CSV·스냅샷 속 타 학생 파일·토큰 집계를 학생이 읽지 못하게 (원칙 3)
  ```

## 검증 기준

- [ ] `htop` 동작 / `tmux` 새 세션에서 마우스 스크롤 동작
- [ ] `ls -ld /opt/scripts /srv/snapshots /srv/backup /var/lib/tokmon` → 700 root
- [ ] `getenforce` → Enforcing 유지
- [ ] 기존 운영 서비스 정상

## 결정 기록

- 2026-08-16 · `dnf update` 전체 실행을 선택 사항으로 강등 — 공용 서버에서 서비스 재시작 리스크 > 이득. 보안 패치만 적용.
