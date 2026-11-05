# Скинемся 💸

CLI-утилита, чтобы делить общие траты: поездка, общага, подарок одногруппнику.
Записываете, кто сколько заплатил и за кого, — утилита считает, кто в плюсе,
а кто в минусе.

> Это стартовый репозиторий практики курса «Агентно-ориентированный SDLC».
> Задание — в [ASSIGNMENT.md](ASSIGNMENT.md).

## Установка

Нужен Python 3.11+.

```bash
# вариант 1: uv
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# вариант 2: pip
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Использование

```bash
skinemsya init "Карелия-2026"
skinemsya member add Аня Боря Вика
skinemsya expense add --payer Аня --amount 1500 --desc "Продукты"
skinemsya expense add --payer Боря --amount 600 --for Боря,Вика --desc "Такси"
skinemsya expenses      # список трат
skinemsya balance       # кто в плюсе, кто в минусе
```

Готовый пример поездки на 6 человек:

```bash
skinemsya --file examples/karelia.json balance
```

## Разработка

```bash
pytest          # тесты
ruff check .    # линтер
```

## Структура

```
src/skinemsya/
  money.py      # рубли <-> копейки (деньги всегда int-копейки, см. ADR-0001)
  models.py     # Group, Expense, валидация
  split.py      # как делится одна трата между участниками
  balance.py    # балансы участников группы
  storage.py    # JSON-файл группы
  cli.py        # argparse-команды
tests/          # pytest
docs/
  adr/          # архитектурные решения (ADR)
  specs/        # спецификации фич
  issues/       # задачи: баги и фичи
  JOURNAL.md    # ваш журнал работы с агентом
examples/       # готовые данные для экспериментов
```
