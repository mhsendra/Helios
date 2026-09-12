import pandas as pd
import pytest

from helios.core.statistics import ConsumptionStatistics


def create_full_year_dataset(start, end):
    index = pd.date_range(start, end, freq="h")
    return pd.DataFrame({"AE_kWh": 1.0}, index=index)


def test_representative_year_has_8760_hours_and_annual_total():
    engine = ConsumptionStatistics()

    df = create_full_year_dataset(
        "2023-01-01 00:00:00",
        "2023-12-31 23:00:00",
    )

    result = engine.calculate_representative_year_consumption(df)

    assert len(result) == 8760
    assert result.index[0] == pd.Timestamp("2025-01-01 00:00:00")
    assert result.index[-1] == pd.Timestamp("2025-12-31 23:00:00")
    assert result.sum() == pytest.approx(8760.0)
    assert engine.representative_year_consumption is result
    assert engine.representative_annual_consumption == pytest.approx(8760.0)


def test_representative_year_uses_median_by_month_weekday_and_hour():
    engine = ConsumptionStatistics()

    frames = []
    for year, offset in [(2023, 0.0), (2025, 100.0)]:
        index = pd.date_range(
            f"{year}-01-01 00:00:00",
            f"{year}-12-31 23:00:00",
            freq="h",
        )
        values = (
            index.month.to_numpy(dtype=float) * 10
            + index.dayofweek.to_numpy(dtype=float)
            + index.hour.to_numpy(dtype=float) / 100
            + offset
        )
        frames.append(pd.DataFrame({"AE_kWh": values}, index=index))

    df = pd.concat(frames)

    result = engine.calculate_representative_year_consumption(df)

    # The two source years differ by exactly 100 kWh per slot, so their
    # median is the midpoint (source value + 50) before normalization.
    target_timestamp = pd.Timestamp("2025-01-02 13:00:00")
    expected_shape_value = 10 + 3 + 13 / 100 + 50

    ratio = result.loc[target_timestamp] / result.loc[
        pd.Timestamp("2025-01-02 00:00:00")
    ]
    expected_ratio = expected_shape_value / (10 + 3 + 50)

    assert ratio == pytest.approx(expected_ratio)
    assert result.index.is_unique
    assert not result.isna().any()
    assert result.sum() == pytest.approx(
        df["AE_kWh"].sum() / 1096 * 365
    )


def test_representative_year_ignores_nan_consumption():
    engine = ConsumptionStatistics()

    df = create_full_year_dataset(
        "2023-01-01 00:00:00",
        "2023-12-31 23:00:00",
    )
    df.iloc[0, 0] = float("nan")

    result = engine.calculate_representative_year_consumption(df)

    assert len(result) == 8760
    assert result.sum() == pytest.approx(8760.0)


def test_representative_year_rejects_missing_temporal_slots():
    engine = ConsumptionStatistics()

    index = pd.date_range(
        "2023-01-01 00:00:00",
        "2023-12-31 23:00:00",
        freq="h",
    ).delete(100)
    df = pd.DataFrame({"AE_kWh": 1.0}, index=index)

    with pytest.raises(ValueError, match="enough temporal coverage"):
        engine.calculate_representative_year_consumption(df)


def test_representative_year_rejects_invalid_input():
    engine = ConsumptionStatistics()

    with pytest.raises(KeyError, match="AE_kWh"):
        engine.calculate_representative_year_consumption(
            pd.DataFrame({"other": [1.0]})
        )

    with pytest.raises(ValueError, match="empty dataset"):
        engine.calculate_representative_year_consumption(
            pd.DataFrame(columns=["AE_kWh"])
        )

    with pytest.raises(TypeError, match="DatetimeIndex"):
        engine.calculate_representative_year_consumption(
            pd.DataFrame({"AE_kWh": [1.0]})
        )
