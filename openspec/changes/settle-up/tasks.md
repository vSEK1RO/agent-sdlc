# Tasks

## 1. Спека и red-тесты

- [x] 1.1 Зафиксировать спеку в `docs/specs/settle-up.md` с тремя сценариями, инвариантами и порогом `m ≤ 14`; проверить `git show b800481` — файл есть в коммите.
- [x] 1.2 Добавить `tests/test_settle.py` с примерами из спеки, property-тестами и оракулом полного перебора; проверить `git show cf91208` и то, что red-прогон падал с `ModuleNotFoundError: skinemsya.settle`.

## 2. Решение и green-реализация

- [x] 2.1 Зафиксировать ADR-0002 с критерием `m − k`, замерами `n=10..17` и выбором гибрида; проверить `git show ca04dc8` — таблица замеров и раздел «Решение» на месте.
- [x] 2.2 Реализовать `src/skinemsya/settle.py`: точный DP до 14 ненулевых участников, жадный выше, валидация нулевой суммы; проверить `pytest tests/test_settle.py -q`.
- [x] 2.3 Добавить подкоманду `settle` в `src/skinemsya/cli.py`; проверить, что `python -m skinemsya --file examples/karelia.json settle` печатает 4 перевода из сценария 4.4.
- [x] 2.4 Держать тесты и линтер зелёными; проверить `pytest -q` (244 теста) и `ruff check .` (`All checks passed`).

## 3. Журнал процесса

- [x] 3.1 Дописать в `docs/JOURNAL.md` фейл с разграничением прав (`grep` обошёл запрет на `ASSIGNMENT.md`), причины неоптимального фикса и роль ADR-0002; проверить `git show 4198cf1`.

## 4. Интеграционная проверка

- [x] 4.1 Прогнать `openspec validate settle-up --strict` и убедиться, что proposal, spec, design и tasks согласованы.
- [x] 4.2 Проверить порядок истории: `git log --oneline` показывает `b800481 → cf91208 → ca04dc8 → 6219392 → 4198cf1`.

## Workflow follow-up

- Заархивировать change после ревью: `openspec archive settle-up`.
- Синхронизировать дельту в основные спеки: `openspec sync`.
