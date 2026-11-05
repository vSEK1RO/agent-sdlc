"""Работа с деньгами.

Все суммы внутри приложения — целые копейки (int).
Почему так — см. docs/adr/0001-money-in-kopecks.md.
"""

from __future__ import annotations

import re

_MONEY_RE = re.compile(r"^\s*(\d+)(?:[.,](\d{1,2}))?\s*(?:₽|руб\.?|р\.?)?\s*$", re.IGNORECASE)


def parse_rub(text: str) -> int:
    """Разбирает строку с суммой в рублях и возвращает копейки.

    >>> parse_rub("350")
    35000
    >>> parse_rub("350.5")
    35050
    >>> parse_rub("350,05 ₽")
    35005
    """
    match = _MONEY_RE.match(text)
    if match is None:
        raise ValueError(f"Не могу разобрать сумму: {text!r}")
    rub, kop = match.groups()
    kop = (kop or "0").ljust(2, "0")
    return int(rub) * 100 + int(kop)


def format_rub(kopecks: int) -> str:
    """Форматирует копейки как рубли: 123450 -> '1 234.50 ₽'."""
    sign = "-" if kopecks < 0 else ""
    rub, kop = divmod(abs(kopecks), 100)
    rub_str = f"{rub:,}".replace(",", " ")
    return f"{sign}{rub_str}.{kop:02d} ₽"
