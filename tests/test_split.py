import pytest

from skinemsya.split import split_equally


def test_split_between_two():
    assert split_equally(100_00, ["Аня", "Боря"]) == {"Аня": 50_00, "Боря": 50_00}


def test_split_single_participant_pays_all():
    assert split_equally(777_77, ["Аня"]) == {"Аня": 777_77}


def test_split_requires_participants():
    with pytest.raises(ValueError):
        split_equally(100, [])
