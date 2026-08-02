from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QFormLayout
)


class ValidationPage(QWidget):

    def __init__(self, project):

        super().__init__()

        self.project = project
        self.analyzer = project.analyzer

        layout = QVBoxLayout(self)

        title = QLabel("<h2>Validación del proyecto</h2>")
        layout.addWidget(title)

        form = QFormLayout()

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

        quality = self.analyzer.quality

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
            f'{icons[rating]}  {rating}'
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