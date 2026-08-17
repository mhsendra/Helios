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
        # Comparativas
        # ==================================================

        comparisons_group = QGroupBox(
            "Comparativas"
        )

        comparisons_layout = QGridLayout()

        self.monthly_comparison_button = QPushButton(
            "Comparativa mensual"
        )

        self.monthly_variation_button = QPushButton(
            "Variación mensual"
        )

        self.weekly_comparison_button = QPushButton(
            "Comparativa semanal"
        )

        self.weekly_variation_button = QPushButton(
            "Variación semanal"
        )

        self.yearly_comparison_button = QPushButton(
            "Comparativa anual"
        )

        comparisons_layout.addWidget(
            self.monthly_comparison_button,
            0,
            0
        )

        comparisons_layout.addWidget(
            self.monthly_variation_button,
            0,
            1
        )

        comparisons_layout.addWidget(
            self.weekly_comparison_button,
            1,
            0
        )

        comparisons_layout.addWidget(
            self.weekly_variation_button,
            1,
            1
        )

        comparisons_layout.addWidget(
            self.yearly_comparison_button,
            2,
            0
        )

        comparisons_group.setLayout(
            comparisons_layout
        )

        layout.addWidget(
            comparisons_group
        )

        # ==================================================
        # Estadísticas
        # ==================================================

        statistics_group = QGroupBox(
            "Estadísticas"
        )

        statistics_layout = QGridLayout()

        self.statistics_button = QPushButton(
            "Estadísticas generales"
        )

        self.daily_statistics_button = QPushButton(
            "Estadísticas diarias"
        )

        self.monthly_statistics_button = QPushButton(
            "Estadísticas mensuales"
        )

        self.yearly_statistics_button = QPushButton(
            "Estadísticas anuales"
        )

        statistics_layout.addWidget(
            self.statistics_button,
            0,
            0
        )

        statistics_layout.addWidget(
            self.daily_statistics_button,
            0,
            1
        )

        statistics_layout.addWidget(
            self.monthly_statistics_button,
            1,
            0
        )

        statistics_layout.addWidget(
            self.yearly_statistics_button,
            1,
            1
        )

        statistics_group.setLayout(
            statistics_layout
        )

        layout.addWidget(
            statistics_group
        )

        # ==================================================
        # Tarifas
        # ==================================================

        tariffs_group = QGroupBox(
            "Tarifas eléctricas"
        )

        tariffs_layout = QGridLayout()

        self.tariff_periods_button = QPushButton(
            "Periodos tarifarios"
        )

        tariffs_layout.addWidget(
            self.tariff_periods_button,
            0,
            0
        )

        tariffs_group.setLayout(
            tariffs_layout
        )

        layout.addWidget(
            tariffs_group
        )

        # ==================================================
        # Economía
        # ==================================================

        economics_group = QGroupBox(
            "Economía"
        )

        economics_layout = QGridLayout()

        self.annual_economics_button = QPushButton(
            "Informe económico anual"
        )

        self.economic_scenarios_button = QPushButton(
            "Escenarios económicos"
        )

        economics_layout.addWidget(
            self.annual_economics_button,
            0,
            0
        )

        economics_layout.addWidget(
            self.economic_scenarios_button,
            0,
            1
        )

        economics_group.setLayout(
            economics_layout
        )

        layout.addWidget(
            economics_group
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

        self.monthly_comparison_button.clicked.connect(
            self.show_monthly_comparison_report
        )

        self.monthly_variation_button.clicked.connect(
            self.show_monthly_variation_report
        )

        self.weekly_comparison_button.clicked.connect(
            self.show_weekly_comparison_report
        )

        self.weekly_variation_button.clicked.connect(
            self.show_weekly_variation_report
        )

        self.yearly_comparison_button.clicked.connect(
            self.show_yearly_comparison_report
        )

        self.statistics_button.clicked.connect(
            self.show_statistics_report
        )

        self.daily_statistics_button.clicked.connect(
            self.show_daily_statistics_report
        )

        self.monthly_statistics_button.clicked.connect(
            self.show_monthly_statistics_report
        )

        self.yearly_statistics_button.clicked.connect(
            self.show_yearly_statistics_report
        )

        self.tariff_periods_button.clicked.connect(
            self.show_tariff_periods_report
        )

        self.annual_economics_button.clicked.connect(
            self.show_annual_economics_report
        )

        self.economic_scenarios_button.clicked.connect(
            self.show_economic_scenarios_report
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

    # ==================================================
    # Informes de comparativas
    # ==================================================

    def show_monthly_comparison_report(self):

        self._show_report(
            self.project.comparisons.monthly_comparison_report
        )

    def show_monthly_variation_report(self):

        self._show_report(
            self.project.comparisons.monthly_variation_report
        )

    def show_weekly_comparison_report(self):

        self._show_report(
            self.project.comparisons.weekly_comparison_report
        )

    def show_weekly_variation_report(self):

        self._show_report(
            self.project.comparisons.weekly_variation_report
        )

    def show_yearly_comparison_report(self):

        self._show_report(
            self.project.comparisons.yearly_comparison_report
        )

    # ==================================================
    # Informes de estadísticas
    # ==================================================

    def show_statistics_report(self):

        self._show_report(
            self.project.statistics.statistics_report
        )

    def show_daily_statistics_report(self):

        self._show_report(
            self.project.statistics.daily_report
        )

    def show_monthly_statistics_report(self):

        self._show_report(
            self.project.statistics.monthly_report
        )

    def show_yearly_statistics_report(self):

        self._show_report(
            self.project.statistics.yearly_report
        )

    # ==================================================
    # Informes de tarifas
    # ==================================================

    def show_tariff_periods_report(self):

        self._show_report(
            self.project.tariffs.tariff_periods_report
        )

    # ==================================================
    # Informes de economía
    # ==================================================

    def show_annual_economics_report(self):

        self._show_report(
            self.project.economics.annual_economics_report
        )

    def show_economic_scenarios_report(self):

        self._show_report(
            self.project.economics.economic_scenarios_report
        )