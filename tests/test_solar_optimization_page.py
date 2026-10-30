import pytest
import pandas as pd

from unittest.mock import MagicMock, call

from PySide6.QtWidgets import QApplication

from helios.gui.widgets.solar_optimization_page import (
    SolarOptimizationPage,
    RoofLayoutWidget,
)

from helios.solar.configuration import SolarConfiguration
from helios.solar.installation_configuration import (
    InstallationConfiguration,
)
from helios.core.consumption_scenario import (
    ConsumptionScenario,
)

from helios.solar.battery_economic_configuration import (
    BatteryEconomicParameters,
)

from helios.gui.widgets.solar_optimization_page import (
    ELECTRICAL_PROTECTION_GROSS_EUR,
    INVERTER_COST_GROSS_EUR,
    INSTALLATION_LABOUR_GROSS_EUR,
    LEGALIZATION_ESTIMATE_EUR,
    PANEL_COST_GROSS_EUR,
    STRUCTURE_COST_GROSS_PER_PANEL_EUR,
    CABLING_AND_ACCESSORIES_GROSS_EUR,
    INSTALLATION_VAT_RATE,
    LEGALIZATION_ESTIMATE_NET_EUR,
)

class TestSolarOptimizationPage:

    @classmethod
    def setup_class(cls):

        cls.app = QApplication.instance()

        if cls.app is None:
            cls.app = QApplication([])

    def create_project(
        self,
        solar_configuration=None,
    ):

        project = MagicMock()

        project.solar_configuration = (
            solar_configuration
        )

        project.solar = MagicMock()
        project.analyzer = MagicMock()

        return project

    def create_solar_configuration(self):

        return SolarConfiguration(
            latitude=41.620000,
            longitude=2.090000,
            tilt=30,
            azimuth=0,
            reference_year=2023,
            losses=14.0,
            pv_technology="crystSi",
            mounting_place="building",
        )

    def create_consumption_scenario(
        self,
        value=1.0,
    ):

        index = pd.date_range(
            start="2025-01-01 00:00:00",
            periods=8760,
            freq="h",
        )

        consumption = pd.Series(
            value,
            index=index,
            name="AE_kWh",
        )

        return ConsumptionScenario(
            hourly_consumption=consumption,
            reference_year=2025,
        )

    def create_page(
        self,
        solar_configuration=None,
        main_window=None,
    ):

        project = self.create_project(
            solar_configuration
        )

        page = SolarOptimizationPage(
            project=project,
            main_window=main_window,
        )

        return page, project

    # ==========================================================
    # INICIALIZACIÓN
    # ==========================================================

    def test_initialization(
        self,
    ):

        page, _ = self.create_page()

        assert (
            page.status_label.text()
            == "Pendiente de datos"
        )

        assert (
            page.optimize_button.isEnabled()
            is True
        )

    def test_battery_table_initialization(
        self,
    ):

        page, _ = self.create_page()

        assert (
            page.battery_table.columnCount()
            == 5
        )

        assert (
            page.battery_table.rowCount()
            == 0
        )

        assert (
            page.battery_status_label.text()
            == (
                "No hay una evaluación de baterías disponible."
            )
        )

    def test_show_battery_economic_results(self):
        page, _ = self.create_page()

        recommendations = []

        for capacity in [5.0, 8.3]:
            recommendation = MagicMock()

            recommendation.capacity_kwh = capacity
            recommendation.annual_additional_savings_eur = 200.0
            recommendation.incremental_battery_cost_eur = 1000.0
            recommendation.incremental_savings_eur = 50.0
            recommendation.marginal_payback_years = 20.0
            recommendation.economic_npv_eur = 1500.0
            recommendation.economic_irr_percent = 8.5
            recommendation.economic_payback_years = 10.0

            # Representa el flujo anterior: recomendación de batería
            # sin una recomendación de instalación asociada.
            recommendation.installation_recommendation = None
            recommendation.battery_recommendation = recommendation

            recommendations.append(recommendation)

        page.show_battery_economic_results(recommendations)

        assert page.battery_table.rowCount() == 2
        assert page.battery_table.columnCount() == 5

        assert page.battery_table.item(0, 0).text() == "—"
        assert page.battery_table.item(0, 1).text() == "5.0 kWh"
        assert page.battery_table.item(0, 2).text() == "1,500.00 €"
        assert page.battery_table.item(0, 3).text() == "8.50 %"
        assert page.battery_table.item(0, 4).text() == "10.00 años"

        assert page.battery_table.item(1, 1).text() == "8.3 kWh"

        assert (
            page.battery_status_label.text()
            == "Evaluación económica completada. "
            "2 alternativas comparadas."
        )

    def test_evaluate_batteries_calls_controller(
        self,
    ):

        page, project = self.create_page(
            self.create_solar_configuration()
        )

        recommendations = [
            MagicMock(),
            MagicMock(),
        ]

        project.solar.evaluate_batteries.return_value = (
            recommendations
        )

        page.show_battery_economic_results = MagicMock()

        result = page.evaluate_batteries()

        assert result == recommendations

        project.solar.evaluate_batteries.assert_called_once_with(
            [
                5.0,
                8.3,
                16.6,
                24.9,
                30.0,
            ],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            battery_economic_parameters=BatteryEconomicParameters(
                cost_per_kwh_eur=(
                    4145.27 / 16.6
                ) * 1.21,
            ),
        )

        page.show_battery_economic_results.assert_called_once_with(
            recommendations
        )

    # ==========================================================
    # INSTALLATION CONFIGURATION
    # ==========================================================

    def test_get_installation_configuration_default_values(
        self,
    ):

        page, _ = self.create_page()

        configuration = (
            page.get_installation_configuration()
        )

        assert isinstance(
            configuration,
            InstallationConfiguration,
        )

        assert (
            configuration.max_panels
            is None
        )

        assert (
            configuration.maintenance_passage_required
            is False
        )

        assert (
            configuration.panel_orientation
            == "auto"
        )

        assert (
            configuration.maintenance_passage_orientation
            == "auto"
        )

    def test_get_installation_configuration_reads_widgets(
        self,
    ):

        page, _ = self.create_page()

        page.available_area_spinbox.setValue(42.5)
        page.roof_width_spinbox.setValue(6.5)
        page.roof_height_spinbox.setValue(7.25)

        page.panel_width_spinbox.setValue(1.134)
        page.panel_height_spinbox.setValue(2.278)
        page.panel_power_spinbox.setValue(540)

        page.panel_orientation_combobox.setCurrentIndex(1)

        page.min_panels_spinbox.setValue(8)

        page.max_panels_checkbox.setChecked(True)
        page.max_panels_spinbox.setValue(15)

        page.maintenance_required_checkbox.setChecked(
            True
        )

        page.maintenance_width_spinbox.setValue(0.50)
        page.maintenance_orientation_combobox.setCurrentIndex(1)

        configuration = (
            page.get_installation_configuration()
        )

        assert (
            configuration.available_area_m2
            == pytest.approx(42.5)
        )

        assert (
            configuration.roof_width_m
            == pytest.approx(6.5)
        )

        assert (
            configuration.roof_height_m
            == pytest.approx(7.25)
        )

        assert (
            configuration.panel_width_m
            == pytest.approx(1.134)
        )

        assert (
            configuration.panel_height_m
            == pytest.approx(2.278)
        )

        assert (
            configuration.panel_power_wp
            == pytest.approx(540)
        )

        assert (
            configuration.panel_orientation
            == "vertical"
        )

        assert configuration.min_panels == 8
        assert configuration.max_panels == 15

        assert (
            configuration.maintenance_passage_required
            is True
        )

        assert (
            configuration.maintenance_passage_width_m
            == pytest.approx(0.50)
        )

        assert (
            configuration.maintenance_passage_orientation
            == "vertical"
        )

    def test_zero_roof_dimensions_become_none(
        self,
    ):

        page, _ = self.create_page()

        configuration = (
            page.get_installation_configuration()
        )

        assert (
            configuration.roof_width_m
            is None
        )

        assert (
            configuration.roof_height_m
            is None
        )

    def test_maximum_panel_limit_is_optional(
        self,
    ):

        page, _ = self.create_page()

        page.max_panels_spinbox.setValue(15)

        page.max_panels_checkbox.setChecked(False)

        configuration = (
            page.get_installation_configuration()
        )

        assert configuration.max_panels is None

        page.max_panels_checkbox.setChecked(True)

        configuration = (
            page.get_installation_configuration()
        )

        assert configuration.max_panels == 15

    # ==========================================================
    # WIDGET CONTROLS
    # ==========================================================

    def test_max_panels_checkbox_enables_spinbox(
        self,
    ):

        page, _ = self.create_page()

        page.max_panels_checkbox.setChecked(False)

        assert (
            page.max_panels_spinbox.isEnabled()
            is False
        )

        page.max_panels_checkbox.setChecked(True)

        assert (
            page.max_panels_spinbox.isEnabled()
            is True
        )

    def test_maintenance_checkbox_enables_controls(
        self,
    ):

        page, _ = self.create_page()

        page.maintenance_required_checkbox.setChecked(
            False
        )

        assert (
            page.maintenance_width_spinbox.isEnabled()
            is False
        )

        assert (
            page.maintenance_orientation_combobox.isEnabled()
            is False
        )

        page.maintenance_required_checkbox.setChecked(
            True
        )

        assert (
            page.maintenance_width_spinbox.isEnabled()
            is True
        )

        assert (
            page.maintenance_orientation_combobox.isEnabled()
            is True
        )

    # ==========================================================
    # RESULTADO
    # ==========================================================

    def create_result(self):

        result = MagicMock()

        result.panel_count = 15
        result.installed_power_kwp = 8.10
        result.annual_production_kwh = 12150.0
        result.annual_consumption_kwh = 19541.72
        result.occupied_area_m2 = 39.5
        result.remaining_area_m2 = 2.75
        result.area_utilization_percent = 93.5
        result.self_sufficiency_percent = 42.5
        result.production_coverage_percent = 62.2
        result.energy_surplus_kwh = 1250.0
        result.energy_deficit_kwh = 8650.0
        result.layout = None

        return result

    def test_show_optimization_result_updates_labels(
        self,
    ):

        configuration = (
            self.create_solar_configuration()
        )

        page, _ = self.create_page(
            configuration
        )

        result = self.create_result()

        page.show_optimization_result(result)

        assert (
            page.result_panel_count_label.text()
            == "15"
        )

        assert (
            page.result_power_label.text()
            == "8.10 kWp"
        )

        assert (
            page.result_production_label.text()
            == "12,150 kWh/año"
        )

        assert (
            page.result_consumption_label.text()
            == "19,542 kWh/año"
        )

        assert (
            page.result_occupied_area_label.text()
            == "39.50 m²"
        )

        assert (
            page.result_remaining_area_label.text()
            == "2.75 m²"
        )

        assert (
            page.result_utilization_label.text()
            == "93.5 %"
        )

        assert (
            page.result_self_sufficiency_label.text()
            == "42.5 %"
        )

        assert (
            page.result_coverage_label.text()
            == "62.2 %"
        )

        assert (
            page.result_surplus_label.text()
            == "1,250 kWh/año"
        )

        assert (
            page.result_deficit_label.text()
            == "8,650 kWh/año"
        )

    def test_show_optimization_result_shows_south(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        page.show_optimization_result(
            self.create_result()
        )

        assert (
            page.result_orientation_label.text()
            == "Sur (0°)"
        )

    @pytest.mark.parametrize(
        "azimuth, expected",
        [
            (
                15,
                "15° respecto al Sur (15°)",
            ),
            (
                -15,
                "-15° respecto al Sur (-15°)",
            ),
        ],
    )
    def test_show_optimization_result_non_zero_azimuth(
        self,
        azimuth,
        expected,
    ):

        configuration = (
            self.create_solar_configuration()
        )

        configuration.azimuth = azimuth

        page, _ = self.create_page(
            configuration
        )

        page.show_optimization_result(
            self.create_result()
        )

        assert (
            page.result_orientation_label.text()
            == expected
        )

    # ==========================================================
    # LAYOUT
    # ==========================================================

    def create_layout(self):

        layout = MagicMock()

        layout.rows = 3
        layout.columns = 5
        layout.orientation = "vertical"
        layout.occupied_width_m = 5.67
        layout.occupied_height_m = 6.83
        layout.occupied_area_m2 = 38.71
        layout.walkway_width_m = 0.45
        layout.walkway_position = "vertical"

        return layout

    def test_show_installation_layout_without_layout(
        self,
    ):

        page, _ = self.create_page()

        result = MagicMock()
        result.layout = None

        page.walkway_slider.setEnabled(True)

        page.show_installation_layout(result)

        assert (
            page.result_rows_label.text()
            == "-"
        )

        assert (
            page.result_columns_label.text()
            == "-"
        )

        assert (
            page.result_dimensions_label.text()
            == "-"
        )

        assert (
            page.result_walkway_label.text()
            == "-"
        )

        assert (
            page.walkway_slider.isEnabled()
            is False
        )

        assert (
            page.layout_info_label.text()
            == "No hay una distribución física disponible."
        )

    def test_show_installation_layout_with_vertical_walkway(
        self,
    ):

        page, _ = self.create_page()

        result = MagicMock()
        result.layout = self.create_layout()

        page.roof_width_spinbox.setValue(6.5)
        page.roof_height_spinbox.setValue(6.5)
        page.panel_width_spinbox.setValue(1.134)
        page.panel_height_spinbox.setValue(2.278)

        page.show_installation_layout(result)

        assert (
            page.result_rows_label.text()
            == "3"
        )

        assert (
            page.result_columns_label.text()
            == "5"
        )

        assert (
            page.result_dimensions_label.text()
            == "5.67 × 6.83 m"
        )

        assert (
            page.result_walkway_label.text()
            == "0.45 m vertical"
        )

        assert (
            page.walkway_slider.isEnabled()
            is True
        )

        assert (
            "3 filas × 5 columnas"
            in page.layout_info_label.text()
        )

    def test_show_installation_layout_without_walkway(
        self,
    ):

        page, _ = self.create_page()

        layout = self.create_layout()
        layout.walkway_width_m = 0.0
        layout.walkway_position = None

        result = MagicMock()
        result.layout = layout

        page.show_installation_layout(result)

        assert (
            page.result_walkway_label.text()
            == "No requerido"
        )

        assert (
            page.walkway_slider.isEnabled()
            is False
        )

    # ==========================================================
    # SLIDER
    # ==========================================================

    def test_on_walkway_position_changed(
        self,
    ):

        page, _ = self.create_page()

        page.on_walkway_position_changed(25)

        assert (
            page.walkway_position_label.text()
            == "25 %"
        )

        assert (
            page.roof_layout_widget.walkway_offset_percent
            == 25
        )

    def test_walkway_slider_updates_layout(
        self,
    ):

        page, _ = self.create_page()

        page.walkway_slider.setValue(75)

        assert (
            page.walkway_position_label.text()
            == "75 %"
        )

        assert (
            page.roof_layout_widget.walkway_offset_percent
            == 75
        )

    # ==========================================================
    # RESET
    # ==========================================================

    def test_clear_optimization_result(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        page.show_optimization_result(
            self.create_result()
        )

        page.walkway_slider.setEnabled(True)

        page.clear_optimization_result()

        assert (
            page.result_panel_count_label.text()
            == "-"
        )

        assert (
            page.result_power_label.text()
            == "-"
        )

        assert (
            page.result_production_label.text()
            == "-"
        )

        assert (
            page.result_consumption_label.text()
            == "-"
        )

        assert (
            page.result_rows_label.text()
            == "-"
        )

        assert (
            page.result_columns_label.text()
            == "-"
        )

        assert (
            page.result_walkway_label.text()
            == "-"
        )

        assert (
            page.walkway_slider.isEnabled()
            is False
        )

        assert (
            page.walkway_position_label.text()
            == "50 %"
        )

        assert (
            page.layout_info_label.text()
            == "No hay una instalación calculada."
        )

        assert (
            page.roof_layout_widget.roof_width
            == 0.0
        )

    def test_reset_disables_report(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        page.show_optimization_result(
            self.create_result()
        )

        page.reset()

        assert (
            page.optimize_button.isEnabled()
            is True
        )

        assert (
            page.status_label.text()
            == "Pendiente de datos"
        )

    # ==========================================================
    # OPTIMIZACIÓN
    # ==========================================================

    def test_start_optimization_rejects_missing_scenario(
        self,
    ):

        page, project = self.create_page(
            self.create_solar_configuration()
        )

        project.analyzer.calculate_representative_consumption_scenario.return_value = (
            None
        )

        page.start_optimization()

        assert (
            page.status_label.text()
            == (
                "Error: A representative consumption "
                "scenario is required."
            )
        )

        assert (
            page.optimize_button.isEnabled()
            is True
        )

    def test_start_optimization_rejects_zero_consumption(
        self,
    ):

        page, project = self.create_page(
            self.create_solar_configuration()
        )

        project.analyzer.calculate_representative_consumption_scenario.return_value = (
            self.create_consumption_scenario(
                value=0.0
            )
        )

        page.start_optimization()

        assert (
            page.status_label.text()
            == (
                "Error: Annual consumption must "
                "be greater than zero."
            )
        )

        assert (
            page.optimize_button.isEnabled()
            is True
        )

    def test_start_optimization_calls_recommendation(self):
        page, project = self.create_page(
            self.create_solar_configuration()
        )

        scenario = self.create_consumption_scenario()
        project.analyzer.calculate_representative_consumption_scenario.return_value = (
            scenario
        )

        installation = self.create_result()

        battery = MagicMock()
        battery.capacity_kwh = 8.3
        battery.combined_economic_analysis_calculated = True
        battery.combined_economic_npv_eur = 1000.0

        recommendation = MagicMock()
        recommendation.installation_recommendation = installation
        recommendation.battery_recommendation = battery
        recommendation.panel_count = installation.panel_count
        recommendation.installed_power_kwp = installation.installed_power_kwp
        recommendation.battery_capacity_kwh = battery.capacity_kwh
        recommendation.combined_economic_analysis_calculated = True
        recommendation.combined_economic_npv_eur = 1000.0
        recommendation.alternatives = (recommendation,)

        project.solar.recommend_energy.return_value = recommendation

        page.show_optimization_result = MagicMock()
        page.show_battery_economic_results = MagicMock()
        page._update_total_investment = MagicMock()

        page.start_optimization()

        project.solar.recommend_energy.assert_called_once()
        call_kwargs = project.solar.recommend_energy.call_args.kwargs

        assert call_kwargs["configuration"] is not None
        assert call_kwargs["consumption_scenario"] is scenario
        assert call_kwargs["candidate_capacities_kwh"] == [
            5.0, 8.3, 16.6, 24.9, 30.0,
        ]
        assert call_kwargs["optimization_criterion"] == "combined_npv"

        page.show_optimization_result.assert_called_once_with(
            installation
        )
        project.solar.calculate.assert_called_once_with(
            page.project.solar_configuration,
            installed_power_kwp=installation.installed_power_kwp,
        )

        assert page.status_label.text() == "Optimización conjunta completada"
        assert page.optimize_button.isEnabled() is True

    def test_start_optimization_notifies_main_window(self):
        main_window = MagicMock()

        page, project = self.create_page(
            self.create_solar_configuration(),
            main_window=main_window,
        )

        installation = self.create_result()

        battery = MagicMock()
        battery.capacity_kwh = 8.3
        battery.combined_economic_analysis_calculated = True
        battery.combined_economic_npv_eur = 1000.0

        recommendation = MagicMock()
        recommendation.installation_recommendation = installation
        recommendation.battery_recommendation = battery
        recommendation.panel_count = installation.panel_count
        recommendation.installed_power_kwp = installation.installed_power_kwp
        recommendation.battery_capacity_kwh = battery.capacity_kwh
        recommendation.combined_economic_analysis_calculated = True
        recommendation.combined_economic_npv_eur = 1000.0
        recommendation.alternatives = (recommendation,)

        project.analyzer.calculate_representative_consumption_scenario.return_value = (
            self.create_consumption_scenario()
        )
        project.solar.recommend_energy.return_value = recommendation

        page.show_optimization_result = MagicMock()
        page.show_battery_economic_results = MagicMock()
        page._update_total_investment = MagicMock()

        page.start_optimization()

        project.solar.recommend_energy.assert_called_once()
        assert main_window.set_solar_optimized.call_args_list == [
            call(False),
            call(True),
        ]

    def test_start_optimization_restores_button_after_error(
        self,
    ):

        page, project = self.create_page(
            self.create_solar_configuration()
        )

        project.analyzer.calculate_representative_consumption_scenario.side_effect = (
            RuntimeError("test error")
        )

        page.start_optimization()

        assert (
            page.optimize_button.isEnabled()
            is True
        )

    # ==========================================================
    # ROOF LAYOUT WIDGET
    # ==========================================================

    def test_panel_dimensions_vertical(
        self,
    ):

        widget = RoofLayoutWidget()

        widget.panel_width = 1.10
        widget.panel_height = 2.00
        widget.panel_orientation = "vertical"

        assert widget._panel_dimensions() == (
            1.10,
            2.00,
        )

    def test_panel_dimensions_horizontal(
        self,
    ):

        widget = RoofLayoutWidget()

        widget.panel_width = 1.10
        widget.panel_height = 2.00
        widget.panel_orientation = "horizontal"

        assert widget._panel_dimensions() == (
            2.00,
            1.10,
        )

    def test_paint_event_empty_layout(
        self,
        qtbot,
    ):

        widget = RoofLayoutWidget()

        qtbot.addWidget(widget)

        widget.resize(500, 360)
        widget.show()
        widget.repaint()

        assert widget.roof_width == 0.0
        assert widget.roof_height == 0.0
        assert widget.rows == 0
        assert widget.columns == 0

    def test_paint_event_vertical_layout(
        self,
        qtbot,
    ):

        widget = RoofLayoutWidget()

        qtbot.addWidget(widget)

        widget.set_layout_data(
            roof_width=6.50,
            roof_height=6.50,
            panel_width=1.10,
            panel_height=2.00,
            rows=2,
            columns=3,
            orientation="vertical",
        )

        widget.resize(700, 500)
        widget.show()
        widget.repaint()

        assert widget.rows == 2
        assert widget.columns == 3
        assert widget.panel_orientation == "vertical"

    def test_paint_event_horizontal_layout(
        self,
        qtbot,
    ):

        widget = RoofLayoutWidget()

        qtbot.addWidget(widget)

        widget.set_layout_data(
            roof_width=6.50,
            roof_height=6.50,
            panel_width=1.10,
            panel_height=2.00,
            rows=2,
            columns=3,
            orientation="horizontal",
        )

        widget.resize(700, 500)
        widget.show()
        widget.repaint()

        assert widget.panel_orientation == "horizontal"

    def test_vertical_walkway(
        self,
        qtbot,
    ):

        widget = RoofLayoutWidget()

        qtbot.addWidget(widget)

        widget.set_layout_data(
            roof_width=6.50,
            roof_height=6.50,
            panel_width=1.10,
            panel_height=2.00,
            rows=2,
            columns=3,
            orientation="vertical",
            walkway_width=0.45,
            walkway_position="vertical",
        )

        widget.resize(700, 500)
        widget.show()
        widget.repaint()

        assert widget.walkway_width == 0.45
        assert widget.walkway_position == "vertical"

    def test_horizontal_walkway(
        self,
        qtbot,
    ):

        widget = RoofLayoutWidget()

        qtbot.addWidget(widget)

        widget.set_layout_data(
            roof_width=6.50,
            roof_height=6.50,
            panel_width=1.10,
            panel_height=2.00,
            rows=3,
            columns=2,
            orientation="vertical",
            walkway_width=0.45,
            walkway_position="horizontal",
        )

        widget.resize(700, 500)
        widget.show()
        widget.repaint()

        assert widget.walkway_width == 0.45
        assert widget.walkway_position == "horizontal"

    def test_walkway_offset(
        self,
        qtbot,
    ):

        widget = RoofLayoutWidget()

        qtbot.addWidget(widget)

        widget.set_layout_data(
            roof_width=10.0,
            roof_height=6.0,
            panel_width=1.0,
            panel_height=2.0,
            rows=2,
            columns=3,
            orientation="vertical",
            walkway_width=0.50,
            walkway_position="vertical",
        )

        widget.set_walkway_offset(0)
        widget.set_walkway_offset(100)

        assert (
            widget.walkway_offset_percent
            == 100
        )

    def test_vertical_walkway_reorganizes_panel_groups(self):
        widget = RoofLayoutWidget()
        widget.set_layout_data(
            roof_width=6.5,
            roof_height=6.5,
            panel_width=1.134,
            panel_height=1.99,
            rows=2,
            columns=3,
            orientation="vertical",
            walkway_width=0.45,
            walkway_position="vertical",
        )

        widget.set_walkway_offset(0)
        panels_left, walkway_left = (
            widget._calculate_layout_rectangles(
                0.0, 0.0, 100.0
            )
        )

        widget.set_walkway_offset(100)
        panels_right, walkway_right = (
            widget._calculate_layout_rectangles(
                0.0, 0.0, 100.0
            )
        )

        assert len(panels_left) == 6
        assert len(panels_right) == 6
        assert walkway_left is not None
        assert walkway_right is not None
        assert walkway_left.x() != walkway_right.x()


    def test_vertical_walkway_does_not_overlap_panels(self):
        widget = RoofLayoutWidget()
        widget.set_layout_data(
            roof_width=6.5,
            roof_height=6.5,
            panel_width=1.134,
            panel_height=1.99,
            rows=2,
            columns=3,
            orientation="vertical",
            walkway_width=0.45,
            walkway_position="vertical",
        )

        panels, walkway = widget._calculate_layout_rectangles(
            0.0, 0.0, 100.0
        )

        assert walkway is not None

        for panel in panels:
            overlap = panel.intersects(walkway)
            assert not overlap


    def test_layout_rectangles_stay_inside_roof(self):
        widget = RoofLayoutWidget()
        widget.set_layout_data(
            roof_width=6.5,
            roof_height=6.5,
            panel_width=1.134,
            panel_height=1.99,
            rows=2,
            columns=3,
            orientation="vertical",
            walkway_width=0.45,
            walkway_position="vertical",
        )

        panels, walkway = widget._calculate_layout_rectangles(
            0.0, 0.0, 100.0
        )

        roof_right = 6.5 * 100.0
        roof_bottom = 6.5 * 100.0

        for panel in panels:
            assert panel.left() >= -1e-6
            assert panel.top() >= -1e-6
            assert panel.right() <= roof_right + 1e-6
            assert panel.bottom() <= roof_bottom + 1e-6

        assert walkway is not None
        assert walkway.left() >= -1e-6
        assert walkway.top() >= -1e-6
        assert walkway.right() <= roof_right + 1e-6
        assert walkway.bottom() <= roof_bottom + 1e-6

    def test_configure_installation_costs_without_optional_auxiliary_items(
        self,
    ):
        from helios.solar.components_catalog import (
            ComponentCatalog,
            Inverter,
            MountingSystem,
            PhotovoltaicPanel,
        )
        from helios.solar.installation_component_selection import (
            InstallationComponentSelection,
        )

        page, project = self.create_page()

        panel = PhotovoltaicPanel(
            id="panel-540",
            manufacturer="Longi",
            model="LR5-72HTH-540M",
            power_wp=540.0,
            width_m=2.256,
            height_m=1.133,
            price_eur=92.196,
        )

        inverter = Inverter(
            id="inverter-8",
            manufacturer="GoodWe",
            model="GW8K",
            nominal_power_kw=8.0,
            max_pv_power_kwp=12.0,
            price_eur=960.38,
            hybrid=True,
        )

        mounting = MountingSystem(
            id="mounting-tile",
            manufacturer="Example",
            model="Tile-Roof",
            price_per_panel_eur=0.0,
            compatible_roof_types=("arabic_tile",),
        )

        catalog = ComponentCatalog(
            panels=(panel,),
            inverters=(inverter,),
            mounting_systems=(mounting,),
        )

        selection = InstallationComponentSelection(
            catalog=catalog,
            panel_id=panel.id,
            inverter_id=inverter.id,
            mounting_system_id=mounting.id,
            roof_type="arabic_tile",
        )

        project.component_selection = selection

        page._configure_installation_costs(result=None)

        project.set_installation_cost_configuration.assert_called_once()

        costs = (
            project.set_installation_cost_configuration.call_args.args[0]
        )

        assert costs.panel_unit_cost_eur == pytest.approx(
            92.196 * 1.21
        )
        assert costs.inverter_unit_cost_eur == pytest.approx(
            960.38 * 1.21
        )
        assert costs.installation_cost_eur == 0.0
        assert costs.electrical_protection_cost_eur == 0.0
        assert costs.cabling_cost_eur == 0.0
        assert costs.legalization_cost_eur == 0.0

    def test_configure_installation_costs_preserves_mounting_packages_and_applies_vat(
        self,
    ):
        from helios.solar.components_catalog import (
            ComponentCatalog,
            Inverter,
            MountingSystem,
            MountingSystemPackage,
            PhotovoltaicPanel,
        )
        from helios.solar.installation_component_selection import (
            InstallationComponentSelection,
        )

        page, project = self.create_page()

        panel = PhotovoltaicPanel(
            id="panel-540",
            manufacturer="Longi",
            model="LR7-60HVH-540M",
            power_wp=540.0,
            width_m=1.134,
            height_m=1.990,
            price_eur=92.196,
        )

        inverter = Inverter(
            id="inverter-8",
            manufacturer="GoodWe",
            model="GW8K",
            nominal_power_kw=8.0,
            max_pv_power_kwp=12.0,
            price_eur=960.375,
            hybrid=True,
        )

        mounting = MountingSystem(
            id="mounting-arabic-tile",
            manufacturer="SUNFER",
            model="01V-CL",
            price_per_panel_eur=None,
            compatible_roof_types=("arabic_tile",),
        )

        package = MountingSystemPackage(
            id="sunfer-test-3-panels",
            mounting_system_id=mounting.id,
            model="Kit de 3 paneles",
            panel_capacity=3,
            quantity=1,
            unit_price_eur=100.00,
        )

        catalog = ComponentCatalog(
            panels=(panel,),
            inverters=(inverter,),
            mounting_systems=(mounting,),
            mounting_packages=(package,),
        )

        selection = InstallationComponentSelection(
            catalog=catalog,
            panel_id=panel.id,
            inverter_id=inverter.id,
            mounting_system_id=mounting.id,
            mounting_package_ids=(package.id,),
            mounting_package_panel_count=3,
            roof_type="arabic_tile",
        )

        project.component_selection = selection

        page._configure_installation_costs(result=None)

        project.set_installation_cost_configuration.assert_called_once()

        costs = (
            project.set_installation_cost_configuration.call_args.args[0]
        )

        assert costs.structure_unit_cost_eur is None
        assert costs.mounting_system_id == mounting.id
        assert len(costs.mounting_packages) == 1

        preserved_package = costs.mounting_packages[0]
        assert preserved_package.id == package.id
        assert preserved_package.unit_price_eur == pytest.approx(121.00)
        assert preserved_package.total_price_eur == pytest.approx(121.00)

        assert costs.structure_package_panel_count == 3
        assert costs.structure_package_cost_eur == pytest.approx(121.00)

    def test_fallback_installation_costs_apply_vat_to_legalization(self):
        page, project = self.create_page()

        # Forzar explícitamente la ruta de respaldo del presupuesto.
        project.component_selection = None

        page._configure_installation_costs(result=None)

        project.set_installation_cost_configuration.assert_called_once()

        costs = (
            project.set_installation_cost_configuration.call_args.args[0]
        )

        assert LEGALIZATION_ESTIMATE_NET_EUR == pytest.approx(650.00)
        assert LEGALIZATION_ESTIMATE_EUR == pytest.approx(786.50)
        assert costs.legalization_cost_eur == pytest.approx(786.50)

        assert costs.panel_unit_cost_eur == pytest.approx(
            PANEL_COST_GROSS_EUR
        )
        assert costs.structure_unit_cost_eur == pytest.approx(
            STRUCTURE_COST_GROSS_PER_PANEL_EUR
        )
        assert costs.installation_cost_eur == pytest.approx(
            INSTALLATION_LABOUR_GROSS_EUR
        )
        assert costs.inverter_unit_cost_eur == pytest.approx(
            INVERTER_COST_GROSS_EUR
        )
        assert costs.electrical_protection_cost_eur == pytest.approx(
            ELECTRICAL_PROTECTION_GROSS_EUR
        )
        assert costs.cabling_cost_eur == pytest.approx(
            CABLING_AND_ACCESSORIES_GROSS_EUR
        )

        assert INSTALLATION_VAT_RATE == pytest.approx(0.21)
