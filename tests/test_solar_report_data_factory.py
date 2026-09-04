import pandas as pd

import pytest

from helios.reports.solar_report_data import SolarReportData
from helios.reports.solar_report_data_factory import (
    SolarReportDataFactory,
)


class TestSolarReportDataFactory:

    @staticmethod
    def _solar_controller():

        solar = type("SolarController", (), {})()

        sizing_result = type("SizingResult", (), {})()

        sizing_result.installed_power_kwp = 8.1
        sizing_result.panel_count = 15
        sizing_result.annual_production_kwh = 12500.0
        sizing_result.annual_consumption_kwh = 19541.72
        sizing_result.self_sufficiency_percent = 64.0

        evaluation = type("Evaluation", (), {})()
        candidate = type("Candidate", (), {})()

        candidate.panel_power_wp = 540.0
        evaluation.candidate = candidate
        sizing_result.evaluation = evaluation

        solar.sizing_result = sizing_result

        solar.specific_production = 1543.21
        solar.self_consumption = 8500.0
        solar.grid_export = 4000.0
        solar.grid_import = 11041.72
        solar.coverage = 43.5

        solar.monthly_production = pd.Series(
            [
                850,
                1020,
                1250,
                1480,
                1650,
                1720,
                1800,
                1760,
                1510,
                1180,
                920,
                780,
            ],
            index=pd.date_range(
                "2025-01-31",
                periods=12,
                freq="ME",
            ),
        )

        solar.statistics = {
            "productive_hours": 4380,
            "daily_average": 34.25,
            "monthly_average": 1041.67,
            "maximum_power": 7.85,
            "capacity_factor": 17.62,
        }

        return solar

    @staticmethod
    def _economics_controller():

        economics_controller = type(
            "EconomicsController",
            (),
            {},
        )()

        economics_engine = type(
            "EconomicsEngine",
            (),
            {},
        )()

        economics_engine.net_investment = 12490.0
        economics_engine.annual_savings = 2338.0
        economics_engine.payback_years = 5.34
        economics_engine.npv = 22071.16
        economics_engine.irr = 0.188

        economics_engine.scenario_results = [
            type(
                "EconomicScenarioResult",
                (),
                {
                    "name": "Conservador",
                    "annual_savings": 2000.0,
                    "payback_years": 6.25,
                    "npv": 18000.0,
                    "irr": 0.15,
                },
            )(),
            type(
                "EconomicScenarioResult",
                (),
                {
                    "name": "Base",
                    "annual_savings": 2338.0,
                    "payback_years": 5.34,
                    "npv": 22071.16,
                    "irr": 0.188,
                },
            )(),
            type(
                "EconomicScenarioResult",
                (),
                {
                    "name": "Optimista",
                    "annual_savings": 2700.0,
                    "payback_years": 4.63,
                    "npv": 28000.0,
                    "irr": 0.22,
                },
            )(),
        ]

        analyzer = type("Analyzer", (), {})()
        analyzer.economics_engine = economics_engine

        economics_controller.analyzer = analyzer

        return economics_controller

    def test_create_returns_solar_report_data(self):

        solar_controller = self._solar_controller()
        economics_controller = self._economics_controller()

        result = SolarReportDataFactory.create(
            solar_controller,
            economics_controller,
        )

        assert isinstance(
            result,
            SolarReportData,
        )

    def test_create_contains_installation_values(self):

        result = SolarReportDataFactory.create(
            self._solar_controller(),
            self._economics_controller(),
        )

        assert result.installed_power_kwp == 8.1
        assert result.panel_count == 15
        assert result.panel_power_wp == 540.0

    def test_create_contains_production_values(self):

        result = SolarReportDataFactory.create(
            self._solar_controller(),
            self._economics_controller(),
        )

        assert result.yearly_production_kwh == 12500.0
        assert result.specific_production_kwh_kwp == 1543.21

        pd.testing.assert_series_equal(
            result.monthly_production,
            self._solar_controller().monthly_production,
        )

    def test_create_uses_solar_statistics_results(self):

        result = SolarReportDataFactory.create(
            self._solar_controller(),
            self._economics_controller(),
        )

        assert result.productive_hours == 4380
        assert result.daily_average_kwh == 34.25
        assert result.monthly_average_kwh == 1041.67
        assert result.maximum_power_kw == 7.85
        assert result.capacity_factor_percent == 17.62

    def test_create_contains_energy_balance_values(self):

        result = SolarReportDataFactory.create(
            self._solar_controller(),
            self._economics_controller(),
        )

        assert result.yearly_consumption_kwh == 19541.72
        assert result.self_consumption_kwh == 8500.0
        assert result.grid_export_kwh == 4000.0
        assert result.grid_import_kwh == 11041.72
        assert result.self_consumption_rate_percent == 43.5
        assert result.self_sufficiency_rate_percent == 64.0

    def test_create_contains_economics_values(self):

        result = SolarReportDataFactory.create(
            self._solar_controller(),
            self._economics_controller(),
        )

        assert result.investment_eur == 12490.0
        assert result.yearly_savings_eur == 2338.0
        assert result.payback_years == 5.34
        assert result.net_present_value_eur == 22071.16
        assert (
            result.internal_rate_of_return_percent
            == 18.8
        )

    def test_create_contains_economic_scenarios(self):

        result = SolarReportDataFactory.create(
            self._solar_controller(),
            self._economics_controller(),
        )

        assert len(result.scenario_results) == 3

        assert [
            scenario.name
            for scenario in result.scenario_results
        ] == [
            "Conservador",
            "Base",
            "Optimista",
        ]

    def test_create_preserves_economic_scenario_results(self):

        economics_controller = (
            self._economics_controller()
        )

        result = SolarReportDataFactory.create(
            self._solar_controller(),
            economics_controller,
        )

        expected = (
            economics_controller
            .analyzer
            .economics_engine
            .scenario_results
        )

        assert result.scenario_results is expected

    def test_create_contains_exact_economic_scenario_values(
        self,
    ):

        result = SolarReportDataFactory.create(
            self._solar_controller(),
            self._economics_controller(),
        )

        assert [
            (
                scenario.name,
                scenario.annual_savings,
                scenario.payback_years,
                scenario.npv,
                scenario.irr,
            )
            for scenario in result.scenario_results
        ] == [
            (
                "Conservador",
                2000.0,
                6.25,
                18000.0,
                0.15,
            ),
            (
                "Base",
                2338.0,
                5.34,
                22071.16,
                0.188,
            ),
            (
                "Optimista",
                2700.0,
                4.63,
                28000.0,
                0.22,
            ),
        ]

    def test_create_requires_economic_scenario_results(
        self,
    ):

        economics_controller = (
            self._economics_controller()
        )

        economics_controller.analyzer.economics_engine.scenario_results = []

        with pytest.raises(
            ValueError,
            match="economic scenario results are required",
        ):
            SolarReportDataFactory.create(
                self._solar_controller(),
                economics_controller,
            )

    def test_factory_does_not_calculate_solar(self):

        solar_controller = self._solar_controller()
        economics_controller = self._economics_controller()

        solar_controller.calculate = pytest.fail

        SolarReportDataFactory.create(
            solar_controller,
            economics_controller,
        )

    def test_factory_does_not_calculate_economics(self):

        solar_controller = self._solar_controller()
        economics_controller = self._economics_controller()

        economics_controller.calculate = pytest.fail

        SolarReportDataFactory.create(
            solar_controller,
            economics_controller,
        )

    def test_create_requires_solar_controller(self):

        with pytest.raises(
            ValueError,
            match="solar controller is required",
        ):
            SolarReportDataFactory.create(
                None,
                self._economics_controller(),
            )

    def test_create_requires_economics_controller(self):

        with pytest.raises(
            ValueError,
            match="economics controller is required",
        ):
            SolarReportDataFactory.create(
                self._solar_controller(),
                None,
            )

    def test_create_requires_sizing_result(self):

        solar_controller = self._solar_controller()
        solar_controller.sizing_result = None

        with pytest.raises(
            ValueError,
            match="solar installation sizing is required",
        ):
            SolarReportDataFactory.create(
                solar_controller,
                self._economics_controller(),
            )

    def test_create_requires_solar_statistics(self):

        solar_controller = self._solar_controller()
        solar_controller.statistics = None

        with pytest.raises(
            ValueError,
            match="solar statistics are required",
        ):
            SolarReportDataFactory.create(
                solar_controller,
                self._economics_controller(),
            )