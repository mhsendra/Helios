from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFormLayout,
    QScrollArea,
)

from helios.utils.platform import is_android

class StatisticsPage(QWidget):

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

        title = QLabel("<h2>Estadísticas generales</h2>")
        layout.addWidget(title)

        form = QFormLayout()

        if is_android():
            form.setRowWrapPolicy(
                QFormLayout.WrapAllRows
            )

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

        stats = self.project.statistics.statistics

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