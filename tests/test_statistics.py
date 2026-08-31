import pandas as pd
import pytest

from helios.core.statistics import ConsumptionStatistics


# ==========================================================
# Helpers
# ==========================================================


def create_engine():

    return ConsumptionStatistics()


def create_dataset():

    index = pd.to_datetime(
        [
            "2024-01-01 00:00:00",
            "2024-01-01 01:00:00",
            "2024-01-02 00:00:00",
            "2024-01-02 01:00:00",
            "2024-01-06 00:00:00",
            "2024-01-07 00:00:00",
        ]
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
            ]
        },
        index=index,
    )


def create_full_year_monthly_dataset():

    index = pd.date_range(
        "2024-01-01",
        periods=12,
        freq="MS",
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
                9.0,
                10.0,
                11.0,
                12.0,
            ]
        },
        index=index,
    )


# ==========================================================
# Estado inicial
# ==========================================================


def test_initial_state():

    engine = create_engine()

    assert engine.statistics is None
    assert engine.daily_consumption is None
    assert engine.monthly_consumption is None
    assert engine.yearly_consumption is None
    assert engine.hourly_profile is None
    assert engine.weekday_profile is None
    assert engine.monthly_profile is None
    assert engine.seasonal_profile is None
    assert engine.workday_vs_weekend_profile is None


# ==========================================================
# Estadísticas generales
# ==========================================================


def test_calculate():

    engine = create_engine()

    df = create_dataset()

    result = engine.calculate(df)

    assert result is engine.statistics

    assert result["total_consumption"] == pytest.approx(21.0)
    assert result["mean_hourly"] == pytest.approx(3.5)

    assert result["max_consumption"] == pytest.approx(6.0)
    assert result["max_consumption_time"] == pd.Timestamp(
        "2024-01-07 00:00:00"
    )

    assert result["min_consumption"] == pytest.approx(1.0)
    assert result["min_consumption_time"] == pd.Timestamp(
        "2024-01-01 00:00:00"
    )

    assert result["std_consumption"] == pytest.approx(
        pd.Series([1, 2, 3, 4, 5, 6]).std()
    )


def test_calculate_ignores_nan_values():

    engine = create_engine()

    index = pd.date_range(
        "2024-01-01",
        periods=3,
        freq="h",
    )

    df = pd.DataFrame(
        {
            "AE_kWh": [
                1.0,
                float("nan"),
                3.0,
            ]
        },
        index=index,
    )

    result = engine.calculate(df)

    assert result["total_consumption"] == pytest.approx(
        4.0
    )

    assert result["mean_hourly"] == pytest.approx(
        2.0
    )

    assert result["min_consumption"] == pytest.approx(
        1.0
    )

    assert result["max_consumption"] == pytest.approx(
        3.0
    )


def test_calculate_single_value_dataset():

    engine = create_engine()

    index = pd.to_datetime(
        ["2024-01-01 12:00:00"]
    )

    df = pd.DataFrame(
        {
            "AE_kWh": [5.0]
        },
        index=index,
    )

    result = engine.calculate(df)

    assert result["total_consumption"] == pytest.approx(
        5.0
    )

    assert result["mean_hourly"] == pytest.approx(
        5.0
    )

    assert result["min_consumption"] == pytest.approx(
        5.0
    )

    assert result["max_consumption"] == pytest.approx(
        5.0
    )

    assert result["min_consumption_time"] == index[0]
    assert result["max_consumption_time"] == index[0]

    assert pd.isna(result["std_consumption"])


def test_calculate_constant_consumption():

    engine = create_engine()

    index = pd.date_range(
        "2024-01-01",
        periods=5,
        freq="h",
    )

    df = pd.DataFrame(
        {
            "AE_kWh": [3.0] * 5
        },
        index=index,
    )

    result = engine.calculate(df)

    assert result["total_consumption"] == pytest.approx(
        15.0
    )

    assert result["mean_hourly"] == pytest.approx(
        3.0
    )

    assert result["std_consumption"] == pytest.approx(
        0.0
    )


def test_calculate_missing_consumption_column():

    engine = create_engine()

    index = pd.date_range(
        "2024-01-01",
        periods=3,
        freq="h",
    )

    df = pd.DataFrame(
        {
            "other_column": [1.0, 2.0, 3.0]
        },
        index=index,
    )

    with pytest.raises(
        KeyError,
        match="AE_kWh",
    ):
        engine.calculate(df)


