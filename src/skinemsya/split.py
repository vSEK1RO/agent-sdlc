"""Как делится одна трата между участниками."""

from __future__ import annotations

from collections.abc import Sequence


def split_equally(
    amount: int,
    participants: Sequence[str],
    *,
    payer: str | None = None,
) -> dict[str, int]:
    """Делит сумму (в копейках) поровну между участниками.

    Возвращает словарь «участник -> его доля в копейках».

    Если сумма не делится нацело, остаток достаётся плательщику: он заплатил
    всю сумму, поэтому расхождение не должно оседать на нём. Если плательщика
    нет среди участников траты, остаток получает первый участник — так сумма
    долей всегда равна сумме траты.
    """
    if not participants:
        raise ValueError("Нельзя разделить трату на ноль участников")
    people = list(dict.fromkeys(participants))
    share, remainder = divmod(amount, len(people))
    shares = {person: share for person in people}
    if remainder:
        receiver = payer if payer in shares else people[0]
        shares[receiver] += remainder
    return shares
