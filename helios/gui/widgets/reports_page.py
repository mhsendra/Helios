from io import StringIO
from contextlib import redirect_stdout

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QGroupBox,
    QTextEdit,
)


class ReportsPage(QWidget):

    def __init__(self, project):

        super().__init__()

        self.project = project

        layout = QVBoxLayout(self)

        # ==================================================
        # Título
        # ==================================================

        title = QLabel("<h2>Informes</h2>")

        layout.addWidget(title)

        # ==================================================
        # Perfiles
        # ==================================================

        profiles_group = QGroupBox(
            "Perfiles de consumo"
        )

        profiles_layout = QGridLayout()

        self.hourly_button = QPushButton(
            "Perfil horario"
        )

        self.weekday_button = QPushButton(
            "Perfil semanal"
        )

        self.monthly_button = QPushButton(
            "Perfil mensual"
        )

        self.seasonal_button = QPushButton(
            "Perfil estacional"
        )

        profiles_layout.addWidget(
            self.hourly_button,
            0,
            0
        )

        profiles_layout.addWidget(
            self.weekday_button,
            0,
            1
        )

        profiles_layout.addWidget(
            self.monthly_button,
            1,
            0
        )

        profiles_layout.addWidget(
            self.seasonal_button,
            1,
            1
        )

        profiles_group.setLayout(
            profiles_layout
        )

        layout.addWidget(
            profiles_group
        )

        # ==================================================
        # Indicadores
        # ==================================================

        indicators_group = QGroupBox(
            "Indicadores"
        )

        indicators_layout = QGridLayout()

        self.mean_consumption_button = QPushButton(
            "Consumo medio"
        )

        self.extremes_button = QPushButton(
            "Extremos de consumo"
        )

        self.base_load_button = QPushButton(
            "Carga base"
        )

        indicators_layout.addWidget(
            self.mean_consumption_button,
            0,
            0
        )

        indicators_layout.addWidget(
            self.extremes_button,
            0,
            1
        )

        indicators_layout.addWidget(
            self.base_load_button,
            1,
            0
        )

        indicators_group.setLayout(
            indicators_layout
        )

        layout.addWidget(
            indicators_group
        )

        # ==================================================
        # Área del informe
        # ==================================================

        layout.addWidget(
            QLabel("<h3>Informe</h3>")
        )

        self.report_output = QTextEdit()

        self.report_output.setReadOnly(True)

        layout.addWidget(
            self.report_output
        )

        # ==================================================
        # Conexiones
        # ==================================================

        self.hourly_button.clicked.connect(
            self.show_hourly_report
        )

        self.weekday_button.clicked.connect(
            self.show_weekday_report
        )

        self.monthly_button.clicked.connect(
            self.show_monthly_report
        )

        self.seasonal_button.clicked.connect(
            self.show_seasonal_report
        )

        self.mean_consumption_button.clicked.connect(
            self.show_mean_consumption_report
        )

        self.extremes_button.clicked.connect(
            self.show_extremes_report
        )

        self.base_load_button.clicked.connect(
            self.show_base_load_report
        )

    # ==================================================
    # Captura de informes
    # ==================================================

    def _show_report(self, report_function):

        buffer = StringIO()

        with redirect_stdout(buffer):
            report_function()

        report = buffer.getvalue()

        self.report_output.setPlainText(
            report
        )

    # ==================================================
    # Informes de perfiles
    # ==================================================

    def show_hourly_report(self):

        self._show_report(
            self.project.profiles.hourly_profile_report
        )

    def show_weekday_report(self):

        self._show_report(
            self.project.profiles.weekday_profile_report
        )

    def show_monthly_report(self):

        self._show_report(
            self.project.profiles.monthly_profile_report
        )

    def show_seasonal_report(self):

        self._show_report(
            self.project.profiles.seasonal_profile_report
        )

    # ==================================================
    # Informes de indicadores
    # ==================================================

    def show_mean_consumption_report(self):

        self._show_report(
            self.project.indicators.mean_consumption_report
        )

    def show_extremes_report(self):

        self._show_report(
            self.project.indicators.extremes_report
        )

    def show_base_load_report(self):

        self._show_report(
            self.project.indicators.base_load_report
        )