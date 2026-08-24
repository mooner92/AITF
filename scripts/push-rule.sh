#!/bin/bash
# 규칙 문서를 학생 저장소 rules/ 에 배포 — specs/060 (모노레포)
#
# 심링크가 아니라 복사다. 이유:
#   - 배포 즉시 작업 트리에 실파일로 나타나 Codex 가 바로 읽는다
#   - 학생의 다음 `git add .` 에 자연히 포함돼 자기 히스토리가 된다
#   - 수료 후 GitHub 이전 때 문서가 함께 간다 (심링크는 깨진다)
# 같은 이름 재배포는 덮어쓴다 — 규칙 문서는 강사 소유 (문서 머리말에 명시).
#
# 사용:
#   push-rule.sh naming            # materials/rules/naming.md → 전 학생
#   push-rule.sh sdd make_sdd      # 여러 개
#   push-rule.sh --sync            # /opt/harness/rules 전체 재배포 (리셋 복구)
#   push-rule.sh --sync ⟪계정⟫      # 한 계정만
#   push-rule.sh --list
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$REPO/materials/rules"
STORE=/opt/harness/rules
ROSTER=/opt/scripts/roster.csv

accounts() {  # roster 학생 + 테스트 계정 (실존하는 것만)
  { [ -f "$ROSTER" ] && awk -F, 'NR>1 && $2!="" {print $2}' "$ROSTER"
    for h in /home/test* /home/bash* /home/demo*; do [ -d "$h" ] && basename "$h"; done
  } | sort -u | while read -r u; do id -u "$u" >/dev/null 2>&1 && echo "$u"; done
}

deliver() {  # deliver <계정> <파일>...
  local u="$1"; shift
  local proj="/home/$u/project"
  [ -d "$proj" ] || { echo "  · $u (project 없음 — 건너뜀)"; return; }
  install -d -o "$u" -g "$u" -m 755 "$proj/rules"
  for f in "$@"; do
    install -o "$u" -g "$u" -m 644 "$f" "$proj/rules/$(basename "$f")"
  done
  # 저장소 README 는 없을 때만 만든다 (학생이 고쳤을 수 있음)
  if [ ! -f "$proj/README.md" ] && [ -f "$STORE/_repo-README.md" ]; then
    install -o "$u" -g "$u" -m 644 "$STORE/_repo-README.md" "$proj/README.md"
  fi
  echo "  ✓ $u"
}

case "${1:-}" in
  --list)
    echo "── 배포 가능 (materials/rules/) ──"
    ls "$SRC"/*.md 2>/dev/null | grep -v README.md | xargs -n1 basename 2>/dev/null || echo "(없음)"
    echo "── 배포됨 (/opt/harness/rules/) ──"
    ls "$STORE" 2>/dev/null | grep -v '^_' || echo "(없음)"
    exit 0 ;;

  --sync)
    shift
    files=("$STORE"/*.md)
    real=(); for f in "${files[@]}"; do case "$(basename "$f")" in _*) ;; *) [ -f "$f" ] && real+=("$f") ;; esac; done
    [ ${#real[@]} -gt 0 ] || { echo "배포된 규칙 없음"; exit 0; }
    targets="${1:-}"
    echo "재배포: $(printf '%s ' "${real[@]##*/}")"
    if [ -n "$targets" ]; then deliver "$targets" "${real[@]}"
    else for u in $(accounts); do deliver "$u" "${real[@]}"; done; fi
    exit 0 ;;

  "" )
    echo "사용: push-rule.sh <규칙이름>... | --sync [계정] | --list"; exit 1 ;;
esac

# ── 이름으로 배포 ──
install -d -m 755 "$STORE"
# 저장소 README 템플릿도 보관소에 항상 최신으로
[ -f "$REPO/materials/student-repo/README.md" ] && \
  install -m 644 "$REPO/materials/student-repo/README.md" "$STORE/_repo-README.md"

files=()
for name in "$@"; do
  f="$SRC/${name%.md}.md"
  [ -f "$f" ] || { echo "없는 규칙: $name (materials/rules/ 확인)"; exit 1; }
  [ "$(basename "$f")" = "README.md" ] && { echo "README.md 는 내부 문서 — 배포 불가"; exit 1; }
  install -m 644 "$f" "$STORE/$(basename "$f")"
  files+=("$STORE/$(basename "$f")")
done

echo "배포: $(printf '%s ' "${files[@]##*/}")"
for u in $(accounts); do deliver "$u" "${files[@]}"; done
echo "완료. 학생 화면에서는: ls rules/ → 새 문서 발견 → 열어보기 → 다음 커밋에 포함"
