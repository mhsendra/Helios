import pytest

import pandas as pd

from unittest.mock import MagicMock

from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QSpinBox,
    QComboBox,
    QCheckBox,
)

from helios.gui.widgets.solar_config_page import (
    SolarConfigPage,
)

from helios.solar.installation_configuration import (
    InstallationConfiguration,
)

from helios.solar.installation_recommendation import (
    InstallationRecommendation,
)

from helios.core.solar import SolarEngine

class SolarConfiguration:

    latitude = 41.6167
    longitude = 2.0833
    tilt = 30
    azimuth = 0
    reference_year = 2025
    losses = 14.0
    pv_technology = "crystSi"
    mounting_place = "building"


class SolarEngine:

    configuration = SolarConfiguration()


class Analyzer:

    solar_engine = SolarEngine()

    def valid_dataset(self):

        return pd.DataFrame(
            {
                "AE_kWh": [5000.0],
            }
        )


class Solar:

    sizing_result = None


class Project:

    analyzer = Analyzer()
    solar = Solar()

class TestSolarConfigPage:

    @pytest.fixture
    def project(self):

        return Project()

    @pytest.fixture
    def page(
        self,
        qtbot,
        project,
    ):

        page = SolarConfigPage(
            project=project,
        )

        qtbot.addWidget(page)

        return page

    # ==================================================
    # Construction
    # ==================================================

    def test_page_can_be_created(
        self,
        page,
    ):

        assert page is not None

    def test_page_stores_project(
        self,
        page,
        project,
    ):

        assert page.project is project

    # ==================================================
    # Solar basis
    # ==================================================

    def test_loads_solar_basis(
        self,
        page,
    ):

        assert page.latitude_label.text() == (
            "41.616700°"
        )

        assert page.longitude_label.text() == (
            "2.083300°"
        )

        assert page.tilt_label.text() == "30°"

        assert page.azimuth_label.text() == "0°"

        assert page.reference_year_label.text() == (
            "2025"
        )

        assert page.losses_label.text() == (
            "14.0 %"
        )

    def test_translates_pv_technology(
        self,
        page,
    ):

        assert (
            page.technology_label.text()
            == "Silicio cristalino"
        )

    def test_translates_mounting_place(
        self,
        page,
    ):

        assert (
            page.mounting_label.text()
            == "Integrado en edificio"
        )

    # ==================================================
    # Solar basis remains read-only
    # ==================================================

    def test_solar_basis_is_display_only(
        self,
        page,
    ):

        assert not hasattr(
            page.latitude_label,
            "setReadOnly",
        )

        assert not hasattr(
            page.longitude_label,
            "setReadOnly",
        )

        # Los datos de la base solar se presentan
        # mediante QLabel y no mediante controles editables.
        assert page.latitude_label.__class__.__name__ == (
            "QLabel"
        )

        assert page.longitude_label.__class__.__name__ == (
            "QLabel"
        )

    # ==================================================
    # Installation widgets
    # ==================================================

    def test_installation_controls_exist(
        self,
        page,
    ):

        assert isinstance(
            page.available_area_spinbox,
            QDoubleSpinBox,
        )

        assert isinstance(
            page.roof_width_spinbox,
            QDoubleSpinBox,
        )

        assert isinstance(
            page.roof_height_spinbox,
            QDoubleSpinBox,
        )

    def test_panel_controls_exist(
        self,
        page,
    ):

        assert isinstance(
            page.panel_width_spinbox,
            QDoubleSpinBox,
        )

        assert isinstance(
            page.panel_height_spinbox,
            QDoubleSpinBox,
        )

        assert isinstance(
            page.panel_power_spinbox,
            QDoubleSpinBox,
        )

        assert isinstance(
            page.min_panels_spinbox,
            QSpinBox,
        )

        assert isinstance(
            page.max_panels_spinbox,
            QSpinBox,
        )

        assert isinstance(
            page.max_panels_checkbox,
            QCheckBox,
        )

    def test_maintenance_controls_exist(
        self,
        page,
    ):

        assert isinstance(
            page.maintenance_required_checkbox,
            QCheckBox,
        )

        assert isinstance(
            page.maintenance_width_spinbox,
            QDoubleSpinBox,
        )

        assert isinstance(
            page.maintenance_orientation_combobox,
            QComboBox,
        )

    # ==================================================
    # Default widget state
    # ==================================================

    def test_maximum_panel_count_is_disabled_by_default(
        self,
        page,
    ):

        assert (
            not page.max_panels_spinbox.isEnabled()
        )

    def test_maximum_panel_count_can_be_enabled(
        self,
        page,
    ):

        page.max_panels_checkbox.setChecked(
            True
        )

        assert (
            page.max_panels_spinbox.isEnabled()
        )

    def test_maximum_panel_count_can_be_disabled(
        self,
        page,
    ):

        page.max_panels_checkbox.setChecked(
            True
        )

        page.max_panels_checkbox.setChecked(
            False
        )

        assert (
            not page.max_panels_spinbox.isEnabled()
        )

    # ==================================================
    # Maintenance state
    # ==================================================

    def test_maintenance_controls_are_disabled_by_default(
        self,
        page,
    ):

        assert (
            not page.maintenance_width_spinbox.isEnabled()
        )

        assert not (
            page.maintenance_orientation_combobox.isEnabled()
        )

    def test_maintenance_controls_are_enabled_when_required(
        self,
        page,
    ):

        page.maintenance_required_checkbox.setChecked(
            True
        )

        assert (
            page.maintenance_width_spinbox.isEnabled()
        )

        assert (
            page.maintenance_orientation_combobox.isEnabled()
        )

    def test_maintenance_controls_are_disabled_when_not_required(
        self,
        page,
    ):

        page.maintenance_required_checkbox.setChecked(
            True
        )

        page.maintenance_required_checkbox.setChecked(
            False
        )

        assert (
            not page.maintenance_width_spinbox.isEnabled()
        )

        assert not (
            page.maintenance_orientation_combobox.isEnabled()
        )

    # ==================================================
    # Maintenance orientation
    # ==================================================

    def test_maintenance_orientations_are_available(
        self,
        page,
    ):

        assert (
            page.maintenance_orientation_combobox
            .findData("auto")
            >= 0
        )

        assert (
            page.maintenance_orientation_combobox
            .findData("vertical")
            >= 0
        )

        assert (
            page.maintenance_orientation_combobox
            .findData("horizontal")
            >= 0
        )

    # ==================================================
    # Installation configuration
    # ==================================================

    def test_get_installation_configuration_returns_configuration(
        self,
        page,
    ):

        page.available_area_spinbox.setValue(
            42.25
        )

        page.panel_width_spinbox.setValue(
            1.134
        )

        page.panel_height_spinbox.setValue(
            1.762
        )

        page.panel_power_spinbox.setValue(
            540
        )

        page.min_panels_spinbox.setValue(
            5
        )

        configuration = (
            page.get_installation_configuration()
        )

        assert isinstance(
            configuration,
            InstallationConfiguration,
        )

    def test_get_installation_configuration_maps_values(
        self,
        page,
    ):

        page.available_area_spinbox.setValue(
            42.25
        )

        page.panel_width_spinbox.setValue(
            1.134
        )

        page.panel_height_spinbox.setValue(
            1.762
        )

        page.panel_power_spinbox.setValue(
            540
        )

        page.min_panels_spinbox.setValue(
            5
        )

        configuration = (
            page.get_installation_configuration()
        )

        assert (
            configuration.available_area_m2
            == pytest.approx(42.25)
        )

        assert (
            configuration.panel_width_m
            == pytest.approx(1.134)
        )

        assert (
            configuration.panel_height_m
            == pytest.approx(1.762)
        )

        assert (
            configuration.panel_power_wp
            == pytest.approx(540)
        )

        assert configuration.min_panels == 5

    # ==================================================
    # Maximum panels
    # ==================================================

    def test_unchecked_maximum_panels_returns_none(
        self,
        page,
    ):

        page.max_panels_checkbox.setChecked(
            False
        )

        page.max_panels_spinbox.setValue(
            20
        )

        configuration = (
            page.get_installation_configuration()
        )

        assert configuration.max_panels is None

    def test_checked_maximum_panels_is_returned(
        self,
        page,
    ):

        page.max_panels_checkbox.setChecked(
            True
        )

        page.max_panels_spinbox.setValue(
            20
        )

        configuration = (
            page.get_installation_configuration()
        )

        assert configuration.max_panels == 20

    # ==================================================
    # Roof dimensions
    # ==================================================

    def test_zero_roof_dimensions_become_none(
        self,
        page,
    ):

        page.roof_width_spinbox.setValue(
            0
        )

        page.roof_height_spinbox.setValue(
            0
        )

        configuration = (
            page.get_installation_configuration()
        )

        assert configuration.roof_width_m is None
        assert configuration.roof_height_m is None

    def test_roof_dimensions_are_preserved(
        self,
        page,
    ):

        page.roof_width_spinbox.setValue(
            6.5
        )

        page.roof_height_spinbox.setValue(
            6.5
        )

        configuration = (
            page.get_installation_configuration()
        )

        assert (
            configuration.roof_width_m
            == pytest.approx(6.5)
        )

        assert (
            configuration.roof_height_m
            == pytest.approx(6.5)
        )

    # ==================================================
    # Maintenance configuration
    # ==================================================

    def test_maintenance_configuration_is_mapped(
        self,
        page,
    ):

        page.maintenance_required_checkbox.setChecked(
            True
        )

        page.maintenance_width_spinbox.setValue(
            0.45
        )

        page.maintenance_orientation_combobox.setCurrentIndex(
            page.maintenance_orientation_combobox.findData(
                "vertical"
            )
        )

        configuration = (
            page.get_installation_configuration()
        )

        assert (
            configuration.maintenance_passage_required
            is True
        )

        assert (
            configuration.maintenance_passage_width_m
            == pytest.approx(0.45)
        )

        assert (
            configuration.maintenance_passage_orientation
            == "vertical"
        )

    # ==================================================
    # Conversion to constraints
    # ==================================================

    def test_configuration_can_be_converted_to_constraints(
        self,
        page,
    ):

        page.available_area_spinbox.setValue(
            42.25
        )

        page.panel_width_spinbox.setValue(
            1.134
        )

        page.panel_height_spinbox.setValue(
            1.762
        )

        page.panel_power_spinbox.setValue(
            540
        )

        configuration = (
            page.get_installation_configuration()
        )

        constraints = (
            configuration.to_constraints()
        )

        assert (
            constraints.available_area_m2
            == pytest.approx(42.25)
        )

        assert (
            constraints.panel_power_wp
            == pytest.approx(540)
        )

    # ==================================================
    # Static name translations
    # ==================================================

    def test_get_technology_name_known_values(
        self,
    ):

        assert (
            SolarConfigPage.get_technology_name(
                "crystSi"
            )
            == "Silicio cristalino"
        )

        assert (
            SolarConfigPage.get_technology_name(
                "CIS"
            )
            == "CIS"
        )

        assert (
            SolarConfigPage.get_technology_name(
                "CdTe"
            )
            == "CdTe"
        )

    def test_get_technology_name_unknown_value(
        self,
    ):

        assert (
            SolarConfigPage.get_technology_name(
                "unknown"
            )
            == "unknown"
        )

    def test_get_mounting_name_known_values(
        self,
    ):

        assert (
            SolarConfigPage.get_mounting_name(
                "free"
            )
            == "Estructura sobre el suelo"
        )

        assert (
            SolarConfigPage.get_mounting_name(
                "building"
            )
            == "Integrado en edificio"
        )

    def test_get_mounting_name_unknown_value(
        self,
    ):

        assert (
            SolarConfigPage.get_mounting_name(
                "unknown"
            )
            == "unknown"
        )

    # ==================================================
    # Optimization
    # ==================================================

    def test_start_optimization_completes_successfully(
        self,
        page,
        project,
    ):

        page.pvgis_service.get_specific_production = MagicMock(
            return_value=1000.0
        )

        page.available_area_spinbox.setValue(
            42.25
        )

        page.panel_width_spinbox.setValue(
            1.134
        )

        page.panel_height_spinbox.setValue(
            1.762
        )

        page.panel_power_spinbox.setValue(
            540
        )

        page.min_panels_spinbox.setValue(
            5
        )

        page.start_optimization()

        assert page.status_label.text() == (
            "Optimización completada"
        )

        assert (
            project.solar.sizing_result
            is not None
        )

        result = project.solar.sizing_result

        assert result.panel_count >= 5

        assert result.installed_power_kwp == pytest.approx(
            result.panel_count * 0.54
        )

        assert result.annual_production_kwh == pytest.approx(
            result.installed_power_kwp * 1000.0
        )

    def test_start_optimization_stores_installation_result(
        self,
        page,
        project,
    ):

        page.pvgis_service.get_specific_production = MagicMock(
            return_value=1000.0
        )

        page.available_area_spinbox.setValue(
            42.25
        )

        page.panel_width_spinbox.setValue(
            1.134
        )

        page.panel_height_spinbox.setValue(
            1.762
        )

        page.panel_power_spinbox.setValue(
            540
        )

        page.min_panels_spinbox.setValue(
            5
        )

        page.start_optimization()

        result = project.solar.sizing_result

        assert isinstance(
            result,
            InstallationRecommendation,
        )

        assert result.panel_count >= 5

        assert result.installed_power_kwp == pytest.approx(
            result.panel_count * 0.54
        )

        assert result.annual_production_kwh == pytest.approx(
            result.installed_power_kwp * 1000.0
        )

    def test_start_optimization_result_is_consistent(
        self,
        page,
        project,
    ):

        page.pvgis_service.get_specific_production = MagicMock(
            return_value=1000.0
        )

        page.available_area_spinbox.setValue(
            42.25
        )

        page.panel_width_spinbox.setValue(
            1.134
        )

        page.panel_height_spinbox.setValue(
            1.762
        )

        page.panel_power_spinbox.setValue(
            540
        )

        page.min_panels_spinbox.setValue(
            5
        )

        page.start_optimization()

        result = (
            project.solar.sizing_result
        )

        assert result.panel_count >= 5

        assert result.installed_power_kwp == pytest.approx(
            result.panel_count * 0.54
        )

        assert result.annual_production_kwh == pytest.approx(
            result.installed_power_kwp * 1000.0
        )

    def test_start_optimization_reenables_button_after_success(
        self,
        page,
        project,
    ):

        page.pvgis_service.get_specific_production = MagicMock(
            return_value=1000.0
        )

        page.available_area_spinbox.setValue(
            42.25
        )

        page.panel_width_spinbox.setValue(
            1.134
        )

        page.panel_height_spinbox.setValue(
            1.762
        )

        page.panel_power_spinbox.setValue(
            540
        )

        page.min_panels_spinbox.setValue(
            5
        )

        page.optimize_button.setEnabled(
            False
        )

        page.start_optimization()

        assert page.optimize_button.isEnabled()

        assert page.status_label.text() == (
            "Optimización completada"
        )

        assert (
            project.solar.sizing_result
            is not None
        )

    # ==================================================
    # Reset
    # ==================================================

    def test_reset_restores_available_configuration_status(
        self,
        page,
    ):

        assert page.status_label.text() == (
            "Configuración solar disponible"
        )

        page.optimize_button.setEnabled(
            False
        )

        page.reset()

        assert page.status_label.text() == (
            "Configuración solar disponible"
        )

        assert page.optimize_button.isEnabled()

    # ==================================================
    # Missing solar configuration
    # ==================================================

    def test_missing_solar_configuration_is_handled(
        self,
        qtbot,
    ):

        class EmptySolarEngine:
            configuration = None

        class EmptyAnalyzer:
            solar_engine = EmptySolarEngine()

        class EmptySolar:
            sizing_result = None

        class EmptyProject:
            analyzer = EmptyAnalyzer()
            solar = EmptySolar()

        page = SolarConfigPage(
            EmptyProject()
        )

        qtbot.addWidget(page)

        assert page.status_label.text() == (
            "Configuración solar no disponible"
        )

    def test_start_optimization_uses_valid_dataset_consumption(
        self,
        page,
        project,
    ):

        page.pvgis_service.get_specific_production = MagicMock(
            return_value=1000.0
        )

        project.analyzer.valid_dataset = MagicMock(
            return_value=pd.DataFrame(
                {
                    "AE_kWh": [
                        1000.0,
                        1500.0,
                        2000.0,
                    ]
                }
            )
        )

        page.available_area_spinbox.setValue(
            42.25
        )

        page.panel_width_spinbox.setValue(
            1.134
        )

        page.panel_height_spinbox.setValue(
            1.762
        )

        page.panel_power_spinbox.setValue(
            540
        )

        page.min_panels_spinbox.setValue(
            5
        )

        page.max_panels_checkbox.setChecked(
            True
        )

        page.max_panels_spinbox.setValue(
            15
        )

        page.start_optimization()

        assert (
            page.status_label.text()
            == "Optimización completada"
        )

        assert (
            project.solar.sizing_result
            is not None
        )

        assert (
            project.solar.sizing_result
            .annual_consumption_kwh
            == pytest.approx(4500.0)
        )


    def test_start_optimization_rejects_empty_dataset(
        self,
        page,
        project,
    ):

        previous_result = (
            project.solar.sizing_result
        )

        project.analyzer.valid_dataset = MagicMock(
            return_value=pd.DataFrame(
                columns=["AE_kWh"]
            )
        )

        page.start_optimization()

        assert (
            page.status_label.text()
            == "Error: A valid consumption dataset is required."
        )

        assert (
            project.solar.sizing_result
            is previous_result
        )

        assert page.optimize_button.isEnabled()

    def test_start_optimization_rejects_missing_dataset(
        self,
        page,
        project,
    ):

        previous_result = (
            project.solar.sizing_result
        )

        project.analyzer.valid_dataset = MagicMock(
            return_value=None
        )

        page.start_optimization()

        assert (
            page.status_label.text()
            == "Error: A valid consumption dataset is required."
        )

        assert (
            project.solar.sizing_result
            is previous_result
        )

        assert page.optimize_button.isEnabled()

    def test_start_optimization_rejects_zero_consumption(
        self,
        page,
        project,
    ):

        previous_result = (
            project.solar.sizing_result
        )

        project.analyzer.valid_dataset = MagicMock(
            return_value=pd.DataFrame(
                {
                    "AE_kWh": [
                        0.0,
                        0.0,
                        0.0,
                    ]
                }
            )
        )

        page.start_optimization()

        assert (
            page.status_label.text()
            == "Error: Annual consumption must be greater than zero."
        )

        assert (
            project.solar.sizing_result
            is previous_result
        )

        assert page.optimize_button.isEnabled()