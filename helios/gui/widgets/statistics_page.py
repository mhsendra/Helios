from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFormLayout
)
class StatisticsPage(QWidget):

    def __init__(self, analyzer):

        super().__init__()

        self.analyzer = analyzer

        layout = QVBoxLayout(self)

        title = QLabel("<h2>Estadísticas generales</h2>")
        layout.addWidget(title)

        form = QFormLayout()

        self.total_label = QLabel("-")
        self.mean_label = QLabel("-")
        self.min_label = QLabel("-")
        self.max_label = QLabel("-")
        self.std_label = QLabel("-")
        self.max_time_label = QLabel("-")
        self.min_time_label = QLabel("-")

        form.addRow("Consumo total", self.total_label)
        form.addRow("Consumo medio", self.mean_label)
        form.addRow("Consumo mínimo", self.min_label)
        form.addRow("Consumo máximo", self.max_label)
        form.addRow("Desviación estándar", self.std_label)
        form.addRow("Fecha/hora máximo", self.max_time_label)
        form.addRow("Fecha/hora mínimo", self.min_time_label)

        layout.addLayout(form)

        layout.addStretch()

    def update_data(self):

        stats = self.analyzer.statistics_engine.statistics

        if stats is None:
            return

        self.total_label.setText(
            f'{stats["total_consumption"]:.2f} kWh'
        )

        self.mean_label.setText(
            f'{stats["mean_hourly"]:.3f} kWh'
        )

        self.min_label.setText(
            f'{stats["min_consumption"]:.3f} kWh'
        )

        self.max_label.setText(
            f'{stats["max_consumption"]:.3f} kWh'
        )

        self.std_label.setText(
            f'{stats["std_consumption"]:.3f} kWh'
        )

        self.max_time_label.setText(
            stats["max_consumption_time"].strftime("%d/%m/%Y %H:%M")
        )

        self.min_time_label.setText(
            stats["min_consumption_time"].strftime("%d/%m/%Y %H:%M")
        )