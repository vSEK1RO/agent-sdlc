"""План расчёта: кто кому сколько переводит.

Алгоритм и порог описаны в docs/specs/settle-up.md и docs/adr/0002-settle-algorithm.md.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .balance import compute_balances
from .models import Group

# Число участников с ненулевым балансом, до которого гарантирован минимум переводов.
EXACT_LIMIT = 14


@dataclass(frozen=True)
class Transfer:
    """Один перевод: должник отправляет кредитору amount копеек."""

    debtor: str
    creditor: str
    amount: int


def settle_balances(balances: Mapping[str, int]) -> list[Transfer]:
    """Строит план переводов по балансам в копейках.

    При `m <= EXACT_LIMIT` число переводов минимально. При `m > EXACT_LIMIT`
    план корректный, но минимальность не гарантируется (см. ADR-0002).
    """
    total = sum(balances.values())
    if total != 0:
        raise ValueError(f"Балансы не сходятся: сумма {total} копеек")

    items = sorted((name, value) for name, value in balances.items() if value)
    names = [name for name, _ in items]
    values = [value for _, value in items]
    if not values:
        return []

    if len(values) <= EXACT_LIMIT:
        groups = _exact_groups(values)
        return _match_by_groups(names, values, groups)
    return _greedy_plan(names, values)


def settle(group: Group) -> list[Transfer]:
    """Строит план переводов для группы."""
    return settle_balances(compute_balances(group))


def _exact_groups(values: list[int]) -> tuple[tuple[int, ...], ...]:
    """Возвращает разбиение на подгруппы с нулевой суммой с максимумом групп.

    Чем больше таких групп, тем меньше переводов: группа из k человек
    рассчитывается k - 1 переводами. Перебору подвергаются только
    подмножества, сумма которых равна нулю.
    """
    count = len(values)
    full = 1 << count

    sums = [0] * full
    for mask in range(1, full):
        low = mask & -mask
        index = low.bit_length() - 1
        sums[mask] = sums[mask ^ low] + values[index]

    # best[mask] — разбиение mask на подгруппы с нулевой суммой.
    best: list[tuple[int, ...] | None] = [None] * full
    best[0] = ()
    for mask in range(1, full):
        if sums[mask] == 0:
            best[mask] = (mask,)
        low = mask & -mask
        submask = mask
        while submask:
            if submask & low and sums[submask] == 0:
                left, right = best[submask], best[mask ^ submask]
                if left is not None and right is not None:
                    candidate = left + right
                    if best[mask] is None or len(candidate) > len(best[mask]):
                        best[mask] = candidate
            submask = (submask - 1) & mask

    groups = best[full - 1]
    if groups is None:  # sum(values) == 0, поэтому такой ситуации быть не должно.
        raise ValueError("Не удалось построить план переводов")
    return groups


def _match(
    debtors: list[tuple[str, int]],
    creditors: list[tuple[str, int]],
) -> list[Transfer]:
    """Попарно гасит должников и кредиторов, пока кто-то не закончится."""
    transfers: list[Transfer] = []
    debtor_index = creditor_index = 0
    while debtor_index < len(debtors) and creditor_index < len(creditors):
        debtor, debt = debtors[debtor_index]
        creditor, credit = creditors[creditor_index]
        amount = min(debt, credit)
        transfers.append(Transfer(debtor, creditor, amount))
        debtors[debtor_index] = (debtor, debt - amount)
        creditors[creditor_index] = (creditor, credit - amount)
        if debt == amount:
            debtor_index += 1
        if credit == amount:
            creditor_index += 1
    return transfers


def _match_by_groups(
    names: list[str],
    values: list[int],
    groups: tuple[tuple[int, ...], ...],
) -> list[Transfer]:
    """Гасит участников внутри каждой подгруппы с нулевой суммой."""
    transfers: list[Transfer] = []
    for group in groups:
        debtors = sorted(
            (names[index], -values[index])
            for index in range(len(values))
            if (group >> index) & 1 and values[index] < 0
        )
        creditors = sorted(
            (names[index], values[index])
            for index in range(len(values))
            if (group >> index) & 1 and values[index] > 0
        )
        transfers.extend(_match(debtors, creditors))
    return sorted(transfers, key=lambda transfer: (transfer.debtor, transfer.creditor, transfer.amount))


def _greedy_plan(names: list[str], values: list[int]) -> list[Transfer]:
    """Жадный план для больших групп: сначала гасим самые крупные суммы."""
    debtors = sorted(
        ((names[index], -values[index]) for index, value in enumerate(values) if value < 0),
        key=lambda item: (-item[1], item[0]),
    )
    creditors = sorted(
        ((names[index], values[index]) for index, value in enumerate(values) if value > 0),
        key=lambda item: (-item[1], item[0]),
    )
    return sorted(_match(debtors, creditors), key=lambda t: (t.debtor, t.creditor, t.amount))
