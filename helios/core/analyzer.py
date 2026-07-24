"""
HELIOS
Consumption Analyzer
"""

from pathlib import Path
from helios.core.cleaning import ConsumptionCleaner
from helios.core.statistics import ConsumptionStatistics
from helios.core.visualizer import ConsumptionVisualizer
from helios.core.comparisons import ConsumptionComparisons
from helios.core.indicators import IndicatorsEngine
from helios.core.tariffs import TariffEngine
from helios.core.solar import (SolarEngine, SolarConfiguration)
import pandas as pd
import calendar


class ConsumptionAnalyzer:

    def __init__(self):

        self.dataset: pd.DataFrame | None = None

        # Resultados de análisis
        self.statistics = None
        self.daily_consumption = None
        self.monthly_consumption = None
        self.yearly_consumption = None
        self.profiles = None
        self.hourly_profile = None
        self.weekday_profile = None
        self.monthly_profile = None
        self.seasonal_profile = None
        self.monthly_comparison = None
        self.monthly_variation = None
        self.yearly_comparison = None
        self.weekly_comparison = None
        self.weekly_variation = None
        self.mean_consumption = None
        self.extremes = None
        self.base_load = None
        self.period_consumption = None
        self.period_percentage = None
        self.solar_configuration = None
        self.solar_production = None
        

        # Motores de procesamiento
        self.cleaner = ConsumptionCleaner()
        self.statistics_engine = ConsumptionStatistics()
        self.visualizer = ConsumptionVisualizer()
        self.comparisons_engine = ConsumptionComparisons()
        self.indicators_engine = IndicatorsEngine()
        self.tariff_engine = TariffEngine()   
        self.solar_engine = SolarEngine()    

    def load_excel(self, path: str | Path):

        #xls = pd.ExcelFile(path)

        #print("Hojas encontradas:", xls.sheet_names)

        self.dataset = pd.read_excel(
        path,
        sheet_name="18_06_2025"
        )

        #print(f"Registros cargados: {len(self.dataset)}")

    def inspect_gap(self, gap_id: int):

        gap = self.dataset[self.dataset["gap_id"] == gap_id]

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

        print(gap[["Fecha", "Hora", "AE_kWh"]])

    def inspect_data(self):

        print("\n=== Calidad de los datos ===")

        print(f"Registros totales: {len(self.dataset)}")

        print(f"Valores nulos:\n{self.dataset.isnull().sum()}")

        print(f"\nDuplicados: {self.dataset.duplicated().sum()}")

        #print("\nTipos:")

        #print(self.dataset.dtypes)

    def valid_dataset(self) -> pd.DataFrame:

        """
        Devuelve únicamente los registros válidos
        para realizar cálculos estadísticos.

        No modifica self.dataset.
        """

        return self.dataset[
            self.dataset["data_status"] != "missing"
        ]

    def clean_data(self):

        print("\n=== LIMPIEZA DE DATOS ===")

        self.dataset = self.cleaner.mark_missing_data(self.dataset)
        self.dataset = self.cleaner.classify_gaps(self.dataset)

        missing = (self.dataset["data_status"] == "missing").sum()
        blocks = self.dataset["gap_id"].nunique()

        print(f"Registros perdidos..... {missing}")
        print(f"Bloques detectados..... {blocks}")
        
    def build_datetime(self):

        """
        Construye el índice temporal respetando el formato horario
        de e-distribución.
        """

        self.dataset = (
            self.dataset
            .groupby("Fecha", group_keys=False)
            .apply(self._build_day_datetime)
        )

        self.dataset.set_index("datetime", inplace=True)

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
        last_sunday_march = max(week[calendar.SUNDAY] for week in march)

        # Último domingo de octubre
        october = calendar.monthcalendar(year, 10)
        last_sunday_october = max(week[calendar.SUNDAY] for week in october)

        # Cambio a horario de verano
        if day.month == 3 and day.day == last_sunday_march:
            return set(range(1, 24))

        # Cambio a horario de invierno
        if day.month == 10 and day.day == last_sunday_october:
            return set(range(1, 26))

        # Día normal
        return set(range(1, 25))

    def find_missing_hours(self):

        print("\n=== VALIDACIÓN DE HORAS POR DÍA ===")

        errors = 0

        for fecha, day_df in self.dataset.groupby("Fecha"):

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

        duplicates = self.dataset.index[self.dataset.index.duplicated()]

        print("\n=== FECHAS DUPLICADAS ===")

        if len(duplicates) == 0:
            print("No existen.")
        else:

            for dt in duplicates:
                print(dt)

                print(self.dataset.loc[dt])

    def inspect_dst_days(self):

        dates = [
            "2024-03-31",
            "2024-10-27",
            "2025-03-30",
            "2025-10-26",
            "2026-03-29"
        ]

        for d in dates:

            print(f"\n===== {d} =====")

            print(
                self.dataset[
                    self.dataset["Fecha"] == d
                ][["Fecha", "Hora", "AE_kWh"]]
            )

    def validate_timeseries(self):

        print("\n=== VALIDACIÓN TEMPORAL ===")

        print(f"Primer registro : {self.dataset.index.min()}")
        print(f"Último registro : {self.dataset.index.max()}")

    def quality_report(self):

        total = len(self.dataset)
        nulls = self.dataset["AE_kWh"].isna().sum()
        duplicates = self.dataset.index.duplicated().sum()

        coverage = (1 - nulls / total) * 100

        print("\n")
        print("=" * 45)
        print("HELIOS - DATA QUALITY REPORT")
        print("=" * 45)

        print(f"Registros.............. {total}")
        print(f"Valores nulos......... {nulls}")
        print(f"Duplicados............ {duplicates}")
        print(f"Cobertura............. {coverage:.2f} %")

        if coverage >= 99:
            quality = "EXCELENTE"
        elif coverage >= 97:
            quality = "MUY BUENA"
        elif coverage >= 95:
            quality = "BUENA"
        else:
            quality = "REVISAR"

        print(f"Calidad............... {quality}")

    def gap_report(self):

        print("\n")
        print("=" * 45)
        print("HELIOS - GAP REPORT")
        print("=" * 45)

        gaps = self.dataset[self.dataset["gap_id"].notna()]

        summary = (
            gaps
            .groupby("gap_id")
            .agg(
                start=("gap_size", lambda s: s.index.min()),
                end=("gap_size", lambda s: s.index.max()),
                hours=("gap_size", "first"),
                gap_type=("gap_type", "first")
            )
        )

        if gaps.empty:
            print("No se han detectado huecos.")
            return

        total_missing = (self.dataset["data_status"] == "missing").sum()
        total_blocks = len(summary)

        print(f"Registros perdidos..... {total_missing}")
        print(f"Bloques detectados..... {total_blocks}")
        print(f"Mayor hueco............ {gaps['gap_size'].max()} horas")
        small = (summary["gap_type"] == "small").sum()
        large = (summary["gap_type"] == "large").sum()
        print(f"Huecos pequeños........ {small}")
        print(f"Huecos grandes......... {large}")

        print("\nDistribución de huecos")

        distribution = (
            summary["hours"]
            .value_counts()
            .sort_index()
        )

        for size, count in distribution.items():
            print(f"{size:>2} horas............. {count}")

        print("\nDetalle de bloques")
        print("-" * 78)
        print(f"{'ID':>3} {'Inicio':<20} {'Fin':<20} {'Horas':>7} {'Tipo':>8}")
        print("-" * 78)

        for gap_id, gap in (
            self.dataset[self.dataset["gap_id"].notna()]
            .groupby("gap_id")
        ):

            start = gap.index.min()
            end = gap.index.max()

            print(
                f"{int(gap_id):>3} "
                f"{start.strftime('%Y-%m-%d %H:%M'):<20} "
                f"{end.strftime('%Y-%m-%d %H:%M'):<20} "
                f"{gap['gap_size'].iloc[0]:>7} "
                f"{gap['gap_type'].iloc[0]:>8}"
            )

    def statistics_report(self):

        if self.statistics is None:
            print("No hay estadísticas calculadas.")
            return

        print()
        print("=" * 45)
        print("HELIOS - STATISTICS REPORT")
        print("=" * 45)

        print(
            f"Consumo total.......... "
            f"{self.statistics['total_consumption']:.2f} kWh"
        )

        print(
            f"Consumo medio horario.. "
            f"{self.statistics['mean_hourly']:.3f} kWh"
        )

        print(
            f"Consumo máximo......... "
            f"{self.statistics['max_consumption']:.3f} kWh"
        )

        print(
            f"Fecha del máximo....... "
            f"{self.statistics['max_consumption_time']:%d/%m/%Y %H:%M}"
        )

        print(
            f"Consumo mínimo......... "
            f"{self.statistics['min_consumption']:.3f} kWh"
        )

        print(
            f"Fecha del mínimo....... "
            f"{self.statistics['min_consumption_time']:%d/%m/%Y %H:%M}"
        )

        print(
            f"Desv. estándar......... "
            f"{self.statistics['std_consumption']:.3f} kWh"
        )

    def gap_report(self):

        gaps = self.dataset[
            self.dataset["data_status"] == "missing"
        ]

        if len(gaps) == 0:
            print("\n=== GAP REPORT ===")
            print("No existen huecos.")
            return


        summary = (
            gaps
            .groupby("gap_id")
            .agg(
                start=("gap_size", lambda s: s.index.min()),
                end=("gap_size", lambda s: s.index.max()),
                hours=("gap_size", "first"),
                gap_type=("gap_type", "first")
            )
        )


        largest = summary["hours"].max()


        print()
        print("=" * 45)
        print("HELIOS - GAP REPORT")
        print("=" * 45)

        print(f"Registros faltantes..... {len(gaps)}")
        print(f"Bloques detectados...... {len(summary)}")
        print(f"Mayor hueco............. {largest} horas")


        print()
        print("Detalle de bloques")
        print("-" * 75)

        print(
            f"{'ID':>3} "
            f"{'Inicio':<20} "
            f"{'Fin':<20} "
            f"{'Horas':>8} "
            f"{'Tipo':>10}"
        )

        print("-" * 75)


        for gap_id, row in summary.iterrows():

            print(
                f"{int(gap_id):>3} "
                f"{row['start'].strftime('%Y-%m-%d %H:%M'):<20} "
                f"{row['end'].strftime('%Y-%m-%d %H:%M'):<20} "
                f"{row['hours']:>8} "
                f"{row['gap_type']:>10}"
            )

    def calculate_statistics(self):

        self.statistics = self.statistics_engine.calculate(
            self.valid_dataset()
        )

    def calculate_daily_consumption(self):

        self.daily_consumption = (
            self.statistics_engine.calculate_daily_consumption(
                self.valid_dataset()
            )
        )

    def daily_report(self):

        if self.daily_consumption is None:
            print("No hay consumos diarios calculados.")
            return

        print()
        print("=" * 45)
        print("HELIOS - DAILY CONSUMPTION REPORT")
        print("=" * 45)

        print(f"Días analizados......... {len(self.daily_consumption)}")
        print(f"Consumo total........... {self.daily_consumption.sum():.2f} kWh")
        print(f"Consumo diario medio.... {self.daily_consumption.mean():.2f} kWh")

        print(f"Consumo máximo diario... {self.daily_consumption.max():.2f} kWh")
        print(f"Fecha del máximo........ {self.daily_consumption.idxmax():%d/%m/%Y}")

        print(f"Consumo mínimo diario... {self.daily_consumption.min():.2f} kWh")
        print(f"Fecha del mínimo........ {self.daily_consumption.idxmin():%d/%m/%Y}")

    def calculate_monthly_consumption(self):

        self.monthly_consumption = (
            self.statistics_engine.calculate_monthly_consumption(
                self.valid_dataset()
            )
        )

    def monthly_report(self):

        if self.monthly_consumption is None:
            print("No hay consumos mensuales calculados.")
            return

        print()
        print("=" * 45)
        print("HELIOS - MONTHLY CONSUMPTION REPORT")
        print("=" * 45)

        print(f"Meses analizados........ {len(self.monthly_consumption)}")
        print(f"Consumo total........... {self.monthly_consumption.sum():.2f} kWh")
        print(f"Consumo mensual medio... {self.monthly_consumption.mean():.2f} kWh")

        print()

        print(f"Consumo máximo mensual.. {self.monthly_consumption.max():.2f} kWh")
        print(
            f"Fecha del máximo........ "
            f"{self.monthly_consumption.idxmax():%m/%Y}"
        )

        print()

        print(f"Consumo mínimo mensual.. {self.monthly_consumption.min():.2f} kWh")
        print(
            f"Fecha del mínimo........ "
            f"{self.monthly_consumption.idxmin():%m/%Y}"
        )

    def calculate_yearly_consumption(self):

        self.yearly_consumption = (
            self.statistics_engine.calculate_yearly_consumption(
                self.valid_dataset()
            )
        )
    
    def yearly_report(self):

        if self.yearly_consumption is None:
            print("No hay consumos anuales calculados.")
            return

        print()
        print("=" * 45)
        print("HELIOS - YEARLY CONSUMPTION REPORT")
        print("=" * 45)

        print(f"Años analizados......... {len(self.yearly_consumption)}")
        print(f"Consumo total........... {self.yearly_consumption.sum():.2f} kWh")
        print(f"Consumo anual medio..... {self.yearly_consumption.mean():.2f} kWh")

        print()

        print(f"Consumo máximo anual.... {self.yearly_consumption.max():.2f} kWh")
        print(
            f"Año del máximo.......... "
            f"{self.yearly_consumption.idxmax():%Y}"
        )

        print()

        print(f"Consumo mínimo anual.... {self.yearly_consumption.min():.2f} kWh")
        print(
            f"Año del mínimo.......... "
            f"{self.yearly_consumption.idxmin():%Y}"
        )

    def calculate_hourly_profile(self):

        self.hourly_profile = (
            self.statistics_engine.calculate_hourly_profile(
                self.valid_dataset()
            )
        )

    def hourly_profile_report(self):

        if self.hourly_profile is None:
            print("No hay perfil horario calculado.")
            return

        print()
        print("=" * 45)
        print("HELIOS - HOURLY PROFILE REPORT")
        print("=" * 45)

        print(f"Horas analizadas........ {len(self.hourly_profile)}")
        print(f"Consumo medio........... {self.hourly_profile.mean():.3f} kWh")

        print()

        print(f"Hora de mayor consumo... {self.hourly_profile.idxmax():02d}:00")
        print(f"Consumo máximo.......... {self.hourly_profile.max():.3f} kWh")

        print()

        print(f"Hora de menor consumo... {self.hourly_profile.idxmin():02d}:00")
        print(f"Consumo mínimo.......... {self.hourly_profile.min():.3f} kWh")

        print()
        print("Top 5 horas de consumo")
        print("-" * 30)

        print(f"{'Hora':<8}{'Consumo':>12}")
        print("-" * 30) 

        top5 = self.hourly_profile.sort_values(ascending=False).head(5)

        for hour, value in top5.items():
            print(f"{hour:02d}:00    {value:>12.3f} kWh")

    def calculate_weekday_profile(self):

        self.weekday_profile = (
            self.statistics_engine.calculate_weekday_profile(
                self.valid_dataset()
            )
        )

    def weekday_profile_report(self):

        if self.weekday_profile is None:
            print("No hay perfil semanal calculado.")
            return
        laborables = self.weekday_profile.iloc[:5].mean()
        fin_semana = self.weekday_profile.iloc[5:].mean()

        incremento = (
            (fin_semana - laborables)
            / laborables
            * 100
        )

        print()
        print("=" * 45)
        print("HELIOS - WEEKDAY PROFILE REPORT")
        print("=" * 45)

        print(f"Consumo medio........... {self.weekday_profile.mean():.3f} kWh")

        print()

        print(f"Media laborables........ {laborables:.3f} kWh")
        print(f"Media fin de semana..... {fin_semana:.3f} kWh")
        print(f"Incremento.............. {incremento:+.1f} %")
        

        print()

        print(f"Día de mayor consumo.... {self.weekday_profile.idxmax()}")
        print(f"Consumo máximo.......... {self.weekday_profile.max():.3f} kWh")

        print()

        print(f"Día de menor consumo.... {self.weekday_profile.idxmin()}")
        print(f"Consumo mínimo.......... {self.weekday_profile.min():.3f} kWh")

        print()
        print("Consumo medio por día")
        print("-" * 30)
        print(f"{'Día':<12}{'Consumo':>10}")
        print("-" * 30)

        for day, value in self.weekday_profile.items():
            print(f"{day:<12}{value:>10.3f} kWh")

    def calculate_monthly_profile(self):

        self.monthly_profile = (
            self.statistics_engine.calculate_monthly_profile(
                self.valid_dataset()
            )
        )
    
    def monthly_profile_report(self):

        if self.monthly_profile is None:
            print("No hay perfil mensual calculado.")
            return

        incremento = (
            (self.monthly_profile.max() - self.monthly_profile.min())
            / self.monthly_profile.min()
            * 100
        )

        print()
        print("=" * 45)
        print("HELIOS - MONTHLY PROFILE REPORT")
        print("=" * 45)

        print()

        print(f"Mes de mayor consumo.... {self.monthly_profile.idxmax()}")
        print(f"Consumo máximo.......... {self.monthly_profile.max():.3f} kWh")

        print()

        print(f"Mes de menor consumo.... {self.monthly_profile.idxmin()}")
        print(f"Consumo mínimo.......... {self.monthly_profile.min():.3f} kWh")

        print()

        print(f"Variación estacional... {incremento:+.1f} %")

        print()
        print("Consumo medio por mes")
        print()
        print("-" * 30)
        print(f"{'Mes':<15}{'Consumo':>10}")
        print("-" * 30)

        for month, value in self.monthly_profile.items():
            print(f"{month:<15}{value:>10.3f} kWh")

    def calculate_seasonal_profile(self):

        self.seasonal_profile = (
            self.statistics_engine.calculate_seasonal_profile(
                self.monthly_profile
            )
        )

    def seasonal_profile_report(self):

        if self.seasonal_profile is None:
            print("No hay perfil estacional calculado.")
            return

        incremento = (
            (self.seasonal_profile.max() - self.seasonal_profile.min())
            / self.seasonal_profile.min()
            * 100
        )

        print()
        print("=" * 45)
        print("HELIOS - SEASONAL PROFILE REPORT")
        print("=" * 45)

        print(f"Estación de mayor consumo... {self.seasonal_profile.idxmax()}")
        print(f"Consumo máximo.............. {self.seasonal_profile.max():.3f} kWh")

        print()

        print(f"Estación de menor consumo... {self.seasonal_profile.idxmin()}")
        print(f"Consumo mínimo.............. {self.seasonal_profile.min():.3f} kWh")

        print()

        print(f"Variación estacional........ {incremento:+.1f} %")

        print()
        print("Consumo medio por estación")
        print()
        print("-" * 35)
        print(f"{'Estación':<15}{'Consumo':>10}")
        print("-" * 35)

        for season, value in self.seasonal_profile.items():
            print(f"{season:<15}{value:>10.3f} kWh")

    def show_plots(self):

        self.visualizer.show()

    def plot_hourly_profile(self):

        self.visualizer.plot_series(
            self.hourly_profile,
            title="Perfil horario de consumo",
            xlabel="Hora",
            ylabel="Consumo medio (kWh)"
        )

    def plot_weekday_profile(self):

        self.visualizer.plot_weekday_profile(
            self.weekday_profile
        )

    def plot_monthly_profile(self):

        self.visualizer.plot_monthly_profile(
            self.monthly_profile
        )


    def plot_seasonal_profile(self):

        self.visualizer.plot_seasonal_profile(
            self.seasonal_profile
        )
    def compare_months_by_year(self):

        self.monthly_comparison = (
            self.comparisons_engine.compare_months_by_year(
                self.dataset
            )
        )
    def monthly_comparison_report(self):

        self.comparisons_engine.monthly_comparison_report(
            self.monthly_comparison
        )
    
    def calculate_monthly_variation(self):

        self.monthly_variation = (
            self.comparisons_engine.calculate_variation(
                self.monthly_comparison
            )
        )

    def monthly_variation_report(self):

        self.comparisons_engine.monthly_variation_report(
            self.monthly_variation
        )

    def plot_monthly_comparison(self):

        self.visualizer.plot_comparison_lines(
            dataframe=self.monthly_comparison,
            title="Comparativa mensual",
            xlabel="Mes",
            ylabel="Consumo (kWh)"
        )


    def plot_monthly_variation(self):

        self.visualizer.plot_monthly_variation(
            self.monthly_variation
        )
    
    def compare_years(self):

        self.yearly_comparison = (
            self.comparisons_engine.compare_years(
                self.valid_dataset()
            )
        )

    def yearly_comparison_report(self):

        self.comparisons_engine.yearly_comparison_report(
            self.yearly_comparison
        )

    def plot_yearly_comparison(self):

        self.visualizer.plot_yearly_comparison(
            self.yearly_comparison
        )

    def compare_weeks_by_year(self):

        self.weekly_comparison = (
            self.comparisons_engine.compare_weeks_by_year(
                self.valid_dataset()
            )
        )
    
    def weekly_comparison_report(self):

        self.comparisons_engine.weekly_comparison_report(
            self.weekly_comparison
        )

    def calculate_weekly_variation(self):

        self.weekly_variation = (
            self.comparisons_engine.calculate_variation(
                self.weekly_comparison
            )
        )
    
    def weekly_variation_report(self):

        self.comparisons_engine.weekly_variation_report(
            self.weekly_variation
        )

    def plot_weekly_variation(self):

        self.visualizer.plot_variation_bars(
            dataframe=self.weekly_variation,
            title="Variación semanal",
            xlabel="Semana",
            ylabel="Variación (%)"
        )

    def plot_monthly_variation(self):

        self.visualizer.plot_variation_bars(
            dataframe=self.monthly_variation,
            title="Variación mensual",
            xlabel="Mes",
            ylabel="Variación (%)"
        )

    def plot_weekly_comparison(self):

        self.visualizer.plot_comparison_lines(
            dataframe=self.weekly_comparison,
            title="Comparativa semanal",
            xlabel="Semana",
            ylabel="Consumo (kWh)"
        )

    def calculate_mean_consumption(self):

        self.mean_consumption = (
            self.indicators_engine.calculate_mean_consumption(
                self.valid_dataset()
            )
        )

    def mean_consumption_report(self):

        print()
        print("=" * 45)
        print("HELIOS - MEAN CONSUMPTION")
        print("=" * 45)
        print()

        labels = {

            "hourly": "Consumo medio horario",

            "daily": "Consumo medio diario",

            "weekly": "Consumo medio semanal",

            "monthly": "Consumo medio mensual",

            "yearly": "Consumo medio anual",

            "workday": "Consumo medio laborable",

            "weekend": "Consumo medio fin de semana"
        }

        for key, label in labels.items():

            print(
                f"{label:.<32}"
                f"{self.mean_consumption[key]:>10.3f} kWh"
            )
    def calculate_extremes(self):

        self.extremes = (
            self.indicators_engine.calculate_extremes(
                dataset=self.valid_dataset(),
                daily=self.daily_consumption,
                monthly=self.monthly_consumption,
                weekly=self.weekly_comparison
            )
        )

    def _print_extreme(
        self,
        title: str,
        key: str,
        formatter
    ):

        index, value = self.extremes[key]

        print(title)
        print(f"  {formatter(index)}")
        print(f"  {value:.3f} kWh")
        print()
    
    def extremes_report(self):

        print()
        print("=" * 45)
        print("HELIOS - CONSUMPTION EXTREMES")
        print("=" * 45)
        print()

        self._print_extreme(
            "Mayor consumo horario",
            "hourly_max",
            self._format_datetime
        )

        self._print_extreme(
            "Menor consumo horario",
            "hourly_min",
            self._format_datetime
        )

        self._print_extreme(
            "Mayor consumo diario",
            "daily_max",
            self._format_date
        )

        self._print_extreme(
            "Menor consumo diario",
            "daily_min",
            self._format_date
        )

        self._print_extreme(
            "Mayor consumo semanal",
            "weekly_max",
            self._format_week
        )

        self._print_extreme(
            "Menor consumo semanal",
            "weekly_min",
            self._format_week
        )

        self._print_extreme(
            "Mayor consumo mensual",
            "monthly_max",
            self._format_month
        )

        self._print_extreme(
            "Menor consumo mensual",
            "monthly_min",
            self._format_month
        )

    def _format_datetime(
        self,
        timestamp
    ) -> str:

        return timestamp.strftime(
            "%d/%m/%Y %H:%M"
        )
    
    def _format_date(
        self,
        timestamp
    ) -> str:

        return timestamp.strftime(
            "%d/%m/%Y"
        )
    
    def _format_week(
        self,
        week
    ) -> str:

        year, week_number = week

        return f"{week_number} ({year})"
    
    def _format_month(
        self,
        timestamp
    ) -> str:

        months = [
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre"
        ]

        month = months[
            timestamp.month - 1
        ]

        return f"{month} {timestamp.year}"
    
    def calculate_base_load(self):

        self.base_load = (
            self.indicators_engine.calculate_base_load(
                self.valid_dataset()
            )
        )

    def base_load_report(self):

        print()
        print("=" * 45)
        print("HELIOS - BASE LOAD")
        print("=" * 45)
        print()

        print(
            f"Carga base{'':.<24}"
            f"{self.base_load:.3f} kWh/h"
        )
    
    def calculate_tariff_periods(self):

        self.period_consumption = (
            self.tariff_engine.calculate_period_consumption(
                self.valid_dataset()
            )
        )

        self.period_percentage = (
            self.tariff_engine.calculate_period_percentage(
                self.period_consumption
            )
        )
    
    def tariff_periods_report(self):

        print()

        print("=" * 45)
        print("HELIOS - TARIFF PERIODS")
        print("=" * 45)
        print()

        print(
            f"{'Periodo':<10}"
            f"{'Consumo':>18}"
            f"{'%':>10}"
        )

        print("-" * 40)

        for period in self.tariff_engine.PERIODS:

            consumption = self.period_consumption[period]

            percentage = self.period_percentage[period]

            print(
                f"{period:<10}"
                f"{consumption:>12.2f} kWh"
                f"{percentage:>9.2f}%"
            )
    
    def calculate_solar_production(
        self,
        configuration
    ):

        self.solar_production = (
            self.solar_engine.calculate_hourly_production(
                configuration
            )
        )

    def solar_production_report(self):

        print()

        print("=== PRODUCCIÓN SOLAR ===")

        print()

        print(self.solar_production.head())

    def calculate_solar_statistics(self):

        self.solar_engine.calculate_statistics()
    
    def calculate_monthly_solar_production(self):

        self.solar_engine.calculate_monthly_production()

    def monthly_solar_production_report(self):

        self.solar_engine.monthly_production_report()

    def solar_statistics_report(self):

        self.solar_engine.statistics_report()

    def calculate_energy_balance(self):

        consumption = self.valid_dataset()["AE_kWh"]

        self.solar_engine.calculate_energy_balance(
            consumption
        )

    def energy_balance_report(self):

        self.solar_engine.energy_balance_report()

    def calculate_daily_solar_production(self):

        self.solar_engine.calculate_daily_production()

    def calculate_yearly_solar_production(self):

        self.solar_engine.calculate_yearly_production()

    def calculate_energy_statistics(self):

        self.solar_engine.calculate_energy_statistics()

    def energy_statistics_report(self):

        self.solar_engine.energy_statistics_report()