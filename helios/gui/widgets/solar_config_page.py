from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QDoubleSpinBox,
    QComboBox,
    QPushButton,
    QSpinBox,
    QLabel,
)

import traceback

from helios.solar.configuration import SolarConfiguration


class SolarConfigPage(QWidget):
    """
    Página de configuración de la instalación fotovoltaica.

    Permite definir los parámetros de la instalación y
    lanzar la simulación solar.

    La página no muestra resultados de producción.
    Estos se consultan posteriormente desde SolarPage.
    """

    def __init__(self, project, main_window=None):

        super().__init__()

        self.project = project
        self.main_window = main_window

        self.setup_ui()
        self.configure_widgets()
        self.connect_signals()

    # ==================================================
    # Interfaz
    # ==================================================

    def setup_ui(self):

        layout = QVBoxLayout(self)

        layout.addWidget(
            self.create_installation_group()
        )

        layout.addWidget(
            self.create_location_group()
        )

        layout.addWidget(
            self.create_calculation_group()
        )

        layout.addStretch()

    # ==================================================
    # Grupos
    # ==================================================

    def create_installation_group(self):

        group = QGroupBox("Instalación")

        layout = QFormLayout(group)

        self.peak_power_spinbox = QDoubleSpinBox()
        self.pv_technology_combobox = QComboBox()
        self.system_losses_spinbox = QDoubleSpinBox()
        self.tilt_spinbox = QSpinBox()
        self.azimuth_spinbox = QSpinBox()
        self.mounting_place_combobox = QComboBox()

        layout.addRow(
            "Potencia instalada",
            self.peak_power_spinbox
        )

        layout.addRow(
            "Tecnología FV",
            self.pv_technology_combobox
        )

        layout.addRow(
            "Pérdidas del sistema",
            self.system_losses_spinbox
        )

        layout.addRow(
            "Inclinación",
            self.tilt_spinbox
        )

        layout.addRow(
            "Orientación",
            self.azimuth_spinbox
        )

        layout.addRow(
            "Montaje",
            self.mounting_place_combobox
        )

        return group

    def create_location_group(self):

        group = QGroupBox("Ubicación")

        layout = QFormLayout(group)

        self.latitude_spinbox = QDoubleSpinBox()
        self.longitude_spinbox = QDoubleSpinBox()

        layout.addRow(
            "Latitud",
            self.latitude_spinbox
        )

        layout.addRow(
            "Longitud",
            self.longitude_spinbox
        )

        return group

    def create_calculation_group(self):

        group = QGroupBox("Simulación")

        layout = QFormLayout(group)

        self.reference_year_label = QLabel("2023")

        self.calculate_production_button = QPushButton(
            "Calcular producción"
        )

        self.status_label = QLabel(
            "No calculada"
        )

        layout.addRow(
            "Año de referencia",
            self.reference_year_label
        )

        layout.addRow(
            "Estado",
            self.status_label
        )

        layout.addRow(
            "",
            self.calculate_production_button
        )

        return group

    # ==================================================
    # Configuración de widgets
    # ==================================================

    def configure_widgets(self):

        self.configure_peak_power()
        self.configure_pv_technology()
        self.configure_system_losses()
        self.configure_tilt()
        self.configure_azimuth()
        self.configure_mounting_place()

        self.configure_latitude()
        self.configure_longitude()

        self.calculate_production_button.setMinimumHeight(
            40
        )

        self.calculate_production_button.setToolTip(
            "Obtiene la producción fotovoltaica desde PVGIS."
        )

    def configure_peak_power(self):

        self.peak_power_spinbox.setRange(
            0.10,
            100.00
        )

        self.peak_power_spinbox.setDecimals(2)

        self.peak_power_spinbox.setSingleStep(
            0.10
        )

        self.peak_power_spinbox.setSuffix(
            " kWp"
        )

    def configure_pv_technology(self):

        self.pv_technology_combobox.addItem(
            "Silicio cristalino",
            "crystSi"
        )

        self.pv_technology_combobox.addItem(
            "CIS",
            "CIS"
        )

        self.pv_technology_combobox.addItem(
            "CdTe",
            "CdTe"
        )

    def configure_system_losses(self):

        self.system_losses_spinbox.setRange(
            0.0,
            100.0
        )

        self.system_losses_spinbox.setDecimals(
            1
        )

        self.system_losses_spinbox.setSingleStep(
            0.5
        )

        self.system_losses_spinbox.setSuffix(
            " %"
        )

    def configure_latitude(self):

        self.latitude_spinbox.setRange(
            -90.0,
            90.0
        )

        self.latitude_spinbox.setDecimals(
            6
        )

        self.latitude_spinbox.setSingleStep(
            0.000001
        )

    def configure_longitude(self):

        self.longitude_spinbox.setRange(
            -180.0,
            180.0
        )

        self.longitude_spinbox.setDecimals(
            6
        )

        self.longitude_spinbox.setSingleStep(
            0.000001
        )

    def configure_tilt(self):

        self.tilt_spinbox.setRange(
            0,
            90
        )

        self.tilt_spinbox.setSuffix(
            " °"
        )

    def configure_azimuth(self):

        self.azimuth_spinbox.setRange(
            -180,
            180
        )

        self.azimuth_spinbox.setSuffix(
            " °"
        )

    def configure_mounting_place(self):

        self.mounting_place_combobox.addItem(
            "Estructura sobre el suelo",
            "free"
        )

        self.mounting_place_combobox.addItem(
            "Integrado en edificio",
            "building"
        )

    # ==================================================
    # Señales
    # ==================================================

    def connect_signals(self):

        self.calculate_production_button.clicked.connect(
            self.calculate_production
        )

    # ==================================================
    # Configuración solar
    # ==================================================

    def get_configuration(self) -> SolarConfiguration:
        """
        Construye la configuración solar a partir
        de los valores introducidos en la interfaz.
        """

        return SolarConfiguration(

            installed_power_kwp=(
                self.peak_power_spinbox.value()
            ),

            latitude=(
                self.latitude_spinbox.value()
            ),

            longitude=(
                self.longitude_spinbox.value()
            ),

            tilt=(
                self.tilt_spinbox.value()
            ),

            azimuth=(
                self.azimuth_spinbox.value()
            ),

            reference_year=2023,

            losses=(
                self.system_losses_spinbox.value()
            ),

            pv_technology=(
                self.pv_technology_combobox.currentData()
            ),

            mounting_place=(
                self.mounting_place_combobox.currentData()
            ),
        )

    # ==================================================
    # Cálculo
    # ==================================================

    def calculate_production(self):

        configuration = self.get_configuration()

        self.status_label.setText(
            "Calculando..."
        )

        self.calculate_production_button.setEnabled(
            False
        )

        try:

            self.project.solar.calculate(
                configuration
            )

            self.status_label.setText(
                "Simulación disponible"
            )

            if self.main_window is not None:

                self.main_window.set_solar_calculated(
                    True
                )

        except Exception as error:

            self.status_label.setText(
                f"Error: {error}"
            )

            traceback.print_exc()

        finally:

            self.calculate_production_button.setEnabled(
                True
            )

    # ==================================================
    # Reset
    # ==================================================

    def reset(self):

        self.status_label.setText(
            "No calculada"
        )

        self.calculate_production_button.setEnabled(
            True
        )