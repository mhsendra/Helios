import pytest

import pandas as pd

from unittest.mock import MagicMock , patch

from PySide6.QtWidgets import QApplication

from helios.gui.widgets.solar_config_page import (
    SolarConfigPage,
)

from helios.solar.configuration import SolarConfiguration
from helios.solar.installation_configuration import (
    InstallationConfiguration,
)

from helios.solar.installation_coordinator import InstallationCoordinator

from helios.gui.widgets.solar_config_page import RoofLayoutWidget


class TestSolarConfigPage:

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

    def create_page(
        self,
        solar_configuration=None,
    ):

        project = self.create_project(
            solar_configuration
        )

        page = SolarConfigPage(
            project=project,
        )

        return page, project

    # ==========================================================
    # INICIALIZACIÓN
    # ==========================================================

    def test_initialization_without_solar_configuration(
        self,
    ):

        page, project = self.create_page(
            solar_configuration=None,
        )

        assert (
            page.status_label.text()
            == "Configuración solar no disponible"
        )

        assert page.latitude_label.text() == "-"
        assert page.longitude_label.text() == "-"
        assert page.tilt_label.text() == "-"
        assert page.azimuth_label.text() == "-"
        assert page.reference_year_label.text() == "-"
        assert page.losses_label.text() == "-"
        assert page.technology_label.text() == "-"
        assert page.mounting_label.text() == "-"

    def test_initialization_with_solar_configuration(
        self,
    ):

        configuration = (
            self.create_solar_configuration()
        )

        page, project = self.create_page(
            configuration,
        )

        assert (
            page.status_label.text()
            == "Configuración solar disponible"
        )

        assert (
            page.latitude_label.text()
            == "41.620000°"
        )

        assert (
            page.longitude_label.text()
            == "2.090000°"
        )

        assert (
            page.tilt_label.text()
            == "30°"
        )

        assert (
            page.azimuth_label.text()
            == "0°"
        )

        assert (
            page.reference_year_label.text()
            == "2023"
        )

        assert (
            page.losses_label.text()
            == "14.0 %"
        )

        assert (
            page.technology_label.text()
            == "Silicio cristalino"
        )

        assert (
            page.mounting_label.text()
            == "Integrado en edificio"
        )

    # ==========================================================
    # NOMBRES DESCRIPTIVOS
    # ==========================================================

    @pytest.mark.parametrize(
        "technology, expected",
        [
            (
                "crystSi",
                "Silicio cristalino",
            ),
            (
                "CIS",
                "CIS",
            ),
            (
                "CdTe",
                "CdTe",
            ),
            (
                "unknown",
                "unknown",
            ),
        ],
    )
    def test_get_technology_name(
        self,
        technology,
        expected,
    ):

        assert (
            SolarConfigPage.get_technology_name(
                technology
            )
            == expected
        )

    @pytest.mark.parametrize(
        "mounting_place, expected",
        [
            (
                "free",
                "Estructura sobre el suelo",
            ),
            (
                "building",
                "Integrado en edificio",
            ),
            (
                "unknown",
                "unknown",
            ),
        ],
    )
    def test_get_mounting_name(
        self,
        mounting_place,
        expected,
    ):

        assert (
            SolarConfigPage.get_mounting_name(
                mounting_place
            )
            == expected
        )

    # ==========================================================
    # CONFIGURACIÓN DE INSTALACIÓN
    # ==========================================================

    def test_get_installation_configuration_default_values(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

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

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        page.available_area_spinbox.setValue(
            42.5
        )

        page.roof_width_spinbox.setValue(
            6.5
        )

        page.roof_height_spinbox.setValue(
            7.25
        )

        page.panel_width_spinbox.setValue(
            1.134
        )

        page.panel_height_spinbox.setValue(
            2.278
        )

        page.panel_power_spinbox.setValue(
            540
        )

        page.panel_orientation_combobox.setCurrentIndex(
            1
        )

        page.min_panels_spinbox.setValue(
            8
        )

        page.max_panels_checkbox.setChecked(
            True
        )

        page.max_panels_spinbox.setValue(
            15
        )

        page.maintenance_required_checkbox.setChecked(
            True
        )

        page.maintenance_width_spinbox.setValue(
            0.50
        )

        page.maintenance_orientation_combobox.setCurrentIndex(
            1
        )

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

        assert (
            configuration.min_panels
            == 8
        )

        assert (
            configuration.max_panels
            == 15
        )

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

    def test_get_installation_configuration_converts_zero_roof_dimensions_to_none(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        page.roof_width_spinbox.setValue(
            0.0
        )

        page.roof_height_spinbox.setValue(
            0.0
        )

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

    def test_get_installation_configuration_without_maximum(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        page.max_panels_spinbox.setValue(
            15
        )

        page.max_panels_checkbox.setChecked(
            False
        )

        configuration = (
            page.get_installation_configuration()
        )

        assert (
            configuration.max_panels
            is None
        )

    def test_get_installation_configuration_with_maximum(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        page.max_panels_checkbox.setChecked(
            True
        )

        page.max_panels_spinbox.setValue(
            15
        )

        configuration = (
            page.get_installation_configuration()
        )

        assert (
            configuration.max_panels
            == 15
        )

    # ==========================================================
    # CONFIGURACIÓN DE WIDGETS
    # ==========================================================

    def test_max_panels_checkbox_enables_spinbox(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        page.max_panels_checkbox.setChecked(
            False
        )

        assert (
            page.max_panels_spinbox.isEnabled()
            is False
        )

        page.max_panels_checkbox.setChecked(
            True
        )

        assert (
            page.max_panels_spinbox.isEnabled()
            is True
        )

    def test_maintenance_checkbox_enables_controls(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

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
    # PVGIS
    # ==========================================================

    def test_get_pvgis_configuration_copies_solar_configuration(
        self,
    ):

        configuration = (
            self.create_solar_configuration()
        )

        page, project = self.create_page(
            configuration,
        )

        result = (
            page.get_pvgis_configuration()
        )

        assert isinstance(
            result,
            SolarConfiguration,
        )

        assert (
            result.latitude
            == configuration.latitude
        )

        assert (
            result.longitude
            == configuration.longitude
        )

        assert (
            result.tilt
            == configuration.tilt
        )

        assert (
            result.azimuth
            == configuration.azimuth
        )

        assert (
            result.reference_year
            == configuration.reference_year
        )

        assert (
            result.losses
            == configuration.losses
        )

        assert (
            result.pv_technology
            == configuration.pv_technology
        )

        assert (
            result.mounting_place
            == configuration.mounting_place
        )

    def test_get_pvgis_configuration_does_not_use_installed_power(
        self,
    ):
        configuration = (
            self.create_solar_configuration()
        )

        configuration.installed_power_kwp = 15.0

        page, _ = self.create_page(
            configuration,
        )

        result = (
            page.get_pvgis_configuration()
        )

        assert result.latitude == configuration.latitude
        assert result.longitude == configuration.longitude
        assert result.tilt == configuration.tilt
        assert result.azimuth == configuration.azimuth
        assert result.reference_year == configuration.reference_year
        assert result.losses == configuration.losses
        assert result.pv_technology == configuration.pv_technology
        assert result.mounting_place == configuration.mounting_place

        # SolarConfiguration ya no contiene la potencia instalada.
        assert not hasattr(
            result,
            "installed_power_kwp",
        )


    def test_get_pvgis_configuration_without_solar_configuration_raises(
        self,
    ):

        page, _ = self.create_page(
            solar_configuration=None,
        )

        with pytest.raises(
            ValueError,
            match=(
                "La configuración solar "
                "no está disponible."
            ),
        ):

            page.get_pvgis_configuration()

    # ==========================================================
    # PRODUCCIÓN
    # ==========================================================

    def test_calculate_installation_production(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        candidate = MagicMock()

        candidate.installed_power_kwp = (
            8.1
        )

        result = (
            page._calculate_installation_production(
                candidate,
                1500.0,
            )
        )

        assert (
            result
            == pytest.approx(
                8.1 * 1500.0
            )
        )

    def test_calculate_installation_production_returns_float(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        candidate = MagicMock()

        candidate.installed_power_kwp = 10

        result = (
            page._calculate_installation_production(
                candidate,
                1000,
            )
        )

        assert isinstance(
            result,
            float,
        )

        assert result == 10000.0

    def test_calculate_installation_production_rejects_zero_specific_production(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        candidate = MagicMock()

        candidate.installed_power_kwp = 10.0

        with pytest.raises(
            ValueError,
            match=(
                "PVGIS specific production "
                "must be greater than zero."
            ),
        ):

            page._calculate_installation_production(
                candidate,
                0.0,
            )

    def test_calculate_installation_production_rejects_negative_specific_production(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        candidate = MagicMock()

        candidate.installed_power_kwp = 10.0

        with pytest.raises(
            ValueError,
            match=(
                "PVGIS specific production "
                "must be greater than zero."
            ),
        ):

            page._calculate_installation_production(
                candidate,
                -1.0,
            )

    # ==========================================================
    # RESULTADO
    # ==========================================================

    def create_result(self):

        result = MagicMock()

        result.panel_count = 15

        result.installed_power_kwp = 8.10

        result.annual_production_kwh = (
            12150.0
        )

        result.annual_consumption_kwh = (
            19541.72
        )

        result.occupied_area_m2 = (
            39.5
        )

        result.remaining_area_m2 = (
            2.75
        )

        result.area_utilization_percent = (
            93.5
        )

        result.self_sufficiency_percent = (
            42.5
        )

        result.production_coverage_percent = (
            62.2
        )

        result.energy_surplus_kwh = (
            1250.0
        )

        result.energy_deficit_kwh = (
            8650.0
        )

        result.layout = None

        return result

    def test_show_optimization_result_updates_numeric_labels(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        result = self.create_result()

        page.show_optimization_result(
            result
        )

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

    def test_show_optimization_result_shows_south_orientation(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        result = self.create_result()

        page.show_optimization_result(
            result
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
    def test_show_optimization_result_shows_non_zero_azimuth(
        self,
        azimuth,
        expected,
    ):

        configuration = (
            self.create_solar_configuration()
        )

        configuration.azimuth = azimuth

        page, _ = self.create_page(
            configuration,
        )

        result = self.create_result()

        page.show_optimization_result(
            result
        )

        assert (
            page.result_orientation_label.text()
            == expected
        )

    def test_show_optimization_result_without_configuration(
        self,
    ):

        page, _ = self.create_page(
            solar_configuration=None,
        )

        result = self.create_result()

        page.show_optimization_result(
            result
        )

        assert (
            page.result_orientation_label.text()
            == "-"
        )

    def test_show_optimization_result_enables_report_button(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        assert (
            page.simulation_report_button.isEnabled()
            is False
        )

        result = self.create_result()

        page.show_optimization_result(
            result
        )

        assert (
            page.simulation_report_button.isEnabled()
            is True
        )

    # ==========================================================
    # LAYOUT FÍSICO
    # ==========================================================

    def create_layout(self):

        layout = MagicMock()

        layout.rows = 3
        layout.columns = 5

        layout.orientation = "vertical"

        layout.occupied_width_m = (
            5.67
        )

        layout.occupied_height_m = (
            6.83
        )

        layout.occupied_area_m2 = (
            38.71
        )

        layout.walkway_width_m = (
            0.45
        )

        layout.walkway_position = (
            "vertical"
        )

        return layout

    def test_show_installation_layout_without_layout(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        result = MagicMock()

        result.layout = None

        page.walkway_slider.setEnabled(
            True
        )

        page.show_installation_layout(
            result
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
            == (
                "No hay una distribución "
                "física disponible."
            )
        )

    def test_show_installation_layout_with_vertical_walkway(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        result = MagicMock()

        result.layout = self.create_layout()

        page.roof_width_spinbox.setValue(
            6.5
        )

        page.roof_height_spinbox.setValue(
            6.5
        )

        page.panel_width_spinbox.setValue(
            1.134
        )

        page.panel_height_spinbox.setValue(
            2.278
        )

        page.show_installation_layout(
            result
        )

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

        assert (
            "Orientación de los paneles: Vertical"
            in page.layout_info_label.text()
        )

        assert (
            "Superficie ocupada: 38.71 m²"
            in page.layout_info_label.text()
        )

    def test_show_installation_layout_with_horizontal_walkway(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        layout = self.create_layout()

        layout.orientation = (
            "horizontal"
        )

        layout.walkway_position = (
            "horizontal"
        )

        result = MagicMock()

        result.layout = layout

        page.show_installation_layout(
            result
        )

        assert (
            page.result_walkway_label.text()
            == "0.45 m horizontal"
        )

        assert (
            page.walkway_slider.isEnabled()
            is True
        )

    def test_show_installation_layout_without_walkway(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        layout = self.create_layout()

        layout.walkway_width_m = 0.0

        result = MagicMock()

        result.layout = layout

        page.show_installation_layout(
            result
        )

        assert (
            page.result_walkway_label.text()
            == "No requerido"
        )

        assert (
            page.walkway_slider.isEnabled()
            is False
        )

    # ==========================================================
    # SLIDER DEL PASILLO
    # ==========================================================

    def test_on_walkway_position_changed_updates_label(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        page.on_walkway_position_changed(
            25
        )

        assert (
            page.walkway_position_label.text()
            == "25 %"
        )

        assert (
            page.roof_layout_widget.walkway_offset_percent
            == 25
        )

    def test_walkway_slider_updates_roof_layout(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        page.walkway_slider.setValue(
            75
        )

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

        result = self.create_result()

        page.show_optimization_result(
            result
        )

        page.walkway_slider.setEnabled(
            True
        )

        page.walkway_position_label.setText(
            "80 %"
        )

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
            page.result_occupied_area_label.text()
            == "-"
        )

        assert (
            page.result_remaining_area_label.text()
            == "-"
        )

        assert (
            page.result_utilization_label.text()
            == "-"
        )

        assert (
            page.result_self_sufficiency_label.text()
            == "-"
        )

        assert (
            page.result_coverage_label.text()
            == "-"
        )

        assert (
            page.result_surplus_label.text()
            == "-"
        )

        assert (
            page.result_deficit_label.text()
            == "-"
        )

        assert (
            page.result_orientation_label.text()
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

        assert (
            page.roof_layout_widget.roof_height
            == 0.0
        )

    def test_reset_clears_results_and_disables_report_button(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        result = self.create_result()

        page.show_optimization_result(
            result
        )

        assert (
            page.simulation_report_button.isEnabled()
            is True
        )

        page.reset()

        assert (
            page.simulation_report_button.isEnabled()
            is False
        )

        assert (
            page.optimize_button.isEnabled()
            is True
        )

        assert (
            page.status_label.text()
            == "Configuración solar disponible"
        )

    # ==========================================================
    # UPDATE DATA
    # ==========================================================

    def test_update_data_reloads_solar_basis(
        self,
    ):

        configuration = (
            self.create_solar_configuration()
        )

        page, project = self.create_page(
            configuration,
        )

        project.solar_configuration = (
            SolarConfiguration(
                latitude=40.000000,
                longitude=1.000000,
                tilt=20,
                azimuth=10,
                reference_year=2024,
                losses=10.0,
                pv_technology="CIS",
                mounting_place="free",
            )
        )

        page.update_data()

        assert (
            page.latitude_label.text()
            == "40.000000°"
        )

        assert (
            page.longitude_label.text()
            == "1.000000°"
        )

        assert (
            page.tilt_label.text()
            == "20°"
        )

        assert (
            page.azimuth_label.text()
            == "10°"
        )

        assert (
            page.reference_year_label.text()
            == "2024"
        )

        assert (
            page.losses_label.text()
            == "10.0 %"
        )

        assert (
            page.technology_label.text()
            == "CIS"
        )

        assert (
            page.mounting_label.text()
            == "Estructura sobre el suelo"
        )

    # ==========================================================
    # INFORME DE SIMULACIÓN
    # ==========================================================

    def test_generate_simulation_report_without_recommendation(
        self,
    ):

        page, project = self.create_page(
            self.create_solar_configuration()
        )

        project.solar.sizing_result = None

        page.generate_simulation_report()

        assert (
            page.status_label.text()
            == "No hay una simulación disponible."
        )

        project.solar.installation_simulation_report.assert_not_called()

    def test_generate_simulation_report_calls_project(
        self,
    ):

        page, project = self.create_page(
            self.create_solar_configuration()
        )

        project.solar.sizing_result = (
            MagicMock()
        )

        page.generate_simulation_report()

        project.solar.installation_simulation_report.assert_called_once_with()

        assert (
            page.status_label.text()
            == "Informe de simulación generado."
        )

    def test_generate_simulation_report_handles_error(
        self,
    ):

        page, project = self.create_page(
            self.create_solar_configuration()
        )

        project.solar.sizing_result = (
            MagicMock()
        )

        project.solar.installation_simulation_report.side_effect = (
            RuntimeError("test error")
        )

        page.generate_simulation_report()

        assert (
            page.status_label.text()
            == "Error al generar el informe: test error"
        )

    # ==========================================================
    # OPTIMIZACIÓN
    # ==========================================================

    def test_start_optimization_rejects_empty_dataset(
        self,
    ):

        page, project = self.create_page(
            self.create_solar_configuration()
        )

        project.analyzer.valid_dataset.return_value = None

        page.start_optimization()

        assert (
            page.status_label.text()
            == (
                "Error: A valid consumption "
                "dataset is required."
            )
        )

        assert (
            page.optimize_button.isEnabled()
            is True
        )

    def test_start_optimization_rejects_empty_dataframe(
        self,
    ):

        page, project = self.create_page(
            self.create_solar_configuration()
        )

        project.analyzer.valid_dataset.return_value = (
            pd.DataFrame()
        )

        page.start_optimization()

        assert (
            page.status_label.text()
            == (
                "Error: A valid consumption "
                "dataset is required."
            )
        )

    def test_start_optimization_rejects_zero_consumption(
        self,
    ):

        page, project = self.create_page(
            self.create_solar_configuration()
        )

        project.analyzer.valid_dataset.return_value = (
            pd.DataFrame(
                {
                    "AE_kWh": [0.0, 0.0, 0.0],
                }
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

    def test_start_optimization_rejects_zero_pvgis_production(
        self,
    ):
        page, project = self.create_page(
            self.create_solar_configuration()
        )

        project.analyzer.valid_dataset.return_value = (
            pd.DataFrame(
                {
                    "AE_kWh": [
                        1.0,
                        2.0,
                        3.0,
                    ],
                }
            )
        )

        project.solar.sizing_result = None

        with patch.object(
            page.pvgis_service,
            "get_specific_production",
            return_value=0.0,
        ):
            page.start_optimization()

        assert (
            page.status_label.text()
            == "Error: PVGIS specific production must be greater than zero."
        )

        assert (
            project.solar.sizing_result
            is None
        )
        
    def test_start_optimization_restores_button_after_error(
        self,
    ):

        page, project = self.create_page(
            self.create_solar_configuration()
        )

        project.analyzer.valid_dataset.side_effect = (
            RuntimeError("dataset error")
        )

        page.start_optimization()

        assert (
            page.optimize_button.isEnabled()
            is True
        )

    def test_start_optimization_disables_button_during_execution(
        self,
    ):
        page, project = self.create_page(
            self.create_solar_configuration()
        )

        project.analyzer.valid_dataset.return_value = (
            pd.DataFrame(
                {
                    "AE_kWh": [
                        1.0,
                    ],
                }
            )
        )

        original_enabled_states = []

        def fake_get_specific_production(
            configuration,
        ):
            original_enabled_states.append(
                page.optimize_button.isEnabled()
            )

            return 1000.0

        installation_result = MagicMock()

        installation_result.panel_count = 10
        installation_result.installed_power_kwp = 5.0
        installation_result.annual_production_kwh = 5000.0
        installation_result.annual_consumption_kwh = 1.0
        installation_result.occupied_area_m2 = 20.0
        installation_result.remaining_area_m2 = 10.0
        installation_result.area_utilization_percent = 66.7
        installation_result.self_sufficiency_percent = 100.0
        installation_result.production_coverage_percent = 100.0
        installation_result.energy_surplus_kwh = 4999.0
        installation_result.energy_deficit_kwh = 0.0
        installation_result.layout = None

        with patch.object(
            page.pvgis_service,
            "get_specific_production",
            side_effect=fake_get_specific_production,
        ):
            with patch(
                "helios.gui.widgets.solar_config_page.InstallationCoordinator"
            ) as coordinator_class:

                coordinator = (
                    coordinator_class.return_value
                )

                coordinator.recommend.return_value = (
                    installation_result
                )

                page.start_optimization()

        assert original_enabled_states == [False]

        assert (
            page.optimize_button.isEnabled()
            is True
        )

        assert (
            page.status_label.text()
            == "Optimización completada"
        )

    # ==================================================
    # RoofLayoutWidget
    # ==================================================

    def test_panel_dimensions_returns_original_dimensions_for_vertical(
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


    def test_panel_dimensions_swaps_dimensions_for_horizontal(
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


    def test_paint_event_handles_empty_layout(
        self,
        qtbot,
    ):

        widget = RoofLayoutWidget()

        qtbot.addWidget(widget)

        widget.resize(
            500,
            360,
        )

        widget.show()

        widget.repaint()

        assert widget.roof_width == 0.0
        assert widget.roof_height == 0.0
        assert widget.rows == 0
        assert widget.columns == 0


    def test_paint_event_handles_insufficient_available_size(
        self,
        qtbot,
    ):

        widget = RoofLayoutWidget()

        qtbot.addWidget(widget)

        widget.set_layout_data(
            roof_width=10.0,
            roof_height=10.0,
            panel_width=1.0,
            panel_height=2.0,
            rows=2,
            columns=2,
            orientation="vertical",
        )

        with patch.object(
            widget,
            "width",
            return_value=500,
        ):
            with patch.object(
                widget,
                "height",
                return_value=90,
            ):
                widget.repaint()


    def test_paint_event_draws_normal_vertical_layout(
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

        widget.resize(
            700,
            500,
        )

        widget.show()

        widget.repaint()

        assert widget.rows == 2
        assert widget.columns == 3
        assert widget.panel_orientation == "vertical"


    def test_paint_event_draws_horizontal_layout(
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

        widget.resize(
            700,
            500,
        )

        widget.show()

        widget.repaint()

        assert widget.panel_orientation == "horizontal"


    def test_paint_event_draws_vertical_maintenance_passage(
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

        widget.resize(
            700,
            500,
        )

        widget.show()

        widget.repaint()

        assert widget.walkway_width == 0.45
        assert widget.walkway_position == "vertical"


    def test_paint_event_draws_horizontal_maintenance_passage(
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

        widget.resize(
            700,
            500,
        )

        widget.show()

        widget.repaint()

        assert widget.walkway_width == 0.45
        assert widget.walkway_position == "horizontal"


    def test_paint_event_handles_vertical_passage_offset(
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

        widget.resize(
            700,
            500,
        )

        widget.show()

        widget.repaint()

        widget.set_walkway_offset(100)

        widget.repaint()

        assert widget.walkway_offset_percent == 100


    def test_paint_event_handles_horizontal_passage_offset(
        self,
        qtbot,
    ):

        widget = RoofLayoutWidget()

        qtbot.addWidget(widget)

        widget.set_layout_data(
            roof_width=6.0,
            roof_height=10.0,
            panel_width=1.0,
            panel_height=2.0,
            rows=3,
            columns=2,
            orientation="vertical",
            walkway_width=0.50,
            walkway_position="horizontal",
        )

        widget.set_walkway_offset(0)

        widget.resize(
            700,
            500,
        )

        widget.show()

        widget.repaint()

        widget.set_walkway_offset(100)

        widget.repaint()

        assert widget.walkway_offset_percent == 100


    def test_paint_event_handles_single_column_without_vertical_panel_shift(
        self,
        qtbot,
    ):

        widget = RoofLayoutWidget()

        qtbot.addWidget(widget)

        widget.set_layout_data(
            roof_width=4.0,
            roof_height=6.0,
            panel_width=1.0,
            panel_height=2.0,
            rows=2,
            columns=1,
            orientation="vertical",
            walkway_width=0.45,
            walkway_position="vertical",
        )

        widget.resize(
            700,
            500,
        )

        widget.show()

        widget.repaint()

        assert widget.columns == 1


    def test_paint_event_handles_single_row_without_horizontal_panel_shift(
        self,
        qtbot,
    ):

        widget = RoofLayoutWidget()

        qtbot.addWidget(widget)

        widget.set_layout_data(
            roof_width=6.0,
            roof_height=4.0,
            panel_width=1.0,
            panel_height=2.0,
            rows=1,
            columns=2,
            orientation="vertical",
            walkway_width=0.45,
            walkway_position="horizontal",
        )

        widget.resize(
            700,
            500,
        )

        widget.show()

        widget.repaint()

        assert widget.rows == 1

    def test_show_installation_layout_handles_layout_without_walkway(
        self,
    ):

        page, _ = self.create_page(
            self.create_solar_configuration()
        )

        layout = MagicMock()

        layout.rows = 2
        layout.columns = 3
        layout.orientation = "vertical"

        layout.occupied_width_m = 3.0
        layout.occupied_height_m = 4.0
        layout.occupied_area_m2 = 12.0

        layout.walkway_width_m = 0.0
        layout.walkway_position = None

        result = MagicMock()
        result.layout = layout

        page.show_installation_layout(
            result
        )

        assert (
            page.result_walkway_label.text()
            == "No requerido"
        )

        assert (
            page.walkway_slider.isEnabled()
            is False
        )