"""
HELIOS
Consumption Analyzer
Coordinador principal del sistema de análisis energético.
"""

from pathlib import Path
import pandas as pd
import calendar

# Motores principales
from helios.core.cleaning import ConsumptionCleaner
from helios.core.statistics import ConsumptionStatistics
from helios.core.comparisons import ConsumptionComparisons
from helios.core.indicators import IndicatorsEngine
from helios.core.tariffs import TariffEngine
from helios.core.solar import SolarEngine
from helios.core.quality import DataQualityEngine
from helios.core.validation import ValidationEngine
from helios.core.economics import EconomicsEngine

# Controladores
from helios.core.controllers.validation_controller import ValidationController
from helios.core.controllers.profiles_controller import ProfilesController
from helios.core.controllers.comparisons_controller import ComparisonsController
from helios.core.controllers.indicators_controller import IndicatorsController
from helios.core.controllers.tariffs_controller import TariffsController
from helios.core.controllers.solar_controller import SolarController
from helios.core.controllers.economics_controller import EconomicsController

# Reporteros
from helios.reports.statistics import StatisticsReports
from helios.reports.profiles import ProfilesReports
from helios.reports.quality import QualityReports
from helios.reports.indicators import IndicatorsReports
from helios.reports.tariffs import TariffReports

# Gráficas
from helios.plots.plotter import Plotter


