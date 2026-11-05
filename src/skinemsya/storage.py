"""Хранение группы в JSON-файле."""

from __future__ import annotations

import json
from pathlib import Path

from .models import Expense, Group

DEFAULT_FILE = Path(".skinemsya.json")


def save_group(group: Group, path: Path = DEFAULT_FILE) -> None:
    data = {
        "name": group.name,
        "members": group.members,
        "expenses": [
            {
                "id": e.id,
                "payer": e.payer,
                "amount": e.amount,
                "participants": list(e.participants),
                "description": e.description,
                "created_at": e.created_at,
            }
            for e in group.expenses
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_group(path: Path = DEFAULT_FILE) -> Group:
    if not path.exists():
        raise FileNotFoundError(
            f"Файл группы {path} не найден. Создайте группу: skinemsya init <название>"
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    return Group(
        name=data["name"],
        members=list(data["members"]),
        expenses=[
            Expense(
                id=e["id"],
                payer=e["payer"],
                amount=e["amount"],
                participants=tuple(e["participants"]),
                description=e.get("description", ""),
                created_at=e.get("created_at", ""),
            )
            for e in data["expenses"]
        ],
    )
