import pandas as pd
import pytest

from helios.core.consumption_scenario import ConsumptionScenario
from helios.ev.scenario import EVScenario
from helios.ev.solar_charging_strategy import SolarChargingStrategy
from helios.solar.production_profile import SolarProductionProfile


class DummySolarChargingStrategy(SolarChargingStrategy):
    """Implementación mínima para probar el contrato."""

    def apply(
        self,
        ev_scenario: EVScenario,
        consumption_scenario: ConsumptionScenario,
        production_profile: SolarProductionProfile,
    ) -> EVScenario:
        return ev_scenario


def create_index():
    return pd.date_range(
        "2025-01-01 00:00:00",
        "2025-12-31 23:00:00",
        freq="h",
    )


def create_ev_scenario():
    index = create_index()

    return EVScenario(
        hourly_consumption=pd.Series(
            1.0,
            index=index,
            dtype=float,
        ),
        reference_year=2025,
    )


def create_consumption_scenario():
    index = create_index()

    return ConsumptionScenario(
        hourly_consumption=pd.Series(
            2.0,
            index=index,
            dtype=float,
        ),
        reference_year=2025,
    )


def create_production_profile():
    index = create_index()

    return SolarProductionProfile(
        hourly_production=pd.Series(
            3.0,
            index=index,
            dtype=float,
        ),
        reference_year=2025,
        installed_power_kwp=8.1,
    )


def test_solar_charging_strategy_is_abstract():

    assert SolarChargingStrategy.__abstractmethods__ == {
        "apply"
    }


def test_concrete_solar_strategy_can_be_instantiated():

    strategy = DummySolarChargingStrategy()

    assert isinstance(
        strategy,
        SolarChargingStrategy,
    )


def test_concrete_solar_strategy_returns_ev_scenario():

    strategy = DummySolarChargingStrategy()

    result = strategy.apply(
        create_ev_scenario(),
        create_consumption_scenario(),
        create_production_profile(),
    )

    assert isinstance(
        result,
        EVScenario,
    )


def test_concrete_solar_strategy_receives_expected_inputs():

    strategy = DummySolarChargingStrategy()

    ev_scenario = create_ev_scenario()
    consumption_scenario = create_consumption_scenario()
    production_profile = create_production_profile()

    result = strategy.apply(
        ev_scenario,
        consumption_scenario,
        production_profile,
    )

    assert result is ev_scenario


def test_apply_requires_implementation():

    class IncompleteSolarStrategy(SolarChargingStrategy):
        pass

    with pytest.raises(TypeError):
        IncompleteSolarStrategy()