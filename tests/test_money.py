import pytest

from skinemsya.money import format_rub, parse_rub


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("350", 35000),
        ("350.5", 35050),
        ("350,05", 35005),
        ("0.01", 1),
        (" 1200 ₽ ", 120000),
        ("99 руб.", 9900),
    ],
)
def test_parse_rub(text, expected):
    assert parse_rub(text) == expected


@pytest.mark.parametrize("bad", ["", "abc", "-5", "1.234", "1 000"])
def test_parse_rub_rejects_garbage(bad):
    with pytest.raises(ValueError):
        parse_rub(bad)


@pytest.mark.parametrize(
    ("kopecks", "expected"),
    [
        (0, "0.00 ₽"),
        (1, "0.01 ₽"),
        (35050, "350.50 ₽"),
        (123456789, "1 234 567.89 ₽"),
        (-70000, "-700.00 ₽"),
    ],
)
def test_format_rub(kopecks, expected):
    assert format_rub(kopecks) == expected
