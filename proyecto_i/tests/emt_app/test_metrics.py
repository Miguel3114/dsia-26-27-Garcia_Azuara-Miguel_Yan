
import pandas as pd
import pytest

from emt_app.metrics import (
    average_passengers,
    passengers_by_line,
    peak_time_slot,
    total_passengers,
)


@pytest.fixture
def emt_mini():
    return pd.DataFrame({
        "line": ["001", "001", "027", "027"],
        "time_slot": ["H07", "H08", "H07", "H08"],
        "passengers": [10, 30, 20, 40],
    })


def test_total_passengers(emt_mini):
    assert total_passengers(emt_mini) == 100


def test_average_passengers(emt_mini):
    assert average_passengers(emt_mini) == 25


def test_passengers_by_line(emt_mini):
    totals = passengers_by_line(emt_mini)

    assert totals.index[0] == "027"
    assert totals["027"] == 60
    assert totals["001"] == 40


def test_peak_time_slot(emt_mini):
    assert peak_time_slot(emt_mini) == "H08"
