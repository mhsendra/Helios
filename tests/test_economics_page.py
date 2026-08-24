import pytest

import pandas as pd

from unittest.mock import Mock

from PySide6.QtWidgets import QApplication

from helios.gui.widgets.economics_page import EconomicsPage


@pytest.fixture
def app():
    return QApplication.instance() or QApplication([])


class TestEconomicsPage:

    def test_page_initialization(self, app):

        project = type("Project", (), {})()

        project.economics = type(
            "EconomicsController",
            (),
            {}
        )()

        page = EconomicsPage(project)

        assert page.project is project

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

    def test_update_summary(self, app):

        project = type("Project", (), {})()

        project.economics = type(
            "EconomicsController",
            (),
            {}
        )()

        project.analyzer = type(
            "Analyzer",
            (),
            {}
        )()

        project.analyzer.economics_engine = type(
            "EconomicsEngine",
            (),
            {}
        )()

        economics = project.analyzer.economics_engine

        economics.cost_without_pv = 1200.0
        economics.cost_with_pv = 400.0
        economics.annual_savings = 800.0
        economics.self_consumption_savings = 650.0
        economics.export_income = 150.0
        economics.net_investment = 10000.0

        page = EconomicsPage(project)

        page.update_summary()

        assert page.cost_without_pv_label.text() == "1,200.00 €"
        assert page.cost_with_pv_label.text() == "400.00 €"
        assert page.annual_savings_label.text() == "800.00 €"

        assert (
            page.self_consumption_savings_label.text()
            == "650.00 €"
        )

        assert page.export_income_label.text() == "150.00 €"
        assert page.net_investment_label.text() == "10,000.00 €"

    def test_update_profitability(self, app):

        project = type("Project", (), {})()

        project.economics = type(
            "EconomicsController",
            (),
            {}
        )()

        project.economics.configuration = type(
            "Configuration",
            (),
            {
                "discount_rate": 0.05
            }
        )()

        project.analyzer = type(
            "Analyzer",
            (),
            {}
        )()

        project.analyzer.economics_engine = type(
            "EconomicsEngine",
            (),
            {}
        )()

        economics = project.analyzer.economics_engine

        economics.payback_years = 5.34
        economics.npv = 22071.16
        economics.irr = 0.188

        page = EconomicsPage(project)

        page.update_profitability()

        assert page.payback_label.text() == "5.34 años"

        assert page.npv_label.text() == "22,071.16 €"

        assert page.irr_label.text() == "18.80 %"

        assert page.discount_rate_label.text() == "5.00 %"

    def test_update_cash_flow(self, app):

        project = type("Project", (), {})()

        project.economics = type(
            "EconomicsController",
            (),
            {}
        )()

        project.analyzer = type(
            "Analyzer",
            (),
            {}
        )()

        project.analyzer.economics_engine = type(
            "EconomicsEngine",
            (),
            {}
        )()

        project.analyzer.economics_engine.cash_flow = pd.DataFrame(
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
        assert table.item(0, 4).text() == "-10,000.00"

        assert table.item(1, 1).text() == "700.00"
        assert table.item(1, 4).text() == "650.00"
        assert table.item(1, 5).text() == "-9,350.00"

    def test_update_cash_flow_without_data(self, app):

        project = type("Project", (), {})()

        project.economics = type(
            "EconomicsController",
            (),
            {}
        )()

        project.analyzer = type(
            "Analyzer",
            (),
            {}
        )()

        project.analyzer.economics_engine = type(
            "EconomicsEngine",
            (),
            {}
        )()

        project.analyzer.economics_engine.cash_flow = None

        page = EconomicsPage(project)

        page.update_cash_flow()

        assert page.cash_flow_table.rowCount() == 0
        assert page.cash_flow_table.columnCount() == 0

    def test_calculate(self, app):

        project = type("Project", (), {})()

        project.economics = Mock()

        project.analyzer = type(
            "Analyzer",
            (),
            {}
        )()

        project.analyzer.economics_engine = Mock()

        page = EconomicsPage(project)

        page.update_summary = Mock()
        page.update_profitability = Mock()
        page.update_cash_flow = Mock()

        page.calculate()

        project.economics.calculate.assert_called_once_with()

        page.update_summary.assert_called_once_with()

        page.update_profitability.assert_called_once_with()

        page.update_cash_flow.assert_called_once_with()

    def test_calculate_button_triggers_calculate(self, app):

        project = type("Project", (), {})()

        project.economics = Mock()

        page = EconomicsPage(project)

        page.calculate = Mock()

        page.calculate_button.click()

        page.calculate.assert_called_once_with()