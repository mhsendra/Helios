from helios.reports.printer import ReportPrinter


class IndicatorsReports:

    def mean_consumption(self, mean_consumption):

        ReportPrinter.title(
            "MEAN CONSUMPTION"
        )

        ReportPrinter.blank()

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

            ReportPrinter.energy(
                label,
                mean_consumption[key],
                decimals=3
            )

    def extremes(self, extremes):

        ReportPrinter.title("CONSUMPTION EXTREMES")
        ReportPrinter.blank()

        # ==========================================
        # Horario
        # ==========================================

        date, value = extremes["hourly_max"]

        ReportPrinter.text(
            "Mayor consumo horario",
            self._format_datetime(date)
        )

        ReportPrinter.energy(
            "Consumo",
            value
        )

        ReportPrinter.blank()

        date, value = extremes["hourly_min"]

        ReportPrinter.text(
            "Menor consumo horario",
            self._format_datetime(date)
        )

        ReportPrinter.energy(
            "Consumo",
            value
        )

        ReportPrinter.blank()

        # ==========================================
        # Diario
        # ==========================================

        date, value = extremes["daily_max"]

        ReportPrinter.text(
            "Mayor consumo diario",
            self._format_date(date)
        )

        ReportPrinter.energy(
            "Consumo",
            value
        )

        ReportPrinter.blank()

        date, value = extremes["daily_min"]

        ReportPrinter.text(
            "Menor consumo diario",
            self._format_date(date)
        )

        ReportPrinter.energy(
            "Consumo",
            value
        )

        ReportPrinter.blank()

        # ==========================================
        # Semanal
        # ==========================================

        date, value = extremes["weekly_max"]

        ReportPrinter.text(
            "Mayor consumo semanal",
            self._format_week(date)
        )

        ReportPrinter.energy(
            "Consumo",
            value
        )

        ReportPrinter.blank()

        date, value = extremes["weekly_min"]

        ReportPrinter.text(
            "Menor consumo semanal",
            self._format_week(date)
        )

        ReportPrinter.energy(
            "Consumo",
            value
        )

        ReportPrinter.blank()

        # ==========================================
        # Mensual
        # ==========================================

        date, value = extremes["monthly_max"]

        ReportPrinter.text(
            "Mayor consumo mensual",
            self._format_month(date)
        )

        ReportPrinter.energy(
            "Consumo",
            value
        )

        ReportPrinter.blank()

        date, value = extremes["monthly_min"]

        ReportPrinter.text(
            "Menor consumo mensual",
            self._format_month(date)
        )

        ReportPrinter.energy(
            "Consumo",
            value
        )
        
    def base_load(self, base_load):

        ReportPrinter.title(
            "BASE LOAD"
        )

        ReportPrinter.blank()

        ReportPrinter.text(
            "Carga base",
            f"{base_load:.3f} kWh/h"
        )

    def _print_extreme(
        self,
        extremes,
        title: str,
        key: str,
        formatter
    ):

        index, value = extremes[key]

        print(title)
        print(f"  {formatter(index)}")
        print(f"  {value:.3f} kWh")
        print()

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
    