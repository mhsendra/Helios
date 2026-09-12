import pandas as pd
import pytest

from helios.core.consumption_scenario import ConsumptionScenario
from helios.core.statistics import ConsumptionStatistics


def create_series():
    index = pd.date_range(
        "2025-01-01 00:00:00",
        periods=8760,
        freq="h",
    )

    return pd.Series(1.0, index=index, name="AE_kWh")


def test_consumption_scenario_accepts_valid_hourly_series():
    series = create_series()

    scenario = ConsumptionScenario(
        hourly_consumption=series,
        reference_year=2025,
    )

    assert scenario.hourly_consumption.equals(series)
    assert scenario.reference_year == 2025
    assert scenario.annual_consumption == 8760.0


def test_consumption_scenario_requires_8760_hours():
    series = create_series().iloc[:-1]

    with pytest.raises(ValueError, match="8760"):
        ConsumptionScenario(
            hourly_consumption=series,
            reference_year=2025,
        )


def test_consumption_scenario_rejects_nan_values():
    series = create_series()
    series.iloc[100] = float("nan")

    with pytest.raises(ValueError, match="NaN"):
        ConsumptionScenario(
            hourly_consumption=series,
            reference_year=2025,
        )


def test_consumption_scenario_rejects_negative_values():
    series = create_series()
    series.iloc[100] = -1.0

    with pytest.raises(ValueError, match="negative"):
        ConsumptionScenario(
            hourly_consumption=series,
            reference_year=2025,
        )


def test_consumption_scenario_requires_datetime_index():
    series = pd.Series(range(8760))

    with pytest.raises(TypeError, match="DatetimeIndex"):
        ConsumptionScenario(
            hourly_consumption=series,
            reference_year=2025,
        )


def test_consumption_scenario_rejects_incomplete_year():
    series = create_series()
    series = series.drop(series.index[500])

    with pytest.raises(ValueError, match="8760"):
        ConsumptionScenario(series)


def test_consumption_scenario_calculates_annual_consumption():
    series = create_series()
    series.iloc[0] = 2.5

    scenario = ConsumptionScenario(
        hourly_consumption=series,
        reference_year=2025,
    )

    assert scenario.annual_consumption == 8761.5

def test_representative_year_calculation_creates_consumption_scenario():
    statistics = ConsumptionStatistics()

    index = pd.date_range(
        "2023-01-01 00:00:00",
        periods=8760,
        freq="h",
    )

    data = pd.DataFrame(
        {"AE_kWh": 1.0},
        index=index,
    )

    result = statistics.calculate_representative_year_consumption(
        data,
        reference_year=2025,
    )

    scenario = statistics.representative_consumption_scenario

    assert scenario is not None
    assert scenario.hourly_consumption is result
    assert scenario.reference_year == 2025
    assert scenario.annual_consumption == pytest.approx(result.sum())

def test_consumption_scenario_exposes_annual_consumption_from_hourly_profile():
    series = create_series()

    scenario = ConsumptionScenario(
        hourly_consumption=series,
        reference_year=2025,
    )

    assert scenario.annual_consumption == pytest.approx(series.sum())