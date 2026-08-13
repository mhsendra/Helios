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