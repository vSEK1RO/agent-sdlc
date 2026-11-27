"""Как делится одна трата между участниками."""

from __future__ import annotations

from collections.abc import Sequence


def split_equally(amount: int, participants: Sequence[str]) -> dict[str, int]:
    """Делит сумму (в копейках) поровну между участниками.

    Возвращает словарь «участник -> его доля в копейках».
    """
    if not participants:
        raise ValueError("Нельзя разделить трату на ноль участников")
    share = amount // len(participants)
    return {person: share for person in participants}
