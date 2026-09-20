import pytest

from unittest.mock import MagicMock

from PySide6.QtWidgets import QApplication

from helios.gui.widgets.solar_config_page import (
    SolarConfigPage,
)

from helios.solar.configuration import SolarConfiguration


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
        main_window=None,
    ):

        project = self.create_project(
            solar_configuration
        )

        page = SolarConfigPage(
            project=project,
            main_window=main_window,
        )

        return page, project

    # ==========================================================
    # INICIALIZACIÓN
    # ==========================================================

    def test_initialization_without_solar_configuration(
        self,
    ):

        page, _ = self.create_page()

        assert (
            page.status_label.text()
            == "Configuración solar pendiente"
        )

        assert (
            page.latitude_spinbox.value()
            == pytest.approx(0.0)
        )

        assert (
            page.longitude_spinbox.value()
            == pytest.approx(0.0)
        )

        assert page.tilt_spinbox.value() == 0
        assert page.azimuth_spinbox.value() == 0

        assert (
            page.reference_year_spinbox.value()
            == 2023
        )

        assert (
            page.system_losses_spinbox.value()
            == pytest.approx(14.0)
        )

    def test_initialization_with_solar_configuration(
        self,
    ):

        configuration = (
            self.create_solar_configuration()
        )

        page, _ = self.create_page(
            configuration
        )

        assert (
            page.status_label.text()
            == "Configuración solar disponible"
        )

        assert (
            page.latitude_spinbox.value()
            == pytest.approx(41.62)
        )

        assert (
            page.longitude_spinbox.value()
            == pytest.approx(2.09)
        )

        assert page.tilt_spinbox.value() == 30
        assert page.azimuth_spinbox.value() == 0

        assert (
            page.reference_year_spinbox.value()
            == 2023
        )

        assert (
            page.system_losses_spinbox.value()
            == pytest.approx(14.0)
        )

        assert (
            page.pv_technology_combobox.currentData()
            == "crystSi"
        )

        assert (
            page.mounting_place_combobox.currentData()
            == "building"
        )

    # ==========================================================
    # GET CONFIGURATION
    # ==========================================================

    def test_get_solar_configuration_reads_widgets(
        self,
    ):

        page, _ = self.create_page()

        page.latitude_spinbox.setValue(41.62)
        page.longitude_spinbox.setValue(2.09)
        page.tilt_spinbox.setValue(30)
        page.azimuth_spinbox.setValue(0)
        page.reference_year_spinbox.setValue(2023)
        page.system_losses_spinbox.setValue(14.0)

        page.pv_technology_combobox.setCurrentIndex(
            page.pv_technology_combobox.findData(
                "crystSi"
            )
        )

        page.mounting_place_combobox.setCurrentIndex(
            page.mounting_place_combobox.findData(
                "building"
            )
        )

        configuration = (
            page.get_solar_configuration()
        )

        assert isinstance(
            configuration,
            SolarConfiguration,
        )

        assert configuration.latitude == pytest.approx(41.62)
        assert configuration.longitude == pytest.approx(2.09)
        assert configuration.tilt == 30
        assert configuration.azimuth == 0
        assert configuration.reference_year == 2023
        assert configuration.losses == pytest.approx(14.0)
        assert configuration.pv_technology == "crystSi"
        assert configuration.mounting_place == "building"

    # ==========================================================
    # SAVE
    # ==========================================================

    def test_save_solar_configuration_stores_configuration(
        self,
    ):

        configuration = (
            self.create_solar_configuration()
        )

        page, project = self.create_page()

        page.latitude_spinbox.setValue(
            configuration.latitude
        )

        page.longitude_spinbox.setValue(
            configuration.longitude
        )

        page.tilt_spinbox.setValue(
            configuration.tilt
        )

        page.azimuth_spinbox.setValue(
            configuration.azimuth
        )

        page.reference_year_spinbox.setValue(
            configuration.reference_year
        )

        page.system_losses_spinbox.setValue(
            configuration.losses
        )

        page.save_solar_configuration()

        project.set_solar_configuration.assert_called_once()

        saved_configuration = (
            project.set_solar_configuration.call_args.args[0]
        )

        assert isinstance(
            saved_configuration,
            SolarConfiguration,
        )

        assert (
            saved_configuration.latitude
            == pytest.approx(41.62)
        )

        assert (
            saved_configuration.longitude
            == pytest.approx(2.09)
        )

        assert (
            saved_configuration.tilt
            == 30
        )

        assert (
            saved_configuration.reference_year
            == 2023
        )

        assert (
            page.status_label.text()
            == "Configuración solar guardada."
        )

    def test_save_configuration_notifies_main_window(
        self,
    ):

        main_window = MagicMock()

        page, project = self.create_page(
            main_window=main_window
        )

        page.save_solar_configuration()

        main_window.set_solar_configured.assert_called_once_with(
            True
        )

        project.set_solar_configuration.assert_called_once()

    def test_saving_new_configuration_resets_previous_solar_calculation(
        self,
    ):

        previous_configuration = (
            self.create_solar_configuration()
        )

        main_window = MagicMock()

        page, project = self.create_page(
            solar_configuration=previous_configuration,
            main_window=main_window,
        )

        page.save_solar_configuration()

        project.solar.reset.assert_called_once()

        main_window.set_solar_calculated.assert_called_once_with(
            False
        )

    # ==========================================================
    # LOAD / UPDATE
    # ==========================================================

    def test_load_solar_basis_updates_widgets(
        self,
    ):

        configuration = SolarConfiguration(
            latitude=40.0,
            longitude=1.0,
            tilt=20,
            azimuth=10,
            reference_year=2024,
            losses=10.0,
            pv_technology="CIS",
            mounting_place="free",
        )

        page, _ = self.create_page(
            configuration
        )

        page.latitude_spinbox.setValue(0.0)

        page.load_solar_basis()

        assert (
            page.latitude_spinbox.value()
            == pytest.approx(40.0)
        )

        assert (
            page.longitude_spinbox.value()
            == pytest.approx(1.0)
        )

        assert page.tilt_spinbox.value() == 20
        assert page.azimuth_spinbox.value() == 10

        assert (
            page.reference_year_spinbox.value()
            == 2024
        )

        assert (
            page.system_losses_spinbox.value()
            == pytest.approx(10.0)
        )

        assert (
            page.pv_technology_combobox.currentData()
            == "CIS"
        )

        assert (
            page.mounting_place_combobox.currentData()
            == "free"
        )

        assert (
            page.status_label.text()
            == "Configuración solar disponible"
        )

    def test_update_data_reloads_configuration(
        self,
    ):

        configuration = (
            self.create_solar_configuration()
        )

        page, project = self.create_page(
            configuration
        )

        project.solar_configuration = SolarConfiguration(
            latitude=40.0,
            longitude=1.0,
            tilt=20,
            azimuth=10,
            reference_year=2024,
            losses=10.0,
            pv_technology="CIS",
            mounting_place="free",
        )

        page.update_data()

        assert (
            page.latitude_spinbox.value()
            == pytest.approx(40.0)
        )

        assert (
            page.longitude_spinbox.value()
            == pytest.approx(1.0)
        )

        assert page.tilt_spinbox.value() == 20
        assert page.azimuth_spinbox.value() == 10
        assert page.reference_year_spinbox.value() == 2024
        assert page.system_losses_spinbox.value() == pytest.approx(10.0)

        assert (
            page.pv_technology_combobox.currentData()
            == "CIS"
        )

        assert (
            page.mounting_place_combobox.currentData()
            == "free"
        )

    # ==========================================================
    # RESET
    # ==========================================================

    def test_reset_reloads_solar_configuration(
        self,
    ):

        configuration = (
            self.create_solar_configuration()
        )

        page, project = self.create_page(
            configuration
        )

        page.latitude_spinbox.setValue(0.0)

        page.reset()

        assert (
            page.latitude_spinbox.value()
            == pytest.approx(41.62)
        )

        assert (
            page.longitude_spinbox.value()
            == pytest.approx(2.09)
        )

        assert page.tilt_spinbox.value() == 30
        assert page.reference_year_spinbox.value() == 2023