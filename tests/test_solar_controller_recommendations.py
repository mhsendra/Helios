import pandas as pd

from helios.core.controllers.solar_controller import SolarController
from helios.core.diagnostics import RecommendationResult


class _FakeSolarEngine:
    def __init__(self, energy_balance=None):
        self.energy_balance = energy_balance


class _FakeAnalyzer:
    def __init__(self, energy_balance=None):
        self.solar_engine = _FakeSolarEngine(energy_balance)


def _build_controller(
    energy_balance=None,
) -> SolarController:
    controller = SolarController.__new__(SolarController)
    controller.analyzer = _FakeAnalyzer(energy_balance)
    return controller


def _build_balance(
    consumption=(10.0, 10.0),
    production=(20.0, 20.0),
    self_consumption=(10.0, 10.0),
    grid_import=(0.0, 0.0),
    grid_export=(10.0, 10.0),
):
    return pd.DataFrame(
        {
            "consumption_kwh": consumption,
            "production_kwh": production,
            "self_consumption_kwh": self_consumption,
            "grid_import_kwh": grid_import,
            "grid_export_kwh": grid_export,
        }
    )


def test_recommendations_returns_empty_when_balance_is_not_available():
    controller = _build_controller(None)

    assert controller.recommendations == []


def test_recommendations_returns_empty_when_balance_is_empty():
    controller = _build_controller(
        _build_balance(
            consumption=(),
            production=(),
            self_consumption=(),
            grid_import=(),
            grid_export=(),
        )
    )

    assert controller.recommendations == []


def test_recommendations_are_derived_from_current_balance():
    controller = _build_controller(
        _build_balance(
            consumption=(10.0, 10.0),
            production=(20.0, 20.0),
            self_consumption=(10.0, 10.0),
            grid_import=(0.0, 0.0),
            grid_export=(10.0, 10.0),
        )
    )

    recommendations = controller.recommendations

    assert len(recommendations) == 1
    assert all(
        isinstance(item, RecommendationResult)
        for item in recommendations
    )
    assert recommendations[0].code == (
        "CONSIDER_SELF_CONSUMPTION_IMPROVEMENT"
    )


def test_recommendations_change_when_balance_changes():
    controller = _build_controller(
        _build_balance(
            consumption=(10.0, 10.0),
            production=(10.0, 10.0),
            self_consumption=(10.0, 10.0),
            grid_import=(0.0, 0.0),
            grid_export=(0.0, 0.0),
        )
    )

    assert controller.recommendations == []

    controller.analyzer.solar_engine.energy_balance = _build_balance(
        consumption=(10.0, 10.0),
        production=(30.0, 30.0),
        self_consumption=(10.0, 10.0),
        grid_import=(0.0, 0.0),
        grid_export=(20.0, 20.0),
    )

    recommendations = controller.recommendations

    assert len(recommendations) == 1
    assert recommendations[0].code == (
        "CONSIDER_SELF_CONSUMPTION_IMPROVEMENT"
    )