def test_calculate_overwrites_previous_statistics():

    engine = create_engine()

    first_dataset = pd.DataFrame(
        {
            "AE_kWh": [1.0, 2.0]
        },
        index=pd.date_range(
            "2024-01-01",
            periods=2,
            freq="h",
        ),
    )

    second_dataset = pd.DataFrame(
        {
            "AE_kWh": [10.0, 20.0]
        },
        index=pd.date_range(
            "2024-02-01",
            periods=2,
            freq="h",
        ),
    )

    engine.calculate(first_dataset)

    assert engine.statistics[
        "total_consumption"
    ] == pytest.approx(3.0)

    engine.calculate(second_dataset)

    assert engine.statistics[
        "total_consumption"
    ] == pytest.approx(30.0)

    assert engine.statistics[
        "mean_hourly"
    ] == pytest.approx(15.0)


# ==========================================================
# Consumo diario
# ==========================================================


def test_calculate_daily_consumption():

    engine = create_engine()

    df = create_dataset()

    result = engine.calculate_daily_consumption(df)

    assert result is engine.daily_consumption

    assert result.loc["2024-01-01"] == pytest.approx(3.0)
    assert result.loc["2024-01-02"] == pytest.approx(7.0)
    assert result.loc["2024-01-06"] == pytest.approx(5.0)
    assert result.loc["2024-01-07"] == pytest.approx(6.0)


def test_calculate_daily_consumption_handles_missing_days():

    engine = create_engine()

    index = pd.to_datetime(
        [
            "2024-01-01 00:00",
            "2024-01-03 00:00",
        ]
    )

    df = pd.DataFrame(
        {
            "AE_kWh": [2.0, 5.0]
        },
        index=index,
    )

    result = engine.calculate_daily_consumption(df)

    assert result.loc["2024-01-01"] == pytest.approx(
        2.0
    )

    assert result.loc["2024-01-03"] == pytest.approx(
        5.0
    )


def test_calculate_daily_consumption_ignores_nan_values():

    engine = create_engine()

    index = pd.date_range(
        "2024-01-01",
        periods=3,
        freq="h",
    )

    df = pd.DataFrame(
        {
            "AE_kWh": [
                1.0,
                float("nan"),
                3.0,
            ]
        },
        index=index,
    )

    result = engine.calculate_daily_consumption(df)

    assert result.iloc[0] == pytest.approx(
        4.0
    )


def test_calculate_daily_consumption_updates_engine_state():

    engine = create_engine()

    df = create_dataset()

    result = engine.calculate_daily_consumption(df)

    assert engine.daily_consumption is result

    assert len(engine.daily_consumption) == 7

    assert engine.daily_consumption.loc[
        pd.Timestamp("2024-01-01")
    ] == pytest.approx(3.0)

    assert engine.daily_consumption.loc[
        pd.Timestamp("2024-01-02")
    ] == pytest.approx(7.0)

    assert engine.daily_consumption.loc[
        pd.Timestamp("2024-01-03")
    ] == pytest.approx(0.0)

    assert engine.daily_consumption.loc[
        pd.Timestamp("2024-01-04")
    ] == pytest.approx(0.0)

    assert engine.daily_consumption.loc[
        pd.Timestamp("2024-01-05")
    ] == pytest.approx(0.0)

    assert engine.daily_consumption.loc[
        pd.Timestamp("2024-01-06")
    ] == pytest.approx(5.0)

    assert engine.daily_consumption.loc[
        pd.Timestamp("2024-01-07")
    ] == pytest.approx(6.0)


# ==========================================================
# Consumo mensual
# ==========================================================


def test_calculate_monthly_consumption():

    engine = create_engine()

    df = create_dataset()

    result = engine.calculate_monthly_consumption(df)

    assert result is engine.monthly_consumption

    assert len(result) == 1
    assert result.iloc[0] == pytest.approx(21.0)

    assert result.index[0] == pd.Timestamp(
        "2024-01-31"
    )


