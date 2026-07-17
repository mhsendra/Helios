"""
HELIOS
Consumption Analyzer
"""

from pathlib import Path
from helios.core.cleaning import ConsumptionCleaner
from helios.core.statistics import ConsumptionStatistics
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

        # Motores de procesamiento
        self.cleaner = ConsumptionCleaner()
        self.statistics_engine = ConsumptionStatistics()

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

        self.dataset = self.dataset.groupby("Fecha", group_keys=False).apply(
            self._build_day_datetime
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

        fecha = day_df["Fecha"].iloc[0]

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
            self.dataset
        )

    def calculate_daily_consumption(self):

        self.daily_consumption = (
            self.statistics_engine.calculate_daily_consumption(
                self.dataset
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
                self.dataset
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
                self.dataset
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
    def build_profiles(self):
        pass

    def export_results(self):
        pass