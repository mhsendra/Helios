import pandas as pd
from unittest.mock import call, patch

from helios.reports.statistics import StatisticsReports


class TestStatisticsReports:

    def setup_method(self):

        self.report = StatisticsReports()

    # ==================================================
    # statistics
    # ==================================================

    def test_statistics_none(self, capsys):

        result = self.report.statistics(None)

        assert result is None

        captured = capsys.readouterr()

        assert captured.out == (
            "No hay estadísticas calculadas.\n"
        )

    @patch(
        "helios.reports.statistics.ReportPrinter"
    )
    def test_statistics(self, printer):

        statistics = {
            "total_consumption": 12345.678,
            "mean_hourly": 1.23456,
            "max_consumption": 5.67891,
            "max_consumption_time": pd.Timestamp(
                "2025-01-15 18:00"
            ),
            "min_consumption": 0.12345,
            "min_consumption_time": pd.Timestamp(
                "2025-01-15 03:00"
            ),
        }

        result = self.report.statistics(statistics)

        assert result is None

        printer.title.assert_called_once_with(
            "STATISTICS REPORT"
        )

        printer.energy.assert_has_calls(
            [
                call(
                    "Consumo total",
                    statistics["total_consumption"]
                ),
                call(
                    "Consumo medio horario",
                    statistics["mean_hourly"],
                    decimals=3
                ),
                call(
                    "Consumo máximo",
                    statistics["max_consumption"],
                    decimals=3
                ),
                call(
                    "Consumo mínimo",
                    statistics["min_consumption"],
                    decimals=3
                ),
            ]
        )

        assert printer.energy.call_count == 4

        printer.datetime.assert_has_calls(
            [
                call(
                    "Fecha del máximo",
                    statistics["max_consumption_time"]
                ),
                call(
                    "Fecha del mínimo",
                    statistics["min_consumption_time"]
                ),
            ]
        )

        assert printer.datetime.call_count == 2

    # ==================================================
    # daily
    # ==================================================

    def test_daily_none(self, capsys):

        result = self.report.daily(None)

        assert result is None

        captured = capsys.readouterr()

        assert captured.out == (
            "No hay consumos diarios calculados.\n"
        )

    @patch(
        "helios.reports.statistics.ReportPrinter"
    )
    def test_daily(self, printer):

        daily = pd.Series(
            [10.0, 20.0, 15.0, 30.0],
            index=pd.to_datetime(
                [
                    "2025-01-01",
                    "2025-01-02",
                    "2025-01-03",
                    "2025-01-04"
                ]
            )
        )

        result = self.report.daily(daily)

        assert result is None

        printer.title.assert_called_once_with(
            "DAILY CONSUMPTION REPORT"
        )

        printer.blank.assert_has_calls(
            [
                call(),
                call(),
            ]
        )

        assert printer.blank.call_count == 2

        printer.count.assert_called_once_with(
            "Días analizados",
            len(daily)
        )

        printer.energy.assert_has_calls(
            [
                call(
                    "Consumo total",
                    daily.sum()
                ),
                call(
                    "Consumo diario medio",
                    daily.mean()
                ),
                call(
                    "Consumo máximo diario",
                    daily.max(),
                    decimals=3
                ),
                call(
                    "Consumo mínimo diario",
                    daily.min(),
                    decimals=3
                ),
            ]
        )

        assert printer.energy.call_count == 4

        printer.day.assert_has_calls(
            [
                call(
                    "Fecha del máximo",
                    daily.idxmax()
                ),
                call(
                    "Fecha del mínimo",
                    daily.idxmin()
                ),
            ]
        )

        assert printer.day.call_count == 2

    # ==================================================
    # monthly
    # ==================================================

    def test_monthly_none(self, capsys):

        result = self.report.monthly(None)

        assert result is None

        captured = capsys.readouterr()

        assert captured.out == (
            "No hay consumos mensuales calculados.\n"
        )

    @patch(
        "helios.reports.statistics.ReportPrinter"
    )
    def test_monthly(self, printer):

        monthly = pd.Series(
            [100.0, 200.0, 150.0, 300.0],
            index=pd.to_datetime(
                [
                    "2025-01-01",
                    "2025-02-01",
                    "2025-03-01",
                    "2025-04-01"
                ]
            )
        )

        result = self.report.monthly(monthly)

        assert result is None

        printer.title.assert_called_once_with(
            "MONTHLY CONSUMPTION REPORT"
        )

        printer.blank.assert_has_calls(
            [
                call(),
                call(),
            ]
        )

        assert printer.blank.call_count == 2

        printer.count.assert_called_once_with(
            "Meses analizados",
            len(monthly)
        )

        printer.energy.assert_has_calls(
            [
                call(
                    "Consumo total",
                    monthly.sum(),
                    decimals=3
                ),
                call(
                    "Consumo mensual medio",
                    monthly.mean()
                ),
                call(
                    "Consumo máximo mensual",
                    monthly.max(),
                    decimals=3
                ),
                call(
                    "Consumo mínimo mensual",
                    monthly.min(),
                    decimals=3
                ),
            ]
        )

        assert printer.energy.call_count == 4

        printer.month.assert_has_calls(
            [
                call(
                    "Mes del máximo",
                    monthly.idxmax()
                ),
                call(
                    "Mes del mínimo",
                    monthly.idxmin()
                ),
            ]
        )

        assert printer.month.call_count == 2

    # ==================================================
    # yearly
    # ==================================================

    def test_yearly_none(self, capsys):

        result = self.report.yearly(None)

        assert result is None

        captured = capsys.readouterr()

        assert captured.out == (
            "No hay consumos anuales calculados.\n"
        )

    @patch(
        "helios.reports.statistics.ReportPrinter"
    )
    def test_yearly(self, printer):

        yearly = pd.Series(
            [1000.0, 2000.0, 1500.0, 3000.0],
            index=pd.to_datetime(
                [
                    "2022-12-31",
                    "2023-12-31",
                    "2024-12-31",
                    "2025-12-31"
                ]
            )
        )

        result = self.report.yearly(yearly)

        assert result is None

        printer.title.assert_called_once_with(
            "YEARLY CONSUMPTION REPORT"
        )

        printer.blank.assert_has_calls(
            [
                call(),
                call(),
            ]
        )

        assert printer.blank.call_count == 2

        printer.count.assert_called_once_with(
            "Años analizados",
            len(yearly)
        )

        printer.energy.assert_has_calls(
            [
                call(
                    "Consumo total",
                    yearly.sum(),
                    decimals=3
                ),
                call(
                    "Consumo anual medio",
                    yearly.mean()
                ),
                call(
                    "Consumo máximo anual",
                    yearly.max(),
                    decimals=3
                ),
                call(
                    "Consumo mínimo anual",
                    yearly.min(),
                    decimals=3
                ),
            ]
        )

        assert printer.energy.call_count == 4

        printer.year.assert_has_calls(
            [
                call(
                    "Año del máximo",
                    yearly.idxmax()
                ),
                call(
                    "Año del mínimo",
                    yearly.idxmin()
                ),
            ]
        )

        assert printer.year.call_count == 2