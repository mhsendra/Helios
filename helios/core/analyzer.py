"""
HELIOS
Consumption Analyzer
"""

from pathlib import Path
import pandas as pd


class ConsumptionAnalyzer:

    def __init__(self):

        self.dataset: pd.DataFrame | None = None
        self.statistics = None
        self.profiles = None

    def load_excel(self, path: str | Path):

        xls = pd.ExcelFile(path)

        print("Hojas encontradas:", xls.sheet_names)

        self.dataset = pd.read_excel(
        path,
        sheet_name="18_06_2025"
        )

        print(f"Registros cargados: {len(self.dataset)}")

    def analyze_missing_data(self):

        missing = self.dataset[self.dataset["AE_kWh"].isna()]

        print("\n========== DATOS FALTANTES ==========")

        print(f"Total registros sin consumo: {len(missing)}")

        if len(missing) > 0:
            print("\nPrimeros registros:")

            print(missing.head(20))

            print("\nÚltimos registros:")

            print(missing.tail(20))
    def clean_data(self):

        print("\n=== Calidad de los datos ===")

        print(f"Registros totales: {len(self.dataset)}")

        print(f"Valores nulos:\n{self.dataset.isnull().sum()}")

        print(f"\nDuplicados: {self.dataset.duplicated().sum()}")

        print("\nTipos:")

        print(self.dataset.dtypes)

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

    def find_missing_hours(self):

        expected = pd.date_range(
            start=self.dataset.index.min(),
            end=self.dataset.index.max(),
            freq="h"
        )

        missing = expected.difference(self.dataset.index)

        print("\n=== HORAS AUSENTES ===")

        if len(missing) == 0:
            print("No faltan horas.")
        else:
            for dt in missing:
                print(dt)

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

        first = self.dataset.index.min()
        last = self.dataset.index.max()

        expected = len(
            pd.date_range(
                start=first,
                end=last,
                freq="h"
            )
        )

        existing = len(self.dataset)

        missing = expected - existing

        print(f"Primer registro : {first}")
        print(f"Último registro : {last}")
        print(f"Horas esperadas : {expected}")
        print(f"Horas existentes: {existing}")
        print(f"Horas ausentes  : {missing}")

        if missing == 0:
            print("Serie temporal continua: OK")
        else:
            print("ATENCIÓN: existen horas ausentes")

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

    def calculate_statistics(self):
        pass

    def build_profiles(self):
        pass

    def export_results(self):
        pass