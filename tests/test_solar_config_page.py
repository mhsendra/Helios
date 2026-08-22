import pytest

from PySide6.QtWidgets import QApplication

from helios.gui.widgets.solar_config_page import SolarConfigPage
from helios.solar.configuration import SolarConfiguration


@pytest.fixture(autouse=True)
def app():
    return QApplication.instance() or QApplication([])

class FakeSolar:

    def __init__(self):
        self.calculate_calls = []

    def calculate(self, configuration):

        self.calculate_calls.append(
            configuration
        )


class FakeProject:

    def __init__(self):

        self.solar = FakeSolar()


class FakeMainWindow:

    def __init__(self):

        self.solar_calculated_calls = []

    def set_solar_calculated(self, calculated):

        self.solar_calculated_calls.append(
            calculated
        )


class TestSolarConfigPage:

    def setup_method(self):

        self.project = FakeProject()
        self.main_window = FakeMainWindow()

        self.page = SolarConfigPage(
            self.project,
            self.main_window
        )

    # ==================================================
    # Creación
    # ==================================================

    def test_page_uses_project(self):

        assert self.page.project is self.project

    def test_page_uses_main_window(self):

        assert (
            self.page.main_window
            is self.main_window
        )

    # ==================================================
    # Widgets
    # ==================================================

    def test_installation_widgets_exist(self):

        assert self.page.peak_power_spinbox is not None
        assert self.page.pv_technology_combobox is not None
        assert self.page.system_losses_spinbox is not None
        assert self.page.tilt_spinbox is not None
        assert self.page.azimuth_spinbox is not None
        assert (
            self.page.mounting_place_combobox
            is not None
        )

    def test_location_widgets_exist(self):

        assert self.page.latitude_spinbox is not None
        assert self.page.longitude_spinbox is not None

    def test_calculation_widgets_exist(self):

        assert (
            self.page.reference_year_label.text()
            == "2023"
        )

        assert (
            self.page.status_label.text()
            == "No calculada"
        )

        assert (
            self.page.calculate_production_button
            is not None
        )

    # ==================================================
    # Configuración de potencia
    # ==================================================

    def test_peak_power_configuration(self):

        widget = self.page.peak_power_spinbox

        assert widget.minimum() == pytest.approx(0.10)
        assert widget.maximum() == pytest.approx(100.00)
        assert widget.decimals() == 2
        assert widget.singleStep() == pytest.approx(0.10)
        assert widget.suffix() == " kWp"

    # ==================================================
    # Tecnología FV
    # ==================================================

    def test_pv_technology_options(self):

        widget = self.page.pv_technology_combobox

        assert widget.count() == 3

        assert widget.itemText(0) == "Silicio cristalino"
        assert widget.itemData(0) == "crystSi"

        assert widget.itemText(1) == "CIS"
        assert widget.itemData(1) == "CIS"

        assert widget.itemText(2) == "CdTe"
        assert widget.itemData(2) == "CdTe"

    # ==================================================
    # Pérdidas
    # ==================================================

    def test_system_losses_configuration(self):

        widget = self.page.system_losses_spinbox

        assert widget.minimum() == pytest.approx(0.0)
        assert widget.maximum() == pytest.approx(100.0)
        assert widget.decimals() == 1
        assert widget.singleStep() == pytest.approx(0.5)
        assert widget.suffix() == " %"

    # ==================================================
    # Ubicación
    # ==================================================

    def test_latitude_configuration(self):

        widget = self.page.latitude_spinbox

        assert widget.minimum() == pytest.approx(-90.0)
        assert widget.maximum() == pytest.approx(90.0)
        assert widget.decimals() == 6
        assert widget.singleStep() == pytest.approx(
            0.000001
        )

    def test_longitude_configuration(self):

        widget = self.page.longitude_spinbox

        assert widget.minimum() == pytest.approx(-180.0)
        assert widget.maximum() == pytest.approx(180.0)
        assert widget.decimals() == 6
        assert widget.singleStep() == pytest.approx(
            0.000001
        )

    # ==================================================
    # Inclinación
    # ==================================================

    def test_tilt_configuration(self):

        widget = self.page.tilt_spinbox

        assert widget.minimum() == 0
        assert widget.maximum() == 90
        assert widget.suffix() == " °"

    # ==================================================
    # Orientación
    # ==================================================

    def test_azimuth_configuration(self):

        widget = self.page.azimuth_spinbox

        assert widget.minimum() == -180
        assert widget.maximum() == 180
        assert widget.suffix() == " °"

    # ==================================================
    # Montaje
    # ==================================================

    def test_mounting_place_options(self):

        widget = self.page.mounting_place_combobox

        assert widget.count() == 2

        assert (
            widget.itemText(0)
            == "Estructura sobre el suelo"
        )

        assert widget.itemData(0) == "free"

        assert (
            widget.itemText(1)
            == "Integrado en edificio"
        )

        assert widget.itemData(1) == "building"

    # ==================================================
    # Configuración
    # ==================================================

    def test_get_configuration_returns_solar_configuration(
        self
    ):

        configuration = self.page.get_configuration()

        assert isinstance(
            configuration,
            SolarConfiguration
        )

    def test_get_configuration_uses_widget_values(
        self
    ):

        self.page.peak_power_spinbox.setValue(8.10)

        self.page.latitude_spinbox.setValue(
            41.590
        )

        self.page.longitude_spinbox.setValue(
            2.267
        )

        self.page.tilt_spinbox.setValue(30)

        self.page.azimuth_spinbox.setValue(10)

        self.page.system_losses_spinbox.setValue(
            14.5
        )

        self.page.pv_technology_combobox.setCurrentIndex(
            1
        )

        self.page.mounting_place_combobox.setCurrentIndex(
            1
        )

        configuration = self.page.get_configuration()

        assert (
            configuration.installed_power_kwp
            == pytest.approx(8.10)
        )

        assert (
            configuration.latitude
            == pytest.approx(41.590)
        )

        assert (
            configuration.longitude
            == pytest.approx(2.267)
        )

        assert configuration.tilt == 30
        assert configuration.azimuth == 10

        assert (
            configuration.losses
            == pytest.approx(14.5)
        )

        assert (
            configuration.pv_technology
            == "CIS"
        )

        assert (
            configuration.mounting_place
            == "building"
        )

        assert configuration.reference_year == 2023

    # ==================================================
    # Simulación
    # ==================================================

    def test_calculate_production_calls_solar_engine(
        self
    ):

        self.page.peak_power_spinbox.setValue(
            5.40
        )

        self.page.calculate_production()

        assert len(
            self.project.solar.calculate_calls
        ) == 1

        configuration = (
            self.project.solar.calculate_calls[0]
        )

        assert isinstance(
            configuration,
            SolarConfiguration
        )

        assert (
            configuration.installed_power_kwp
            == pytest.approx(5.40)
        )

    def test_calculate_production_enables_economics(
        self
    ):

        self.page.calculate_production()

        assert (
            self.main_window.solar_calculated_calls
            == [True]
        )

    def test_calculate_production_updates_status(
        self
    ):

        self.page.calculate_production()

        assert (
            self.page.status_label.text()
            == "Simulación disponible"
        )

    def test_calculate_production_reenables_button(
        self
    ):

        self.page.calculate_production()

        assert (
            self.page.calculate_production_button
            .isEnabled()
        )

    # ==================================================
    # Errores
    # ==================================================

    def test_calculate_production_handles_error(self):

        def failing_calculate(configuration):

            raise RuntimeError(
                "PVGIS unavailable"
            )

        self.project.solar.calculate = (
            failing_calculate
        )

        self.page.calculate_production()

        assert (
            self.page.status_label.text()
            == "Error: PVGIS unavailable"
        )

    def test_calculate_production_does_not_enable_economics_on_error(
        self
    ):

        def failing_calculate(configuration):

            raise RuntimeError(
                "PVGIS unavailable"
            )

        self.project.solar.calculate = (
            failing_calculate
        )

        self.page.calculate_production()

        assert (
            self.main_window.solar_calculated_calls
            == []
        )

    def test_calculate_production_reenables_button_after_error(
        self
    ):

        def failing_calculate(configuration):

            raise RuntimeError(
                "PVGIS unavailable"
            )

        self.project.solar.calculate = (
            failing_calculate
        )

        self.page.calculate_production()

        assert (
            self.page.calculate_production_button
            .isEnabled()
        )

    # ==================================================
    # Reset
    # ==================================================

    def test_reset_restores_status(self):

        self.page.status_label.setText(
            "Simulación disponible"
        )

        self.page.reset()

        assert (
            self.page.status_label.text()
            == "No calculada"
        )

    def test_reset_enables_calculation_button(self):

        self.page.calculate_production_button.setEnabled(
            False
        )

        self.page.reset()

        assert (
            self.page.calculate_production_button
            .isEnabled()
        )