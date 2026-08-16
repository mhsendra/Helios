import pandas as pd
from unittest.mock import patch

from helios.reports.statistics import StatisticsReports


class TestStatisticsReports:

    def setup_method(self):

        self.report = StatisticsReports()

    # ==================================================
    # statistics
    # ==================================================

    def test_statistics_none(self, capsys):

        result = self.report.statistics(
            None
        )

        assert result is None

        captured = capsys.readouterr()

        assert (
            captured.out
            == "No hay estadísticas calculadas.\n"
        )

    @patch(
        "helios.reports.statistics.ReportPrinter"
    )
    def test_statistics(self, printer):

        statistics = {

            "total_consumption": 12345.678,

            "mean_hourly": 1.23456,

            "max_consumption": 5.67891,

            "max_consumption_time":
                pd.Timestamp(
                    "2025-01-15 18:00"
                ),

            "min_consumption": 0.12345,

            "min_consumption_time":
                pd.Timestamp(
                    "2025-01-15 03:00"
                ),

            "std_consumption": 0.98765,
        }

        result = self.report.statistics(
            statistics
        )

        assert result is None

        printer.title.assert_called_once_with(
            "STATISTICS REPORT"
        )

        assert printer.energy.call_count == 4

        printer.datetime.assert_any_call(
            "Fecha del máximo",
            statistics["max_consumption_time"]
        )

        printer.datetime.assert_any_call(
            "Fecha del mínimo",
            statistics["min_consumption_time"]
        )

    # ==================================================
    # daily
    # ==================================================

    def test_daily_none(self, capsys):

        result = self.report.daily(
            None
        )

        assert result is None

        captured = capsys.readouterr()

        assert (
            captured.out
            == "No hay consumos diarios calculados.\n"
        )

    @patch(
        "helios.reports.statistics.ReportPrinter"
    )
    def test_daily(self, printer):

        daily = pd.Series(
            [
                10.0,
                20.0,
                15.0,
                30.0
            ],
            index=pd.to_datetime(
                [
                    "2025-01-01",
                    "2025-01-02",
                    "2025-01-03",
                    "2025-01-04"
                ]
            )
        )

        result = self.report.daily(
            daily
        )

        assert result is None

        printer.title.assert_called_once_with(
            "DAILY CONSUMPTION REPORT"
        )

        printer.count.assert_called_once_with(
            "Días analizados",
            4
        )

        assert printer.energy.call_count == 4

        printer.day.assert_any_call(
            "Fecha del máximo",
            daily.idxmax()
        )

        printer.day.assert_any_call(
            "Fecha del mínimo",
            daily.idxmin()
        )

    # ==================================================
    # monthly
    # ==================================================

    def test_monthly_none(self, capsys):

        result = self.report.monthly(
            None
        )

        assert result is None

        captured = capsys.readouterr()

        assert (
            captured.out
            == "No hay consumos mensuales calculados.\n"
        )

    @patch(
        "helios.reports.statistics.ReportPrinter"
    )
    def test_monthly(self, printer):

        monthly = pd.Series(
            [
                100.0,
                200.0,
                150.0,
                300.0
            ],
            index=pd.to_datetime(
                [
                    "2025-01-01",
                    "2025-02-01",
                    "2025-03-01",
                    "2025-04-01"
                ]
            )
        )

        result = self.report.monthly(
            monthly
        )

        assert result is None

        printer.title.assert_called_once_with(
            "MONTHLY CONSUMPTION REPORT"
        )

        printer.count.assert_called_once_with(
            "Meses analizados",
            4
        )

        assert printer.energy.call_count == 4

        printer.month.assert_any_call(
            "Mes del máximo",
            monthly.idxmax()
        )

        printer.month.assert_any_call(
            "Mes del mínimo",
            monthly.idxmin()
        )

    # ==================================================
    # yearly
    # ==================================================

    def test_yearly_none(self, capsys):

        result = self.report.yearly(
            None
        )

        assert result is None

        captured = capsys.readouterr()

        assert (
            captured.out
            == "No hay consumos anuales calculados.\n"
        )

    @patch(
        "helios.reports.statistics.ReportPrinter"
    )
    def test_yearly(self, printer):

        yearly = pd.Series(
            [
                1000.0,
                2000.0,
                1500.0,
                3000.0
            ],
            index=pd.to_datetime(
                [
                    "2022-12-31",
                    "2023-12-31",
                    "2024-12-31",
                    "2025-12-31"
                ]
            )
        )

        result = self.report.yearly(
            yearly
        )

        assert result is None

        printer.title.assert_called_once_with(
            "YEARLY CONSUMPTION REPORT"
        )

        printer.count.assert_called_once_with(
            "Años analizados",
            4
        )

        assert printer.energy.call_count == 4

        printer.year.assert_any_call(
            "Año del máximo",
            yearly.idxmax()
        )

        printer.year.assert_any_call(
            "Año del mínimo",
            yearly.idxmin()
        )