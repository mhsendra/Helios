from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QFormLayout,
    QScrollArea,
)

from helios.utils.platform import is_android

class ValidationPage(QWidget):

    def __init__(self, project):

        super().__init__()

        self.project = project

        if is_android():
            outer_layout = QVBoxLayout(self)
            outer_layout.setContentsMargins(0, 0, 0, 0)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(
                Qt.ScrollBarAlwaysOff
            )

            content = QWidget()
            layout = QVBoxLayout(content)

            scroll.setWidget(content)
            outer_layout.addWidget(scroll)

            self.scroll_area = scroll
        else:
            layout = QVBoxLayout(self)
            self.scroll_area = None

        title = QLabel("<h2>Validación del proyecto</h2>")
        layout.addWidget(title)

        form = QFormLayout()

        if is_android():
            form.setRowWrapPolicy(
                QFormLayout.WrapAllRows
            )

        self.quality_label = QLabel("-")
        self.coverage_label = QLabel("-")
        self.records_label = QLabel("-")
        self.valid_hours_label = QLabel("-")
        self.missing_hours_label = QLabel("-")
        self.duplicates_label = QLabel("-")

        form.addRow("Calidad", self.quality_label)
        form.addRow("Cobertura", self.coverage_label)
        form.addRow("Registros", self.records_label)
        form.addRow("Horas válidas", self.valid_hours_label)
        form.addRow("Horas ausentes", self.missing_hours_label)
        form.addRow("Duplicados", self.duplicates_label)

        layout.addLayout(form)

        layout.addStretch()

    def update_data(self):

        quality = self.project.quality

        if quality is None:
            return
        
        rating = quality["rating"]

        colors = {
            "EXCELENTE": "#2E7D32",   # Verde
            "MUY BUENA": "#FDD835",   # Amarillo
            "BUENA": "#FB8C00",       # Naranja
            "REVISAR": "#D32F2F"      # Rojo
        }

        icons = {
            "EXCELENTE": "🟢",
            "MUY BUENA": "🟡",
            "BUENA": "🟠",
            "REVISAR": "🔴"
        }

        self.quality_label.setText(
            f'{icons[rating]} {rating}'
        )

        self.quality_label.setStyleSheet(
            f"""
            color: {colors.get(rating, "black")};
            font-size: 16px;
            font-weight: bold;
            """
        )

        self.coverage_label.setText(
            f'{quality["coverage"]:.2f} %'
        )

        self.records_label.setText(
            f'{quality["total_hours"]:,}'.replace(",", ".")
        )

        self.valid_hours_label.setText(
            f'{quality["valid_hours"]:,}'.replace(",", ".")
        )

        self.missing_hours_label.setText(
            str(quality["missing_hours"])
        )

        self.duplicates_label.setText(
            str(quality["duplicates"])
        )