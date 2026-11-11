import pytest

from skinemsya.split import split_equally


def test_split_between_two():
    assert split_equally(100_00, ["Аня", "Боря"]) == {"Аня": 50_00, "Боря": 50_00}


def test_split_single_participant_pays_all():
    assert split_equally(777_77, ["Аня"]) == {"Аня": 777_77}


def test_split_requires_participants():
    with pytest.raises(ValueError):
        split_equally(100, [])


def test_remainder_goes_to_payer():
    shares = split_equally(100_00, ["Аня", "Боря", "Вика"], payer="Аня")
    assert shares == {"Аня": 33_34, "Боря": 33_33, "Вика": 33_33}


def test_remainder_goes_to_payer_not_first_participant():
    shares = split_equally(100_00, ["Аня", "Боря", "Вика"], payer="Вика")
    assert shares == {"Аня": 33_33, "Боря": 33_33, "Вика": 33_34}


def test_remainder_falls_back_to_first_participant_when_payer_not_in_split():
    shares = split_equally(101, ["Боря", "Вика"], payer="Аня")
    assert shares == {"Боря": 51, "Вика": 50}


@pytest.mark.parametrize("amount", range(1, 200))
def test_shares_always_sum_to_amount(amount):
    participants = ["Аня", "Боря", "Вика"]
    shares = split_equally(amount, participants, payer="Боря")
    assert sum(shares.values()) == amount
    share, remainder = divmod(amount, len(participants))
    assert shares["Боря"] == share + remainder
    assert shares["Аня"] == shares["Вика"] == share
