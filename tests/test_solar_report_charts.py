import pytest

import pandas as pd

from reportlab.graphics.shapes import Drawing

from reportlab.graphics.charts.barcharts import VerticalBarChart

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

    def test_monthly_consumption_vs_production_returns_drawing(self):

        monthly_consumption = pd.Series(
            [
                1600.0,
                1500.0,
                1550.0,
                1580.0,
                1650.0,
                1700.0,
                1720.0,
                1680.0,
                1570.0,
                1600.0,
                1650.0,
                1741.72,
            ],
            index=pd.date_range(
                "2025-01-31",
                periods=12,
                freq="ME",
            ),
        )

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

        result = (
            SolarReportCharts
            .monthly_consumption_vs_production(
                monthly_consumption,
                monthly_production,
            )
        )

        assert isinstance(result, Drawing)


    def test_monthly_consumption_vs_production_contains_two_series(self):

        monthly_consumption = pd.Series(
            [1000.0, 1100.0, 1200.0],
            index=pd.date_range(
                "2025-01-31",
                periods=3,
                freq="ME",
            ),
        )

        monthly_production = pd.Series(
            [800.0, 1300.0, 1500.0],
            index=pd.date_range(
                "2025-01-31",
                periods=3,
                freq="ME",
            ),
        )

        drawing = (
            SolarReportCharts
            .monthly_consumption_vs_production(
                monthly_consumption,
                monthly_production,
            )
        )

        chart = next(
            item
            for item in drawing.contents
            if isinstance(item, VerticalBarChart)
        )

        assert chart.data == [
            [1000.0, 1100.0, 1200.0],
            [800.0, 1300.0, 1500.0],
        ]

        assert chart.categoryAxis.categoryNames == [
            "Jan",
            "Feb",
            "Mar",
        ]


    def test_monthly_consumption_vs_production_rejects_empty_consumption(self):

        monthly_consumption = pd.Series(
            dtype=float,
        )

        monthly_production = pd.Series(
            [800.0, 900.0],
            index=pd.date_range(
                "2025-01-31",
                periods=2,
                freq="ME",
            ),
        )

        with pytest.raises(
            ValueError,
            match="monthly consumption data is required",
        ):
            (
                SolarReportCharts
                .monthly_consumption_vs_production(
                    monthly_consumption,
                    monthly_production,
                )
            )


    def test_monthly_consumption_vs_production_rejects_mismatched_lengths(self):

        monthly_consumption = pd.Series(
            [1000.0, 1100.0],
            index=pd.date_range(
                "2025-01-31",
                periods=2,
                freq="ME",
            ),
        )

        monthly_production = pd.Series(
            [800.0, 900.0, 1000.0],
            index=pd.date_range(
                "2025-01-31",
                periods=3,
                freq="ME",
            ),
        )

        with pytest.raises(
            ValueError,
            match="must have the same length",
        ):
            (
                SolarReportCharts
                .monthly_consumption_vs_production(
                    monthly_consumption,
                    monthly_production,
                )
            )


    def test_monthly_consumption_vs_production_rejects_negative_consumption(self):

        monthly_consumption = pd.Series(
            [1000.0, -100.0],
            index=pd.date_range(
                "2025-01-31",
                periods=2,
                freq="ME",
            ),
        )

        monthly_production = pd.Series(
            [800.0, 900.0],
            index=pd.date_range(
                "2025-01-31",
                periods=2,
                freq="ME",
            ),
        )

        with pytest.raises(
            ValueError,
            match="monthly consumption cannot be negative",
        ):
            (
                SolarReportCharts
                .monthly_consumption_vs_production(
                    monthly_consumption,
                    monthly_production,
                )
            )


    def test_battery_marginal_savings_returns_drawing(self):

        recommendations = [
            type(
                "BatteryRecommendation",
                (),
                {
                    "capacity_kwh": 5.0,
                    "marginal_savings_per_kwh": 0.0,
                },
            )(),
            type(
                "BatteryRecommendation",
                (),
                {
                    "capacity_kwh": 8.3,
                    "marginal_savings_per_kwh": 20.43,
                },
            ),
            type(
                "BatteryRecommendation",
                (),
                {
                    "capacity_kwh": 16.6,
                    "marginal_savings_per_kwh": 9.74,
                },
            ),
        ]

        result = (
            SolarReportCharts
            .battery_marginal_savings(
                recommendations,
            )
        )

        assert isinstance(result, Drawing)


    def test_battery_marginal_savings_contains_expected_data(self):

        recommendations = [
            type(
                "BatteryRecommendation",
                (),
                {
                    "capacity_kwh": 5.0,
                    "marginal_savings_per_kwh": 0.0,
                },
            )(),
            type(
                "BatteryRecommendation",
                (),
                {
                    "capacity_kwh": 8.3,
                    "marginal_savings_per_kwh": 20.43,
                },
            ),
            type(
                "BatteryRecommendation",
                (),
                {
                    "capacity_kwh": 16.6,
                    "marginal_savings_per_kwh": 9.74,
                },
            ),
        ]

        drawing = (
            SolarReportCharts
            .battery_marginal_savings(
                recommendations,
            )
        )

        chart = next(
            item
            for item in drawing.contents
            if isinstance(item, VerticalBarChart)
        )

        assert chart.data == [
            [0.0, 20.43, 9.74]
        ]

        assert chart.categoryAxis.categoryNames == [
            "5.0",
            "8.3",
            "16.6",
        ]


    def test_battery_marginal_savings_rejects_empty_data(self):

        with pytest.raises(
            ValueError,
            match="battery recommendation data is required",
        ):
            SolarReportCharts.battery_marginal_savings([])

    def test_battery_marginal_savings_accepts_negative_values(self):
        recommendations = [
            type(
                "BatteryRecommendation",
                (),
                {
                    "capacity_kwh": 5.0,
                    "marginal_savings_per_kwh": -12.0,
                },
            )(),
            type(
                "BatteryRecommendation",
                (),
                {
                    "capacity_kwh": 8.3,
                    "marginal_savings_per_kwh": 20.0,
                },
            )(),
        ]

        drawing = SolarReportCharts.battery_marginal_savings(
            recommendations
        )

        chart = next(
            item
            for item in drawing.contents
            if isinstance(item, VerticalBarChart)
        )

        assert chart.data == [[-12.0, 20.0]]
        assert chart.valueAxis.valueMin < 0
        assert chart.valueAxis.valueMax > 0


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

    def test_economic_scenarios_returns_drawing(self):

        scenarios = [
            type(
                "ScenarioResult",
                (),
                {
                    "name": "Conservador",
                    "annual_savings": 2000.0,
                },
            )(),
            type(
                "ScenarioResult",
                (),
                {
                    "name": "Base",
                    "annual_savings": 2338.0,
                },
            )(),
            type(
                "ScenarioResult",
                (),
                {
                    "name": "Optimista",
                    "annual_savings": 2700.0,
                },
            )(),
        ]

        drawing = SolarReportCharts.economic_scenarios(
            scenarios
        )

        assert isinstance(
            drawing,
            Drawing,
        )


    def test_economic_scenarios_contains_expected_data(self):

        scenarios = [
            type(
                "ScenarioResult",
                (),
                {
                    "name": "Conservador",
                    "annual_savings": 2000.0,
                },
            )(),
            type(
                "ScenarioResult",
                (),
                {
                    "name": "Base",
                    "annual_savings": 2338.0,
                },
            )(),
            type(
                "ScenarioResult",
                (),
                {
                    "name": "Optimista",
                    "annual_savings": 2700.0,
                },
            )(),
        ]

        drawing = SolarReportCharts.economic_scenarios(
            scenarios
        )

        chart = next(
            item
            for item in drawing.contents
            if isinstance(item, VerticalBarChart)
        )

        assert chart.data == [
            [2000.0, 2338.0, 2700.0]
        ]

        assert chart.categoryAxis.categoryNames == [
            "Conservador",
            "Base",
            "Optimista",
        ]


    def test_economic_scenarios_rejects_empty_data(self):

        with pytest.raises(
            ValueError,
            match="economic scenario data is required",
        ):
            SolarReportCharts.economic_scenarios([])


    def test_economic_scenarios_rejects_none(self):

        with pytest.raises(
            ValueError,
            match="economic scenario data is required",
        ):
            SolarReportCharts.economic_scenarios(None)


    def test_economic_scenarios_rejects_negative_savings(self):

        scenarios = [
            type(
                "ScenarioResult",
                (),
                {
                    "name": "Conservador",
                    "annual_savings": -100.0,
                },
            )(),
        ]

        with pytest.raises(
            ValueError,
            match="annual savings cannot be negative",
        ):
            SolarReportCharts.economic_scenarios(
                scenarios
            )

    def test_monthly_consumption_vs_production_accepts_matching_months_different_years(
        self,
    ):
        monthly_consumption = pd.Series(
            [1000.0, 1100.0, 1200.0],
            index=pd.date_range(
                "2025-01-31",
                periods=3,
                freq="ME",
            ),
        )

        monthly_production = pd.Series(
            [800.0, 900.0, 1000.0],
            index=pd.date_range(
                "2026-01-31",
                periods=3,
                freq="ME",
            ),
        )

        drawing = SolarReportCharts.monthly_consumption_vs_production(
            monthly_consumption,
            monthly_production,
        )

        assert drawing is not None

    def test_monthly_consumption_vs_production_accepts_different_years(self):
        consumption_index = pd.date_range(
            "2025-01-01",
            periods=12,
            freq="MS",
        )
        production_index = pd.date_range(
            "2023-01-01",
            periods=12,
            freq="MS",
        )

        monthly_consumption = pd.Series(
            [100.0] * 12,
            index=consumption_index,
        )
        monthly_production = pd.Series(
            [80.0] * 12,
            index=production_index,
        )

        drawing = SolarReportCharts.monthly_consumption_vs_production(
            monthly_consumption,
            monthly_production,
        )

        assert drawing is not None


    def test_monthly_consumption_vs_production_rejects_different_months(self):
        consumption_index = pd.date_range(
            "2025-01-01",
            periods=12,
            freq="MS",
        )
        production_index = pd.date_range(
            "2023-02-01",
            periods=12,
            freq="MS",
        )

        monthly_consumption = pd.Series(
            [100.0] * 12,
            index=consumption_index,
        )
        monthly_production = pd.Series(
            [80.0] * 12,
            index=production_index,
        )

        with pytest.raises(
            ValueError,
            match="same calendar months",
        ):
            SolarReportCharts.monthly_consumption_vs_production(
                monthly_consumption,
                monthly_production,
            )