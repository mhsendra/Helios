from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QScrollArea,
)
from helios.utils.platform import is_android

class ProfilesPage(QWidget):

    def create_form_layout(self, group):
        form = QFormLayout(group)

        if is_android():
            form.setRowWrapPolicy(
                QFormLayout.WrapAllRows
            )

        return form

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

        title = QLabel("<h2>Perfiles de consumo</h2>")
        layout.addWidget(title)

        # ==========================================
        # Perfil horario
        # ==========================================

        hourly_group = QGroupBox("Perfil horario")

        hourly_layout = self.create_form_layout(hourly_group)

        self.hour_max_label = QLabel("-")
        self.hour_min_label = QLabel("-")

        hourly_layout.addRow(
            "Hora de mayor consumo",
            self.hour_max_label
        )

        hourly_layout.addRow(
            "Hora de menor consumo",
            self.hour_min_label
        )

        layout.addWidget(hourly_group)

        # ==========================================
        # Perfil semanal
        # ==========================================

        weekday_group = QGroupBox("Perfil semanal")

        weekday_layout = self.create_form_layout(weekday_group)

        self.weekday_max_label = QLabel("-")
        self.weekday_min_label = QLabel("-")

        weekday_layout.addRow(
            "Día de mayor consumo",
            self.weekday_max_label
        )

        weekday_layout.addRow(
            "Día de menor consumo",
            self.weekday_min_label
        )

        layout.addWidget(weekday_group)

        # ==========================================
        # Perfil mensual
        # ==========================================

        monthly_group = QGroupBox("Perfil mensual")

        monthly_layout = self.create_form_layout(monthly_group)

        self.month_max_label = QLabel("-")
        self.month_min_label = QLabel("-")

        monthly_layout.addRow(
            "Mes de mayor consumo",
            self.month_max_label
        )

        monthly_layout.addRow(
            "Mes de menor consumo",
            self.month_min_label
        )

        layout.addWidget(monthly_group)

        # ==========================================
        # Perfil estacional
        # ==========================================

        seasonal_group = QGroupBox("Perfil estacional")

        seasonal_layout = self.create_form_layout(seasonal_group)

        self.season_max_label = QLabel("-")
        self.season_min_label = QLabel("-")

        seasonal_layout.addRow(
            "Estación de mayor consumo",
            self.season_max_label
        )

        seasonal_layout.addRow(
            "Estación de menor consumo",
            self.season_min_label
        )

        layout.addWidget(seasonal_group)

        layout.addStretch()

    def update_data(self):

        profiles = self.project.profiles

        if (
            profiles.hourly_profile is None or
            profiles.weekday_profile is None or
            profiles.monthly_profile is None or
            profiles.seasonal_profile is None
        ):
            return

        # ==========================================
        # Perfil horario
        # ==========================================

        hourly = profiles.hourly_profile

        self.hour_max_label.setText(
            f'{hourly.idxmax():02d}:00'
        )

        self.hour_min_label.setText(
            f'{hourly.idxmin():02d}:00'
        )

        # ==========================================
        # Perfil semanal
        # ==========================================

        weekday = profiles.weekday_profile

        self.weekday_max_label.setText(
            str(weekday.idxmax())
        )

        self.weekday_min_label.setText(
            str(weekday.idxmin())
        )

        # ==========================================
        # Perfil mensual
        # ==========================================

        monthly = profiles.monthly_profile

        self.month_max_label.setText(
            str(monthly.idxmax())
        )

        self.month_min_label.setText(
            str(monthly.idxmin())
        )

        # ==========================================
        # Perfil estacional
        # ==========================================

        seasonal = profiles.seasonal_profile

        self.season_max_label.setText(
            str(seasonal.idxmax())
        )

        self.season_min_label.setText(
            str(seasonal.idxmin())
        )