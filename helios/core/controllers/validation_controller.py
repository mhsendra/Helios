# helios/core/controllers/validation_controller.py

import calendar
import pandas as pd


class ValidationController:

    def __init__(self, analyzer):
        """
        Controlador de validación y calidad de datos.
        Recibe el ConsumptionAnalyzer para acceder a dataset,
        motores y reporteros.
        """
        self.analyzer = analyzer

    # ==================================================
    # Validación temporal básica
    # ==================================================

    def validate_timeseries(self):
        print("\n=== VALIDACIÓN TEMPORAL ===")
        print(f"Primer registro : {self.analyzer.dataset.index.min()}")
        print(f"Último registro : {self.analyzer.dataset.index.max()}")

    # ==================================================
    # Validación de horas por día
    # ==================================================

    def find_missing_hours(self):
        print("\n=== VALIDACIÓN DE HORAS POR DÍA ===")

        errors = 0

        for fecha, day_df in self.analyzer.dataset.groupby(
            self.analyzer.dataset.index.normalize()
        ):
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

    # ==================================================
    # Duplicados
    # ==================================================

    def find_duplicate_timestamps(self):
        self.analyzer.duplicates = (
            self.analyzer.validation_engine
            .find_duplicate_timestamps(self.analyzer.dataset)
        )

    # ==================================================
    # Calidad de datos
    # ==================================================

    def calculate_gap_summary(self):
        self.analyzer.gap_summary = (
            self.analyzer.validation_engine.calculate_gap_summary(
                self.analyzer.dataset
            )
        )

    def inspect_gap(self, gap_id: int):
        gap = self.analyzer.dataset[
            self.analyzer.dataset["gap_id"] == gap_id
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
        print(gap[["Fecha", "Hora", "AE_kWh"]])

    def inspect_data(self):
        print("\n=== Calidad de los datos ===")
        print(f"Registros totales: {len(self.analyzer.dataset)}")
        print(f"Valores nulos:\n{self.analyzer.dataset.isnull().sum()}")
        print(f"\nDuplicados: {self.analyzer.dataset.duplicated().sum()}")

    # ==================================================
    # Ejecución completa
    # ==================================================

    def calculate(self):
        """
        Ejecuta toda la validación de datos.
        """
        self.validate_timeseries()
        self.find_missing_hours()
        self.find_duplicate_timestamps()
        self.analyzer.calculate_quality()
        self.calculate_gap_summary()

    def reports(self):
        """
        Genera todos los informes de validación.
        """
        self.analyzer.quality_report()
        self.analyzer.gap_report()
        self.analyzer.duplicate_report()

    # ==================================================
    # Métodos auxiliares
    # ==================================================

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