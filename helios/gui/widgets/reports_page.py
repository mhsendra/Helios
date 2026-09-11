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
    QFileDialog,
    QMessageBox,
)

from helios.reports.solar_report_data_builder import (
    SolarReportDataBuilder,
)

from helios.reports.solar_report_generator import (
    SolarReportGenerator,
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

        # ==================================================
        # Informe solar PDF
        # ==================================================

        solar_report_group = QGroupBox(
            "Informe solar"
        )

        solar_report_layout = QVBoxLayout()

        self.generate_solar_pdf_button = QPushButton(
            "Generar informe solar PDF"
        )

        self.generate_solar_pdf_button.setEnabled(
            False
        )

        solar_report_layout.addWidget(
            self.generate_solar_pdf_button
        )

        solar_report_group.setLayout(
            solar_report_layout
        )

        # ==================================================
        # Distribución de grupos
        # ==================================================

        groups_layout = QGridLayout()

        groups_layout.addWidget(
            profiles_group,
            0,
            0
        )

        groups_layout.addWidget(
            indicators_group,
            0,
            1
        )

        groups_layout.addWidget(
            comparisons_group,
            1,
            0
        )

        groups_layout.addWidget(
            statistics_group,
            1,
            1
        )

        groups_layout.addWidget(
            tariffs_group,
            2,
            0
        )

        groups_layout.addWidget(
            economics_group,
            2,
            1
        )

        groups_layout.addWidget(
            solar_report_group,
            3,
            0,
            1,
            2
        )

        groups_layout.setColumnStretch(0, 1)
        groups_layout.setColumnStretch(1, 1)

        layout.addLayout(
            groups_layout
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
            self.report_output,
            1
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

        self.generate_solar_pdf_button.clicked.connect(
            self.generate_solar_pdf_report
        )

        print(">>> BOTÓN PDF CONECTADO")

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

    # ==================================================
    # Informe solar PDF
    # ==================================================

    def set_solar_report_available(
        self,
        available: bool,
    ):
        print(
            ">>> SOLAR REPORT AVAILABLE:",
            available,
        )

        self.generate_solar_pdf_button.setEnabled(
            available
        )

    def generate_solar_pdf_report(self):

        print(">>> GENERATE SOLAR PDF: ENTRANDO")

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar informe solar",
            "Informe_solar.pdf",
            "PDF (*.pdf)",
        )

        if not output_path:
            return

        try:
            data = SolarReportDataBuilder.from_project(
                self.project
            )

            print(">>> SOLAR REPORT DATA:")
            print("installed_power_kwp =", data.installed_power_kwp)
            print("panel_count =", data.panel_count)
            print("panel_power_wp =", data.panel_power_wp)
            print("yearly_production_kwh =", data.yearly_production_kwh)
            print("specific_production_kwh_kwp =", data.specific_production_kwh_kwp)
            print("productive_hours =", data.productive_hours)
            print("daily_average_kwh =", data.daily_average_kwh)
            print("monthly_average_kwh =", data.monthly_average_kwh)
            print("maximum_power_kw =", data.maximum_power_kw)
            print("capacity_factor_percent =", data.capacity_factor_percent)
            print("yearly_consumption_kwh =", data.yearly_consumption_kwh)
            print("self_consumption_kwh =", data.self_consumption_kwh)
            print("grid_export_kwh =", data.grid_export_kwh)
            print("grid_import_kwh =", data.grid_import_kwh)
            print("yearly_savings_eur =", data.yearly_savings_eur)
            print("payback_years =", data.payback_years)
            print("net_present_value_eur =", data.net_present_value_eur)
            print("internal_rate_of_return_percent =", data.internal_rate_of_return_percent)
            print("latitude =", data.latitude)
            print("longitude =", data.longitude)
            print("tilt =", data.tilt)
            print("azimuth =", data.azimuth)
            print("reference_year =", data.reference_year)
            print("losses =", data.losses)

            generator = SolarReportGenerator()

            generator.generate(
                data,
                output_path,
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error",
                (
                    "No se ha podido generar el informe solar.\n\n"
                    f"{error}"
                ),
            )

            return

        QMessageBox.information(
            self,
            "Informe generado",
            (
                "El informe solar se ha generado "
                "correctamente."
            ),
        )