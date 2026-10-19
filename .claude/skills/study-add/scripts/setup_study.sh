#!/usr/bin/env bash
# 새 스터디 디렉토리와 다이어그램 헬퍼를 준비한다.
# 사용법: bash .claude/skills/study-add/scripts/setup_study.sh <slug>
#
# - docs/_study/<slug>/_diagrams/ 와 docs/.vuepress/public/images/study-<slug>/ 생성
# - observability 스터디의 _common.py를 복사하고 출력 경로를 study-<slug>로 바꾼다
set -euo pipefail

slug="${1:?사용법: setup_study.sh <slug>}"
root="$(git rev-parse --show-toplevel)"
src="$root/docs/_study/observability/_diagrams/_common.py"
dst_dir="$root/docs/_study/$slug/_diagrams"
img_dir="$root/docs/.vuepress/public/images/study-$slug"

[ -f "$src" ] || { echo "원본 헬퍼가 없다: $src" >&2; exit 1; }
mkdir -p "$dst_dir" "$img_dir"

if [ -f "$dst_dir/_common.py" ]; then
  echo "이미 있다(덮어쓰지 않음): $dst_dir/_common.py"
else
  sed -e "s/\"study-observability\"/\"study-$slug\"/" \
      -e "s/^\"\"\"관측성 스터디 다이어그램 공통 헬퍼/\"\"\"$slug 스터디 다이어그램 공통 헬퍼/" \
      "$src" > "$dst_dir/_common.py"
  echo "생성: $dst_dir/_common.py"
fi
grep -q "\"study-$slug\"" "$dst_dir/_common.py" && echo "출력 경로 확인: images/study-$slug"
