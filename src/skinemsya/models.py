"""Доменные модели: группа, участники, траты."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


class DomainError(ValueError):
    """Ошибка предметной области: неверные данные от пользователя."""


@dataclass(frozen=True)
class Expense:
    """Трата: кто заплатил, сколько (в копейках) и за кого."""

    id: int
    payer: str
    amount: int
    participants: tuple[str, ...]
    description: str = ""
    created_at: str = ""


@dataclass
class Group:
    """Группа людей, которые скидываются: поездка, общага, подарок."""

    name: str
    members: list[str] = field(default_factory=list)
    expenses: list[Expense] = field(default_factory=list)

    def add_member(self, name: str) -> None:
        name = name.strip()
        if not name:
            raise DomainError("Имя участника не может быть пустым")
        if name in self.members:
            raise DomainError(f"Участник {name!r} уже есть в группе")
        self.members.append(name)

    def add_expense(
        self,
        payer: str,
        amount: int,
        participants: list[str] | None = None,
        description: str = "",
    ) -> Expense:
        """Добавляет трату. Если participants не указаны — делим на всех."""
        if payer not in self.members:
            raise DomainError(f"Плательщик {payer!r} не состоит в группе")
        if amount <= 0:
            raise DomainError("Сумма траты должна быть положительной")
        people = tuple(participants) if participants else tuple(self.members)
        unknown = [p for p in people if p not in self.members]
        if unknown:
            raise DomainError(f"Неизвестные участники: {', '.join(unknown)}")
        if len(set(people)) != len(people):
            raise DomainError("Участники траты не должны повторяться")

        expense = Expense(
            id=len(self.expenses) + 1,
            payer=payer,
            amount=amount,
            participants=people,
            description=description,
            created_at=datetime.now().isoformat(timespec="seconds"),
        )
        self.expenses.append(expense)
        return expense
