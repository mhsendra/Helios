import numpy as np
import pandas as pd
import pytest

from helios.solar.temporal_alignment import (
    align_hourly_series_by_month_day_hour,
)


def test_aligns_series_between_different_reference_years():
    source_index = pd.date_range(
        "2023-01-01",
        periods=8760,
        freq="h",
    )
    target_index = pd.date_range(
        "2025-01-01",
        periods=8760,
        freq="h",
    )

    source = pd.Series(
        np.arange(8760, dtype=float),
        index=source_index,
    )

    result = align_hourly_series_by_month_day_hour(
        target_index,
        source,
    )

    pd.testing.assert_series_equal(
        result,
        pd.Series(
            source.to_numpy(),
            index=target_index,
        ),
    )


def test_fills_february_29_with_zero_when_source_is_non_leap_year():
    source_index = pd.date_range(
        "2023-01-01",
        periods=8760,
        freq="h",
    )
    target_index = pd.date_range(
        "2024-01-01",
        "2024-12-31 23:00",
        freq="h",
    )

    source = pd.Series(
        1.0,
        index=source_index,
    )

    result = align_hourly_series_by_month_day_hour(
        target_index,
        source,
    )

    february_29 = (
        (result.index.month == 2)
        & (result.index.day == 29)
    )

    assert len(result) == 8784
    assert result.loc[february_29].eq(0.0).all()
    assert result.loc[~february_29].eq(1.0).all()


def test_fills_missing_source_hours_with_zero():
    source_index = pd.date_range(
        "2025-01-01",
        periods=8760,
        freq="h",
    ).delete(12)

    target_index = pd.date_range(
        "2025-01-01",
        periods=8760,
        freq="h",
    )

    source = pd.Series(
        2.0,
        index=source_index,
    )

    result = align_hourly_series_by_month_day_hour(
        target_index,
        source,
    )

    assert result.iloc[12] == pytest.approx(0.0)
    assert result.drop(result.index[12]).eq(2.0).all()


def test_replaces_nan_values_with_zero():
    index = pd.date_range(
        "2025-01-01",
        periods=8760,
        freq="h",
    )

    source = pd.Series(
        1.0,
        index=index,
    )
    source.iloc[12] = np.nan

    result = align_hourly_series_by_month_day_hour(
        index,
        source,
    )

    assert result.iloc[12] == pytest.approx(0.0)
    assert result.drop(result.index[12]).eq(1.0).all()


def test_preserves_target_index_and_source_name():
    source_index = pd.date_range(
        "2023-01-01",
        periods=8760,
        freq="h",
    )
    target_index = pd.date_range(
        "2025-01-01",
        periods=8760,
        freq="h",
    )

    source = pd.Series(
        1.0,
        index=source_index,
        name="production",
    )

    result = align_hourly_series_by_month_day_hour(
        target_index,
        source,
    )

    assert result.index.equals(target_index)
    assert result.name == "production"


def test_rejects_invalid_target_index():
    source = pd.Series(
        [1.0],
        index=pd.date_range("2025-01-01", periods=1, freq="h"),
    )

    with pytest.raises(
        TypeError,
        match="target_index must be a DatetimeIndex",
    ):
        align_hourly_series_by_month_day_hour(
            pd.Index([1]),
            source,
        )


def test_rejects_invalid_source():
    target_index = pd.date_range(
        "2025-01-01",
        periods=1,
        freq="h",
    )

    with pytest.raises(
        TypeError,
        match="source must be a pandas Series",
    ):
        align_hourly_series_by_month_day_hour(
            target_index,
            [1.0],
        )