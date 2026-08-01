"""
HELIOS
Consumption Analyzer
"""

from pathlib import Path
from helios.core.cleaning import ConsumptionCleaner
from helios.core.statistics import ConsumptionStatistics
from helios.plots.plotter import Plotter
from helios.core.comparisons import ConsumptionComparisons
from helios.core.indicators import IndicatorsEngine
from helios.core.tariffs import TariffEngine
from helios.core.solar import SolarEngine
from helios.reports.consumption_reports import ConsumptionReports
from helios.core.quality import DataQualityEngine
from helios.core.validation import ValidationEngine

import pandas as pd
import calendar


class ConsumptionAnalyzer:

    # ==================================================
    # Inicialización
    # ==================================================

    def __init__(self):

        # Datos
        self.dataset: pd.DataFrame | None = None

        # Motores de procesamiento
        self.cleaner = ConsumptionCleaner()
        self.statistics_engine = ConsumptionStatistics()
        self.plotter = Plotter()
        self.comparisons_engine = ConsumptionComparisons()
        self.indicators_engine = IndicatorsEngine()
        self.tariff_engine = TariffEngine()   
        self.solar_engine = SolarEngine()
        self.reporter = ConsumptionReports()
        self.quality_engine = DataQualityEngine()
        self.validation_engine = ValidationEngine()

        # Relaciones entre motores
        self.indicators_engine.statistics = self.statistics_engine
        self.indicators_engine.comparisons = self.comparisons_engine

        # Resultados de análisis
  
        self.quality = None
        self.gap_summary = None
        
    # ==================================================
    # Carga y preparación de datos
    # ==================================================

    def load_excel(self, path: str | Path):

        self.dataset = pd.read_excel(
            path,
            sheet_name="18_06_2025"
        )

    def clean_data(self):

        self.dataset = self.cleaner.mark_missing_data(self.dataset)
        self.dataset = self.cleaner.classify_gaps(self.dataset)

    def build_datetime(self):

        """
        Construye el índice temporal respetando el formato horario
        de e-distribución.
        """

        self.dataset = (
            self.dataset
                .groupby("Fecha", group_keys=False)
                .apply(
                    self._build_day_datetime,
                    include_groups=False
                )
        )

        self.dataset.set_index("datetime", inplace=True)

        self._update_engines()

    def valid_dataset(self) -> pd.DataFrame:

        """
        Devuelve únicamente los registros válidos
        para realizar cálculos estadísticos.

        No modifica self.dataset.
        """

        return self.dataset[
            self.dataset["data_status"] != "missing"
        ]
    
    # ==================================================
    # Validación y calidad de datos
    # ==================================================

    def validate_timeseries(self):

        print("\n=== VALIDACIÓN TEMPORAL ===")

        print(f"Primer registro : {self.dataset.index.min()}")
        print(f"Último registro : {self.dataset.index.max()}")

    def calculate_quality(self):

        self.quality = (
            self.quality_engine.calculate(
                self.dataset
            )
        )

    def quality_report(self):

        self.reporter.quality(
            self.quality
        )

    def find_missing_hours(self):

        print("\n=== VALIDACIÓN DE HORAS POR DÍA ===")

        errors = 0

        for fecha, day_df in self.dataset.groupby(self.dataset.index.normalize()):

            expected = self._expected_hours_for_day(fecha)

            existing = set(day_df["Hora"])

            missing = sorted(expected - existing)

            extra = sorted(existing - expected)

            if missing or extra:

                errors += 1

                print(f"\n{fecha.date()}")

                if missing:
                    print(f"  Horas ausentes : {missing}")

                if extra:
                    print(f"  Horas inesperadas: {extra}")

        if errors == 0:
            print("Todos los días tienen la secuencia horaria correcta.")

        return {
            "valid": errors == 0,
            "errors": errors
        }

    def find_duplicate_timestamps(self):

        self.duplicates = (
            self.validation_engine
            .find_duplicate_timestamps(
                self.dataset
            )
        )

    def duplicate_report(self):

        self.reporter.duplicates(
            self.duplicates
        )

    def calculate_gap_summary(self):

        self.gap_summary = (
            self.validation_engine.calculate_gap_summary(
                self.dataset
            )
        )

    def gap_report(self):

        self.reporter.gap(
            self.gap_summary
        )

    def inspect_gap(self, gap_id: int):

        gap = self.dataset[
            self.dataset["gap_id"] == gap_id
        ]

        if gap.empty:
            print(f"No existe el bloque de huecos {gap_id}.")
            return

        print("\n")
        print("=" * 45)
        print(f"HELIOS - GAP #{gap_id}")
        print("=" * 45)

        print(f"Inicio.......... {gap.index.min()}")
        print(f"Fin............. {gap.index.max()}")
        print(f"Duración........ {gap['gap_size'].iloc[0]} horas")

        print("\nRegistros:")

        print(
            gap[
                ["Fecha", "Hora", "AE_kWh"]
            ]
        )

    def inspect_data(self):

        print("\n=== Calidad de los datos ===")

        print(
            f"Registros totales: {len(self.dataset)}"
        )

        print(
            f"Valores nulos:\n{self.dataset.isnull().sum()}"
        )

        print(
            f"\nDuplicados: {self.dataset.duplicated().sum()}"
        )

    def calculate_validation(self):

        self.validate_timeseries()

        self.find_missing_hours()

        self.find_duplicate_timestamps()

        self.calculate_quality()

        self.calculate_gap_summary()

    def validation_reports(self):

        self.duplicate_report()

        self.quality_report()

        self.gap_report()

    # ==================================================
    # Estadísticas de consumo
    # ==================================================
    def calculate_statistics(self):

        dataset = self.valid_dataset()

        # Estadísticas generales
        self.statistics_engine.calculate(dataset)

        # Consumos
        self.statistics_engine.calculate_daily_consumption(dataset)
        self.statistics_engine.calculate_monthly_consumption(dataset)
        self.statistics_engine.calculate_yearly_consumption(dataset)

        # Perfiles
        self.statistics_engine.calculate_hourly_profile(dataset)
        self.statistics_engine.calculate_weekday_profile(dataset)
        self.statistics_engine.calculate_monthly_profile(dataset)
        self.statistics_engine.calculate_seasonal_profile()
    
    def calculate_daily_consumption(self):

        self.statistics_engine.calculate_daily_consumption(
                self.valid_dataset()
            )

    def calculate_monthly_consumption(self):

        self.statistics_engine.calculate_monthly_consumption(
            self.valid_dataset()
        )

    def calculate_yearly_consumption(self):

        self.statistics_engine.calculate_yearly_consumption(
            self.valid_dataset()
        )

    def statistics_report(self):

        self.reporter.statistics(
            self.statistics_engine.statistics
        )

    def daily_report(self):

        self.reporter.daily(self.statistics_engine.daily_consumption)


    def monthly_report(self):

        self.reporter.monthly(
            self.statistics_engine.monthly_consumption
        )

    def yearly_report(self):

        self.reporter.yearly(
            self.statistics_engine.yearly_consumption
        )

    def calculate_statistics_pipeline(self):

        self.calculate_statistics()

        self.calculate_daily_consumption()
        self.calculate_monthly_consumption()
        self.calculate_yearly_consumption()

    def statistics_reports(self):

        self.statistics_report()

        self.daily_report()
        self.monthly_report()
        self.yearly_report()
        
    # ==================================================
    # Perfiles de consumo
    # ==================================================

    def calculate_hourly_profile(self):

        self.statistics_engine.calculate_hourly_profile(
            self.valid_dataset()
        )

    def hourly_profile_report(self):

        self.reporter.hourly_profile(
            self.statistics_engine.hourly_profile
        )

    def calculate_weekday_profile(self):

        self.statistics_engine.calculate_weekday_profile(
                self.valid_dataset()
            )

    def weekday_profile_report(self):

        self.reporter.weekday_profile(
            self.statistics_engine.weekday_profile
        )

    def calculate_monthly_profile(self):

        self.statistics_engine.calculate_monthly_profile(
            self.valid_dataset()
        )

    def monthly_profile_report(self):

        self.reporter.monthly_profile(
            self.statistics_engine.monthly_profile
        )

    def calculate_seasonal_profile(self):

        self.statistics_engine.calculate_seasonal_profile()
        
    def seasonal_profile_report(self):

        self.reporter.seasonal_profile(
            self.statistics_engine.seasonal_profile
        )

    def compare_months_by_year(self):

        self.comparisons_engine.compare_months_by_year(
            self.valid_dataset()
        )

    def calculate_profiles(self):

        self.calculate_hourly_profile()

        self.calculate_weekday_profile()

        self.calculate_monthly_profile()

        self.calculate_seasonal_profile()

    def profile_reports(self):

        self.hourly_profile_report()

        self.weekday_profile_report()

        self.monthly_profile_report()

        self.seasonal_profile_report()
        
    # ==================================================
    # Comparativas
    # ==================================================

    def monthly_comparison_report(self):

        self.comparisons_engine.monthly_comparison_report(
            self.comparisons_engine.monthly_comparison
        )

    def calculate_monthly_variation(self):

        self.comparisons_engine.calculate_monthly_variation()

    def monthly_variation_report(self):

        self.comparisons_engine.monthly_variation_report(
            self.comparisons_engine.monthly_variation
        )

    def compare_weeks_by_year(self):

        self.comparisons_engine.compare_weeks_by_year(
                self.valid_dataset()
            )

    def weekly_comparison_report(self):

        self.comparisons_engine.weekly_comparison_report(
            self.comparisons_engine.weekly_comparison
        )

    def calculate_weekly_variation(self):

        self.comparisons_engine.calculate_weekly_variation()

    def weekly_variation_report(self):

        self.comparisons_engine.weekly_variation_report(
            self.comparisons_engine.weekly_variation
        )


    def compare_years(self):

        self.comparisons_engine.compare_years(
            self.valid_dataset()
        )


    def yearly_comparison_report(self):

        self.comparisons_engine.yearly_comparison_report(
            self.comparisons_engine.yearly_comparison
        )

    def calculate_comparisons(self):

        self.compare_months_by_year()
        self.calculate_monthly_variation()

        self.compare_weeks_by_year()
        self.calculate_weekly_variation()

        self.compare_years()

    def comparison_reports(self):

        self.monthly_comparison_report()
        self.monthly_variation_report()

        self.weekly_comparison_report()
        self.weekly_variation_report()

        self.yearly_comparison_report()
    # ==================================================
    # Indicadores energéticos
    # ==================================================

    def calculate_mean_consumption(self):

        self.indicators_engine.calculate_mean_consumption(
            self.valid_dataset()
        )

    def mean_consumption_report(self):

        self.reporter.mean_consumption(
            self.indicators_engine.mean_consumption
        )    

    def calculate_extremes(self):

        self.indicators_engine.calculate_extremes(
            dataset=self.valid_dataset(),
            daily=self.statistics_engine.daily_consumption,
            monthly=self.statistics_engine.monthly_consumption,
            weekly=self.comparisons_engine.weekly_comparison
        )

    def extremes_report(self):

        self.reporter.extremes(
            self.indicators_engine.extremes
        )

    def calculate_base_load(self):

        self.indicators_engine.calculate_base_load(
            self.valid_dataset()
        )

    def base_load_report(self):

        self.reporter.base_load(
            self.indicators_engine.base_load
        )

    def calculate_indicators(self):

        self.calculate_mean_consumption()

        self.calculate_extremes()

        self.calculate_base_load()

    def indicator_reports(self):

        self.mean_consumption_report()

        self.extremes_report()

        self.base_load_report()

    # ==================================================
    # Tarifas
    # ==================================================

    def calculate_tariff_periods(self):

        self.tariff_engine.calculate_period_consumption(
            self.valid_dataset()
        )

        self.tariff_engine.calculate_period_percentage()

    def tariff_periods_report(self):

        self.reporter.tariff_periods(
            self.tariff_engine.period_consumption,
            self.tariff_engine.period_percentage,
            self.tariff_engine.PERIODS
        )

    def calculate_tariffs(self):

        self.calculate_tariff_periods()

    def tariff_reports(self):

        self.tariff_periods_report()

    # ==================================================
    # Solar
    # ==================================================

    def calculate_solar_production(
        self,
        configuration
    ):

        self.solar_engine.calculate_hourly_production(
            configuration
        )


    def calculate_solar_statistics(self):

        self.solar_engine.calculate_statistics()


    def calculate_daily_solar_production(self):

        self.solar_engine.calculate_daily_production()


    def calculate_monthly_solar_production(self):

        self.solar_engine.calculate_monthly_production()


    def calculate_yearly_solar_production(self):

        self.solar_engine.calculate_yearly_production()


    def calculate_energy_balance(self):

        consumption = self.valid_dataset()["AE_kWh"]

        self.solar_engine.calculate_energy_balance(
            consumption
        )

    def solar_statistics_report(self):

        self.solar_engine.production_statistics_report()


    def monthly_solar_production_report(self):

        self.solar_engine.monthly_production_report()


    def energy_balance_report(self):

        self.solar_engine.energy_balance_report()

    def calculate_solar(
        self,
        configuration
    ):

        self.calculate_solar_production(configuration)

        self.calculate_daily_solar_production()

        self.calculate_monthly_solar_production()

        self.calculate_yearly_solar_production()

        self.calculate_energy_balance()

        self.calculate_solar_statistics()

    def solar_reports(self):

        self.solar_statistics_report()

        self.monthly_solar_production_report()

        self.energy_balance_report()

    # ==================================================
    # Gráficas
    # ==================================================

    def show_plots(self):

        self.plotter.show()


    def plot_hourly_profile(self):

        self.plotter.profiles.plot_hourly_profile(
            self.statistics_engine.hourly_profile
        )

    def plot_weekday_profile(self):

        self.plotter.profiles.plot_weekday_profile(
        self.statistics_engine.weekday_profile
        )


    def plot_monthly_profile(self):

        self.plotter.profiles.plot_monthly_profile(
            self.statistics_engine.monthly_profile
        )


    def plot_seasonal_profile(self):

        self.plotter.profiles.plot_seasonal_profile(
            self.statistics_engine.seasonal_profile
        )


    def plot_monthly_comparison(self):

        self.plotter.comparisons.plot_monthly_comparison(
        self.comparisons_engine.monthly_comparison
    )


    def plot_yearly_comparison(self):

        self.plotter.comparisons.plot_yearly_comparison(
        self.comparisons_engine.yearly_comparison
    )


    def plot_weekly_comparison(self):

        self.plotter.comparisons.plot_weekly_comparison(
        self.comparisons_engine.weekly_comparison
    )

    def plot_weekly_variation(self):

        self.plotter.variations.plot_weekly_variation(
        self.comparisons_engine.weekly_variation
    )

    def plot_monthly_variation(self):

        self.plotter.variations.plot_monthly_variation(
        self.comparisons_engine.monthly_variation
    )

    def profile_plots(self):

        self.plot_hourly_profile()

        self.plot_weekday_profile()

        self.plot_monthly_profile()

        self.plot_seasonal_profile()

    def comparison_plots(self):

        self.plot_monthly_comparison()

        self.plot_monthly_variation()

        self.plot_weekly_comparison()

        self.plot_weekly_variation()

        self.plot_yearly_comparison()

        # ==================================================
    # Métodos privados y auxiliares
    # ==================================================

    def _build_day_datetime(self, day_df):

        """
        Construye la columna datetime para un único día.

        Soporta:
            - días de 23 horas (horario verano)
            - días normales (24 horas)
            - días de 25 horas (horario invierno)
        """

        fecha = day_df.name

        horas = day_df["Hora"].tolist()

        datetimes = []

        for hora in horas:

            if hora <= 24:
                dt = fecha + pd.Timedelta(hours=hora - 1)

            else:
                # Hora 25 -> última hora extraordinaria
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

        # Último domingo de marzo
        march = calendar.monthcalendar(year, 3)
        last_sunday_march = max(
            week[calendar.SUNDAY]
            for week in march
        )

        # Último domingo de octubre
        october = calendar.monthcalendar(year, 10)
        last_sunday_october = max(
            week[calendar.SUNDAY]
            for week in october
        )

        # Cambio a horario de verano
        if day.month == 3 and day.day == last_sunday_march:
            return set(range(1, 24))

        # Cambio a horario de invierno
        if day.month == 10 and day.day == last_sunday_october:
            return set(range(1, 26))

        # Día normal
        return set(range(1, 25))

    def _update_engines(self):

        valid = self.valid_dataset()

        self.statistics_engine.dataset = valid
        self.comparisons_engine.dataset = valid
        self.indicators_engine.dataset = valid
        self.tariff_engine.dataset = valid
        self.solar_engine.dataset = valid