def test_calculate_monthly_consumption_multiple_years():

    engine = create_engine()

    index = pd.to_datetime(
        [
            "2024-01-01",
            "2024-01-15",
            "2024-02-01",
            "2025-01-01",
            "2025-01-15",
        ]
    )

    df = pd.DataFrame(
        {
            "AE_kWh": [
                1.0,
                2.0,
                3.0,
                4.0,
                5.0,
            ]
        },
        index=index,
    )

    result = engine.calculate_monthly_consumption(df)

    assert result.loc[
        "2024-01-31"
    ] == pytest.approx(3.0)

    assert result.loc[
        "2024-02-29"
    ] == pytest.approx(3.0)

    assert result.loc[
        "2025-01-31"
    ] == pytest.approx(9.0)


def test_calculate_monthly_consumption_updates_engine_state():

    engine = create_engine()

    df = create_dataset()

    result = engine.calculate_monthly_consumption(df)

    assert engine.monthly_consumption is result


# ==========================================================
# Consumo anual
# ==========================================================


def test_calculate_yearly_consumption():

    engine = create_engine()

    df = create_dataset()

    result = engine.calculate_yearly_consumption(df)

    assert result is engine.yearly_consumption

    assert len(result) == 1
    assert result.iloc[0] == pytest.approx(21.0)

    assert result.index[0] == pd.Timestamp(
        "2024-12-31"
    )


def test_calculate_yearly_consumption_multiple_years():

    engine = create_engine()

    index = pd.to_datetime(
        [
            "2024-01-01",
            "2024-06-01",
            "2025-01-01",
            "2025-06-01",
        ]
    )

    df = pd.DataFrame(
        {
            "AE_kWh": [
                1.0,
                2.0,
                10.0,
                20.0,
            ]
        },
        index=index,
    )

    result = engine.calculate_yearly_consumption(df)

    assert result.loc[
        "2024-12-31"
    ] == pytest.approx(3.0)

    assert result.loc[
        "2025-12-31"
    ] == pytest.approx(30.0)


def test_calculate_yearly_consumption_updates_engine_state():

    engine = create_engine()

    df = create_dataset()

    result = engine.calculate_yearly_consumption(df)

    assert engine.yearly_consumption is result


# ==========================================================
# Perfil horario
# ==========================================================


def test_calculate_hourly_profile():

    engine = create_engine()

    df = create_dataset()

    result = engine.calculate_hourly_profile(df)

    assert result is engine.hourly_profile

    assert result.loc[0] == pytest.approx(3.75)
    assert result.loc[1] == pytest.approx(3.0)


def test_calculate_hourly_profile_contains_all_24_hours():

    engine = create_engine()

    index = pd.date_range(
        "2024-01-01",
        periods=24,
        freq="h",
    )

    df = pd.DataFrame(
        {
            "AE_kWh": [1.0] * 24
        },
        index=index,
    )

    result = engine.calculate_hourly_profile(df)

    assert len(result) == 24

    assert list(result.index) == list(range(24))

    assert all(
        result.iloc[i] == pytest.approx(1.0)
        for i in range(24)
    )


def test_calculate_hourly_profile_averages_same_hour():

    engine = create_engine()

    index = pd.to_datetime(
        [
            "2024-01-01 10:00",
            "2024-01-02 10:00",
            "2024-01-01 11:00",
            "2024-01-02 11:00",
        ]
    )

    df = pd.DataFrame(
        {
            "AE_kWh": [
                2.0,
                4.0,
                1.0,
                3.0,
            ]
        },
        index=index,
    )

    result = engine.calculate_hourly_profile(df)

    assert result.loc[10] == pytest.approx(3.0)
    assert result.loc[11] == pytest.approx(2.0)


# ==========================================================
# Perfil por día de la semana
# ==========================================================


def test_calculate_weekday_profile():

    engine = create_engine()

    df = create_dataset()

    result = engine.calculate_weekday_profile(df)

    assert result is engine.weekday_profile

    assert list(result.index) == [
        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes",
        "Sábado",
        "Domingo",
    ]

    assert result["Lunes"] == pytest.approx(1.5)
    assert result["Martes"] == pytest.approx(3.5)
    assert result["Sábado"] == pytest.approx(5.0)
    assert result["Domingo"] == pytest.approx(6.0)


