import pandas as pd

from ventas_app.metrics import total_by_region


def test_total_by_region():
    frame = pd.DataFrame({
        "region": ["Norte", "Sur", "Norte"],
        "producto": ["A", "B", "C"],
        "unidades": [2, 4, 3],
        "precio_unitario": [10, 5, 20],
    })

    totals = total_by_region(frame)

    assert totals["Norte"] == 80
    assert totals["Sur"] == 20
    assert list(totals.index) == ["Norte", "Sur"]
