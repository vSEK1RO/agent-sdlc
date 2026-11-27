import pytest

from skinemsya.balance import compute_balances
from skinemsya.models import DomainError, Group


@pytest.fixture
def trio() -> Group:
    group = Group(name="Общага, 512")
    for name in ["Аня", "Боря", "Вика"]:
        group.add_member(name)
    return group


def test_empty_group_has_zero_balances(trio):
    assert compute_balances(trio) == {"Аня": 0, "Боря": 0, "Вика": 0}


def test_one_expense_for_everyone(trio):
    trio.add_expense(payer="Аня", amount=900_00, description="Пицца")
    assert compute_balances(trio) == {"Аня": 600_00, "Боря": -300_00, "Вика": -300_00}


def test_expense_for_subset(trio):
    trio.add_expense(payer="Боря", amount=400_00, participants=["Боря", "Вика"])
    assert compute_balances(trio) == {"Аня": 0, "Боря": 200_00, "Вика": -200_00}


def test_balances_sum_to_zero(trio):
    trio.add_expense(payer="Аня", amount=600_00)
    trio.add_expense(payer="Боря", amount=300_00, participants=["Аня", "Боря", "Вика"])
    trio.add_expense(payer="Вика", amount=50_00, participants=["Аня", "Вика"])
    assert sum(compute_balances(trio).values()) == 0


def test_unknown_payer_rejected(trio):
    with pytest.raises(DomainError):
        trio.add_expense(payer="Гоша", amount=100)


def test_non_positive_amount_rejected(trio):
    with pytest.raises(DomainError):
        trio.add_expense(payer="Аня", amount=0)


def test_duplicate_member_rejected(trio):
    with pytest.raises(DomainError):
        trio.add_member("Аня")
