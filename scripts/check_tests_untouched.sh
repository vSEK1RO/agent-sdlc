#!/usr/bin/env bash
# Проверяет TDD-порядок в ветке относительно base:
#   1) есть red-коммит (сообщение начинается с "test(" и содержит "red");
#   2) до первого red-коммита ветка не меняла src/ (реализация не раньше тестов);
#   3) после последнего red-коммита не менялись tests/ (тесты не подгоняли под код).
# Использование: scripts/check_tests_untouched.sh [base-ref]   (по умолчанию origin/main)
set -euo pipefail

base="${1:-origin/main}"
reds=$(git log --format=%H -i --grep='^test(.*red' "$base"..HEAD)

if [[ -z "$reds" ]]; then
  echo "❌ Не найден red-коммит (сообщение вида 'test(settle): red — ...'). TDD-порядок не подтверждён."
  exit 1
fi

first_red=$(echo "$reds" | tail -n 1)
last_red=$(echo "$reds" | head -n 1)
status=0

early_src=$(git log --format='%h %s' "$base".."$first_red"^ -- src/ || true)
if [[ -n "$early_src" ]]; then
  echo "❌ Реализация появилась раньше первого red-коммита ${first_red:0:7}:"
  echo "$early_src"
  status=1
fi

changed=$(git diff --name-only "$last_red"..HEAD -- tests/ || true)
if [[ -n "$changed" ]]; then
  echo "⚠️  После последнего red-коммита ${last_red:0:7} изменены тесты:"
  echo "$changed"
  echo "Это допустимо только с объяснением в описании PR."
  status=1
fi

if [[ $status -eq 0 ]]; then
  echo "✅ TDD-порядок соблюдён: red ${first_red:0:7} раньше реализации, тесты не менялись после ${last_red:0:7}"
fi
exit $status
