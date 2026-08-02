from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QGroupBox,
    QFormLayout,
    QDoubleSpinBox,
    QComboBox,
    QPushButton,
    QSpinBox
)

class SolarPage(QWidget):

    def __init__(self, analyzer):
        super().__init__()

        self.analyzer = analyzer

        self.setup_ui()

        self.configure_widgets()

    def setup_ui(self):

        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()

        layout.addWidget(self.tabs)

        self.configuration_tab = QWidget()
        self.production_tab = QWidget()
        self.balance_tab = QWidget()
        self.statistics_tab = QWidget()

        self.tabs.addTab(self.configuration_tab, "Configuración")
        self.tabs.addTab(self.production_tab, "Producción")
        self.tabs.addTab(self.balance_tab, "Balance")
        self.tabs.addTab(self.statistics_tab, "Estadísticas")

        self.build_configuration_tab()
        self.build_production_tab()
        self.build_balance_tab()
        self.build_statistics_tab()

    def configure_widgets(self):
        self.configure_peak_power()
        self.configure_pv_technology()
        self.configure_system_losses()
        self.configure_tilt()
        self.configure_azimuth()
        self.configure_mounting_place()

        self.configure_latitude()
        self.configure_longitude()

    def configure_peak_power(self):

        self.peak_power_spinbox.setRange(0.10, 100.00)
        self.peak_power_spinbox.setDecimals(2)
        self.peak_power_spinbox.setSingleStep(0.10)
        self.peak_power_spinbox.setSuffix(" kWp")

    def build_configuration_tab(self):

        layout = QVBoxLayout(self.configuration_tab)

        layout.addWidget(self.create_installation_group())
        layout.addWidget(self.create_location_group())

        layout.addStretch()

        layout.addWidget(self.create_calculate_button())

    def build_production_tab(self):
        pass


    def build_balance_tab(self):
        pass


    def build_statistics_tab(self):
        pass

    def create_installation_group(self):

        group = QGroupBox("Instalación")

        layout = QFormLayout(group)

        self.peak_power_spinbox = QDoubleSpinBox()
        self.pv_technology_combobox = QComboBox()
        self.system_losses_spinbox = QDoubleSpinBox()
        self.tilt_spinbox = QSpinBox()
        self.azimuth_spinbox = QSpinBox()
        self.mounting_place_combobox = QComboBox()

        layout.addRow("Potencia instalada", self.peak_power_spinbox)
        layout.addRow("Tecnología FV", self.pv_technology_combobox)
        layout.addRow("Pérdidas del sistema", self.system_losses_spinbox)
        layout.addRow("Inclinación", self.tilt_spinbox)
        layout.addRow("Orientación", self.azimuth_spinbox)
        layout.addRow("Montaje", self.mounting_place_combobox)

        return group

    def create_location_group(self):

        group = QGroupBox("Ubicación")

        layout = QFormLayout(group)

        self.latitude_spinbox = QDoubleSpinBox()
        self.longitude_spinbox = QDoubleSpinBox()

        layout.addRow("Latitud", self.latitude_spinbox)
        layout.addRow("Longitud", self.longitude_spinbox)

        self.load_location_button = QPushButton(
            "Usar ubicación del proyecto"
        )

        layout.addRow("", self.load_location_button)

        return group

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

        self.system_losses_spinbox.setRange(0.0, 100.0)
        self.system_losses_spinbox.setDecimals(1)
        self.system_losses_spinbox.setSingleStep(0.5)
        self.system_losses_spinbox.setSuffix(" %")

    def configure_latitude(self):

        self.latitude_spinbox.setRange(-90.0, 90.0)
        self.latitude_spinbox.setDecimals(6)
        self.latitude_spinbox.setSingleStep(0.000001)

    def configure_longitude(self):

        self.longitude_spinbox.setRange(-180.0, 180.0)
        self.longitude_spinbox.setDecimals(6)
        self.longitude_spinbox.setSingleStep(0.000001)

    def configure_tilt(self):

        self.tilt_spinbox.setRange(0, 90)
        self.tilt_spinbox.setSuffix(" °")

    def configure_azimuth(self):

        self.azimuth_spinbox.setRange(-180, 180)
        self.azimuth_spinbox.setSuffix(" °")

    def configure_mounting_place(self):

        self.mounting_place_combobox.addItem(
            "Estructura sobre el suelo",
            "free"
        )

        self.mounting_place_combobox.addItem(
            "Integrado en edificio",
            "building"
        )

    def create_calculate_button(self):

        self.calculate_button = QPushButton(
            "Calcular producción"
        )

        self.calculate_button.setMinimumHeight(40)

        return self.calculate_button