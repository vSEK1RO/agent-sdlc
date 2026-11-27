"""Командная строка «Скинемся».

Примеры:
    skinemsya init "Карелия-2026"
    skinemsya member add Аня
    skinemsya expense add --payer Аня --amount 1200 --desc "Продукты"
    skinemsya expense add --payer Боря --amount 600 --for Боря,Гоша,Дима --desc "Баня"
    skinemsya expenses
    skinemsya balance
    skinemsya settle
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .balance import compute_balances
from .models import DomainError, Group
from .money import format_rub, parse_rub
from .settle import settle
from .storage import DEFAULT_FILE, load_group, save_group


def _cmd_init(args: argparse.Namespace) -> int:
    if args.file.exists() and not args.force:
        print(f"Файл {args.file} уже существует. Используйте --force, чтобы перезаписать.")
        return 1
    save_group(Group(name=args.name), args.file)
    print(f"Создана группа «{args.name}» ({args.file})")
    return 0


def _cmd_member_add(args: argparse.Namespace) -> int:
    group = load_group(args.file)
    for name in args.names:
        group.add_member(name)
    save_group(group, args.file)
    print(f"Участники: {', '.join(group.members)}")
    return 0


def _cmd_expense_add(args: argparse.Namespace) -> int:
    group = load_group(args.file)
    participants = [p.strip() for p in args.for_.split(",")] if args.for_ else None
    expense = group.add_expense(
        payer=args.payer,
        amount=parse_rub(args.amount),
        participants=participants,
        description=args.desc,
    )
    save_group(group, args.file)
    print(
        f"#{expense.id} {expense.payer} заплатил(а) {format_rub(expense.amount)}"
        f" за {', '.join(expense.participants)}"
        + (f" — {expense.description}" if expense.description else "")
    )
    return 0


def _cmd_expenses(args: argparse.Namespace) -> int:
    group = load_group(args.file)
    if not group.expenses:
        print("Трат пока нет.")
        return 0
    for e in group.expenses:
        desc = f" — {e.description}" if e.description else ""
        print(f"#{e.id:<3} {e.payer:<10} {format_rub(e.amount):>14}  [{', '.join(e.participants)}]{desc}")
    return 0


def _cmd_balance(args: argparse.Namespace) -> int:
    group = load_group(args.file)
    balances = compute_balances(group)
    width = max((len(m) for m in balances), default=0)
    for member, value in sorted(balances.items(), key=lambda kv: (-kv[1], kv[0])):
        hint = "ему(ей) должны" if value > 0 else ("должен(на)" if value < 0 else "в расчёте")
        print(f"{member:<{width}}  {format_rub(value):>14}  {hint}")
    return 0


def _cmd_settle(args: argparse.Namespace) -> int:
    transfers = settle(load_group(args.file))
    if not transfers:
        print("Переводы не нужны.")
        return 0
    for transfer in transfers:
        print(f"{transfer.debtor} → {transfer.creditor}  {format_rub(transfer.amount)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skinemsya", description="Делим общие траты без боли.")
    parser.add_argument(
        "--file", type=Path, default=DEFAULT_FILE, help="JSON-файл группы (по умолчанию %(default)s)"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="создать группу")
    p_init.add_argument("name")
    p_init.add_argument("--force", action="store_true")
    p_init.set_defaults(func=_cmd_init)

    p_member = sub.add_parser("member", help="участники группы")
    member_sub = p_member.add_subparsers(dest="member_command", required=True)
    p_member_add = member_sub.add_parser("add", help="добавить участников")
    p_member_add.add_argument("names", nargs="+")
    p_member_add.set_defaults(func=_cmd_member_add)

    p_expense = sub.add_parser("expense", help="траты")
    expense_sub = p_expense.add_subparsers(dest="expense_command", required=True)
    p_expense_add = expense_sub.add_parser("add", help="добавить трату")
    p_expense_add.add_argument("--payer", required=True, help="кто заплатил")
    p_expense_add.add_argument("--amount", required=True, help="сумма в рублях: 1500 или 1500.50")
    p_expense_add.add_argument(
        "--for", dest="for_", help="за кого, через запятую (по умолчанию — за всех)"
    )
    p_expense_add.add_argument("--desc", default="", help="описание")
    p_expense_add.set_defaults(func=_cmd_expense_add)

    p_expenses = sub.add_parser("expenses", help="список трат")
    p_expenses.set_defaults(func=_cmd_expenses)

    p_balance = sub.add_parser("balance", help="кто кому сколько должен (балансы)")
    p_balance.set_defaults(func=_cmd_balance)

    p_settle = sub.add_parser("settle", help="план переводов: кто кому сколько переводит")
    p_settle.set_defaults(func=_cmd_settle)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (DomainError, FileNotFoundError, ValueError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
