import pandas as pd
import pytest

from helios.ev.scenario import EVScenario
from helios.core.consumption_scenario import ConsumptionScenario
from helios.solar.production_profile import SolarProductionProfile

from helios.ev.strategies import (
    ImmediateChargingStrategy,
    NightChargingStrategy,
    SolarNightChargingStrategy,
    SolarSurplusChargingStrategy,
)

def create_solar_inputs():
    index = pd.date_range(
        "2025-01-01 00:00:00",
        "2025-12-31 23:00:00",
        freq="h",
    )

    consumption = pd.Series(
        1.0,
        index=index,
        dtype=float,
    )

    production = pd.Series(
        0.0,
        index=index,
        dtype=float,
    )

    return (
        ConsumptionScenario(
            hourly_consumption=consumption,
            reference_year=2025,
        ),
        SolarProductionProfile(
            hourly_production=production,
            reference_year=2025,
            installed_power_kwp=8.1,
        ),
    )

def create_scenario():
    index = pd.date_range(
        "2025-01-01 00:00:00",
        "2025-12-31 23:00:00",
        freq="h",
    )

    values = pd.Series(
        1.0,
        index=index,
        dtype=float,
    )

    values.iloc[100] = 2.5
    values.iloc[5000] = 0.25

    return EVScenario(
        hourly_consumption=values,
        reference_year=2025,
    )

def create_index():
    return pd.date_range(
        "2025-01-01 00:00:00",
        "2025-12-31 23:00:00",
        freq="h",
    )

def create_consumption_scenario(
    values: pd.Series | None = None,
) -> ConsumptionScenario:
    """Crea un escenario doméstico de prueba."""

    index = create_index()

    if values is None:
        values = pd.Series(
            0.0,
            index=index,
            dtype=float,
        )

    return ConsumptionScenario(
        hourly_consumption=values,
        reference_year=2025,
    )


def create_solar_production_profile(
    values: pd.Series | None = None,
) -> SolarProductionProfile:
    """Crea un perfil FV de prueba."""

    index = create_index()

    if values is None:
        values = pd.Series(
            0.0,
            index=index,
            dtype=float,
        )

    return SolarProductionProfile(
        hourly_production=values,
        installed_power_kwp=1.0,
        reference_year=2025,
    )

def test_immediate_strategy_returns_ev_scenario():

    strategy = ImmediateChargingStrategy()
    scenario = create_scenario()

    result = strategy.apply(scenario)

    assert isinstance(result, EVScenario)


def test_immediate_strategy_preserves_hourly_values():

    strategy = ImmediateChargingStrategy()
    scenario = create_scenario()

    result = strategy.apply(scenario)

    pd.testing.assert_series_equal(
        result.hourly_consumption,
        scenario.hourly_consumption,
    )


def test_immediate_strategy_preserves_annual_consumption():

    strategy = ImmediateChargingStrategy()
    scenario = create_scenario()

    result = strategy.apply(scenario)

    assert result.annual_consumption == pytest.approx(
        scenario.annual_consumption
    )


def test_immediate_strategy_does_not_modify_original():

    strategy = ImmediateChargingStrategy()
    scenario = create_scenario()

    original = scenario.hourly_consumption.copy()

    strategy.apply(scenario)

    pd.testing.assert_series_equal(
        scenario.hourly_consumption,
        original,
    )


def test_immediate_strategy_returns_independent_series():

    strategy = ImmediateChargingStrategy()
    scenario = create_scenario()

    result = strategy.apply(scenario)

    assert result.hourly_consumption is not scenario.hourly_consumption


def test_immediate_strategy_rejects_invalid_scenario():

    strategy = ImmediateChargingStrategy()

    with pytest.raises(
        TypeError,
        match="scenario must be an EVScenario.",
    ):
        strategy.apply("invalid")

def test_night_strategy_returns_ev_scenario():

    strategy = NightChargingStrategy()
    scenario = create_scenario()

    result = strategy.apply(scenario)

    assert isinstance(result, EVScenario)


def test_night_strategy_preserves_annual_consumption():

    strategy = NightChargingStrategy()
    scenario = create_scenario()

    result = strategy.apply(scenario)

    assert result.annual_consumption == pytest.approx(
        scenario.annual_consumption
    )


