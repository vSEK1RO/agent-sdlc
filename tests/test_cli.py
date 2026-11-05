"""Смоук-тесты CLI: команды работают от начала до конца на временном файле."""

from skinemsya.cli import main


def run(tmp_path, *args):
    return main(["--file", str(tmp_path / "group.json"), *args])


def test_full_flow(tmp_path, capsys):
    assert run(tmp_path, "init", "Карелия") == 0
    assert run(tmp_path, "member", "add", "Аня", "Боря", "Вика") == 0
    assert run(tmp_path, "expense", "add", "--payer", "Аня", "--amount", "900", "--desc", "Пицца") == 0
    assert run(tmp_path, "expense", "add", "--payer", "Боря", "--amount", "100", "--for", "Боря,Вика") == 0
    capsys.readouterr()

    assert run(tmp_path, "balance") == 0
    out = capsys.readouterr().out
    assert "Аня" in out and "600.00 ₽" in out
    assert "Вика" in out and "-350.00 ₽" in out


def test_error_is_reported_not_raised(tmp_path, capsys):
    run(tmp_path, "init", "Карелия")
    run(tmp_path, "member", "add", "Аня")
    assert run(tmp_path, "expense", "add", "--payer", "Гоша", "--amount", "100") == 2
    assert "Ошибка" in capsys.readouterr().err


def test_missing_file_is_friendly(tmp_path, capsys):
    assert run(tmp_path, "balance") == 2
    assert "skinemsya init" in capsys.readouterr().err
