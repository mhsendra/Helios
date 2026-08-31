import pytest

import pandas as pd

from unittest.mock import Mock

from PySide6.QtWidgets import QApplication

from helios.gui.widgets.economics_page import EconomicsPage


@pytest.fixture
def app():
    return QApplication.instance() or QApplication([])


class TestEconomicsPage:

    def _create_project(self):

        project = type("Project", (), {})()

        project.economics = Mock()

        project.economics.configuration = type(
            "Configuration",
            (),
            {
                "discount_rate": 0.05,
            },
        )()

        project.analyzer = type(
            "Analyzer",
            (),
            {},
        )()

        project.analyzer.economics_engine = type(
            "EconomicsEngine",
            (),
            {},
        )()

        return project

    # ==================================================
    # Inicialización
    # ==================================================

    def test_page_initialization(self, app):

        project = self._create_project()

        page = EconomicsPage(project)

        assert page.project is project
        assert page.controller is project.economics

        assert page.cost_without_pv_label.text() == "-"
        assert page.cost_with_pv_label.text() == "-"
        assert page.annual_savings_label.text() == "-"
        assert page.self_consumption_savings_label.text() == "-"
        assert page.export_income_label.text() == "-"
        assert page.net_investment_label.text() == "-"

        assert page.payback_label.text() == "-"
        assert page.npv_label.text() == "-"
        assert page.irr_label.text() == "-"
        assert page.discount_rate_label.text() == "-"

        assert page.cash_flow_table.rowCount() == 0
        assert page.cash_flow_table.columnCount() == 0

    # ==================================================
    # Resumen económico
    # ==================================================

    def test_update_summary(self, app):

        project = self._create_project()

        economics = project.analyzer.economics_engine

        economics.cost_without_pv = 1200.0
        economics.cost_with_pv = 400.0
        economics.annual_savings = 800.0
        economics.self_consumption_savings = 650.0
        economics.export_income = 150.0
        economics.net_investment = 10000.0

        page = EconomicsPage(project)

        page.update_summary()

        assert page.cost_without_pv_label.text() == (
            "1,200.00 €"
        )

        assert page.cost_with_pv_label.text() == (
            "400.00 €"
        )

        assert page.annual_savings_label.text() == (
            "800.00 €"
        )

        assert page.self_consumption_savings_label.text() == (
            "650.00 €"
        )

        assert page.export_income_label.text() == (
            "150.00 €"
        )

        assert page.net_investment_label.text() == (
            "10,000.00 €"
        )

    def test_update_summary_formats_zero_values(self, app):

        project = self._create_project()

        economics = project.analyzer.economics_engine

        economics.cost_without_pv = 0.0
        economics.cost_with_pv = 0.0
        economics.annual_savings = 0.0
        economics.self_consumption_savings = 0.0
        economics.export_income = 0.0
        economics.net_investment = 0.0

        page = EconomicsPage(project)

        page.update_summary()

        assert page.cost_without_pv_label.text() == (
            "0.00 €"
        )

        assert page.cost_with_pv_label.text() == (
            "0.00 €"
        )

        assert page.annual_savings_label.text() == (
            "0.00 €"
        )

        assert page.self_consumption_savings_label.text() == (
            "0.00 €"
        )

        assert page.export_income_label.text() == (
            "0.00 €"
        )

        assert page.net_investment_label.text() == (
            "0.00 €"
        )

    # ==================================================
    # Rentabilidad
    # ==================================================

    def test_update_profitability(self, app):

        project = self._create_project()

        economics = project.analyzer.economics_engine

        economics.payback_years = 5.34
        economics.npv = 22071.16
        economics.irr = 0.188

        page = EconomicsPage(project)

        page.update_profitability()

        assert page.payback_label.text() == (
            "5.34 años"
        )

        assert page.npv_label.text() == (
            "22,071.16 €"
        )

        assert page.irr_label.text() == (
            "18.80 %"
        )

        assert page.discount_rate_label.text() == (
            "5.00 %"
        )

    def test_update_profitability_formats_zero_values(
        self,
        app,
    ):

        project = self._create_project()

        economics = project.analyzer.economics_engine

        economics.payback_years = 0.0
        economics.npv = 0.0
        economics.irr = 0.0

        page = EconomicsPage(project)

        page.update_profitability()

        assert page.payback_label.text() == (
            "0.00 años"
        )

        assert page.npv_label.text() == (
            "0.00 €"
        )

        assert page.irr_label.text() == (
            "0.00 %"
        )

        assert page.discount_rate_label.text() == (
            "5.00 %"
        )

    # ==================================================
    # Cash flow
    # ==================================================

    def test_update_cash_flow(self, app):

        project = self._create_project()

        project.analyzer.economics_engine.cash_flow = (
            pd.DataFrame(
                [
                    {
                        "year": 0,
                        "self_consumption_savings": 0.0,
                        "export_income": 0.0,
                        "maintenance_cost": 0.0,
                        "cash_flow": -10000.0,
                        "cumulative_cash_flow": -10000.0,
                    },
                    {
                        "year": 1,
                        "self_consumption_savings": 700.0,
                        "export_income": 100.0,
                        "maintenance_cost": 150.0,
                        "cash_flow": 650.0,
                        "cumulative_cash_flow": -9350.0,
                    },
                ]
            )
        )

        page = EconomicsPage(project)

        page.update_cash_flow()

        table = page.cash_flow_table

        assert table.rowCount() == 2
        assert table.columnCount() == 6

        assert [
            table.horizontalHeaderItem(i).text()
            for i in range(table.columnCount())
        ] == [
            "Año",
            "Ahorro autoconsumo",
            "Ingresos excedentes",
            "Mantenimiento",
            "Flujo de caja",
            "Flujo acumulado",
        ]

        assert table.item(0, 0).text() == "0"
        assert table.item(0, 1).text() == "0.00"
        assert table.item(0, 2).text() == "0.00"
        assert table.item(0, 3).text() == "0.00"
        assert table.item(0, 4).text() == "-10,000.00"
        assert table.item(0, 5).text() == "-10,000.00"

        assert table.item(1, 0).text() == "1"
        assert table.item(1, 1).text() == "700.00"
        assert table.item(1, 2).text() == "100.00"
        assert table.item(1, 3).text() == "150.00"
        assert table.item(1, 4).text() == "650.00"
        assert table.item(1, 5).text() == "-9,350.00"

    def test_update_cash_flow_with_multiple_years(
        self,
        app,
    ):

        project = self._create_project()

        project.analyzer.economics_engine.cash_flow = (
            pd.DataFrame(
                [
                    {
                        "year": 0,
                        "self_consumption_savings": 0.0,
                        "export_income": 0.0,
                        "maintenance_cost": 0.0,
                        "cash_flow": -10000.0,
                        "cumulative_cash_flow": -10000.0,
                    },
                    {
                        "year": 1,
                        "self_consumption_savings": 800.0,
                        "export_income": 100.0,
                        "maintenance_cost": 150.0,
                        "cash_flow": 750.0,
                        "cumulative_cash_flow": -9250.0,
                    },
                    {
                        "year": 2,
                        "self_consumption_savings": 820.0,
                        "export_income": 110.0,
                        "maintenance_cost": 160.0,
                        "cash_flow": 770.0,
                        "cumulative_cash_flow": -8480.0,
                    },
                ]
            )
        )

        page = EconomicsPage(project)

        page.update_cash_flow()

        table = page.cash_flow_table

        assert table.rowCount() == 3
        assert table.columnCount() == 6

        assert table.item(2, 0).text() == "2"
        assert table.item(2, 1).text() == "820.00"
        assert table.item(2, 2).text() == "110.00"
        assert table.item(2, 3).text() == "160.00"
        assert table.item(2, 4).text() == "770.00"
        assert table.item(2, 5).text() == "-8,480.00"

    def test_update_cash_flow_without_data(self, app):

        project = self._create_project()

        project.analyzer.economics_engine.cash_flow = None

        page = EconomicsPage(project)

        page.update_cash_flow()

        assert page.cash_flow_table.rowCount() == 0
        assert page.cash_flow_table.columnCount() == 0

    def test_update_cash_flow_with_empty_dataframe(self, app):

        project = self._create_project()

        project.analyzer.economics_engine.cash_flow = (
            pd.DataFrame()
        )

        page = EconomicsPage(project)

        page.update_cash_flow()

        assert page.cash_flow_table.rowCount() == 0
        assert page.cash_flow_table.columnCount() == 0

    # ==================================================
    # Calculate
    # ==================================================

    def test_calculate_delegates_to_controller(self, app):

        project = self._create_project()

        page = EconomicsPage(project)

        page.update_summary = Mock()
        page.update_profitability = Mock()
        page.update_cash_flow = Mock()

        page.calculate()

        project.economics.calculate.assert_called_once_with()

        project.economics.calculate_scenarios.assert_called_once()

        page.update_summary.assert_called_once_with()
        page.update_profitability.assert_called_once_with()
        page.update_cash_flow.assert_called_once_with()

    def test_calculate_uses_default_economic_scenarios(
        self,
        app,
    ):

        project = self._create_project()

        page = EconomicsPage(project)

        page.update_summary = Mock()
        page.update_profitability = Mock()
        page.update_cash_flow = Mock()

        page.calculate()

        project.economics.calculate_scenarios.assert_called_once()

        scenarios = (
            project.economics
            .calculate_scenarios
            .call_args.args[0]
        )

        assert len(scenarios) > 0

        assert all(
            hasattr(
                scenario,
                "name"
            )
            for scenario in scenarios
        )

    # ==================================================
    # Botón
    # ==================================================

    def test_calculate_button_triggers_calculate(
        self,
        app,
    ):

        project = self._create_project()

        page = EconomicsPage(project)

        page.calculate = Mock()

        page.calculate_button.click()

        page.calculate.assert_called_once_with()

    def test_calculate_button_has_expected_text(
        self,
        app,
    ):

        project = self._create_project()

        page = EconomicsPage(project)

        assert (
            page.calculate_button.text()
            == "Calcular análisis económico"
        )

    # ==================================================
    # Integración entre actualización y engine
    # ==================================================

    def test_update_summary_reads_current_engine_values(
        self,
        app,
    ):

        project = self._create_project()

        economics = project.analyzer.economics_engine

        economics.cost_without_pv = 5000.0
        economics.cost_with_pv = 2000.0
        economics.annual_savings = 3000.0
        economics.self_consumption_savings = 2500.0
        economics.export_income = 500.0
        economics.net_investment = 15000.0

        page = EconomicsPage(project)

        page.update_summary()

        economics.cost_without_pv = 6000.0
        economics.cost_with_pv = 2500.0
        economics.annual_savings = 3500.0
        economics.self_consumption_savings = 2900.0
        economics.export_income = 600.0
        economics.net_investment = 14000.0

        page.update_summary()

        assert page.cost_without_pv_label.text() == (
            "6,000.00 €"
        )

        assert page.cost_with_pv_label.text() == (
            "2,500.00 €"
        )

        assert page.annual_savings_label.text() == (
            "3,500.00 €"
        )

        assert page.self_consumption_savings_label.text() == (
            "2,900.00 €"
        )

        assert page.export_income_label.text() == (
            "600.00 €"
        )

        assert page.net_investment_label.text() == (
            "14,000.00 €"
        )

    def test_update_profitability_reads_current_engine_values(
        self,
        app,
    ):

        project = self._create_project()

        economics = project.analyzer.economics_engine

        economics.payback_years = 5.34
        economics.npv = 22071.16
        economics.irr = 0.188

        page = EconomicsPage(project)

        page.update_profitability()

        economics.payback_years = 6.25
        economics.npv = 18000.50
        economics.irr = 0.1625

        project.economics.configuration.discount_rate = 0.06

        page.update_profitability()

        assert page.payback_label.text() == (
            "6.25 años"
        )

        assert page.npv_label.text() == (
            "18,000.50 €"
        )

        assert page.irr_label.text() == (
            "16.25 %"
        )

        assert page.discount_rate_label.text() == (
            "6.00 %"
        )

    # ==================================================
    # Ampliación de cobertura
    # ==================================================


    def test_calculate_executes_steps_in_expected_order(
        self,
        app,
    ):

        project = self._create_project()

        page = EconomicsPage(project)

        page.update_summary = Mock()
        page.update_profitability = Mock()
        page.update_cash_flow = Mock()

        calls = []

        project.economics.calculate.side_effect = (
            lambda: calls.append("calculate")
        )

        project.economics.calculate_scenarios.side_effect = (
            lambda scenarios: calls.append("calculate_scenarios")
        )

        page.update_summary.side_effect = (
            lambda: calls.append("update_summary")
        )

        page.update_profitability.side_effect = (
            lambda: calls.append("update_profitability")
        )

        page.update_cash_flow.side_effect = (
            lambda: calls.append("update_cash_flow")
        )

        page.calculate()

        assert calls == [
            "calculate",
            "calculate_scenarios",
            "update_summary",
            "update_profitability",
            "update_cash_flow",
        ]


    def test_calculate_propagates_controller_calculate_exception(
        self,
        app,
    ):

        project = self._create_project()

        error = RuntimeError(
            "economic calculation failed"
        )

        project.economics.calculate.side_effect = error

        page = EconomicsPage(project)

        with pytest.raises(
            RuntimeError,
            match="economic calculation failed",
        ):
            page.calculate()

        project.economics.calculate_scenarios.assert_not_called()


    def test_calculate_stops_when_scenario_calculation_fails(
        self,
        app,
    ):

        project = self._create_project()

        error = RuntimeError(
            "scenario calculation failed"
        )

        project.economics.calculate_scenarios.side_effect = (
            error
        )

        page = EconomicsPage(project)

        page.update_summary = Mock()
        page.update_profitability = Mock()
        page.update_cash_flow = Mock()

        with pytest.raises(
            RuntimeError,
            match="scenario calculation failed",
        ):
            page.calculate()

        project.economics.calculate.assert_called_once_with()

        page.update_summary.assert_not_called()
        page.update_profitability.assert_not_called()
        page.update_cash_flow.assert_not_called()


    def test_update_summary_reads_values_from_current_engine(
        self,
        app,
    ):

        project = self._create_project()

        economics = project.analyzer.economics_engine

        economics.cost_without_pv = 1234.567
        economics.cost_with_pv = 987.654
        economics.annual_savings = 246.913
        economics.self_consumption_savings = 200.111
        economics.export_income = 46.802
        economics.net_investment = 12345.678

        page = EconomicsPage(project)

        page.update_summary()

        assert page.cost_without_pv_label.text() == (
            "1,234.57 €"
        )

        assert page.cost_with_pv_label.text() == (
            "987.65 €"
        )

        assert page.annual_savings_label.text() == (
            "246.91 €"
        )

        assert page.self_consumption_savings_label.text() == (
            "200.11 €"
        )

        assert page.export_income_label.text() == (
            "46.80 €"
        )

        assert page.net_investment_label.text() == (
            "12,345.68 €"
        )


    def test_update_profitability_uses_current_discount_rate(
        self,
        app,
    ):

        project = self._create_project()

        economics = project.analyzer.economics_engine

        economics.payback_years = 4.567
        economics.npv = 12345.678
        economics.irr = 0.12345

        project.economics.configuration.discount_rate = (
            0.0375
        )

        page = EconomicsPage(project)

        page.update_profitability()

        assert page.payback_label.text() == (
            "4.57 años"
        )

        assert page.npv_label.text() == (
            "12,345.68 €"
        )

        assert page.irr_label.text() == (
            "12.35 %"
        )

        assert page.discount_rate_label.text() == (
            "3.75 %"
        )


    def test_update_cash_flow_uses_column_order_from_dataframe(
        self,
        app,
    ):

        project = self._create_project()

        project.analyzer.economics_engine.cash_flow = (
            pd.DataFrame(
                [
                    {
                        "cash_flow": 100.0,
                        "year": 1,
                        "custom_value": 25.0,
                    },
                ]
            )
        )

        page = EconomicsPage(project)

        page.update_cash_flow()

        table = page.cash_flow_table

        assert table.columnCount() == 3

        assert [
            table.horizontalHeaderItem(i).text()
            for i in range(table.columnCount())
        ] == [
            "Flujo de caja",
            "Año",
            "custom_value",
        ]


    def test_update_cash_flow_formats_integer_values_as_strings(
        self,
        app,
    ):

        project = self._create_project()

        project.analyzer.economics_engine.cash_flow = (
            pd.DataFrame(
                [
                    {
                        "year": 1,
                        "cash_flow": 100,
                    },
                ]
            )
        )

        page = EconomicsPage(project)

        page.update_cash_flow()

        table = page.cash_flow_table

        assert table.item(0, 0).text() == "1"
        assert table.item(0, 1).text() == "100"


    def test_update_cash_flow_formats_float_values_to_two_decimals(
        self,
        app,
    ):

        project = self._create_project()

        project.analyzer.economics_engine.cash_flow = (
            pd.DataFrame(
                [
                    {
                        "cash_flow": 1234.5678,
                    },
                ]
            )
        )

        page = EconomicsPage(project)

        page.update_cash_flow()

        assert page.cash_flow_table.item(
            0,
            0,
        ).text() == "1,234.57"


    def test_update_cash_flow_clears_previous_table(
        self,
        app,
    ):

        project = self._create_project()

        project.analyzer.economics_engine.cash_flow = (
            pd.DataFrame(
                [
                    {
                        "year": 1,
                        "cash_flow": 100.0,
                    },
                ]
            )
        )

        page = EconomicsPage(project)

        page.update_cash_flow()

        assert page.cash_flow_table.rowCount() == 1
        assert page.cash_flow_table.columnCount() == 2

        project.analyzer.economics_engine.cash_flow = None

        page.update_cash_flow()

        assert page.cash_flow_table.rowCount() == 0
        assert page.cash_flow_table.columnCount() == 0


    def test_update_cash_flow_replaces_previous_table_structure(
        self,
        app,
    ):

        project = self._create_project()

        project.analyzer.economics_engine.cash_flow = (
            pd.DataFrame(
                [
                    {
                        "year": 1,
                        "cash_flow": 100.0,
                        "export_income": 20.0,
                    },
                ]
            )
        )

        page = EconomicsPage(project)

        page.update_cash_flow()

        assert page.cash_flow_table.columnCount() == 3

        project.analyzer.economics_engine.cash_flow = (
            pd.DataFrame(
                [
                    {
                        "year": 2,
                        "cash_flow": 250.0,
                    },
                ]
            )
        )

        page.update_cash_flow()

        table = page.cash_flow_table

        assert table.rowCount() == 1
        assert table.columnCount() == 2

        assert [
            table.horizontalHeaderItem(i).text()
            for i in range(table.columnCount())
        ] == [
            "Año",
            "Flujo de caja",
        ]

        assert table.item(0, 0).text() == "2"
        assert table.item(0, 1).text() == "250.00"


    def test_calculate_updates_gui_after_successful_calculation(
        self,
        app,
    ):

        project = self._create_project()

        page = EconomicsPage(project)

        page.update_summary = Mock()
        page.update_profitability = Mock()
        page.update_cash_flow = Mock()

        page.calculate()

        page.update_summary.assert_called_once_with()
        page.update_profitability.assert_called_once_with()
        page.update_cash_flow.assert_called_once_with()


    def test_calculate_scenarios_receives_non_empty_scenario_list(
        self,
        app,
    ):

        project = self._create_project()

        page = EconomicsPage(project)

        page.update_summary = Mock()
        page.update_profitability = Mock()
        page.update_cash_flow = Mock()

        page.calculate()

        args, kwargs = (
            project.economics
            .calculate_scenarios
            .call_args
        )

        assert len(args) == 1
        assert len(args[0]) > 0
        assert kwargs == {}