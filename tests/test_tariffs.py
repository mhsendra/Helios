import pandas as pd
import pytest

from helios.core.tariffs import TariffEngine


# ==========================================================
# Helpers
# ==========================================================

def create_engine():

    return TariffEngine()


def create_dataset():

    index = pd.to_datetime(
        [
            "2025-01-02 07:00",   # Valle
            "2025-01-02 09:00",   # Llano
            "2025-01-02 12:00",   # Punta
            "2025-01-02 16:00",   # Llano
            "2025-01-02 20:00",   # Punta
            "2025-01-02 23:00",   # Llano
            "2025-01-04 12:00",   # Sábado → Valle
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
                7.0,
            ]
        },
        index=index
    )


# ==========================================================
# Estado inicial
# ==========================================================

def test_initial_state():

    engine = create_engine()

    assert isinstance(
        engine.national_holidays,
        set
    )

    assert engine.period_consumption is None

    assert engine.period_percentage is None

    assert engine.prices.buy_p1 == 0.25
    assert engine.prices.buy_p2 == 0.18
    assert engine.prices.buy_p3 == 0.12
    assert engine.prices.sell_price == 0.06


# ==========================================================
# Festivos
# ==========================================================

def test_is_national_holiday():

    engine = create_engine()

    holiday = next(iter(engine.national_holidays))

    timestamp = pd.Timestamp(holiday)

    assert engine.is_national_holiday(timestamp) is True


def test_is_not_national_holiday():

    engine = create_engine()

    timestamp = pd.Timestamp("2025-01-02")

    assert engine.is_national_holiday(timestamp) is False


# ==========================================================
# Clasificación de periodos
# ==========================================================

@pytest.mark.parametrize(
    "timestamp, expected",
    [
        ("2025-01-02 00:00", "Valle"),
        ("2025-01-02 07:59", "Valle"),
        ("2025-01-02 08:00", "Llano"),
        ("2025-01-02 09:59", "Llano"),
        ("2025-01-02 10:00", "Punta"),
        ("2025-01-02 13:59", "Punta"),
        ("2025-01-02 14:00", "Llano"),
        ("2025-01-02 17:59", "Llano"),
        ("2025-01-02 18:00", "Punta"),
        ("2025-01-02 21:59", "Punta"),
        ("2025-01-02 22:00", "Llano"),
        ("2025-01-02 23:00", "Llano"),
    ]
)
def test_classify_period_workday(
    timestamp,
    expected
):

    engine = create_engine()

    timestamp = pd.Timestamp(timestamp)

    assert (
        engine.classify_period(timestamp)
        == expected
    )


def test_classify_period_saturday():

    engine = create_engine()

    timestamp = pd.Timestamp(
        "2025-01-04 12:00"
    )

    assert (
        engine.classify_period(timestamp)
        == "Valle"
    )


def test_classify_period_sunday():

    engine = create_engine()

    timestamp = pd.Timestamp(
        "2025-01-05 12:00"
    )

    assert (
        engine.classify_period(timestamp)
        == "Valle"
    )


def test_classify_period_national_holiday():

    engine = create_engine()

    holiday = next(iter(engine.national_holidays))

    timestamp = pd.Timestamp(
        holiday
    ).replace(hour=12)

    assert (
        engine.classify_period(timestamp)
        == "Valle"
    )


def test_classify_period_invalid_hour():

    engine = create_engine()

    class InvalidTimestamp:

        def weekday(self):
            return 3

        def date(self):
            return pd.Timestamp(
                "2025-01-02"
            ).date()

        hour = 24

    with pytest.raises(
        ValueError,
        match="Hora no válida: 24"
    ):
        engine.classify_period(
            InvalidTimestamp()
        )


# ==========================================================
# Consumo por periodo
# ==========================================================

def test_calculate_period_consumption():

    engine = create_engine()

    dataset = create_dataset()

    result = engine.calculate_period_consumption(
        dataset
    )

    assert result is engine.period_consumption

    assert result == {
        "Punta": 8.0,
        "Llano": 12.0,
        "Valle": 8.0,
    }


def test_calculate_period_consumption_includes_zero_periods():

    engine = create_engine()

    index = pd.to_datetime(
        [
            "2025-01-02 12:00",
        ]
    )

    dataset = pd.DataFrame(
        {
            "AE_kWh": [5.0]
        },
        index=index
    )

    result = engine.calculate_period_consumption(
        dataset
    )

    assert result == {
        "Punta": 5.0,
        "Llano": 0.0,
        "Valle": 0.0,
    }


# ==========================================================
# Porcentajes
# ==========================================================

def test_calculate_period_percentage():

    engine = create_engine()

    engine.period_consumption = {
        "Punta": 20.0,
        "Llano": 30.0,
        "Valle": 50.0,
    }

    result = engine.calculate_period_percentage()

    assert result is engine.period_percentage

    assert result["Punta"] == pytest.approx(20.0)
    assert result["Llano"] == pytest.approx(30.0)
    assert result["Valle"] == pytest.approx(50.0)

    assert sum(result.values()) == pytest.approx(
        100.0
    )


# ==========================================================
# Precios de compra
# ==========================================================

def test_assign_buy_prices():

    engine = create_engine()

    dataset = pd.DataFrame(
        {
            "Periodo": [
                "Punta",
                "Llano",
                "Valle",
                "Desconocido",
            ]
        }
    )

    engine.assign_buy_prices(dataset)

    assert list(
        dataset["buy_price_eur_kwh"]
    ) == [
        0.25,
        0.18,
        0.12,
        0.0,
    ]


# ==========================================================
# Precio de venta
# ==========================================================

def test_assign_sell_price():

    engine = create_engine()

    dataset = pd.DataFrame(
        {
            "AE_kWh": [
                1.0,
                2.0,
                3.0,
            ]
        }
    )

    engine.assign_sell_price(dataset)

    assert list(
        dataset["sell_price_eur_kwh"]
    ) == [
        0.06,
        0.06,
        0.06,
    ]


# ==========================================================
# Asignación de periodos
# ==========================================================

def test_assign_tariff_periods():

    engine = create_engine()

    dataset = create_dataset()

    engine.assign_tariff_periods(
        dataset
    )

    assert list(
        dataset["Periodo"]
    ) == [
        "Valle",
        "Llano",
        "Punta",
        "Llano",
        "Punta",
        "Llano",
        "Valle",
    ]

def test_calculate_period_percentage_zero_consumption():

    engine = create_engine()

    engine.period_consumption = {
        "Punta": 0.0,
        "Llano": 0.0,
        "Valle": 0.0,
    }

    result = engine.calculate_period_percentage()

    assert result is engine.period_percentage

    assert result == {
        "Punta": 0.0,
        "Llano": 0.0,
        "Valle": 0.0,
    }