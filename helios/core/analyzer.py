"""
HELIOS
Consumption Analyzer
"""

from pathlib import Path
from helios.core.cleaning import ConsumptionCleaner
import pandas as pd
import calendar


class ConsumptionAnalyzer:

    def __init__(self):

        self.dataset: pd.DataFrame | None = None
        self.statistics = None
        self.profiles = None
        self.cleaner = ConsumptionCleaner()

    def load_excel(self, path: str | Path):

        xls = pd.ExcelFile(path)

        print("Hojas encontradas:", xls.sheet_names)

        self.dataset = pd.read_excel(
        path,
        sheet_name="18_06_2025"
        )

        print(f"Registros cargados: {len(self.dataset)}")

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

    def build_datetime(self):

        """
        Construye el índice temporal respetando el formato horario
        de e-distribución.
        """

        self.dataset = self.dataset.groupby("Fecha", group_keys=False).apply(
            self._build_day_datetime
        )

        self.dataset.set_index("datetime", inplace=True)
        print(self.dataset.index.is_unique)
        print(self.dataset.index.is_monotonic_increasing)

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

        print(f"Índice ordenado : {'Sí' if self.dataset.index.is_monotonic_increasing else 'No'}")
        print(f"Índice único    : {'Sí' if self.dataset.index.is_unique else 'No'}")

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

        gaps = (
            self.dataset[self.dataset["gap_id"].notna()]
            .groupby("gap_id")["gap_size"]
            .first()
        )

        print(f"Bloques detectados..... {len(gaps)}")
        print(f"Mayor hueco............ {gaps.max()} horas")

        print("\nDistribución:")

        for size, count in gaps.value_counts().sort_index().items():
            print(f"{size:>3} horas........... {count}")

    def clean_data(self):

        self.dataset = self.cleaner.mark_missing_data(self.dataset)
        self.dataset = self.cleaner.classify_gaps(self.dataset)

        missing = (self.dataset["data_status"] == "missing").sum()
        blocks = self.dataset["gap_id"].nunique()
        largest = self.dataset["gap_size"].max()

        print("\n=== LIMPIEZA DE DATOS ===")
        print(f"Registros faltantes..... {missing}")
        print(f"Bloques de huecos....... {blocks}")
        print(f"Mayor hueco............. {largest} horas")
        

    def calculate_statistics(self):
        pass

    def build_profiles(self):
        pass

    def export_results(self):
        pass