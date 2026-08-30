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