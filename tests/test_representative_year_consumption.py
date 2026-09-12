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

    # Construimos una semana completa de cada mes en dos años.
    # Así cada combinación mes/día de semana/hora aparece exactamente
    # una vez por año y la mediana entre ambos años es inequívocamente
    # el punto medio (+50).
    for year, offset in [(2023, 0.0), (2025, 100.0)]:
        rows = []

        for month in range(1, 13):
            month_start = pd.Timestamp(year=year, month=month, day=1)

            # Primer bloque de 7 días del mes: contiene los 7 días
            # de la semana exactamente una vez.
            for day_offset in range(7):
                day = month_start + pd.Timedelta(days=day_offset)

                for hour in range(24):
                    timestamp = day + pd.Timedelta(hours=hour)

                    value = (
                        month * 10
                        + timestamp.dayofweek
                        + hour / 100
                        + offset
                    )

                    rows.append(
                        {
                            "timestamp": timestamp,
                            "AE_kWh": value,
                        }
                    )

        frame = pd.DataFrame(rows).set_index("timestamp")
        frames.append(frame)

    df = pd.concat(frames)

    result = engine.calculate_representative_year_consumption(df)

    target_timestamp = pd.Timestamp("2025-01-02 13:00:00")
    midnight_timestamp = pd.Timestamp("2025-01-02 00:00:00")

    expected_shape_value = 10 + 3 + 13 / 100 + 50
    expected_midnight_value = 10 + 3 + 50

    ratio = result.loc[target_timestamp] / result.loc[midnight_timestamp]
    expected_ratio = expected_shape_value / expected_midnight_value

    assert ratio == pytest.approx(expected_ratio)


def test_representative_year_ignores_nan_consumption():
    engine = ConsumptionStatistics()

    df = create_full_year_dataset(
        "2023-01-01 00:00:00",
        "2023-12-31 23:00:00",
    )
    df.iloc[0, 0] = float("nan")

    result = engine.calculate_representative_year_consumption(df)

    assert len(result) == 8760    
    assert result.notna().all()
    assert result.sum() == pytest.approx(8759.0)


def test_representative_year_rejects_missing_temporal_slots():
    engine = ConsumptionStatistics()

    frames = []

    for year in [2023, 2025]:
        index = pd.date_range(
            f"{year}-01-01 00:00:00",
            f"{year}-12-31 23:00:00",
            freq="h",
        )

        values = pd.Series(1.0, index=index)

        # Eliminamos todas las observaciones correspondientes a:
        # enero + lunes + 00:00.
        mask = ~(
            (values.index.month == 1)
            & (values.index.dayofweek == 0)
            & (values.index.hour == 0)
        )

        frames.append(
            pd.DataFrame(
                {"AE_kWh": values[mask]},
                index=values.index[mask],
            )
        )

    df = pd.concat(frames)

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
