import pandas as pd
import pytest

from helios.ev.scenario import EVScenario


def create_series():
    index = pd.date_range(
        "2025-01-01 00:00:00",
        periods=8760,
        freq="h",
    )

    return pd.Series(1.0, index=index, name="EV_kWh")


def test_ev_scenario_accepts_valid_hourly_series():
    series = create_series()

    scenario = EVScenario(
        hourly_consumption=series,
        reference_year=2025,
    )

    assert scenario.hourly_consumption.equals(series)
    assert scenario.reference_year == 2025
    assert scenario.annual_consumption == 8760.0


def test_ev_scenario_requires_8760_hours():
    series = create_series().iloc[:-1]

    with pytest.raises(ValueError, match="8760"):
        EVScenario(
            hourly_consumption=series,
            reference_year=2025,
        )


def test_ev_scenario_rejects_nan_values():
    series = create_series()
    series.iloc[100] = float("nan")

    with pytest.raises(ValueError, match="NaN"):
        EVScenario(
            hourly_consumption=series,
            reference_year=2025,
        )


def test_ev_scenario_rejects_negative_values():
    series = create_series()
    series.iloc[100] = -1.0

    with pytest.raises(ValueError, match="negative"):
        EVScenario(
            hourly_consumption=series,
            reference_year=2025,
        )


def test_ev_scenario_requires_datetime_index():
    series = pd.Series(range(8760))

    with pytest.raises(TypeError, match="DatetimeIndex"):
        EVScenario(
            hourly_consumption=series,
            reference_year=2025,
        )


def test_ev_scenario_rejects_incomplete_year():
    series = create_series()
    series = series.drop(series.index[500])

    with pytest.raises(ValueError, match="8760"):
        EVScenario(series)


def test_ev_scenario_calculates_annual_consumption():
    series = create_series()
    series.iloc[0] = 2.5

    scenario = EVScenario(
        hourly_consumption=series,
        reference_year=2025,
    )

    assert scenario.annual_consumption == 8761.5


def test_ev_scenario_accepts_bissextile_reference_year_without_february_29():
    index = pd.date_range(
        "2024-01-01 00:00:00",
        "2024-12-31 23:00:00",
        freq="h",
    )

    index = index[
        ~(
            (index.month == 2)
            & (index.day == 29)
        )
    ]

    series = pd.Series(1.0, index=index)

    scenario = EVScenario(
        hourly_consumption=series,
        reference_year=2024,
    )

    assert len(scenario.hourly_consumption) == 8760
    assert scenario.hourly_consumption.index[0] == pd.Timestamp(
        "2024-01-01 00:00:00"
    )
    assert scenario.hourly_consumption.index[-1] == pd.Timestamp(
        "2024-12-31 23:00:00"
    )


def test_ev_scenario_bissextile_reference_year_excludes_february_29():
    index = pd.date_range(
        "2024-01-01 00:00:00",
        "2024-12-31 23:00:00",
        freq="h",
    )

    index = index[
        ~(
            (index.month == 2)
            & (index.day == 29)
        )
    ]

    series = pd.Series(1.0, index=index)

    scenario = EVScenario(
        hourly_consumption=series,
        reference_year=2024,
    )

    assert len(scenario.hourly_consumption) == 8760
    assert not (
        (scenario.hourly_consumption.index.month == 2)
        & (scenario.hourly_consumption.index.day == 29)
    ).any()

    assert pd.Timestamp("2024-02-28 23:00:00") in (
        scenario.hourly_consumption.index
    )

    assert pd.Timestamp("2024-03-01 00:00:00") in (
        scenario.hourly_consumption.index
    )