def test_calculate_weekday_profile_contains_seven_days():

    engine = create_engine()

    index = pd.date_range(
        "2024-01-01",
        periods=7,
        freq="D",
    )

    df = pd.DataFrame(
        {
            "AE_kWh": [1.0] * 7
        },
        index=index,
    )

    result = engine.calculate_weekday_profile(df)

    assert len(result) == 7

    assert list(result.index) == [
        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes",
        "Sábado",
        "Domingo",
    ]

    assert all(
        result.iloc[i] == pytest.approx(1.0)
        for i in range(7)
    )


def test_calculate_weekday_profile_averages_same_weekday():

    engine = create_engine()

    index = pd.to_datetime(
        [
            "2024-01-01",
            "2024-01-08",
            "2024-01-02",
            "2024-01-09",
        ]
    )

    df = pd.DataFrame(
        {
            "AE_kWh": [
                2.0,
                4.0,
                1.0,
                3.0,
            ]
        },
        index=index,
    )

    result = engine.calculate_weekday_profile(df)

    assert result["Lunes"] == pytest.approx(3.0)
    assert result["Martes"] == pytest.approx(2.0)


# ==========================================================
# Perfil mensual
# ==========================================================


def test_calculate_monthly_profile():

    engine = create_engine()

    df = create_dataset()

    result = engine.calculate_monthly_profile(df)

    assert result is engine.monthly_profile

    assert list(result.index) == [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]

    assert result["Enero"] == pytest.approx(3.5)


def test_calculate_monthly_profile_contains_twelve_months():

    engine = create_engine()

    df = create_full_year_monthly_dataset()

    result = engine.calculate_monthly_profile(df)

    assert len(result) == 12

    assert list(result.index) == [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]


def test_calculate_monthly_profile_returns_mean_by_month():

    engine = create_engine()

    index = pd.to_datetime(
        [
            "2024-01-01",
            "2025-01-01",
            "2024-02-01",
            "2025-02-01",
        ]
    )

    df = pd.DataFrame(
        {
            "AE_kWh": [
                2.0,
                4.0,
                1.0,
                3.0,
            ]
        },
        index=index,
    )

    result = engine.calculate_monthly_profile(df)

    assert result["Enero"] == pytest.approx(3.0)
    assert result["Febrero"] == pytest.approx(2.0)


# ==========================================================
# Perfil estacional
# ==========================================================


def test_calculate_seasonal_profile():

    engine = create_engine()

    engine.monthly_profile = pd.Series(
        {
            "Enero": 1.0,
            "Febrero": 2.0,
            "Marzo": 3.0,
            "Abril": 4.0,
            "Mayo": 5.0,
            "Junio": 6.0,
            "Julio": 7.0,
            "Agosto": 8.0,
            "Septiembre": 9.0,
            "Octubre": 10.0,
            "Noviembre": 11.0,
            "Diciembre": 12.0,
        }
    )

    result = engine.calculate_seasonal_profile()

    assert result is engine.seasonal_profile

    assert result["Invierno"] == pytest.approx(5.0)
    assert result["Primavera"] == pytest.approx(4.0)
    assert result["Verano"] == pytest.approx(7.0)
    assert result["Otoño"] == pytest.approx(10.0)


def test_calculate_seasonal_profile_without_monthly_profile():

    engine = create_engine()

    with pytest.raises(
        RuntimeError,
        match="Monthly profile has not been calculated.",
    ):
        engine.calculate_seasonal_profile()


def test_calculate_seasonal_profile_contains_four_seasons():

    engine = create_engine()

    engine.monthly_profile = pd.Series(
        {
            "Enero": 1.0,
            "Febrero": 1.0,
            "Marzo": 1.0,
            "Abril": 1.0,
            "Mayo": 1.0,
            "Junio": 1.0,
            "Julio": 1.0,
            "Agosto": 1.0,
            "Septiembre": 1.0,
            "Octubre": 1.0,
            "Noviembre": 1.0,
            "Diciembre": 1.0,
        }
    )

    result = engine.calculate_seasonal_profile()

    assert list(result.index) == [
        "Invierno",
        "Primavera",
        "Verano",
        "Otoño",
    ]

    assert all(
        result.iloc[i] == pytest.approx(1.0)
        for i in range(4)
    )


# ==========================================================
# Laborables vs fin de semana
# ==========================================================


def test_calculate_workday_vs_weekend_profile():

    engine = create_engine()

    df = create_dataset()

    result = engine.calculate_workday_vs_weekend_profile(df)

    assert result is engine.workday_vs_weekend_profile

    assert result["workdays"] == pytest.approx(2.5)
    assert result["weekend"] == pytest.approx(5.5)


