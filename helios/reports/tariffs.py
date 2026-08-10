from helios.reports.printer import ReportPrinter


class TariffReports:

    def tariff_periods(self, period_consumption, period_percentage, periods):

        ReportPrinter.title(
            "TARIFF PERIODS"
        )

        ReportPrinter.blank()

        widths = [10, 18, 10]

        ReportPrinter.table_header(
            ["Periodo", "Consumo", "%"],
            widths,
            ["left", "right", "right"]
        )

        for period in periods:

            ReportPrinter.table_row(
                [
                    period,
                    f"{period_consumption[period]:.2f} kWh",
                    f"{period_percentage[period]:.2f} %"
                ],
                widths,
                ["left", "right", "right"]
            )
