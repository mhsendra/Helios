from unittest.mock import call, patch

from helios.reports.tariffs import TariffReports


class TestTariffReports:

    def setup_method(self):

        self.report = TariffReports()

    @patch(
        "helios.reports.tariffs.ReportPrinter"
    )
    def test_tariff_periods(
        self,
        printer
    ):

        period_consumption = {
            "P1": 100.0,
            "P2": 200.0,
            "P3": 300.0,
        }

        period_percentage = {
            "P1": 10.0,
            "P2": 20.0,
            "P3": 30.0,
        }

        periods = [
            "P1",
            "P2",
            "P3",
        ]

        result = self.report.tariff_periods(
            period_consumption,
            period_percentage,
            periods
        )

        assert result is None

        printer.title.assert_called_once_with(
            "TARIFF PERIODS"
        )

        printer.blank.assert_called_once_with()

        printer.table_header.assert_called_once_with(
            ["Periodo", "Consumo", "%"],
            [10, 18, 10],
            ["left", "right", "right"]
        )

        expected_rows = [
            call(
                [
                    "P1",
                    "100.00 kWh",
                    "10.00 %",
                ],
                [10, 18, 10],
                ["left", "right", "right"]
            ),
            call(
                [
                    "P2",
                    "200.00 kWh",
                    "20.00 %",
                ],
                [10, 18, 10],
                ["left", "right", "right"]
            ),
            call(
                [
                    "P3",
                    "300.00 kWh",
                    "30.00 %",
                ],
                [10, 18, 10],
                ["left", "right", "right"]
            ),
        ]

        printer.table_row.assert_has_calls(
            expected_rows
        )

        assert printer.table_row.call_count == 3