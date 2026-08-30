# helios/core/controllers/validation_controller.py

import calendar


class ValidationController:

    def __init__(self, analyzer):
        """
        Controlador de validación y calidad de datos.
        Recibe el ConsumptionAnalyzer para acceder a dataset,
        motores y reporteros.
        """
        self.analyzer = analyzer

    # ==================================================
    # Validación de horas por día
    # ==================================================

    def find_missing_hours(self):

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

    def calculate_quality(self):
        self.analyzer.quality = (
            self.analyzer.quality_engine.calculate(
                self.analyzer.dataset
            )
        )

    def quality_report(self):
        self.analyzer.quality_reporter.quality(
            self.analyzer.quality
        )

    def duplicate_report(self):
        self.analyzer.quality_reporter.duplicates(
            self.analyzer.duplicates
        )

    def gap_report(self):
        self.analyzer.quality_reporter.gap(
            self.analyzer.gap_summary
        )

    # ==================================================
    # Ejecución completa
    # ==================================================

    def calculate(self):
        """
        Ejecuta toda la validación de datos.
        """
        self.find_missing_hours()
        self.find_duplicate_timestamps()
        self.calculate_quality()
        self.calculate_gap_summary()

        self.analyzer.validation_stats = {
            "missing_pct": self.analyzer.quality.get("missing_pct", 0),
            "corrected_pct": self.analyzer.quality.get("corrected_pct", 0),
            "zero_days": self.analyzer.quality.get("zero_days", 0),
            "anomaly_days": self.analyzer.quality.get("anomaly_days", 0)
        }


    def reports(self):
        """
        Genera todos los informes de validación.
        """
        self.quality_report()
        self.gap_report()
        self.duplicate_report()

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