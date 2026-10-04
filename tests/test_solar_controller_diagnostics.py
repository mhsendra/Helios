import pandas as pd

from helios.core.controllers.solar_controller import SolarController
from helios.core.diagnostics import DiagnosticResult


class _FakeSolarEngine:
    def __init__(self, energy_balance=None):
        self.energy_balance = energy_balance


class _FakeAnalyzer:
    def __init__(self, energy_balance=None):
        self.solar_engine = _FakeSolarEngine(energy_balance)


def _build_controller(energy_balance=None) -> SolarController:
    controller = SolarController.__new__(SolarController)
    controller.analyzer = _FakeAnalyzer(energy_balance)
    return controller


def _build_balance(
    *,
    consumption=(10.0,),
    production=(10.0,),
    self_consumption=(10.0,),
    grid_import=(0.0,),
    grid_export=(0.0,),
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "consumption_kwh": consumption,
            "production_kwh": production,
            "self_consumption_kwh": self_consumption,
            "grid_import_kwh": grid_import,
            "grid_export_kwh": grid_export,
        }
    )


def test_diagnostics_returns_empty_when_balance_is_not_available():
    controller = _build_controller(None)

    assert controller.diagnostics == []


def test_diagnostics_returns_empty_when_balance_is_empty():
    controller = _build_controller(
        _build_balance(
            consumption=(),
            production=(),
            self_consumption=(),
            grid_import=(),
            grid_export=(),
        )
    )

    assert controller.diagnostics == []


def test_diagnostics_returns_energy_diagnostics_from_balance():
    controller = _build_controller(
        _build_balance(
            consumption=(10.0, 10.0),
            production=(20.0, 20.0),
            self_consumption=(10.0, 10.0),
            grid_import=(10.0, 10.0),
            grid_export=(10.0, 10.0),
        )
    )

    diagnostics = controller.diagnostics

    assert len(diagnostics) == 2
    assert all(isinstance(item, DiagnosticResult) for item in diagnostics)

    codes = {item.code for item in diagnostics}

    assert codes == {
        "HIGH_SOLAR_SURPLUS",
        "HIGH_GRID_DEPENDENCE",
    }


def test_diagnostics_recalculates_from_current_balance():
    controller = _build_controller(
        _build_balance()
    )

    assert controller.diagnostics == []

    controller.analyzer.solar_engine.energy_balance = _build_balance(
        consumption=(10.0,),
        production=(30.0,),
        self_consumption=(10.0,),
        grid_import=(0.0,),
        grid_export=(20.0,),
    )

    diagnostics = controller.diagnostics

    assert len(diagnostics) == 1
    assert diagnostics[0].code == "HIGH_SOLAR_SURPLUS"