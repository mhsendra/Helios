from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QDoubleSpinBox,
    QSpinBox,
    QComboBox,
    QPushButton,
    QLabel,
    QFrame,
    QScrollArea,
    QGroupBox,
)

from helios.solar.configuration import SolarConfiguration


class SolarConfigPage(QWidget):
    """
    Página de configuración de la simulación solar.

    Esta página únicamente define y guarda la configuración solar
    utilizada por PVGIS y por la simulación fotovoltaica.
    """

    def __init__(
        self,
        project,
        main_window=None,
    ):

        super().__init__()

        self.project = project
        self.main_window = main_window

        self.setup_ui()
        self.configure_widgets()
        self.connect_signals()
        self.load_solar_basis()

    # ==================================================
    # INTERFAZ
    # ==================================================

    def setup_ui(self):

        outer_layout = QVBoxLayout(self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        content = QWidget()

        layout = QVBoxLayout(content)
        layout.setSpacing(10)

        layout.addWidget(
            self.create_title()
        )

        layout.addWidget(
            self.create_simulation_basis_group()
        )

        layout.addWidget(
            self.create_action_group()
        )

        layout.addStretch()

        self.scroll_area.setWidget(content)

        outer_layout.addWidget(
            self.scroll_area
        )

    # ==================================================
    # CABECERA
    # ==================================================

    def create_title(self):

        frame = QFrame()

        layout = QVBoxLayout(frame)

        title = QLabel(
            "<h2>Configuración solar</h2>"
        )

        description = QLabel(
            "Define la ubicación y los parámetros de la "
            "simulación fotovoltaica que utilizará HELIOS."
        )

        description.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(description)

        return frame

    # ==================================================
    # CONFIGURACIÓN SOLAR
    # ==================================================

    def create_simulation_basis_group(self):

        group = QGroupBox(
            "Configuración solar"
        )

        layout = QFormLayout(group)

        self.latitude_spinbox = QDoubleSpinBox()
        self.longitude_spinbox = QDoubleSpinBox()

        self.tilt_spinbox = QSpinBox()
        self.azimuth_spinbox = QSpinBox()

        self.reference_year_spinbox = QSpinBox()

        self.system_losses_spinbox = QDoubleSpinBox()

        self.pv_technology_combobox = QComboBox()
        self.mounting_place_combobox = QComboBox()

        layout.addRow(
            "Latitud",
            self.latitude_spinbox,
        )

        layout.addRow(
            "Longitud",
            self.longitude_spinbox,
        )

        layout.addRow(
            "Inclinación",
            self.tilt_spinbox,
        )

        layout.addRow(
            "Orientación",
            self.azimuth_spinbox,
        )

        layout.addRow(
            "Año de referencia",
            self.reference_year_spinbox,
        )

        layout.addRow(
            "Pérdidas del sistema",
            self.system_losses_spinbox,
        )

        layout.addRow(
            "Tecnología FV",
            self.pv_technology_combobox,
        )

        layout.addRow(
            "Montaje",
            self.mounting_place_combobox,
        )

        return group

    # ==================================================
    # ACCIÓN
    # ==================================================

    def create_action_group(self):

        group = QGroupBox(
            "Configuración"
        )

        layout = QFormLayout(group)

        self.status_label = QLabel(
            "Configuración pendiente"
        )

        self.save_configuration_button = QPushButton(
            "Guardar configuración solar"
        )

        layout.addRow(
            "Estado",
            self.status_label,
        )

        layout.addRow(
            "",
            self.save_configuration_button,
        )

        return group

    # ==================================================
    # CONFIGURACIÓN DE WIDGETS
    # ==================================================

    def configure_widgets(self):

        self.latitude_spinbox.setRange(
            -90.0,
            90.0,
        )

        self.latitude_spinbox.setDecimals(6)
        self.latitude_spinbox.setSingleStep(0.000001)
        self.latitude_spinbox.setSuffix(" °")

        self.longitude_spinbox.setRange(
            -180.0,
            180.0,
        )

        self.longitude_spinbox.setDecimals(6)
        self.longitude_spinbox.setSingleStep(0.000001)
        self.longitude_spinbox.setSuffix(" °")

        self.tilt_spinbox.setRange(0, 90)
        self.tilt_spinbox.setSuffix(" °")

        self.azimuth_spinbox.setRange(-180, 180)
        self.azimuth_spinbox.setSuffix(" °")

        self.reference_year_spinbox.setRange(
            2000,
            2100,
        )

        self.system_losses_spinbox.setRange(
            0.0,
            100.0,
        )

        self.system_losses_spinbox.setDecimals(1)
        self.system_losses_spinbox.setSingleStep(0.5)
        self.system_losses_spinbox.setSuffix(" %")

        self.pv_technology_combobox.addItem(
            "Silicio cristalino",
            "crystSi",
        )

        self.pv_technology_combobox.addItem(
            "CIS",
            "CIS",
        )

        self.pv_technology_combobox.addItem(
            "CdTe",
            "CdTe",
        )

        self.mounting_place_combobox.addItem(
            "Estructura sobre el suelo",
            "free",
        )

        self.mounting_place_combobox.addItem(
            "Integrado en edificio",
            "building",
        )

        self.latitude_spinbox.setValue(0.0)
        self.longitude_spinbox.setValue(0.0)
        self.tilt_spinbox.setValue(0)
        self.azimuth_spinbox.setValue(0)
        self.reference_year_spinbox.setValue(2023)
        self.system_losses_spinbox.setValue(14.0)

        self.pv_technology_combobox.setCurrentIndex(
            self.pv_technology_combobox.findData(
                "crystSi"
            )
        )

        self.mounting_place_combobox.setCurrentIndex(
            self.mounting_place_combobox.findData(
                "building"
            )
        )

    # ==================================================
    # SEÑALES
    # ==================================================

    def connect_signals(self):

        self.save_configuration_button.clicked.connect(
            self.save_solar_configuration
        )

    # ==================================================
    # CONFIGURACIÓN SOLAR
    # ==================================================

    def get_solar_configuration(
        self,
    ) -> SolarConfiguration:

        return SolarConfiguration(
            latitude=self.latitude_spinbox.value(),
            longitude=self.longitude_spinbox.value(),
            tilt=self.tilt_spinbox.value(),
            azimuth=self.azimuth_spinbox.value(),
            reference_year=self.reference_year_spinbox.value(),
            losses=self.system_losses_spinbox.value(),
            pv_technology=(
                self.pv_technology_combobox.currentData()
            ),
            mounting_place=(
                self.mounting_place_combobox.currentData()
            ),
        )

    def save_solar_configuration(self):

        previous_configuration = (
            self.project.solar_configuration
        )

        configuration = (
            self.get_solar_configuration()
        )

        if previous_configuration is not None:

            self.project.solar.reset()

            if self.main_window is not None:

                self.main_window.set_solar_calculated(
                    False
                )

        self.project.set_solar_configuration(
            configuration
        )

        if self.main_window is not None:

            self.main_window.set_solar_configured(
                True
            )

        self.status_label.setText(
            "Configuración solar guardada."
        )

    def load_solar_basis(self):

        configuration = (
            self.project.solar_configuration
        )

        if configuration is None:

            self.status_label.setText(
                "Configuración solar pendiente"
            )

            return

        self.latitude_spinbox.setValue(
            configuration.latitude
        )

        self.longitude_spinbox.setValue(
            configuration.longitude
        )

        self.tilt_spinbox.setValue(
            configuration.tilt
        )

        self.azimuth_spinbox.setValue(
            configuration.azimuth
        )

        self.reference_year_spinbox.setValue(
            configuration.reference_year
        )

        self.system_losses_spinbox.setValue(
            configuration.losses
        )

        technology_index = (
            self.pv_technology_combobox.findData(
                configuration.pv_technology
            )
        )

        if technology_index >= 0:

            self.pv_technology_combobox.setCurrentIndex(
                technology_index
            )

        mounting_index = (
            self.mounting_place_combobox.findData(
                configuration.mounting_place
            )
        )

        if mounting_index >= 0:

            self.mounting_place_combobox.setCurrentIndex(
                mounting_index
            )

        self.status_label.setText(
            "Configuración solar disponible"
        )

    # ==================================================
    # RESET / ACTUALIZACIÓN
    # ==================================================

    def reset(self):

        self.load_solar_basis()

    def update_data(self):

        self.load_solar_basis()