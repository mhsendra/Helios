import pytest
import pandas as pd

from unittest.mock import MagicMock, patch

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

    def test_start_optimization_calls_recommendation(
        self,
    ):

        page, project = self.create_page(
            self.create_solar_configuration()
        )

        scenario = (
            self.create_consumption_scenario()
        )

        project.analyzer.calculate_representative_consumption_scenario.return_value = (
            scenario
        )

        result = self.create_result()

        project.solar.recommend_installation.return_value = (
            result
        )

        page.show_optimization_result = MagicMock()

        page.start_optimization()

        project.solar.recommend_installation.assert_called_once()

        project.solar.calculate.assert_called_once_with(
            page.project.solar_configuration,
            installed_power_kwp=(
                result.installed_power_kwp
            ),
        )

        assert (
            page.status_label.text()
            == "Optimización completada"
        )

        assert (
            page.optimize_button.isEnabled()
            is True
        )

    def test_start_optimization_notifies_main_window(
        self,
    ):

        main_window = MagicMock()

        page, project = self.create_page(
            self.create_solar_configuration(),
            main_window=main_window,
        )

        project.analyzer.calculate_representative_consumption_scenario.return_value = (
            self.create_consumption_scenario()
        )

        project.solar.recommend_installation.return_value = (
            self.create_result()
        )

        page.show_optimization_result = MagicMock()

        page.start_optimization()

        main_window.set_solar_optimized.assert_called_once_with(
           True
        )

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