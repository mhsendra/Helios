import pandas as pd
import pytest

from helios.core.statistics import ConsumptionStatistics


# ==========================================================
# Helpers
# ==========================================================


def create_engine():

    return ConsumptionStatistics()


def create_dataset():

    index = pd.to_datetime([
        "2024-01-01 00:00:00",
        "2024-01-01 01:00:00",
        "2024-01-02 00:00:00",
        "2024-01-02 01:00:00",
        "2024-01-06 00:00:00",
        "2024-01-07 00:00:00",
    ])

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
        index=index
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

    assert result.index[0] == pd.Timestamp("2024-01-31")


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

    assert result.index[0] == pd.Timestamp("2024-12-31")


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
        "Domingo"
    ]

    assert result["Lunes"] == pytest.approx(1.5)
    assert result["Martes"] == pytest.approx(3.5)
    assert result["Sábado"] == pytest.approx(5.0)
    assert result["Domingo"] == pytest.approx(6.0)


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
        "Diciembre"
    ]

    assert result["Enero"] == pytest.approx(3.5)


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
        match="Monthly profile has not been calculated."
    ):
        engine.calculate_seasonal_profile()


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