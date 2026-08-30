from unittest.mock import MagicMock, call

import pytest

from helios.core.controllers.economics_controller import (
    EconomicsController,
)
from helios.core.economic_scenarios import EconomicScenario


class TestEconomicsController:

    def setup_method(self):

        self.analyzer = MagicMock()
        self.configuration = MagicMock()

        self.analyzer.dataset = MagicMock()
        self.analyzer.solar.energy_balance = MagicMock()
        self.analyzer.economics_engine = MagicMock()

        self.configuration.discount_rate = 0.05

        self.controller = EconomicsController(
            self.analyzer,
            self.configuration,
        )

    # ==========================================================
    # Inicialización
    # ==========================================================

    def test_initialization(self):

        assert self.controller.analyzer is self.analyzer
        assert self.controller.configuration is self.configuration
        assert self.controller.reports_engine is not None

    # ==========================================================
    # Coste sin FV
    # ==========================================================

    def test_calculate_cost_without_pv(self):

        engine = self.analyzer.economics_engine

        engine.calculate_cost_without_pv.return_value = 1234.56

        result = self.controller.calculate_cost_without_pv()

        assert result == 1234.56

        engine.calculate_cost_without_pv.assert_called_once_with(
            self.analyzer.dataset
        )

    # ==========================================================
    # Ingresos por excedentes
    # ==========================================================

    def test_calculate_export_income(self):

        engine = self.analyzer.economics_engine

        engine.calculate_export_income.return_value = 250.0

        result = self.controller.calculate_export_income()

        assert result == 250.0

        engine.calculate_export_income.assert_called_once_with(
            self.analyzer.solar.energy_balance,
            self.analyzer.dataset,
        )

    # ==========================================================
    # Coste con FV
    # ==========================================================

    def test_calculate_cost_with_pv(self):

        engine = self.analyzer.economics_engine

        engine.calculate_cost_with_pv.return_value = 500.0

        result = self.controller.calculate_cost_with_pv()

        assert result == 500.0

        engine.calculate_cost_with_pv.assert_called_once_with(
            self.analyzer.solar.energy_balance,
            self.analyzer.dataset,
        )

    # ==========================================================
    # Ahorro anual
    # ==========================================================

    def test_calculate_annual_savings(self):

        engine = self.analyzer.economics_engine

        engine.calculate_annual_savings.return_value = 750.0

        result = self.controller.calculate_annual_savings()

        assert result == 750.0

        engine.calculate_annual_savings.assert_called_once_with()

    # ==========================================================
    # Inversión neta
    # ==========================================================

    def test_calculate_net_investment(self):

        engine = self.analyzer.economics_engine

        engine.calculate_net_investment.return_value = 10000.0

        result = self.controller.calculate_net_investment()

        assert result == 10000.0

        engine.calculate_net_investment.assert_called_once_with(
            self.configuration
        )

    # ==========================================================
    # Cash flow
    # ==========================================================

    def test_calculate_cash_flow_default_years(self):

        engine = self.analyzer.economics_engine

        engine.calculate_cash_flow.return_value = "cash_flow"

        result = self.controller.calculate_cash_flow()

        assert result == "cash_flow"

        engine.calculate_cash_flow.assert_called_once_with(
            self.configuration,
            25,
        )

    def test_calculate_cash_flow_custom_years(self):

        engine = self.analyzer.economics_engine

        engine.calculate_cash_flow.return_value = "cash_flow"

        result = self.controller.calculate_cash_flow(
            years=10
        )

        assert result == "cash_flow"

        engine.calculate_cash_flow.assert_called_once_with(
            self.configuration,
            10,
        )

    # ==========================================================
    # Indicadores económicos
    # ==========================================================

    def test_calculate_economic_indicators(self):

        engine = self.analyzer.economics_engine

        expected = {
            "payback_years": 5.2,
            "npv": 12000.0,
            "irr": 0.18,
        }

        engine.calculate_economic_indicators.return_value = expected

        result = self.controller.calculate_economic_indicators()

        assert result == expected

        engine.calculate_economic_indicators.assert_called_once_with(
            0.05
        )

    # ==========================================================
    # Resumen económico
    # ==========================================================

    def test_economic_summary(self):

        engine = self.analyzer.economics_engine

        expected = MagicMock()

        engine.economic_summary.return_value = expected

        result = self.controller.economic_summary()

        assert result is expected

        engine.economic_summary.assert_called_once_with()

    # ==========================================================
    # Calculate completo
    # ==========================================================

    def test_calculate_calls_all_steps_in_order(
        self,
        monkeypatch,
    ):

        calls = []

        monkeypatch.setattr(
            self.controller,
            "calculate_cost_without_pv",
            lambda: calls.append(
                "calculate_cost_without_pv"
            ),
        )

        monkeypatch.setattr(
            self.controller,
            "calculate_export_income",
            lambda: calls.append(
                "calculate_export_income"
            ),
        )

        monkeypatch.setattr(
            self.controller,
            "calculate_cost_with_pv",
            lambda: calls.append(
                "calculate_cost_with_pv"
            ),
        )

        monkeypatch.setattr(
            self.controller,
            "calculate_annual_savings",
            lambda: calls.append(
                "calculate_annual_savings"
            ),
        )

        monkeypatch.setattr(
            self.controller,
            "calculate_net_investment",
            lambda: calls.append(
                "calculate_net_investment"
            ),
        )

        monkeypatch.setattr(
            self.controller,
            "calculate_cash_flow",
            lambda: calls.append(
                "calculate_cash_flow"
            ),
        )

        monkeypatch.setattr(
            self.controller,
            "calculate_economic_indicators",
            lambda: calls.append(
                "calculate_economic_indicators"
            ),
        )

        result = self.controller.calculate()

        assert result is None

        assert calls == [
            "calculate_cost_without_pv",
            "calculate_export_income",
            "calculate_cost_with_pv",
            "calculate_annual_savings",
            "calculate_net_investment",
            "calculate_cash_flow",
            "calculate_economic_indicators",
        ]

    # ==========================================================
    # Calculate no devuelve resultado
    # ==========================================================

    def test_calculate_returns_none(self):

        result = self.controller.calculate()

        assert result is None

    # ==========================================================
    # Escenario individual
    # ==========================================================

    def test_calculate_scenario(self):

        engine = self.analyzer.economics_engine

        scenario = MagicMock(spec=EconomicScenario)
        expected = MagicMock()

        engine.calculate_scenario.return_value = expected

        result = self.controller.calculate_scenario(
            scenario
        )

        assert result is expected

        engine.calculate_scenario.assert_called_once_with(
            scenario,
            self.configuration,
            self.analyzer.dataset,
            self.analyzer.solar.energy_balance,
            self.analyzer.dataset,
        )

    # ==========================================================
    # Escenarios múltiples
    # ==========================================================

    def test_calculate_scenarios_default_years(self):

        engine = self.analyzer.economics_engine

        scenarios = [
            MagicMock(),
            MagicMock(),
            MagicMock(),
        ]

        expected = [
            MagicMock(),
            MagicMock(),
            MagicMock(),
        ]

        engine.calculate_scenarios.return_value = expected

        result = self.controller.calculate_scenarios(
            scenarios
        )

        assert result == expected

        engine.calculate_scenarios.assert_called_once_with(
            scenarios,
            self.configuration,
            self.analyzer.dataset,
            self.analyzer.solar.energy_balance,
            self.analyzer.dataset,
            25,
        )

    def test_calculate_scenarios_custom_years(self):

        engine = self.analyzer.economics_engine

        scenarios = [
            MagicMock(),
            MagicMock(),
        ]

        expected = [
            MagicMock(),
            MagicMock(),
        ]

        engine.calculate_scenarios.return_value = expected

        result = self.controller.calculate_scenarios(
            scenarios,
            years=10,
        )

        assert result == expected

        engine.calculate_scenarios.assert_called_once_with(
            scenarios,
            self.configuration,
            self.analyzer.dataset,
            self.analyzer.solar.energy_balance,
            self.analyzer.dataset,
            10,
        )

    # ==========================================================
    # Informe anual
    # ==========================================================

    def test_annual_economics_report(self):

        engine = self.analyzer.economics_engine

        engine.cost_without_pv = 1000.0
        engine.grid_import_cost = 400.0
        engine.export_income = 100.0
        engine.cost_with_pv = 300.0
        engine.annual_savings = 700.0
        engine.net_investment = 10000.0
        engine.payback_years = 5.5
        engine.cash_flow = "cash_flow"
        engine.npv = 2500.0
        engine.irr = 0.18

        self.controller.reports_engine.annual_economics = (
            MagicMock()
        )

        self.controller.annual_economics_report()

        self.controller.reports_engine.annual_economics.assert_called_once_with(
            1000.0,
            400.0,
            100.0,
            300.0,
            700.0,
            10000.0,
            5.5,
            "cash_flow",
            2500.0,
            0.05,
            0.18,
        )

    # ==========================================================
    # Informe de escenarios
    # ==========================================================

    def test_economic_scenarios_report(self):

        scenarios = [
            MagicMock(),
            MagicMock(),
            MagicMock(),
        ]

        self.analyzer.economics_engine.scenario_results = scenarios

        self.controller.reports_engine.economic_scenarios = (
            MagicMock()
        )

        self.controller.economic_scenarios_report()

        self.controller.reports_engine.economic_scenarios.assert_called_once_with(
            scenarios
        )

    # ==========================================================
    # scenarios_report
    # ==========================================================

    def test_scenarios_report(self):

        scenarios = [
            MagicMock(),
            MagicMock(),
        ]

        self.analyzer.economics_engine.scenario_results = scenarios

        self.controller.reports_engine.economic_scenarios = (
            MagicMock()
        )

        self.controller.scenarios_report()

        self.controller.reports_engine.economic_scenarios.assert_called_once_with(
            scenarios
        )

    # ==========================================================
    # reports
    # ==========================================================

    def test_reports_calls_both_reports_in_order(
        self,
        monkeypatch,
    ):

        calls = []

        monkeypatch.setattr(
            self.controller,
            "annual_economics_report",
            lambda: calls.append(
                "annual_economics_report"
            ),
        )

        monkeypatch.setattr(
            self.controller,
            "economic_scenarios_report",
            lambda: calls.append(
                "economic_scenarios_report"
            ),
        )

        result = self.controller.reports()

        assert result is None

        assert calls == [
            "annual_economics_report",
            "economic_scenarios_report",
        ]

    # ==========================================================
    # Propagación de excepciones
    # ==========================================================

    def test_calculate_cost_without_pv_propagates_exception(self):

        engine = self.analyzer.economics_engine

        engine.calculate_cost_without_pv.side_effect = (
            RuntimeError("test error")
        )

        with pytest.raises(
            RuntimeError,
            match="test error",
        ):
            self.controller.calculate_cost_without_pv()

    def test_calculate_annual_savings_propagates_exception(self):

        engine = self.analyzer.economics_engine

        engine.calculate_annual_savings.side_effect = (
            RuntimeError("test error")
        )

        with pytest.raises(
            RuntimeError,
            match="test error",
        ):
            self.controller.calculate_annual_savings()

    def test_calculate_net_investment_propagates_exception(self):

        engine = self.analyzer.economics_engine

        engine.calculate_net_investment.side_effect = (
            RuntimeError("test error")
        )

        with pytest.raises(
            RuntimeError,
            match="test error",
        ):
            self.controller.calculate_net_investment()

    def test_calculate_cash_flow_propagates_exception(self):

        engine = self.analyzer.economics_engine

        engine.calculate_cash_flow.side_effect = (
            RuntimeError("test error")
        )

        with pytest.raises(
            RuntimeError,
            match="test error",
        ):
            self.controller.calculate_cash_flow()

    def test_calculate_economic_indicators_propagates_exception(
        self,
    ):

        engine = self.analyzer.economics_engine

        engine.calculate_economic_indicators.side_effect = (
            RuntimeError("test error")
        )

        with pytest.raises(
            RuntimeError,
            match="test error",
        ):
            self.controller.calculate_economic_indicators()