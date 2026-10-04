import pandas as pd
import pytest

from helios.core.diagnostics import DiagnosticResult
from helios.core.diagnostics.energy import (
    EnergyDiagnostics,
)


def make_balance(
    consumption,
    production,
    self_consumption,
    grid_import,
    grid_export,
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


class TestEnergyDiagnostics:

    def test_detects_high_solar_surplus(self):
        balance = make_balance(
            consumption=[2.0, 2.0],
            production=[10.0, 10.0],
            self_consumption=[2.0, 2.0],
            grid_import=[0.0, 0.0],
            grid_export=[8.0, 8.0],
        )

        diagnostics = EnergyDiagnostics.diagnose(
            balance
        )

        assert len(diagnostics) == 1

        diagnostic = diagnostics[0]

        assert isinstance(
            diagnostic,
            DiagnosticResult,
        )

        assert diagnostic.code == (
            "HIGH_SOLAR_SURPLUS"
        )

        assert diagnostic.category == "energy"
        assert diagnostic.severity == "warning"

        assert diagnostic.evidence[
            "production_kwh"
        ] == pytest.approx(20.0)

        assert diagnostic.evidence[
            "grid_export_kwh"
        ] == pytest.approx(16.0)

        assert diagnostic.evidence[
            "export_ratio_percent"
        ] == pytest.approx(80.0)

    def test_detects_high_grid_dependence(self):
        balance = make_balance(
            consumption=[10.0, 10.0],
            production=[2.0, 2.0],
            self_consumption=[2.0, 2.0],
            grid_import=[8.0, 8.0],
            grid_export=[0.0, 0.0],
        )

        diagnostics = EnergyDiagnostics.diagnose(
            balance
        )

        assert len(diagnostics) == 1

        diagnostic = diagnostics[0]

        assert diagnostic.code == (
            "HIGH_GRID_DEPENDENCE"
        )

        assert diagnostic.evidence[
            "consumption_kwh"
        ] == pytest.approx(20.0)

        assert diagnostic.evidence[
            "grid_import_kwh"
        ] == pytest.approx(16.0)

        assert diagnostic.evidence[
            "grid_import_ratio_percent"
        ] == pytest.approx(80.0)

    def test_detects_both_conditions_when_present(self):
        balance = make_balance(
            consumption=[10.0, 10.0],
            production=[20.0, 20.0],
            self_consumption=[10.0, 10.0],
            grid_import=[0.0, 0.0],
            grid_export=[10.0, 10.0],
        )

        diagnostics = EnergyDiagnostics.diagnose(
            balance
        )

        codes = {
            diagnostic.code
            for diagnostic in diagnostics
        }

        assert codes == {
            "HIGH_SOLAR_SURPLUS",
        }

    def test_returns_no_diagnostics_for_balanced_system(self):
        balance = make_balance(
            consumption=[10.0, 10.0],
            production=[10.0, 10.0],
            self_consumption=[10.0, 10.0],
            grid_import=[0.0, 0.0],
            grid_export=[0.0, 0.0],
        )

        diagnostics = EnergyDiagnostics.diagnose(
            balance
        )

        assert diagnostics == []

    def test_threshold_is_not_triggered_below_50_percent(self):
        balance = make_balance(
            consumption=[10.0],
            production=[10.0],
            self_consumption=[6.0],
            grid_import=[4.0],
            grid_export=[4.0],
        )

        diagnostics = EnergyDiagnostics.diagnose(
            balance
        )

        codes = {
            diagnostic.code
            for diagnostic in diagnostics
        }

        assert "HIGH_SOLAR_SURPLUS" not in codes
        assert "HIGH_GRID_DEPENDENCE" not in codes

    def test_threshold_is_triggered_at_50_percent(self):
        balance = make_balance(
            consumption=[10.0],
            production=[10.0],
            self_consumption=[5.0],
            grid_import=[5.0],
            grid_export=[5.0],
        )

        diagnostics = EnergyDiagnostics.diagnose(
            balance
        )

        codes = {
            diagnostic.code
            for diagnostic in diagnostics
        }

        assert "HIGH_SOLAR_SURPLUS" in codes
        assert "HIGH_GRID_DEPENDENCE" in codes

    def test_zero_production_does_not_create_surplus_diagnostic(
        self,
    ):
        balance = make_balance(
            consumption=[10.0],
            production=[0.0],
            self_consumption=[0.0],
            grid_import=[10.0],
            grid_export=[0.0],
        )

        diagnostics = EnergyDiagnostics.diagnose(
            balance
        )

        codes = {
            diagnostic.code
            for diagnostic in diagnostics
        }

        assert "HIGH_SOLAR_SURPLUS" not in codes
        assert "HIGH_GRID_DEPENDENCE" in codes

    def test_zero_consumption_does_not_create_grid_dependence(
        self,
    ):
        balance = make_balance(
            consumption=[0.0],
            production=[10.0],
            self_consumption=[0.0],
            grid_import=[0.0],
            grid_export=[10.0],
        )

        diagnostics = EnergyDiagnostics.diagnose(
            balance
        )

        codes = {
            diagnostic.code
            for diagnostic in diagnostics
        }

        assert "HIGH_GRID_DEPENDENCE" not in codes
        assert "HIGH_SOLAR_SURPLUS" in codes

    def test_rejects_non_dataframe(self):
        with pytest.raises(
            TypeError,
            match="pandas DataFrame",
        ):
            EnergyDiagnostics.diagnose(
                "invalid"
            )

    def test_rejects_missing_columns(self):
        balance = pd.DataFrame(
            {
                "consumption_kwh": [10.0],
            }
        )

        with pytest.raises(
            ValueError,
            match="missing required columns",
        ):
            EnergyDiagnostics.diagnose(
                balance
            )

    def test_rejects_empty_balance(self):
        balance = pd.DataFrame(
            columns=[
                "consumption_kwh",
                "production_kwh",
                "self_consumption_kwh",
                "grid_import_kwh",
                "grid_export_kwh",
            ]
        )

        with pytest.raises(
            ValueError,
            match="cannot be empty",
        ):
            EnergyDiagnostics.diagnose(
                balance
            )

    def test_rejects_non_numeric_column(self):
        balance = make_balance(
            consumption=["10.0"],
            production=[10.0],
            self_consumption=[10.0],
            grid_import=[0.0],
            grid_export=[0.0],
        )

        with pytest.raises(
            TypeError,
            match="must be numeric",
        ):
            EnergyDiagnostics.diagnose(
                balance
            )

    def test_rejects_nan_values(self):
        balance = make_balance(
            consumption=[10.0],
            production=[10.0],
            self_consumption=[float("nan")],
            grid_import=[0.0],
            grid_export=[0.0],
        )

        with pytest.raises(
            ValueError,
            match="cannot contain NaN",
        ):
            EnergyDiagnostics.diagnose(
                balance
            )