def test_calculate_workday_vs_weekend_profile_uses_all_weekdays():

    engine = create_engine()

    index = pd.date_range(
        "2024-01-01",
        periods=7,
        freq="D",
    )

    df = pd.DataFrame(
        {
            "AE_kWh": [
                1.0,
                2.0,
                3.0,
                4.0,
                5.0,
                6.0,
                7.0,
            ]
        },
        index=index,
    )

    result = engine.calculate_workday_vs_weekend_profile(df)

    assert result["workdays"] == pytest.approx(3.0)
    assert result["weekend"] == pytest.approx(6.5)


def test_calculate_workday_vs_weekend_profile_without_weekend_data():

    engine = create_engine()

    index = pd.date_range(
        "2024-01-01",
        periods=5,
        freq="D",
    )

    df = pd.DataFrame(
        {
            "AE_kWh": [
                1.0,
                2.0,
                3.0,
                4.0,
                5.0,
            ]
        },
        index=index,
    )

    result = engine.calculate_workday_vs_weekend_profile(df)

    assert result["workdays"] == pytest.approx(3.0)
    assert pd.isna(result["weekend"])


def test_calculate_workday_vs_weekend_profile_without_workday_data():

    engine = create_engine()

    index = pd.to_datetime(
        [
            "2024-01-06",
            "2024-01-07",
        ]
    )

    df = pd.DataFrame(
        {
            "AE_kWh": [
                5.0,
                7.0,
            ]
        },
        index=index,
    )

    result = engine.calculate_workday_vs_weekend_profile(df)

    assert pd.isna(result["workdays"])
    assert result["weekend"] == pytest.approx(6.0)


def test_calculate_workday_vs_weekend_profile_ignores_nan_values():

    engine = create_engine()

    index = pd.to_datetime(
        [
            "2024-01-01",
            "2024-01-02",
            "2024-01-06",
            "2024-01-07",
        ]
    )

    df = pd.DataFrame(
        {
            "AE_kWh": [
                2.0,
                float("nan"),
                4.0,
                6.0,
            ]
        },
        index=index,
    )

    result = engine.calculate_workday_vs_weekend_profile(df)

    assert result["workdays"] == pytest.approx(
        2.0
    )

    assert result["weekend"] == pytest.approx(
        5.0
    )


# ==========================================================
# Estado después de cálculos
# ==========================================================


def test_calculate_does_not_modify_other_profiles():

    engine = create_engine()

    engine.daily_consumption = pd.Series(
        [100.0]
    )

    engine.monthly_profile = pd.Series(
        {
            "Enero": 1.0,
        }
    )

    df = create_dataset()

    engine.calculate(df)

    assert engine.daily_consumption.iloc[0] == pytest.approx(
        100.0
    )

    assert engine.monthly_profile["Enero"] == pytest.approx(
        1.0
    )


def test_calculate_daily_consumption_does_not_modify_statistics():

    engine = create_engine()

    df = create_dataset()

    engine.calculate(df)

    original_statistics = engine.statistics.copy()

    engine.calculate_daily_consumption(df)

    assert engine.statistics == original_statistics


def test_calculate_monthly_profile_does_not_calculate_seasonal_profile():

    engine = create_engine()

    df = create_full_year_monthly_dataset()

    engine.calculate_monthly_profile(df)

    assert engine.monthly_profile is not None
    assert engine.seasonal_profile is None


def test_calculate_seasonal_profile_uses_current_monthly_profile():

    engine = create_engine()

    engine.monthly_profile = pd.Series(
        {
            "Enero": 10.0,
            "Febrero": 20.0,
            "Marzo": 30.0,
            "Abril": 40.0,
            "Mayo": 50.0,
            "Junio": 60.0,
            "Julio": 70.0,
            "Agosto": 80.0,
            "Septiembre": 90.0,
            "Octubre": 100.0,
            "Noviembre": 110.0,
            "Diciembre": 120.0,
        }
    )

    first_result = engine.calculate_seasonal_profile()

    assert first_result["Invierno"] == pytest.approx(
        50.0
    )

    engine.monthly_profile["Enero"] = 100.0

    second_result = engine.calculate_seasonal_profile()

    assert second_result["Invierno"] == pytest.approx(
        80.0
    )