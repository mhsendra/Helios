from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QFileDialog,
    QMessageBox
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

            self.main_window.update_project_pages()

            self.main_window.set_project_loaded(True)

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