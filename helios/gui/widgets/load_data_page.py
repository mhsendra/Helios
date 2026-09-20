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

        layout.addStretch()

        self.browse_button.clicked.connect(
            self.browse_file
        )

        self.load_button.clicked.connect(
            self.load_dataset
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
        if self.project.solar_configuration is None:
            self.info_label.setText(
                "Debe guardar la configuración solar antes de cargar datos."
            )
            return

        path = self.path_edit.text()

        if not path:

            self.info_label.setText(
                "Seleccione un archivo."
            )

            return

        try:

            self.project.load_data(path)

            print(
                "DEBUG load_data:",
                id(self.project),
                id(self.project.analyzer),
                self.project.dataset is None,
                None if self.project.dataset is None else self.project.dataset.shape,
            )

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

    def load_solar_configuration(self):

        configuration = self.project.solar_configuration

        if configuration is None:
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

        self.solar_configuration_status.setText(
            "Configuración solar cargada."
        )