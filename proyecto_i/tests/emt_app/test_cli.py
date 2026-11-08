
from argparse import Namespace

import pandas as pd
import pytest

from emt_app.cli import main
from emt_app.loader import EmtApiRepository


@pytest.mark.integration
def test_main(tmp_path, monkeypatch, capsys):
    output_path = tmp_path / "emt.csv"

    frame = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-01", "2026-01-01"],
        "line": ["001", "027", "027"],
        "time_slot": ["H07", "H07", "X99"],
        "passengers": ["10", "25", "5"],
    })

    monkeypatch.setattr(
        EmtApiRepository,
        "load",
        lambda self: frame,
    )

    monkeypatch.setattr(
        "emt_app.cli.parse_args",
        lambda: Namespace(
            start_date="2026-01-01",
            end_date="2026-01-02",
            output=str(output_path),
            input=None,
        ),
    )

    main()

    assert output_path.exists()

    resultado = pd.read_csv(output_path)

    assert len(resultado) == 2

    salida = capsys.readouterr().out

    assert "Registros válidos: 2 | inválidos: 1" in salida
    assert "Viajeros totales: 35" in salida
    assert "Franja con más viajeros: H07" in salida


def test_main_fichero_inexistente(tmp_path, monkeypatch, capsys):
    output_path = tmp_path / "emt.csv"

    monkeypatch.setattr(
        "emt_app.cli.parse_args",
        lambda: Namespace(
            start_date="2026-01-01",
            end_date="2026-01-02",
            output=str(output_path),
            input=str(tmp_path / "no_existe.csv"),
        ),
    )

    main()

    assert not output_path.exists()
    assert "Error" in capsys.readouterr().out
