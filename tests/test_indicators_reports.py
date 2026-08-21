from unittest.mock import call, patch

import pandas as pd
import pytest

from helios.reports.indicators import IndicatorsReports


class TestIndicatorsReports:

    def setup_method(self):

        self.report = IndicatorsReports()

    # ==================================================
    # mean_consumption
    # ==================================================

    def test_mean_consumption(self):

        mean_consumption = {
            "hourly": 1.23456,
            "daily": 12.34567,
            "weekly": 86.41987,
            "monthly": 370.12345,
            "yearly": 4441.4814,
            "workday": 13.45678,
            "weekend": 10.98765,
        }

        with patch(
            "helios.reports.indicators.ReportPrinter"
        ) as printer:

            result = self.report.mean_consumption(
                mean_consumption
            )

        assert result is None

        printer.title.assert_called_once_with(
            "MEAN CONSUMPTION"
        )

        printer.blank.assert_called_once()

        assert printer.energy.call_count == 7

        expected_calls = [
            (
                "Consumo medio horario",
                1.23456,
            ),
            (
                "Consumo medio diario",
                12.34567,
            ),
            (
                "Consumo medio semanal",
                86.41987,
            ),
            (
                "Consumo medio mensual",
                370.12345,
            ),
            (
                "Consumo medio anual",
                4441.4814,
            ),
            (
                "Consumo medio laborable",
                13.45678,
            ),
            (
                "Consumo medio fin de semana",
                10.98765,
            ),
        ]

        for printer_call, expected in zip(
            printer.energy.call_args_list,
            expected_calls
        ):

            assert printer_call.args[0] == expected[0]
            assert printer_call.args[1] == expected[1]
            assert printer_call.kwargs["decimals"] == 3

    # ==================================================
    # base_load
    # ==================================================

    def test_base_load(self):

        with patch(
            "helios.reports.indicators.ReportPrinter"
        ) as printer:

            result = self.report.base_load(
                1.23456
            )

        assert result is None

        printer.title.assert_called_once_with(
            "BASE LOAD"
        )

        printer.blank.assert_called_once()

        printer.text.assert_called_once_with(
            "Carga base",
            "1.235 kWh/h"
        )

    # ==================================================
    # format datetime
    # ==================================================

    def test_format_datetime(self):

        timestamp = pd.Timestamp(
            "2025-03-15 18:42"
        )

        result = self.report._format_datetime(
            timestamp
        )

        assert result == "15/03/2025 18:42"

    # ==================================================
    # format date
    # ==================================================

    def test_format_date(self):

        timestamp = pd.Timestamp(
            "2025-03-15"
        )

        result = self.report._format_date(
            timestamp
        )

        assert result == "15/03/2025"

    # ==================================================
    # format week
    # ==================================================

    def test_format_week(self):

        result = self.report._format_week(
            (2025, 12)
        )

        assert result == "12 (2025)"

    # ==================================================
    # format month
    # ==================================================

    @pytest.mark.parametrize(
        "month, expected",
        [
            (1, "Enero 2025"),
            (2, "Febrero 2025"),
            (3, "Marzo 2025"),
            (4, "Abril 2025"),
            (5, "Mayo 2025"),
            (6, "Junio 2025"),
            (7, "Julio 2025"),
            (8, "Agosto 2025"),
            (9, "Septiembre 2025"),
            (10, "Octubre 2025"),
            (11, "Noviembre 2025"),
            (12, "Diciembre 2025"),
        ]
    )
    def test_format_month(
        self,
        month,
        expected
    ):

        timestamp = pd.Timestamp(
            year=2025,
            month=month,
            day=1
        )

        result = self.report._format_month(
            timestamp
        )

        assert result == expected


