import pytest

import pandas as pd

from reportlab.graphics.shapes import Drawing

from helios.reports.solar_report_charts import SolarReportCharts


class TestSolarReportCharts:

    def test_yearly_production_returns_drawing(self):

        result = SolarReportCharts.yearly_production(
            12500.0,
        )

        assert isinstance(result, Drawing)

    def test_yearly_production_accepts_zero(self):

        result = SolarReportCharts.yearly_production(
            0.0,
        )

        assert isinstance(result, Drawing)

    def test_yearly_production_rejects_negative_value(self):

        with pytest.raises(
            ValueError,
            match="production cannot be negative",
        ):
            SolarReportCharts.yearly_production(
                -1.0,
            )

    def test_yearly_production_preserves_requested_size(self):

        result = SolarReportCharts.yearly_production(
            12500.0,
        )

        assert result.width > 0
        assert result.height > 0

    def test_yearly_production_creates_independent_drawings(self):

        first = SolarReportCharts.yearly_production(
            12500.0,
        )

        second = SolarReportCharts.yearly_production(
            12500.0,
        )

        assert first is not second

    def test_monthly_production_returns_drawing(self):

        monthly_production = pd.Series(
            [
                850.0,
                1020.0,
                1250.0,
                1480.0,
                1650.0,
                1720.0,
                1800.0,
                1760.0,
                1510.0,
                1180.0,
                920.0,
                780.0,
            ],
            index=pd.date_range(
                "2025-01-31",
                periods=12,
                freq="ME",
            ),
        )

        result = SolarReportCharts.monthly_production(
            monthly_production,
        )

        assert isinstance(result, Drawing)


    def test_monthly_production_rejects_empty_data(self):

        monthly_production = pd.Series(
            dtype=float,
        )

        with pytest.raises(
            ValueError,
            match="monthly production data is required",
        ):
            SolarReportCharts.monthly_production(
                monthly_production,
            )


    def test_monthly_production_rejects_negative_values(self):

        monthly_production = pd.Series(
            [
                850.0,
                1020.0,
                -1250.0,
                1480.0,
            ],
            index=pd.date_range(
                "2025-01-31",
                periods=4,
                freq="ME",
            ),
        )

        with pytest.raises(
            ValueError,
            match="monthly production cannot be negative",
        ):
            SolarReportCharts.monthly_production(
                monthly_production,
            )

    def test_energy_balance_creates_drawing(self):
        result = SolarReportCharts.energy_balance(
            yearly_production_kwh=12500.0,
            yearly_consumption_kwh=19541.72,
            self_consumption_kwh=8500.0,
            grid_import_kwh=11041.72,
            grid_export_kwh=4000.0,
        )

        assert result is not None

    def test_energy_balance_rejects_negative_production(self):
        with pytest.raises(
            ValueError,
            match="energy balance values cannot be negative",
        ):
            SolarReportCharts.energy_balance(
                yearly_production_kwh=-1.0,
                yearly_consumption_kwh=19541.72,
                self_consumption_kwh=8500.0,
                grid_import_kwh=11041.72,
                grid_export_kwh=4000.0,
            )

    def test_energy_balance_rejects_negative_consumption(self):
        with pytest.raises(
            ValueError,
            match="energy balance values cannot be negative",
        ):
            SolarReportCharts.energy_balance(
                yearly_production_kwh=12500.0,
                yearly_consumption_kwh=-1.0,
                self_consumption_kwh=8500.0,
                grid_import_kwh=11041.72,
                grid_export_kwh=4000.0,
            )