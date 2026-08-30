import pandas as pd
import pytest

from helios.core.indicators import IndicatorsEngine


# ==========================================================
# Helpers
# ==========================================================

def create_engine():

    return IndicatorsEngine()


def create_dataset():

    index = pd.date_range(
        "2025-01-01 00:00",
        periods=8,
        freq="6h"
    )

    return pd.DataFrame(
        {
            "AE_kWh": [
                1.0,
                2.0,
                3.0,
                4.0,
                5.0,
                6.0,
                7.0,
                8.0,
            ]
        },
        index=index
    )


# ==========================================================
# Estado inicial
# ==========================================================

def test_initial_state():

    engine = create_engine()

    assert engine.dataset is None
    assert engine.statistics is None
    assert engine.comparisons is None

    assert engine.mean_consumption is None
    assert engine.extremes is None
    assert engine.base_load is None


# ==========================================================
# Mean consumption
# ==========================================================

def test_calculate_mean_consumption():

    engine = create_engine()

    df = create_dataset()

    result = engine.calculate_mean_consumption(df)

    assert result is engine.mean_consumption

    assert set(result.keys()) == {
        "hourly",
        "daily",
        "weekly",
        "monthly",
        "yearly",
        "workday",
        "weekend",
    }

    assert result["hourly"] == pytest.approx(4.5)

    assert result["daily"] == pytest.approx(18.0)

    assert result["weekly"] == pytest.approx(36.0)

    assert result["monthly"] == pytest.approx(36.0)

    assert result["yearly"] == pytest.approx(36.0)

    assert result["workday"] == pytest.approx(18.0)


def test_calculate_mean_consumption_weekend():

    engine = create_engine()

    index = pd.date_range(
        "2025-01-04 00:00",
        periods=4,
        freq="6h"
    )

    df = pd.DataFrame(
        {
            "AE_kWh": [
                10.0,
                20.0,
                30.0,
                40.0,
            ]
        },
        index=index
    )

    result = engine.calculate_mean_consumption(df)

    assert result["weekend"] == pytest.approx(100.0)


# ==========================================================
# Extremes
# ==========================================================

def test_calculate_extremes():

    engine = create_engine()

    dataset = create_dataset()

    daily = pd.Series(
        [10.0, 20.0],
        index=pd.to_datetime(
            [
                "2025-01-01",
                "2025-01-02",
            ]
        )
    )

    monthly = pd.Series(
        [100.0, 200.0],
        index=pd.to_datetime(
            [
                "2025-01-31",
                "2025-02-28",
            ]
        )
    )

    weekly = pd.DataFrame(
        {
            2024: [50.0, 60.0],
            2025: [70.0, 80.0],
        },
        index=["S01", "S02"]
    )

    result = engine.calculate_extremes(
        dataset,
        daily,
        monthly,
        weekly
    )

    assert result is engine.extremes

    assert result["hourly_max"] == (
        pd.Timestamp("2025-01-02 18:00"),
        8.0
    )

    assert result["hourly_min"] == (
        pd.Timestamp("2025-01-01 00:00"),
        1.0
    )

    assert result["daily_max"] == (
        pd.Timestamp("2025-01-02"),
        20.0
    )

    assert result["daily_min"] == (
        pd.Timestamp("2025-01-01"),
        10.0
    )

    assert result["weekly_max"] == (
        ("S02", 2025),
        80.0
    )

    assert result["weekly_min"] == (
        ("S01", 2024),
        50.0
    )

    assert result["monthly_max"] == (
        pd.Timestamp("2025-02-28"),
        200.0
    )

    assert result["monthly_min"] == (
        pd.Timestamp("2025-01-31"),
        100.0
    )


# ==========================================================
# Base load
# ==========================================================

def test_calculate_base_load():

    engine = create_engine()

    df = create_dataset()

    result = engine.calculate_base_load(df)

    assert result is engine.base_load

    assert result == pytest.approx(
        df["AE_kWh"].quantile(0.10)
    )

def test_calculate_extremes_empty():

    engine = create_engine()

    dataset = pd.DataFrame(
        {
            "AE_kWh": []
        },
        index=pd.DatetimeIndex([])
    )

    daily = pd.Series(
        dtype=float,
        index=pd.DatetimeIndex([])
    )

    monthly = pd.Series(
        dtype=float,
        index=pd.DatetimeIndex([])
    )

    weekly = pd.DataFrame(
        columns=[2024, 2025],
        index=pd.Index([], dtype=object)
    )

    result = engine.calculate_extremes(
        dataset,
        daily,
        monthly,
        weekly
    )

    assert result is engine.extremes

    assert result["hourly_max"] == (None, None)
    assert result["hourly_min"] == (None, None)

    assert result["daily_max"] == (None, None)
    assert result["daily_min"] == (None, None)

    assert result["weekly_max"] == (None, None)
    assert result["weekly_min"] == (None, None)

    assert result["monthly_max"] == (None, None)
    assert result["monthly_min"] == (None, None)