def test_night_strategy_preserves_daily_consumption():

    strategy = NightChargingStrategy()
    scenario = create_scenario()

    result = strategy.apply(scenario)

    original_daily = scenario.hourly_consumption.groupby(
        scenario.hourly_consumption.index.normalize()
    ).sum()

    result_daily = result.hourly_consumption.groupby(
        result.hourly_consumption.index.normalize()
    ).sum()

    pd.testing.assert_series_equal(
        result_daily,
        original_daily,
    )


def test_night_strategy_uses_default_window():

    strategy = NightChargingStrategy()
    scenario = create_scenario()

    result = strategy.apply(scenario)

    outside_window = result.hourly_consumption[
        ~result.hourly_consumption.index.hour.isin(
            range(0, 7)
        )
    ]

    assert (outside_window == 0.0).all()


def test_night_strategy_custom_window():

    strategy = NightChargingStrategy(
        start_hour=22,
        end_hour=24,
    )
    scenario = create_scenario()

    result = strategy.apply(scenario)

    outside_window = result.hourly_consumption[
        ~result.hourly_consumption.index.hour.isin(
            [22, 23]
        )
    ]

    assert (outside_window == 0.0).all()


def test_night_strategy_rejects_invalid_scenario():

    strategy = NightChargingStrategy()

    with pytest.raises(
        TypeError,
        match="scenario must be an EVScenario.",
    ):
        strategy.apply("invalid")


def test_night_strategy_rejects_invalid_start_hour():

    with pytest.raises(
        ValueError,
        match="start_hour must be between 0 and 23.",
    ):
        NightChargingStrategy(
            start_hour=-1,
        )


def test_night_strategy_rejects_invalid_end_hour():

    with pytest.raises(
        ValueError,
        match="end_hour must be between 1 and 24.",
    ):
        NightChargingStrategy(
            end_hour=25,
        )


def test_night_strategy_rejects_reversed_window():

    with pytest.raises(
        ValueError,
        match="start_hour must be lower than end_hour.",
    ):
        NightChargingStrategy(
            start_hour=8,
            end_hour=7,
        )

def test_solar_strategy_returns_ev_scenario():

    strategy = SolarSurplusChargingStrategy()
    scenario = create_scenario()
    consumption, production = create_solar_inputs()

    result = strategy.apply(
        scenario,
        consumption,
        production,
    )

    assert isinstance(result, EVScenario)


def test_solar_strategy_preserves_annual_consumption():

    strategy = SolarSurplusChargingStrategy()
    scenario = create_scenario()
    consumption, production = create_solar_inputs()

    result = strategy.apply(
        scenario,
        consumption,
        production,
    )

    assert result.annual_consumption == pytest.approx(
        scenario.annual_consumption
    )


def test_solar_strategy_uses_pv_surplus_first():

    index = create_index()

    ev = EVScenario(
        hourly_consumption=pd.Series(
            1.0,
            index=index,
            dtype=float,
        ),
        reference_year=2025,
    )

    consumption = ConsumptionScenario(
        hourly_consumption=pd.Series(
            1.0,
            index=index,
            dtype=float,
        ),
        reference_year=2025,
    )

    production_values = pd.Series(
        0.0,
        index=index,
        dtype=float,
    )

    production_values.iloc[12] = 3.0

    production = SolarProductionProfile(
        hourly_production=production_values,
        reference_year=2025,
        installed_power_kwp=8.1,
    )

    strategy = SolarSurplusChargingStrategy()

    result = strategy.apply(
        ev,
        consumption,
        production,
    )

    assert result.hourly_consumption.iloc[12] == pytest.approx(
        2.0
    )