class ConsumptionAnalyzer:
    """
    Coordinador principal del sistema HELIOS.
    Encapsula la interacción entre motores, controladores y reporteros.
    """

    # ==================================================
    # Inicialización
    # ==================================================

    def __init__(self, economics_configuration):

        # Dataset principal
        self.dataset: pd.DataFrame | None = None

        # Motores de procesamiento
        self.cleaner = ConsumptionCleaner()
        self.statistics_engine = ConsumptionStatistics()
        self.comparisons_engine = ConsumptionComparisons()
        self.indicators_engine = IndicatorsEngine()
        self.tariff_engine = TariffEngine()
        self.solar_engine = SolarEngine()
        self.quality_engine = DataQualityEngine()
        self.validation_engine = ValidationEngine()
        self.economics_engine = EconomicsEngine()

        # Controladores
        self.validation = ValidationController(self)
        self.profiles = ProfilesController(self)
        self.comparisons = ComparisonsController(self)
        self.indicators = IndicatorsController(self)
        self.tariffs = TariffsController(self)
        self.solar = SolarController(self)
        self.economics = EconomicsController(self, economics_configuration)

        # Reporteros
        self.statistics_reporter = StatisticsReports()
        self.profile_reporter = ProfilesReports()
        self.quality_reporter = QualityReports()
        self.indicator_reporter = IndicatorsReports()
        self.tariff_reporter = TariffReports()

        # Plotter
        self.plotter = Plotter()

        # Relaciones entre motores
        self.indicators_engine.statistics = self.statistics_engine
        self.indicators_engine.comparisons = self.comparisons_engine

        # Resultados de calidad
        self.quality = None
        self.gap_summary = None

    # ==================================================
    # Carga y preparación de datos
    # ==================================================

    def load_excel(self, path: str | Path):
        """Carga el dataset desde Excel."""
        self.dataset = pd.read_excel(path, sheet_name="18_06_2025")

    def clean_data(self):
        """Marca huecos y clasifica gaps."""
        self.dataset = self.cleaner.mark_missing_data(self.dataset)
        self.dataset = self.cleaner.classify_gaps(self.dataset)

    def build_datetime(self):
        """Construye el índice datetime respetando el formato horario."""
        self.dataset = (
            self.dataset
            .groupby("Fecha", group_keys=False)
            .apply(self._build_day_datetime, include_groups=False)
        )
        self.dataset.set_index("datetime", inplace=True)

    def valid_dataset(self) -> pd.DataFrame:
        """Devuelve únicamente los registros válidos para análisis."""
        return self.dataset[self.dataset["data_status"] != "missing"]

    # ==================================================
    # Validación y calidad de datos
    # ==================================================

    def calculate_validation(self):
        """Delegación al controlador de validación."""
        self.validation.calculate()

    def validation_reports(self):
        """Delegación a reportes de validación."""
        self.validation.reports()

    def calculate_quality(self):
        """Calcula métricas de calidad de datos."""
        self.quality = self.quality_engine.calculate(self.dataset)

    def quality_report(self):
        self.quality_reporter.quality(self.quality)

    def duplicate_report(self):
        self.quality_reporter.duplicates(self.duplicates)

    def gap_report(self):
        self.quality_reporter.gap(self.gap_summary)

    # ==================================================
    # Estadísticas de consumo
    # ==================================================

    def calculate_statistics(self):
        """Calcula estadísticas generales y perfiles base."""
        dataset = self.valid_dataset()

        self.statistics_engine.calculate(dataset)
        self.statistics_engine.calculate_daily_consumption(dataset)
        self.statistics_engine.calculate_monthly_consumption(dataset)
        self.statistics_engine.calculate_yearly_consumption(dataset)

        self.statistics_engine.calculate_hourly_profile(dataset)
        self.statistics_engine.calculate_weekday_profile(dataset)
        self.statistics_engine.calculate_monthly_profile(dataset)
        self.statistics_engine.calculate_seasonal_profile()

    def statistics_report(self):
        self.statistics_reporter.statistics(self.statistics_engine.statistics)

    def daily_report(self):
        self.statistics_reporter.daily(self.statistics_engine.daily_consumption)

    def monthly_report(self):
        self.statistics_reporter.monthly(self.statistics_engine.monthly_consumption)

    def yearly_report(self):
        self.statistics_reporter.yearly(self.statistics_engine.yearly_consumption)

    def statistics_reports(self):
        self.statistics_report()
        self.daily_report()
        self.monthly_report()
        self.yearly_report()

    # ==================================================
    # Perfiles de consumo
    # ==================================================

    def calculate_profiles(self):
        """Delegación al controlador de perfiles."""
        self.profiles.calculate()

    def profile_reports(self):
        """Delegación a reportes de perfiles."""
        self.profiles.reports()

    # ==================================================
    # Comparativas
    # ==================================================

    def calculate_comparisons(self):
        """Delegación al controlador de comparativas."""
        self.comparisons.calculate()

    def comparison_reports(self):
        """Delegación a reportes de comparativas."""
        self.comparisons.reports()

    def comparison_plots(self):
        """Delegación a gráficas de comparativas."""
        self.comparisons.plots()

    # ==================================================
    # Indicadores energéticos
    # ==================================================

    def calculate_indicators(self):
        """Delegación al controlador de indicadores."""
        self.indicators.calculate()

    def indicator_reports(self):
        """Delegación a reportes de indicadores."""
        self.indicators.reports()

    # ==================================================
    # Tarifas
    # ==================================================

    def calculate_tariffs(self):

        """Delegación al controlador de tarifas."""

        self.tariffs.calculate()

    def calculate_economics(self):
        """Delegación al controlador económico."""

        self.economics.calculate()

    def tariff_reports(self):
        
        """Delegación a reportes de tarifas."""

        self.tariffs.reports()

    def economics_reports(self):
        """Delegación a reportes económicos."""

        self.economics.reports()

    # ==================================================
    # Solar
    # ==================================================

    def calculate_solar(self, configuration):
        """Delegación al controlador solar."""
        self.solar.calculate(configuration)

    def solar_reports(self):
        """Delegación a reportes solares."""
        self.solar.reports()

    # ==================================================
    # Gráficas
    # ==================================================

    def show_plots(self):
        """Muestra todas las gráficas acumuladas."""
        self.plotter.show()

    def profile_plots(self):
        """Delegación a gráficas de perfiles."""
        self.profiles.plots()

    # ==================================================
    # Métodos privados y auxiliares
    # ==================================================

    def _build_day_datetime(self, day_df):
        """
        Construye la columna datetime para un único día.
        Soporta días de 23, 24 y 25 horas según horario español.
        """
        fecha = day_df.name
        horas = day_df["Hora"].tolist()

        datetimes = []
        for hora in horas:
            if hora <= 24:
                dt = fecha + pd.Timedelta(hours=hora - 1)
            else:
                dt = fecha + pd.Timedelta(hours=23, minutes=30)
            datetimes.append(dt)

        day_df = day_df.copy()
        day_df["datetime"] = datetimes
        return day_df

    def _expected_hours_for_day(self, day):
        """
        Devuelve el conjunto de horas esperadas para una fecha
        según el calendario español (23, 24 o 25 horas).
        """
        year = day.year

        march = calendar.monthcalendar(year, 3)
        last_sunday_march = max(week[calendar.SUNDAY] for week in march)

        october = calendar.monthcalendar(year, 10)
        last_sunday_october = max(week[calendar.SUNDAY] for week in october)

        if day.month == 3 and day.day == last_sunday_march:
            return set(range(1, 24))

        if day.month == 10 and day.day == last_sunday_october:
            return set(range(1, 26))

        return set(range(1, 25))