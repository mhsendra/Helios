from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLineEdit,
    QFileDialog,
    QFrame,
)


class LoadDataPage(QWidget):

    def __init__(self, project, main_window):

        super().__init__()

        self.project = project
        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("<h2>Carga de datos de consumo</h2>")
        description = QLabel(
            "Selecciona el archivo Excel que contiene los datos de consumo "
            "para iniciar el análisis."
        )
        description.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(description)

        row = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setPlaceholderText("Ningún archivo seleccionado")
        self.browse_button = QPushButton("Examinar...")
        self.load_button = QPushButton("Cargar")
        row.addWidget(self.path_edit, 1)
        row.addWidget(self.browse_button)
        row.addWidget(self.load_button)
        layout.addLayout(row)

        self.info_label = QLabel("Ningún archivo cargado")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        self.info_cards = {}
        self.info_cards_layout = QGridLayout()
        self.info_cards_layout.setHorizontalSpacing(10)
        self.info_cards_layout.setVerticalSpacing(10)
        layout.addLayout(self.info_cards_layout)
        self._create_info_cards()
        self._clear_info_cards()

        layout.addStretch()

        self.browse_button.clicked.connect(self.browse_file)
        self.load_button.clicked.connect(self.load_dataset)

    def _create_info_cards(self):

        cards = [
            ("Archivo", "filename", 0, 0, 2),
            ("Registros", "records", 0, 2, 1),
            ("Período", "period", 0, 3, 1),
            ("Cobertura", "coverage", 1, 0, 1),
            ("Válidos", "valid", 1, 1, 1),
            ("Ausentes", "missing", 1, 2, 1),
            ("Duplicados", "duplicates", 1, 3, 1),
            ("Calidad", "quality", 2, 0, 4),
        ]

        for title, key, row, column, span in cards:
            card = QFrame()
            card.setFrameShape(QFrame.StyledPanel)
            card.setObjectName("infoCard")
            card.setStyleSheet(
                "#infoCard { border: 1px solid #d9dee7; border-radius: 8px; "
                "background: #ffffff; }"
            )
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 8, 12, 8)
            card_layout.setSpacing(2)

            title_label = QLabel(title.upper())
            title_label.setObjectName("infoCardTitle")
            title_label.setStyleSheet("color: #6b7280; font-size: 9pt; font-weight: 600;")
            value_label = QLabel("-")
            value_label.setObjectName("infoCardValue")
            value_label.setStyleSheet("color: #111827; font-size: 13pt; font-weight: 600;")
            value_label.setWordWrap(True)

            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)
            self.info_cards_layout.addWidget(card, row, column, 1, span)
            self.info_cards[key] = value_label

    @staticmethod
    def _format_count(value):

        try:
            return f"{int(value):,}"
        except (TypeError, ValueError):
            return str(value)

    def _clear_info_cards(self):

        for label in self.info_cards.values():
            label.setText("-")

    def browse_file(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de consumo",
            "",
            "Excel (*.xlsx *.xls)"
        )

        if filename:
            self.path_edit.setText(filename)
            self.info_label.setText(
                "Archivo seleccionado. Pulse Cargar para analizarlo."
            )

    def load_dataset(self):

        path = self.path_edit.text()

        if not path:
            self.info_label.setText("Seleccione un archivo.")
            return

        try:
            self.project.load_data(path)
            self.project.analyze_data()

            # Un nuevo dataset invalida los resultados solares,
            # pero conserva la configuración solar del proyecto.
            self.project.solar.reset()
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
            self._clear_info_cards()

    def update_project_info(self):

        if self.project.dataset is None:
            self.info_label.setText("Ningún archivo cargado.")
            self._clear_info_cards()
            return

        dataset = self.project.dataset
        filename = Path(self.path_edit.text()).name
        first = dataset.index.min().strftime("%d/%m/%Y")
        last = dataset.index.max().strftime("%d/%m/%Y")
        records = len(dataset)
        quality = self.project.quality

        valid = quality.get("valid_hours", "-")
        missing = quality.get("missing_hours", "-")
        duplicates = quality.get("duplicates", "-")

        self.info_cards["filename"].setText(filename)
        self.info_cards["records"].setText(f"{records:,}")
        self.info_cards["period"].setText(f"{first} → {last}")
        self.info_cards["coverage"].setText(f"{quality['coverage']:.2f} %")
        self.info_cards["valid"].setText(
            self._format_count(valid)
        )
        self.info_cards["missing"].setText(
            self._format_count(missing)
        )
        self.info_cards["duplicates"].setText(
            self._format_count(duplicates)
        )
        self.info_cards["quality"].setText(str(quality["rating"]))
        self.info_label.setText(
            "✓ Datos cargados y analizados correctamente."
        )
