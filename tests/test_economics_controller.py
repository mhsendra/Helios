from unittest.mock import MagicMock, call

from helios.core.controllers.economics_controller import (
    EconomicsController
)


class TestEconomicsController:

    def setup_method(self):

        self.analyzer = MagicMock()
        self.configuration = MagicMock()

        self.controller = EconomicsController(
            self.analyzer,
            self.configuration
        )

    def test_calculate_calls_steps_in_order(self):

        engine = (
            self.analyzer.economics_engine
        )

        self.controller.calculate()

        assert engine.mock_calls == [
            call.calculate_cost_without_pv(
                self.analyzer.dataset
            ),
            call.calculate_export_income(
                self.analyzer.solar.energy_balance,
                self.analyzer.dataset,
            ),
            call.calculate_cost_with_pv(
                self.analyzer.solar.energy_balance,
                self.analyzer.dataset,
            ),
            call.calculate_annual_savings(),
            call.calculate_net_investment(
                self.configuration
            ),
            call.calculate_cash_flow(
                self.configuration,
                25
            ),
            call.calculate_economic_indicators(
                self.configuration.discount_rate
            ),
        ]

    def test_reports(self):

        economics = self.analyzer.economics_engine

        economics.cost_without_pv = 1000.0
        economics.grid_import_cost = 500.0
        economics.export_income = 200.0
        economics.cost_with_pv = 300.0
        economics.annual_savings = 700.0
        economics.net_investment = 12490.0
        economics.payback_years = 5.34
        economics.cash_flow = MagicMock()
        economics.npv = 22071.16
        economics.irr = 0.188

        self.configuration.discount_rate = 0.05

        self.controller.reports_engine.annual_economics = MagicMock()

        self.controller.reports()

        self.controller.reports_engine.annual_economics.assert_called_once_with(
            1000.0,
            500.0,
            200.0,
            300.0,
            700.0,
            12490.0,
            5.34,
            economics.cash_flow,
            22071.16,
            0.05,
            0.188,
        )

    def test_economic_summary_delegates_to_engine(self):

        engine = self.analyzer.economics_engine

        expected = object()

        engine.economic_summary.return_value = expected

        result = self.controller.economic_summary()

        engine.economic_summary.assert_called_once_with()

        assert result is expected

    def test_calculate_scenario_delegates_to_engine(self):

        engine = self.analyzer.economics_engine

        scenario = MagicMock()
        expected = object()

        engine.calculate_scenario.return_value = expected

        result = self.controller.calculate_scenario(
        scenario
        )

        engine.calculate_scenario.assert_called_once_with(
        scenario,
        self.configuration,
        self.analyzer.dataset,
        self.analyzer.solar.energy_balance,
        self.analyzer.dataset,
        )

        assert result is expected

    def test_calculate_scenarios_delegates_to_engine(self):

        engine = self.analyzer.economics_engine

        scenarios = [MagicMock()]
        expected = object()

        engine.calculate_scenarios.return_value = expected

        result = self.controller.calculate_scenarios(
        scenarios
        )

        engine.calculate_scenarios.assert_called_once_with(
        scenarios,
        self.configuration,
        self.analyzer.dataset,
        self.analyzer.solar.energy_balance,
        self.analyzer.dataset,
        25,
        )

        assert result is expected

    def test_scenarios_report_delegates_to_report_engine(self):

        economics = self.analyzer.economics_engine

        economics.scenario_results = [
        MagicMock(),
        MagicMock(),
        ]

        self.controller.reports_engine.economic_scenarios = MagicMock()

        self.controller.scenarios_report()

        self.controller.reports_engine.economic_scenarios.assert_called_once_with(
        economics.scenario_results
        )

    def test_calculate_net_investment_delegates_to_engine(self):

        engine = self.analyzer.economics_engine

        expected = 10000.0

        engine.calculate_net_investment.return_value = expected

        result = self.controller.calculate_net_investment()

        engine.calculate_net_investment.assert_called_once_with(
            self.configuration
        )

        assert result == expected


    def test_calculate_cash_flow_delegates_to_engine(self):

        engine = self.analyzer.economics_engine

        expected = object()

        engine.calculate_cash_flow.return_value = expected

        result = self.controller.calculate_cash_flow()

        engine.calculate_cash_flow.assert_called_once_with(
            self.configuration,
            25
        )

        assert result is expected


    def test_calculate_economic_indicators_delegates_to_engine(self):

        engine = self.analyzer.economics_engine

        expected = {
            "payback_years": 5.34,
            "npv": 22071.16,
            "irr": 0.188,
        }

        engine.calculate_economic_indicators.return_value = expected

        self.configuration.discount_rate = 0.05

        result = self.controller.calculate_economic_indicators()

        engine.calculate_economic_indicators.assert_called_once_with(
            0.05
        )

        assert result is expected

    def test_reports_calls_scenarios_report(self):

        economics = self.analyzer.economics_engine

        economics.cost_without_pv = 1000.0
        economics.grid_import_cost = 500.0
        economics.export_income = 200.0
        economics.cost_with_pv = 300.0
        economics.annual_savings = 700.0
        economics.net_investment = 12490.0
        economics.payback_years = 5.34
        economics.cash_flow = MagicMock()
        economics.npv = 22071.16
        economics.irr = 0.188

        self.configuration.discount_rate = 0.05

        self.controller.reports_engine.annual_economics = MagicMock()

        self.controller.scenarios_report = MagicMock()

        self.controller.reports()

        self.controller.scenarios_report.assert_called_once_with()