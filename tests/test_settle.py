"""Тесты плана расчёта. Источник ожидаемых значений — docs/specs/settle-up.md."""

from __future__ import annotations

from functools import cache
from pathlib import Path

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from skinemsya.cli import main
from skinemsya.models import Group
from skinemsya.settle import EXACT_LIMIT, Transfer, settle, settle_balances
from skinemsya.storage import load_group

KARELIA = Path(__file__).parents[1] / "examples" / "karelia.json"
NAMES = ("Аня", "Боря", "Вика", "Гоша", "Дима", "Егор", "Женя")


def _net(transfers: list[Transfer], balances: dict[str, int]) -> dict[str, int]:
    """Сколько каждый получил минус отдал после применения плана."""
    net = {name: 0 for name in balances}
    for transfer in transfers:
        net[transfer.debtor] -= transfer.amount
        net[transfer.creditor] += transfer.amount
    return net


def _oracle_minimum(balances: dict[str, int]) -> int:
    """Независимый полный перебор: гасим первого должника попарно с кредиторами."""
    values = tuple(value for value in balances.values() if value)
    if not values:
        return 0

    @cache
    def search(state: tuple[int, ...]) -> int:
        i = next((index for index, value in enumerate(state) if value), None)
        if i is None:
            return 0
        best = len(state)
        for j in range(i + 1, len(state)):
            if state[i] * state[j] < 0:
                nxt = list(state)
                nxt[j] += nxt[i]
                nxt[i] = 0
                best = min(best, 1 + search(tuple(nxt)))
        return best

    return search(values)


@st.composite
def balanced_balances(draw):
    names = draw(st.lists(st.sampled_from(NAMES), min_size=0, max_size=7, unique=True))
    if not names:
        return {}
    values = draw(
        st.lists(st.integers(min_value=-6, max_value=6), min_size=len(names) - 1, max_size=len(names) - 1)
    )
    last = -sum(values)
    assume(-6 <= last <= 6)
    return dict(zip(names, [*values, last], strict=True))


# --- Сценарии из спеки ---------------------------------------------------


def test_two_people_one_transfer():
    assert settle_balances({"Аня": 50_000, "Боря": -50_000}) == [
        Transfer(debtor="Боря", creditor="Аня", amount=50_000)
    ]


def test_trio_after_one_expense():
    group = Group(name="Общага, 512")
    for name in ("Аня", "Боря", "Вика"):
        group.add_member(name)
    group.add_expense(payer="Аня", amount=900_00, description="Пицца")

    assert settle(group) == [
        Transfer(debtor="Боря", creditor="Аня", amount=30_000),
        Transfer(debtor="Вика", creditor="Аня", amount=30_000),
    ]


def test_greedy_would_need_four_transfers_but_minimum_is_three():
    balances = {
        "Аня": 60_000,
        "Боря": 40_000,
        "Вика": -40_000,
        "Гоша": -40_000,
        "Дима": -20_000,
    }
    expected = [
        Transfer(debtor="Вика", creditor="Боря", amount=40_000),
        Transfer(debtor="Гоша", creditor="Аня", amount=40_000),
        Transfer(debtor="Дима", creditor="Аня", amount=20_000),
    ]
    assert settle_balances(balances) == expected
    assert len(expected) == 3 == _oracle_minimum(balances)


def test_karelia_has_four_transfers():
    group = load_group(KARELIA)
    assert settle(group) == [
        Transfer(debtor="Гоша", creditor="Боря", amount=200_000),
        Transfer(debtor="Гоша", creditor="Вика", amount=200_000),
        Transfer(debtor="Дима", creditor="Аня", amount=400_000),
        Transfer(debtor="Егор", creditor="Аня", amount=300_000),
    ]


def test_cli_prints_settle_plan(tmp_path, capsys):
    assert main(["--file", str(KARELIA), "settle"]) == 0
    out = capsys.readouterr().out
    assert out.count("→") == 4
    assert "Гоша → Боря  2 000.00 ₽" in out
    assert "Дима → Аня  4 000.00 ₽" in out


# --- Инварианты, ошибки, границы -----------------------------------------


def test_no_transfers_for_empty_or_zero_balances():
    assert settle_balances({}) == []
    assert settle_balances({"Аня": 0, "Боря": 0}) == []


def test_unbalanced_input_is_rejected():
    with pytest.raises(ValueError, match="сход"):
        settle_balances({"Аня": 100, "Боря": 0})


def test_result_is_independent_of_mapping_order():
    balances = {"Вика": -20_000, "Аня": 50_000, "Боря": -30_000}
    assert settle_balances(balances) == settle_balances(dict(reversed(list(balances.items()))))


def test_large_group_still_settles_but_does_not_promise_minimum():
    names = [f"Участник{index:02d}" for index in range(15)]
    balances = {name: 100 for name in names[:8]}
    balances[names[8]] = -200
    balances.update({name: -100 for name in names[9:]})

    transfers = settle_balances(balances)

    assert len([value for value in balances.values() if value]) == 15 > EXACT_LIMIT
    assert 0 < len(transfers) <= 14
    assert _net(transfers, balances) == balances


# --- Property-тесты -------------------------------------------------------


@given(balanced_balances())
def test_properties_and_minimality_on_small_amounts(balances):
    transfers = settle_balances(balances)

    assert _net(transfers, balances) == balances
    assert all(transfer.amount > 0 for transfer in transfers)
    assert all(
        balances[transfer.debtor] < 0 and balances[transfer.creditor] > 0 for transfer in transfers
    )
    assert all(transfer.debtor != transfer.creditor for transfer in transfers)
    assert transfers == sorted(transfers, key=lambda t: (t.debtor, t.creditor, t.amount))
    assert len(transfers) == _oracle_minimum(balances)
