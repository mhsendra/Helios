from unittest.mock import MagicMock, patch

import pandas as pd

import pytest

from PySide6.QtWidgets import QApplication

from helios.gui.widgets.load_data_page import LoadDataPage

from helios.solar.configuration import SolarConfiguration


class TestLoadDataPage:

    @classmethod
    def setup_class(cls):

        cls.app = QApplication.instance()

        if cls.app is None:
            cls.app = QApplication([])

    def setup_method(self):

        self.project = MagicMock()
        self.main_window = MagicMock()

        self.page = LoadDataPage(
            self.project,
            self.main_window
        )

    # ==================================================
    # Estado inicial
    # ==================================================

    def test_page_stores_project_and_main_window(self):

        assert self.page.project is self.project
        assert self.page.main_window is self.main_window

    def test_widgets_start_with_expected_values(self):

        assert self.page.path_edit.text() == ""

        assert (
            self.page.path_edit.isReadOnly()
        )

        assert (
            self.page.browse_button.text()
            == "Examinar..."
        )

        assert (
            self.page.load_button.text()
            == "Cargar"
        )

        assert (
            self.page.info_label.text()
            == "Ningún archivo cargado"
        )

    # ==================================================
    # browse_file
    # ==================================================

    def test_browse_file_sets_selected_path(self):

        filename = r"C:\datos\consumo.xlsx"

        with patch(
            "helios.gui.widgets.load_data_page.QFileDialog.getOpenFileName",
            return_value=(filename, "Excel (*.xlsx *.xls)")
        ):

            self.page.browse_file()

        assert (
            self.page.path_edit.text()
            == filename
        )

    def test_browse_file_does_not_change_path_when_cancelled(self):

        self.page.path_edit.setText(
            "archivo_anterior.xlsx"
        )

        with patch(
            "helios.gui.widgets.load_data_page.QFileDialog.getOpenFileName",
            return_value=("", "")
        ):

            self.page.browse_file()

        assert (
            self.page.path_edit.text()
            == "archivo_anterior.xlsx"
        )

    # ==================================================
    # load_dataset — sin archivo
    # ==================================================

    def test_load_dataset_without_path(self):

        self.page.load_dataset()

        assert (
            self.page.info_label.text()
            == "Seleccione un archivo."
        )

        self.project.load_data.assert_not_called()
        self.project.analyze_data.assert_not_called()

    # ==================================================
    # load_dataset — carga correcta
    # ==================================================

    def test_load_dataset_success(self):

        self.page.path_edit.setText(
            r"C:\datos\consumo.xlsx"
        )

        self.page.update_project_info = MagicMock()

        self.page.load_dataset()

        self.project.load_data.assert_called_once_with(
            r"C:\datos\consumo.xlsx"
        )

        self.project.analyze_data.assert_called_once_with()

        self.page.update_project_info.assert_called_once_with()

        self.main_window.update_project_pages.assert_called_once_with()

        self.main_window.set_project_loaded.assert_called_once_with(
            True
        )

    def test_load_dataset_resets_solar_results_without_calculating(self):

        self.page.path_edit.setText(
            r"C:\datos\consumo.xlsx"
        )

        self.page.update_project_info = MagicMock()

        self.project.solar_configuration = None

        self.project.solar.reset = MagicMock()
        self.project.solar.calculate = MagicMock()

        self.page.load_dataset()

        self.project.solar.reset.assert_called_once_with()

        self.project.solar.calculate.assert_not_called()

        self.main_window.solar_page.reset_results.assert_called_once_with()

    def test_load_dataset_preserves_stored_solar_configuration(self):

        self.page.path_edit.setText(
            r"C:\datos\consumo.xlsx"
        )

        configuration = SolarConfiguration(
            latitude=41.6167,
            longitude=2.0833,
            tilt=30,
            azimuth=0,
            reference_year=2023,
            losses=14.0,
            pv_technology="crystSi",
            mounting_place="building",
        )

        self.project.solar_configuration = configuration

        self.page.update_project_info = MagicMock()

        self.project.solar.reset = MagicMock()
        self.project.solar.calculate = MagicMock()

        self.page.load_dataset()

        assert (
            self.project.solar_configuration
            is configuration
        )

        self.project.solar.reset.assert_called_once_with()

        self.project.solar.calculate.assert_not_called()
        
    # ==================================================
    # load_dataset — error
    # ==================================================

    def test_load_dataset_handles_error(self):

        self.page.path_edit.setText(
            r"C:\datos\consumo.xlsx"
        )

        self.project.load_data.side_effect = ValueError(
            "Archivo inválido"
        )

        self.page.load_dataset()

        assert (
            self.page.info_label.text()
            == "Error: ValueError: Archivo inválido"
        )

        self.project.load_data.assert_called_once_with(
            r"C:\datos\consumo.xlsx"
        )

        self.project.analyze_data.assert_not_called()

        self.main_window.update_project_pages.assert_not_called()

        self.main_window.set_project_loaded.assert_not_called()

    # ==================================================
    # update_project_info — sin dataset
    # ==================================================

    def test_update_project_info_without_dataset(self):

        self.project.dataset = None

        self.page.update_project_info()

        assert (
            self.page.info_label.text()
            == "Ningún archivo cargado."
        )

    # ==================================================
    # update_project_info — con dataset
    # ==================================================

    def test_update_project_info_sets_project_information(self):

        self.page.path_edit.setText(
            r"C:\datos\consumo.xlsx"
        )

        self.project.dataset = pd.DataFrame(
            {
                "AE_kWh": [1.0, 2.0, 3.0]
            },
            index=pd.to_datetime(
                [
                    "2025-01-01",
                    "2025-01-02",
                    "2025-01-03",
                ]
            )
        )

        self.project.quality = {
            "coverage": 99.43,
            "rating": "EXCELENTE",
        }

        self.page.update_project_info()

        text = self.page.info_label.text()

        assert "consumo.xlsx" in text
        assert "3" in text
        assert "01/01/2025" in text
        assert "03/01/2025" in text
        assert "99.43%" in text
        assert "EXCELENTE" in text

    # ==================================================
    # Configuración solar
    # ==================================================

    def test_get_solar_configuration(self):

        self.page.latitude_spinbox.setValue(41.6167)
        self.page.longitude_spinbox.setValue(2.0833)

        self.page.tilt_spinbox.setValue(30)
        self.page.azimuth_spinbox.setValue(0)

        self.page.system_losses_spinbox.setValue(14.0)

        self.page.pv_technology_combobox.setCurrentIndex(
            self.page.pv_technology_combobox.findData(
                "crystSi"
            )
        )

        self.page.mounting_place_combobox.setCurrentIndex(
            self.page.mounting_place_combobox.findData(
                "building"
            )
        )

        configuration = (
            self.page.get_solar_configuration()
        )

        assert configuration.latitude == pytest.approx(
            41.6167
        )

        assert configuration.longitude == pytest.approx(
            2.0833
        )

        assert configuration.tilt == 30

        assert configuration.azimuth == 0

        assert configuration.reference_year == 2023

        assert configuration.losses == pytest.approx(
            14.0
        )

        assert configuration.pv_technology == "crystSi"

        assert configuration.mounting_place == "building"


    def test_save_solar_configuration_delegates_to_project(self):

        configuration = MagicMock()

        self.page.get_solar_configuration = MagicMock(
            return_value=configuration
        )

        self.page.save_solar_configuration()

        self.project.set_solar_configuration.assert_called_once_with(
            configuration
        )


    def test_save_solar_configuration_does_not_calculate(self):

        configuration = MagicMock()

        self.page.get_solar_configuration = MagicMock(
            return_value=configuration
        )

        self.page.save_solar_configuration()

        self.project.solar.calculate.assert_not_called()

    def test_save_solar_configuration(
        self,
    ):

        configuration = SolarConfiguration(
            latitude=41.6167,
            longitude=2.0833,
            tilt=30,
            azimuth=0,
            reference_year=2023,
            losses=14.0,
            pv_technology="crystSi",
            mounting_place="building",
        )

        self.page.get_solar_configuration = (
            MagicMock(
                return_value=configuration
            )
        )

        self.page.project.set_solar_configuration = (
            MagicMock()
        )

        self.page.main_window.solar_config_page.update_data = (
            MagicMock()
        )

        self.page.save_solar_configuration()

        self.page.project.set_solar_configuration.assert_called_once_with(
            configuration
        )

        self.page.main_window.solar_config_page.update_data.assert_called_once_with()

        assert (
            self.page.solar_configuration_status.text()
            == "Configuración solar guardada."
        )