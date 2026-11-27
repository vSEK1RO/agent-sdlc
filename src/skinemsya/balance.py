"""Подсчёт балансов участников группы."""

from __future__ import annotations

from .models import Group
from .split import split_equally


def compute_balances(group: Group) -> dict[str, int]:
    """Возвращает баланс каждого участника в копейках.

    Баланс > 0 — группа должна этому человеку.
    Баланс < 0 — этот человек должен группе.
    Инвариант: сумма всех балансов равна нулю.
    """
    balances = {member: 0 for member in group.members}
    for expense in group.expenses:
        balances[expense.payer] += expense.amount
        for person, share in split_equally(expense.amount, expense.participants).items():
            balances[person] -= share
    return balances
