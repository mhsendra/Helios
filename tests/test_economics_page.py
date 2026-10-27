import pytest

import pandas as pd

from unittest.mock import Mock

from PySide6.QtWidgets import QApplication, QTableWidget

from helios.gui.widgets.economics_page import EconomicsPage

from helios.solar.battery_recommendation import BatteryRecommendation

@pytest.fixture
def app():
    return QApplication.instance() or QApplication([])


class TestEconomicsPage:

    def _create_project(self):

        project = type("Project", (), {})()

        project.solar = type(
            "SolarController",
            (),
            {
                "battery_recommendations": [],
            },
        )()

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

        assert page.cash_flow_tabs.count() == 0

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

        assert page.calculate_button.text() == (
            "Calcular\nanálisis económico"
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

    # ==================================================
    # Análisis económico del almacenamiento
    # ==================================================

    def test_battery_table_is_empty_without_recommendations(
        self,
        app,
    ):

        project = self._create_project()

        page = EconomicsPage(project)

        page.update_battery_analysis()

        assert page.battery_table.rowCount() == 0
        assert page.battery_table.columnCount() == 10

        assert [
            page.battery_table.horizontalHeaderItem(i).text()
            for i in range(
                page.battery_table.columnCount()
            )
        ] == [
            "Capacidad",
            "Coste anual",
            "Ahorro adicional",
            "Coste incremental",
            "Ahorro incremental",
            "Ahorro marginal",
            "PB marginal",
            "VAN",
            "TIR",
            "PB",
        ]

    def test_battery_table_contains_recommendations(
        self,
        app,
    ):

        project = self._create_project()

        project.solar.battery_recommendations = [
            BatteryRecommendation(
                capacity_kwh=5.0,
                max_charge_power_kw=8.3,
                max_discharge_power_kw=8.3,
                annual_consumption_kwh=8911.90,
                annual_production_kwh=12003.99,
                annual_surplus_kwh=8626.64,
                annual_export_kwh=7121.49,
                annual_grid_import_kwh=4176.15,
                annual_battery_charge_kwh=1505.15,
                annual_battery_discharge_kwh=1429.89,
                self_consumption_kwh=4735.75,
                self_sufficiency_percent=53.14,
                equivalent_cycles=357.47,
                annual_cost_with_battery_eur=320.86,
                annual_additional_savings_eur=102.38,
                marginal_recovered_kwh_per_kwh=0.0,
                incremental_battery_cost_eur=0.0,
                incremental_savings_eur=0.0,
                marginal_savings_per_kwh=0.0,
                marginal_payback_years=float("inf"),
                economic_npv_eur=260.10,
                economic_irr_percent=6.80,
                economic_payback_years=12.47,
            ),
        ]

        page = EconomicsPage(project)

        page.update_battery_analysis()

        table = page.battery_table

        assert table.rowCount() == 1
        assert table.columnCount() == 10

        assert [
            table.item(0, column).text()
            for column in range(
                table.columnCount()
            )
        ] == [
            "5.0 kWh",
            "320.86 €",
            "102.38 €",
            "0.00 €",
            "0.00 €",
            "0.00 €/kWh",
            "N/D",
            "260.10 €",
            "6.80 %",
            "12.47 años",
        ]

    def test_refresh_battery_analysis_updates_table(
        self,
        app,
    ):

        project = self._create_project()

        project.solar.battery_recommendations = [
            BatteryRecommendation(
                capacity_kwh=5.0,
                max_charge_power_kw=8.3,
                max_discharge_power_kw=8.3,
                annual_consumption_kwh=8911.90,
                annual_production_kwh=12003.99,
                annual_surplus_kwh=8626.64,
                annual_export_kwh=7121.49,
                annual_grid_import_kwh=4176.15,
                annual_battery_charge_kwh=1505.15,
                annual_battery_discharge_kwh=1429.89,
                self_consumption_kwh=4735.75,
                self_sufficiency_percent=53.14,
                equivalent_cycles=357.47,
                annual_cost_with_battery_eur=320.86,
                annual_additional_savings_eur=102.38,
                marginal_recovered_kwh_per_kwh=0.0,
                incremental_battery_cost_eur=0.0,
                incremental_savings_eur=0.0,
                marginal_savings_per_kwh=0.0,
                marginal_payback_years=float("inf"),
                economic_npv_eur=260.10,
                economic_irr_percent=6.80,
                economic_payback_years=12.47,
            ),
        ]

        page = EconomicsPage(project)

        page.refresh_battery_analysis()

        assert page.battery_table.rowCount() == 1
        assert page.battery_table.item(0, 0).text() == "5.0 kWh"
        assert page.battery_table.item(0, 7).text() == "260.10 €"
        assert page.battery_table.item(0, 8).text() == "6.80 %"
        assert page.battery_table.item(0, 9).text() == "12.47 años"

    def _create_combined_recommendation(
        self,
        *,
        capacity_kwh=5.0,
        npv_eur=1000.0,
        irr_percent=10.0,
        payback_years=10.0,
        cash_flows=(-10000.0, 650.0, 700.0),
        cumulative_cash_flows=(-10000.0, -9350.0, -8650.0),
        calculated=True,
    ):
        return BatteryRecommendation(
            capacity_kwh=capacity_kwh,
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            annual_consumption_kwh=5000.0,
            annual_production_kwh=6000.0,
            annual_surplus_kwh=2000.0,
            annual_export_kwh=1500.0,
            annual_grid_import_kwh=1000.0,
            annual_battery_charge_kwh=500.0,
            annual_battery_discharge_kwh=450.0,
            self_consumption_kwh=4500.0,
            self_sufficiency_percent=80.0,
            equivalent_cycles=100.0,
            combined_economic_npv_eur=npv_eur,
            combined_economic_irr_percent=irr_percent,
            combined_economic_payback_years=payback_years,
            combined_economic_analysis_calculated=calculated,
            combined_economic_cash_flows=cash_flows,
            combined_economic_cumulative_cash_flow=(
                cumulative_cash_flows
            ),
        )


    def test_update_cash_flow_displays_viable_combined_alternative(
        self,
        app,
    ):
        project = self._create_project()
        recommendation = self._create_combined_recommendation()
        project.solar.battery_recommendations = [recommendation]

        page = EconomicsPage(project)
        page.update_cash_flow()

        assert page.cash_flow_tabs.count() == 1
        assert page.cash_flow_tabs.tabText(0) == "5 kWh"

        details = page.cash_flow_tabs.widget(0)
        table = details.findChild(QTableWidget)

        assert table is not None
        assert table.rowCount() == 3
        assert table.columnCount() == 3

        assert [
            table.horizontalHeaderItem(i).text()
            for i in range(table.columnCount())
        ] == [
            "Año",
            "Flujo de caja (€)",
            "Flujo acumulado (€)",
        ]

        assert table.item(0, 0).text() == "0"
        assert table.item(0, 1).text() == "-10,000.00"
        assert table.item(0, 2).text() == "-10,000.00"
        assert table.item(1, 1).text() == "650.00"
        assert table.item(2, 2).text() == "-8,650.00"


    def test_update_cash_flow_sorts_alternatives_by_combined_npv(
        self,
        app,
    ):
        project = self._create_project()
        project.solar.battery_recommendations = [
            self._create_combined_recommendation(
                capacity_kwh=5.0,
                npv_eur=1000.0,
            ),
            self._create_combined_recommendation(
                capacity_kwh=8.3,
                npv_eur=2500.0,
            ),
        ]

        page = EconomicsPage(project)
        page.update_cash_flow()

        assert page.cash_flow_tabs.count() == 2
        assert page.cash_flow_tabs.tabText(0) == "8.3 kWh"
        assert page.cash_flow_tabs.tabText(1) == "5 kWh"


    def test_update_cash_flow_excludes_nonviable_alternatives(
        self,
        app,
    ):
        project = self._create_project()
        project.solar.battery_recommendations = [
            self._create_combined_recommendation(
                capacity_kwh=5.0,
                npv_eur=-100.0,
            ),
            self._create_combined_recommendation(
                capacity_kwh=8.3,
                npv_eur=1000.0,
                calculated=False,
            ),
        ]

        page = EconomicsPage(project)
        page.update_cash_flow()

        assert page.cash_flow_tabs.count() == 1
        assert page.cash_flow_tabs.tabText(0) == "Sin alternativas viables"


    def test_update_cash_flow_clears_previous_tabs_when_no_alternatives(
        self,
        app,
    ):
        project = self._create_project()
        project.solar.battery_recommendations = [
            self._create_combined_recommendation()
        ]

        page = EconomicsPage(project)
        page.update_cash_flow()

        assert page.cash_flow_tabs.count() == 1

        project.solar.battery_recommendations = []
        page.update_cash_flow()

        assert page.cash_flow_tabs.count() == 1
        assert page.cash_flow_tabs.tabText(0) == "Sin alternativas viables"