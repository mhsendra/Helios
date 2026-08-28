from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QFormLayout,
    QDoubleSpinBox,
    QComboBox,
    QSpinBox,
)

from helios.solar.configuration import SolarConfiguration

from pathlib import Path

class LoadDataPage(QWidget):

    def __init__(self, project, main_window):

        super().__init__()

        self.project = project
        self.main_window = main_window
        
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Archivo de consumo"))

        row = QHBoxLayout()

        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)

        self.browse_button = QPushButton("Examinar...")

        row.addWidget(self.path_edit)
        row.addWidget(self.browse_button)

        layout.addLayout(row)

        self.load_button = QPushButton("Cargar")

        layout.addWidget(self.load_button)

        self.info_label = QLabel("Ningún archivo cargado")

        layout.addWidget(self.info_label)

        layout.addWidget(
            self.create_solar_configuration_group()
        )

        layout.addWidget(
            self.create_location_group()
        )

        self.save_solar_button = QPushButton(
            "Guardar configuración solar"
        )

        layout.addWidget(
            self.save_solar_button
        )

        self.solar_configuration_status = QLabel(
            "Configuración solar no guardada"
        )

        layout.addWidget(
            self.solar_configuration_status
)

        self.configure_solar_widgets()

        layout.addStretch()

        self.browse_button.clicked.connect(
            self.browse_file
        )

        self.load_button.clicked.connect(
            self.load_dataset
        )

        self.save_solar_button.clicked.connect(
            self.save_solar_configuration
        )

    def browse_file(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de consumo",
            "",
            "Excel (*.xlsx *.xls)"
        )

        if filename:

            self.path_edit.setText(filename)

    def load_dataset(self):

        path = self.path_edit.text()

        if not path:

            self.info_label.setText(
                "Seleccione un archivo."
            )

            return

        try:

            self.project.load_data(path)

            self.project.analyze_data()

            # Un nuevo dataset invalida los resultados solares
            self.project.solar.reset()

            # Resetear también la interfaz solar
            self.main_window.solar_page.reset_results()

            self.update_project_info()

            self.main_window.set_project_loaded(True)

            self.main_window.update_project_pages()

        except Exception as e:

            import traceback

            traceback.print_exc()

            self.info_label.setText(
                f"Error: {type(e).__name__}: {e}"
            )

    def update_project_info(self):

        if self.project.dataset is None:

            self.info_label.setText("Ningún archivo cargado.")

            return

        dataset = self.project.dataset

        filename = Path(self.path_edit.text()).name

        first = dataset.index.min().strftime("%d/%m/%Y")

        last = dataset.index.max().strftime("%d/%m/%Y")

        records = len(dataset)

        quality = self.project.quality

        self.info_label.setText(
            f"""
        <b>Archivo</b><br>
        {filename}<br><br>

        <b>Registros</b><br>
        {records:,}<br><br>

        <b>Periodo</b><br>
        {first} → {last}<br><br>

        <b>Cobertura</b><br>
        {quality["coverage"]:.2f}%<br><br>

        <b>Calidad</b><br>
        {quality["rating"]}
        """
        )

    # ==================================================
    # Configuración solar
    # ==================================================

    def create_solar_configuration_group(self):

        group = QGroupBox(
            "Configuración solar"
        )

        layout = QFormLayout(group)

        self.pv_technology_combobox = QComboBox()
        self.system_losses_spinbox = QDoubleSpinBox()
        self.tilt_spinbox = QSpinBox()
        self.azimuth_spinbox = QSpinBox()
        self.mounting_place_combobox = QComboBox()

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

        group = QGroupBox(
            "Ubicación de la instalación"
        )

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


    def configure_solar_widgets(self):

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

        self.system_losses_spinbox.setRange(
            0.0,
            100.0
        )

        self.system_losses_spinbox.setDecimals(1)

        self.system_losses_spinbox.setSingleStep(
            0.5
        )

        self.system_losses_spinbox.setSuffix(
            " %"
        )

        self.tilt_spinbox.setRange(
            0,
            90
        )

        self.tilt_spinbox.setSuffix(
            " °"
        )

        self.azimuth_spinbox.setRange(
            -180,
            180
        )

        self.azimuth_spinbox.setSuffix(
            " °"
        )

        self.mounting_place_combobox.addItem(
            "Estructura sobre el suelo",
            "free"
        )

        self.mounting_place_combobox.addItem(
            "Integrado en edificio",
            "building"
        )

        self.latitude_spinbox.setRange(
            -90.0,
            90.0
        )

        self.latitude_spinbox.setDecimals(6)

        self.latitude_spinbox.setSingleStep(
            0.000001
        )

        self.longitude_spinbox.setRange(
            -180.0,
            180.0
        )

        self.longitude_spinbox.setDecimals(6)

        self.longitude_spinbox.setSingleStep(
            0.000001
        )

    def get_solar_configuration(
        self,
    ) -> SolarConfiguration:

        return SolarConfiguration(

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


    def save_solar_configuration(self):

        configuration = (
            self.get_solar_configuration()
        )

        self.project.set_solar_configuration(
            configuration
        )

        self.solar_configuration_status.setText(
            "Configuración solar guardada."
        )

        self.main_window.solar_config_page.update_data()