def test_solar_strategy_does_not_exceed_pv_surplus():

    index = create_index()

    ev = EVScenario(
        hourly_consumption=pd.Series(
            1.0,
            index=index,
            dtype=float,
        ),
        reference_year=2025,
    )

    consumption = ConsumptionScenario(
        hourly_consumption=pd.Series(
            1.0,
            index=index,
            dtype=float,
        ),
        reference_year=2025,
    )

    production_values = pd.Series(
        0.0,
        index=index,
        dtype=float,
    )

    production_values.iloc[12] = 1.5

    production = SolarProductionProfile(
        hourly_production=production_values,
        reference_year=2025,
        installed_power_kwp=8.1,
    )

    result = SolarSurplusChargingStrategy().apply(
        ev,
        consumption,
        production,
    )

    assert result.hourly_consumption.iloc[12] == pytest.approx(
        0.5
    )


def test_solar_strategy_uses_fallback_when_surplus_is_insufficient():

    index = create_index()

    ev_values = pd.Series(
        1.0,
        index=index,
        dtype=float,
    )

    ev = EVScenario(
        hourly_consumption=ev_values,
        reference_year=2025,
    )

    consumption = ConsumptionScenario(
        hourly_consumption=pd.Series(
            1.0,
            index=index,
            dtype=float,
        ),
        reference_year=2025,
    )

    production_values = pd.Series(
        0.0,
        index=index,
        dtype=float,
    )

    production_values.iloc[12] = 1.5

    production = SolarProductionProfile(
        hourly_production=production_values,
        reference_year=2025,
        installed_power_kwp=8.1,
    )

    result = SolarSurplusChargingStrategy().apply(
        ev,
        consumption,
        production,
    )

    assert result.annual_consumption == pytest.approx(
        ev.annual_consumption
    )

    assert result.hourly_consumption.iloc[12] >= 0.5


def test_solar_strategy_rejects_invalid_consumption():

    strategy = SolarSurplusChargingStrategy()
    scenario = create_scenario()
    _, production = create_solar_inputs()

    with pytest.raises(
        TypeError,
        match="consumption_scenario must be a ConsumptionScenario.",
    ):
        strategy.apply(
            scenario,
            "invalid",
            production,
        )


def test_solar_strategy_rejects_invalid_production():

    strategy = SolarSurplusChargingStrategy()
    scenario = create_scenario()
    consumption, _ = create_solar_inputs()

    with pytest.raises(
        TypeError,
        match="production_profile must be a SolarProductionProfile.",
    ):
        strategy.apply(
            scenario,
            consumption,
            "invalid",
        )


def test_solar_strategy_rejects_different_reference_years():

    strategy = SolarSurplusChargingStrategy()
    scenario = create_scenario()

    consumption_index = pd.date_range(
        "2024-01-01 00:00:00",
        "2024-12-31 23:00:00",
        freq="h",
    )

    consumption_index = consumption_index[
        ~(
            (consumption_index.month == 2)
            & (consumption_index.day == 29)
        )
    ]

    consumption = ConsumptionScenario(
        hourly_consumption=pd.Series(
            1.0,
            index=consumption_index,
            dtype=float,
        ),
        reference_year=2024,
    )

    _, production = create_solar_inputs()

    with pytest.raises(
        ValueError,
        match="same reference year",
    ):
        strategy.apply(
            scenario,
            consumption,
            production,
        )

