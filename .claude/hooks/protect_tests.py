#!/usr/bin/env python3
"""PreToolUse-хук Claude Code: запрещает правку tests/, пока существует .claude/tests.lock.

Процесс:
  1. tester пишет тесты, вы их ревьюите и коммитите (red-коммит);
  2. `touch .claude/tests.lock` — тесты заморожены;
  3. coder реализует фичу и физически не может «подогнать» тесты под код.

Exit code 2 = блокировать вызов; текст из stderr увидит агент.
Ограничение: хук ловит только инструменты Edit/Write, а не `sed -i` через Bash.
Поэтому финальная проверка всё равно в CI: scripts/check_tests_untouched.sh.
"""

import json
import sys
from pathlib import Path

event = json.load(sys.stdin)
file_path = event.get("tool_input", {}).get("file_path", "")
project = Path(event.get("cwd", "."))

if (project / ".claude" / "tests.lock").exists() and "/tests/" in f"/{Path(file_path).as_posix()}":
    print(
        f"Запрещено менять {file_path}: тесты заморожены (.claude/tests.lock). "
        "Если считаешь, что тест неверный, — остановись и объясни человеку почему.",
        file=sys.stderr,
    )
    sys.exit(2)

sys.exit(0)
