import sys

import pandas as pd

from ventas_app.cli import main


def test_main(tmp_path, monkeypatch, capsys):
    input_path = tmp_path / "entrada.csv"
    output_path = tmp_path / "salida.csv"

    input_path.write_text(
        "region,producto,unidades,precio_unitario\n"
        "Norte,A,2,10\n"
        "Sur,B,0,20\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "ventas_app",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        ],
    )

    main()

    assert output_path.exists()

    resultado = pd.read_csv(output_path)

    assert len(resultado) == 1
    assert resultado["region"].iloc[0] == "Norte"

    salida = capsys.readouterr().out

    assert "Registros válidos: 1" in salida
    assert "inválidos: 1" in salida
    assert "Norte: 20.00" in salida