class TestSolarNightChargingStrategy:
    """Tests para la estrategia solar con fallback nocturno."""

    def test_returns_ev_scenario(self):
        ev_scenario = create_scenario()

        consumption = create_consumption_scenario()
        production = create_solar_production_profile()

        strategy = SolarNightChargingStrategy()

        result = strategy.apply(
            ev_scenario,
            consumption,
            production,
        )

        assert isinstance(result, EVScenario)

    def test_preserves_annual_consumption(self):
        ev_scenario = create_scenario()

        consumption = create_consumption_scenario()
        production = create_solar_production_profile()

        strategy = SolarNightChargingStrategy()

        result = strategy.apply(
            ev_scenario,
            consumption,
            production,
        )

        assert result.annual_consumption == pytest.approx(
            ev_scenario.annual_consumption
        )

    def test_uses_solar_surplus_before_night_fallback(self):
        index = create_index()

        ev_values = pd.Series(
            0.0,
            index=index,
            dtype=float,
        )

        ev_values.loc["2025-01-01 12:00"] = 2.0
        ev_values.loc["2025-01-01 20:00"] = 1.0

        ev_scenario = EVScenario(
            hourly_consumption=ev_values,
            reference_year=2025,
        )

        consumption_values = pd.Series(
            0.0,
            index=index,
            dtype=float,
        )

        consumption_values.loc["2025-01-01 12:00"] = 1.0

        consumption = ConsumptionScenario(
            hourly_consumption=consumption_values,
            reference_year=2025,
        )

        production_values = pd.Series(
            0.0,
            index=index,
            dtype=float,
        )

        production_values.loc["2025-01-01 12:00"] = 3.0

        production = SolarProductionProfile(
            hourly_production=production_values,
            installed_power_kwp=1.0,
            reference_year=2025,
        )

        strategy = SolarNightChargingStrategy()

        result = strategy.apply(
            ev_scenario,
            consumption,
            production,
        )

        assert result.hourly_consumption.loc[
            "2025-01-01 12:00"
        ] == pytest.approx(2.0)

        night_hours = result.hourly_consumption.loc[
            "2025-01-01 00:00":"2025-01-01 06:00"
        ]

        assert night_hours.sum() == pytest.approx(1.0)

    def test_remaining_energy_goes_to_night_window(self):
        index = create_index()

        ev_values = pd.Series(
            0.0,
            index=index,
            dtype=float,
        )

        ev_values.loc["2025-01-01 12:00"] = 2.0

        ev_scenario = EVScenario(
            hourly_consumption=ev_values,
            reference_year=2025,
        )

        consumption_values = pd.Series(
            0.0,
            index=index,
            dtype=float,
        )

        consumption_values.loc["2025-01-01 12:00"] = 1.0

        consumption = ConsumptionScenario(
            hourly_consumption=consumption_values,
            reference_year=2025,
        )

        production_values = pd.Series(
            0.0,
            index=index,
            dtype=float,
        )

        production_values.loc["2025-01-01 12:00"] = 1.5

        production = SolarProductionProfile(
            hourly_production=production_values,
            installed_power_kwp=1.0,
            reference_year=2025,
        )

        strategy = SolarNightChargingStrategy()

        result = strategy.apply(
            ev_scenario,
            consumption,
            production,
        )

        # 0.5 kWh de excedente FV:
        # 1.5 kWh de producción - 1 kWh de consumo doméstico.
        # Quedan 1.5 kWh para la ventana nocturna.
        assert result.hourly_consumption.loc[
            "2025-01-01 12:00"
        ] == pytest.approx(0.5)

        night_hours = result.hourly_consumption.loc[
            "2025-01-01 00:00":"2025-01-01 06:00"
        ]

        assert night_hours.sum() == pytest.approx(1.5)

        assert (
            result.hourly_consumption.loc[
                "2025-01-01 07:00"
            ]
            == pytest.approx(0.0)
        )

    def test_does_not_move_energy_between_days(self):
        index = create_index()

        ev_values = pd.Series(
            0.0,
            index=index,
            dtype=float,
        )

        ev_values.loc["2025-01-01 12:00"] = 2.0
        ev_values.loc["2025-01-02 12:00"] = 2.0

        ev_scenario = EVScenario(
            hourly_consumption=ev_values,
            reference_year=2025,
        )

        consumption_values = pd.Series(
            0.0,
            index=index,
            dtype=float,
        )

        consumption_values.loc["2025-01-01 12:00"] = 1.0
        consumption_values.loc["2025-01-02 12:00"] = 1.0

        consumption = ConsumptionScenario(
            hourly_consumption=consumption_values,
            reference_year=2025,
        )

        production_values = pd.Series(
            0.0,
            index=index,
            dtype=float,
        )

        production_values.loc["2025-01-01 12:00"] = 3.0

        production = SolarProductionProfile(
            hourly_production=production_values,
            installed_power_kwp=1.0,
            reference_year=2025,
        )

        strategy = SolarNightChargingStrategy()

        result = strategy.apply(
            ev_scenario,
            consumption,
            production,
        )

        # El día 1 puede cubrir sus 2 kWh con FV.
        assert result.hourly_consumption.loc[
            "2025-01-01 12:00"
        ] == pytest.approx(2.0)

        # El día 2 no puede utilizar el excedente del día 1.
        assert result.hourly_consumption.loc[
            "2025-01-02 12:00"
        ] == pytest.approx(0.0)

        day_2_night = result.hourly_consumption.loc[
            "2025-01-02 00:00":"2025-01-02 06:00"
        ]

        assert day_2_night.sum() == pytest.approx(2.0)

    def test_rejects_invalid_ev_scenario(self):
        strategy = SolarNightChargingStrategy()

        consumption = create_consumption_scenario()
        production = create_solar_production_profile()

        with pytest.raises(TypeError, match="ev_scenario"):
            strategy.apply(
                object(),
                consumption,
                production,
            )

    def test_rejects_invalid_consumption_scenario(self):
        strategy = SolarNightChargingStrategy()

        ev_scenario = create_scenario()
        production = create_solar_production_profile()

        with pytest.raises(
            TypeError,
            match="consumption_scenario",
        ):
            strategy.apply(
                ev_scenario,
                object(),
                production,
            )

    def test_rejects_invalid_production_profile(self):
        strategy = SolarNightChargingStrategy()

        ev_scenario = create_scenario()
        consumption = create_consumption_scenario()

        with pytest.raises(
            TypeError,
            match="production_profile",
        ):
            strategy.apply(
                ev_scenario,
                consumption,
                object(),
            )

    def test_rejects_different_reference_years(self):
        strategy = SolarNightChargingStrategy()

        ev_scenario = create_scenario()

        consumption_index = pd.date_range(
            "2024-01-01 00:00:00",
            "2024-12-31 23:00:00",
            freq="h",
        )

        consumption_index = consumption_index[
            ~(
                (consumption_index.month == 2)
                & (consumption_index.day == 29)
            )
        ]

        consumption_values = pd.Series(
            0.0,
            index=consumption_index,
            dtype=float,
        )

        consumption = ConsumptionScenario(
            hourly_consumption=consumption_values,
            reference_year=2024,
        )

        production = create_solar_production_profile()

        with pytest.raises(
            ValueError,
            match="same reference year",
        ):
            strategy.apply(
                ev_scenario,
                consumption,
                production,
            )

    def test_rejects_invalid_night_window(self):
        with pytest.raises(
            ValueError,
            match="start_hour",
        ):
            SolarNightChargingStrategy(
                start_hour=-1,
                end_hour=7,
            )

        with pytest.raises(
            ValueError,
            match="end_hour",
        ):
            SolarNightChargingStrategy(
                start_hour=0,
                end_hour=25,
            )

        with pytest.raises(
            ValueError,
            match="lower than end_hour",
        ):
            SolarNightChargingStrategy(
                start_hour=7,
                end_hour=7,
            )

    def test_fallback_works_without_original_night_demand(self):
        index = create_index()

        ev_values = pd.Series(
            0.0,
            index=index,
            dtype=float,
        )

        ev_values.loc["2025-01-01 12:00"] = 2.0

        ev_scenario = EVScenario(
            hourly_consumption=ev_values,
            reference_year=2025,
        )

        consumption_values = pd.Series(
            0.0,
            index=index,
            dtype=float,
        )

        consumption_values.loc[
            "2025-01-01 12:00"
        ] = 1.0

        consumption = ConsumptionScenario(
            hourly_consumption=consumption_values,
            reference_year=2025,
        )

        production_values = pd.Series(
            0.0,
            index=index,
            dtype=float,
        )

        production_values.loc[
            "2025-01-01 12:00"
        ] = 1.0

        production = SolarProductionProfile(
            hourly_production=production_values,
            installed_power_kwp=1.0,
            reference_year=2025,
        )

        strategy = SolarNightChargingStrategy()

        result = strategy.apply(
            ev_scenario,
            consumption,
            production,
        )

        # No hay demanda EV nocturna original.
        # Como no existe excedente FV disponible, toda la demanda EV
        # debe distribuirse dentro de la ventana 00:00-07:00.
        night_hours = result.hourly_consumption.loc[
            "2025-01-01 00:00":"2025-01-01 06:00"
        ]

        assert night_hours.sum() == pytest.approx(2.0)

        assert result.annual_consumption == pytest.approx(
            ev_scenario.annual_consumption
        )