class TestIndicatorsReportsExtremes:

    def setup_method(self):

        self.report = IndicatorsReports()

        self.extremes = {

            "hourly_max": (
                pd.Timestamp("2025-01-15 18:00"),
                12.345
            ),

            "hourly_min": (
                pd.Timestamp("2025-01-15 03:00"),
                0.123
            ),

            "daily_max": (
                pd.Timestamp("2025-01-20"),
                45.678
            ),

            "daily_min": (
                pd.Timestamp("2025-01-05"),
                10.111
            ),

            "weekly_max": (
                (2025, 4),
                250.123
            ),

            "weekly_min": (
                (2025, 2),
                100.456
            ),

            "monthly_max": (
                pd.Timestamp("2025-03-01"),
                900.789
            ),

            "monthly_min": (
                pd.Timestamp("2025-01-01"),
                500.321
            )
        }

    # ==================================================
    # extremes
    # ==================================================

    @patch(
        "helios.reports.indicators.ReportPrinter"
    )
    def test_extremes_prints_title(
        self,
        printer
    ):

        self.report.extremes(
            self.extremes
        )

        printer.title.assert_called_once_with(
            "CONSUMPTION EXTREMES"
        )

    @patch(
        "helios.reports.indicators.ReportPrinter"
    )
    def test_extremes_prints_blank_lines(
        self,
        printer
    ):

        self.report.extremes(
            self.extremes
        )

        assert printer.blank.call_count == 8

    @patch(
        "helios.reports.indicators.ReportPrinter"
    )
    def test_extremes_prints_all_energy_values(
        self,
        printer
    ):

        self.report.extremes(
            self.extremes
        )

        printer.energy.assert_has_calls(
            [
                call("Consumo", 12.345),
                call("Consumo", 0.123),
                call("Consumo", 45.678),
                call("Consumo", 10.111),
                call("Consumo", 250.123),
                call("Consumo", 100.456),
                call("Consumo", 900.789),
                call("Consumo", 500.321),
            ]
        )

        assert printer.energy.call_count == 8

    @patch(
        "helios.reports.indicators.ReportPrinter"
    )
    def test_extremes_prints_all_text_values(
        self,
        printer
    ):

        self.report.extremes(
            self.extremes
        )

        printer.text.assert_has_calls(
            [
                call(
                    "Mayor consumo horario",
                    "15/01/2025 18:00"
                ),
                call(
                    "Menor consumo horario",
                    "15/01/2025 03:00"
                ),
                call(
                    "Mayor consumo diario",
                    "20/01/2025"
                ),
                call(
                    "Menor consumo diario",
                    "05/01/2025"
                ),
                call(
                    "Mayor consumo semanal",
                    "4 (2025)"
                ),
                call(
                    "Menor consumo semanal",
                    "2 (2025)"
                ),
                call(
                    "Mayor consumo mensual",
                    "Marzo 2025"
                ),
                call(
                    "Menor consumo mensual",
                    "Enero 2025"
                ),
            ]
        )

        assert printer.text.call_count == 8

    # ==================================================
    # formatters used by extremes
    # ==================================================

    def test_format_datetime(self):

        timestamp = pd.Timestamp(
            "2025-01-15 18:30"
        )

        result = self.report._format_datetime(
            timestamp
        )

        assert result == "15/01/2025 18:30"

    def test_format_date(self):

        timestamp = pd.Timestamp(
            "2025-01-20"
        )

        result = self.report._format_date(
            timestamp
        )

        assert result == "20/01/2025"

    def test_format_week(self):

        result = self.report._format_week(
            (2025, 4)
        )

        assert result == "4 (2025)"

    def test_format_month(self):

        result = self.report._format_month(
            pd.Timestamp("2025-03-01")
        )

        assert result == "Marzo 2025"

    # ==================================================
    # _print_extreme
    # ==================================================

    def test_print_extreme(
        self,
        capsys
    ):

        extremes = {

            "hourly_max": (
                pd.Timestamp(
                    "2025-01-15 18:30"
                ),
                12.34567
            )
        }

        self.report._print_extreme(
            extremes,
            "Mayor consumo horario",
            "hourly_max",
            self.report._format_datetime
        )

        captured = capsys.readouterr()

        assert captured.out == (
            "Mayor consumo horario\n"
            "  15/01/2025 18:30\n"
            "  12.346 kWh\n"
            "\n"
        )