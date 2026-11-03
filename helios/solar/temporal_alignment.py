import numpy as np
import pandas as pd


def align_hourly_series_by_month_day_hour(
    target_index: pd.DatetimeIndex,
    source: pd.Series,
) -> pd.Series:
    """
    Align an hourly series by month, day and hour, ignoring the year.

    Missing calendar hours and missing source values are filled with 0.0.
    The returned series uses target_index.
    """
    if not isinstance(target_index, pd.DatetimeIndex):
        raise TypeError("target_index must be a DatetimeIndex.")

    if not isinstance(source, pd.Series):
        raise TypeError("source must be a pandas Series.")

    if not isinstance(source.index, pd.DatetimeIndex):
        raise TypeError("source index must be a DatetimeIndex.")

    source_keys = (
        source.index.month.to_numpy(dtype=np.int64) * 10000
        + source.index.day.to_numpy(dtype=np.int64) * 100
        + source.index.hour.to_numpy(dtype=np.int64)
    )

    target_keys = (
        target_index.month.to_numpy(dtype=np.int64) * 10000
        + target_index.day.to_numpy(dtype=np.int64) * 100
        + target_index.hour.to_numpy(dtype=np.int64)
    )

    positions = pd.Index(source_keys).get_indexer(target_keys)

    source_values = source.to_numpy(dtype=float, copy=False)
    aligned_values = np.zeros(len(target_index), dtype=float)

    valid_positions = positions >= 0
    aligned_values[valid_positions] = source_values[
        positions[valid_positions]
    ]

    aligned_values[np.isnan(aligned_values)] = 0.0

    return pd.Series(
        aligned_values,
        index=target_index,
        name=source.name,
    )