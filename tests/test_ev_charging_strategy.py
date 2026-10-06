import pandas as pd
import pytest

from helios.ev.charging_strategy import EVChargingStrategy
from helios.ev.scenario import EVScenario


class DummyChargingStrategy(EVChargingStrategy):
    """Implementación mínima para probar el contrato."""

    def apply(self, scenario: EVScenario) -> EVScenario:
        return scenario


def create_scenario():
    index = pd.date_range(
        "2025-01-01 00:00:00",
        "2025-12-31 23:00:00",
        freq="h",
    )

    return EVScenario(
        hourly_consumption=pd.Series(
            1.0,
            index=index,
            dtype=float,
        ),
        reference_year=2025,
    )


def test_charging_strategy_is_abstract():

    assert EVChargingStrategy.__abstractmethods__ == {
        "apply"
    }


def test_concrete_strategy_can_be_instantiated():

    strategy = DummyChargingStrategy()

    assert isinstance(
        strategy,
        EVChargingStrategy,
    )


def test_concrete_strategy_applies_to_scenario():

    strategy = DummyChargingStrategy()
    scenario = create_scenario()

    result = strategy.apply(scenario)

    assert result is scenario


def test_apply_requires_implementation():

    class IncompleteStrategy(EVChargingStrategy):
        pass

    with pytest.raises(TypeError):
        IncompleteStrategy()