from unittest.mock import MagicMock

import pandas as pd

from PySide6.QtWidgets import QApplication

from helios.gui.widgets.statistics_page import StatisticsPage


class TestStatisticsPage:

    @classmethod
    def setup_class(cls):

        cls.app = QApplication.instance()

        if cls.app is None:
            cls.app = QApplication([])

    def setup_method(self):

        self.project = MagicMock()

        self.page = StatisticsPage(
            self.project
        )

    # ==================================================
    # Estado inicial
    # ==================================================

    def test_page_stores_project(self):

        assert self.page.project is self.project

    def test_labels_start_with_dash(self):

        labels = [
            self.page.total_label,
            self.page.mean_label,
            self.page.min_label,
            self.page.max_label,
            self.page.std_label,
            self.page.max_time_label,
            self.page.min_time_label,
        ]

        assert all(
            label.text() == "-"
            for label in labels
        )

    # ==================================================
    # update_data — datos no preparados
    # ==================================================

    def test_update_data_returns_when_statistics_are_missing(self):

        self.project.statistics.statistics = None

        self.page.update_data()

        assert self.page.total_label.text() == "-"
        assert self.page.mean_label.text() == "-"
        assert self.page.min_label.text() == "-"
        assert self.page.max_label.text() == "-"
        assert self.page.std_label.text() == "-"
        assert self.page.max_time_label.text() == "-"
        assert self.page.min_time_label.text() == "-"

    # ==================================================
    # update_data — estadísticas
    # ==================================================

    def test_update_data_sets_consumption_statistics(self):

        import pandas as pd

        self.project.statistics.statistics = {
            "total_consumption": 12345.678,
            "mean_hourly": 2.34567,
            "min_consumption": 0.12345,
            "max_consumption": 15.6789,
            "std_consumption": 3.45678,
            "max_consumption_time": pd.Timestamp(
                "2025-06-15 18:00"
            ),
            "min_consumption_time": pd.Timestamp(
                "2025-01-10 03:00"
            ),
        }

        self.page.update_data()

        assert (
            self.page.total_label.text()
            == "12345.68 kWh"
        )

        assert (
            self.page.mean_label.text()
            == "2.346 kWh"
        )

        assert (
            self.page.min_label.text()
            == "0.123 kWh"
        )

        assert (
            self.page.max_label.text()
            == "15.679 kWh"
        )

        assert (
            self.page.std_label.text()
            == "3.457 kWh"
        )

    # ==================================================
    # Fechas
    # ==================================================

    def test_update_data_formats_maximum_datetime(self):

        import pandas as pd

        self.project.statistics.statistics = {
            "total_consumption": 100.0,
            "mean_hourly": 2.0,
            "min_consumption": 0.5,
            "max_consumption": 10.0,
            "std_consumption": 2.5,
            "max_consumption_time": pd.Timestamp(
                "2025-06-15 18:07"
            ),
            "min_consumption_time": pd.Timestamp(
                "2025-01-10 03:04"
            ),
        }

        self.page.update_data()

        assert (
            self.page.max_time_label.text()
            == "15/06/2025 18:07"
        )

    def test_update_data_formats_minimum_datetime(self):

        import pandas as pd

        self.project.statistics.statistics = {
            "total_consumption": 100.0,
            "mean_hourly": 2.0,
            "min_consumption": 0.5,
            "max_consumption": 10.0,
            "std_consumption": 2.5,
            "max_consumption_time": pd.Timestamp(
                "2025-06-15 18:07"
            ),
            "min_consumption_time": pd.Timestamp(
                "2025-01-10 03:04"
            ),
        }

        self.page.update_data()

        assert (
            self.page.min_time_label.text()
            == "10/01/2025 03:04"
        )

    # ==================================================
    # Sustitución de datos
    # ==================================================

    def test_update_data_replaces_previous_values(self):

        import pandas as pd

        self.project.statistics.statistics = {
            "total_consumption": 100.0,
            "mean_hourly": 2.0,
            "min_consumption": 0.5,
            "max_consumption": 10.0,
            "std_consumption": 2.5,
            "max_consumption_time": pd.Timestamp(
                "2025-06-15 18:00"
            ),
            "min_consumption_time": pd.Timestamp(
                "2025-01-10 03:00"
            ),
        }

        self.page.update_data()

        assert self.page.total_label.text() == "100.00 kWh"

        self.project.statistics.statistics = {
            "total_consumption": 250.5,
            "mean_hourly": 4.1234,
            "min_consumption": 1.2345,
            "max_consumption": 20.9876,
            "std_consumption": 5.6789,
            "max_consumption_time": pd.Timestamp(
                "2026-08-15 21:30"
            ),
            "min_consumption_time": pd.Timestamp(
                "2026-02-20 02:15"
            ),
        }

        self.page.update_data()

        assert self.page.total_label.text() == "250.50 kWh"
        assert self.page.mean_label.text() == "4.123 kWh"
        assert self.page.min_label.text() == "1.234 kWh"
        assert self.page.max_label.text() == "20.988 kWh"
        assert self.page.std_label.text() == "5.679 kWh"
        assert self.page.max_time_label.text() == "15/08/2026 21:30"
        assert self.page.min_time_label.text() == "20/02/2026 02:15"

    # ==================================================
    # Acceso al proyecto
    # ==================================================

    def test_update_data_reads_statistics_from_project(self):

        statistics = {
            "total_consumption": 100.0,
            "mean_hourly": 2.0,
            "min_consumption": 0.5,
            "max_consumption": 10.0,
            "std_consumption": 2.5,
            "max_consumption_time": pd.Timestamp(
                "2025-06-15 18:00"
            ),
            "min_consumption_time": pd.Timestamp(
                "2025-01-10 03:00"
            ),
        }

        self.project.statistics.statistics = statistics

        self.page.update_data()

        assert (
            self.project.statistics.statistics
            is statistics
        )


    # ==================================================
    # Formato numérico
    # ==================================================

    def test_update_data_rounds_total_to_two_decimals(self):

        self.project.statistics.statistics = {
            "total_consumption": 123.456,
            "mean_hourly": 1.0,
            "min_consumption": 0.0,
            "max_consumption": 2.0,
            "std_consumption": 0.5,
            "max_consumption_time": pd.Timestamp(
                "2025-01-01 10:00"
            ),
            "min_consumption_time": pd.Timestamp(
                "2025-01-01 09:00"
            ),
        }

        self.page.update_data()

        assert (
            self.page.total_label.text()
            == "123.46 kWh"
        )


    def test_update_data_rounds_mean_to_three_decimals(self):

        self.project.statistics.statistics = {
            "total_consumption": 100.0,
            "mean_hourly": 1.23456,
            "min_consumption": 0.0,
            "max_consumption": 2.0,
            "std_consumption": 0.5,
            "max_consumption_time": pd.Timestamp(
                "2025-01-01 10:00"
            ),
            "min_consumption_time": pd.Timestamp(
                "2025-01-01 09:00"
            ),
        }

        self.page.update_data()

        assert (
            self.page.mean_label.text()
            == "1.235 kWh"
        )


    def test_update_data_rounds_minimum_to_three_decimals(self):

        self.project.statistics.statistics = {
            "total_consumption": 100.0,
            "mean_hourly": 1.0,
            "min_consumption": 1.23456,
            "max_consumption": 2.0,
            "std_consumption": 0.5,
            "max_consumption_time": pd.Timestamp(
                "2025-01-01 10:00"
            ),
            "min_consumption_time": pd.Timestamp(
                "2025-01-01 09:00"
            ),
        }

        self.page.update_data()

        assert (
            self.page.min_label.text()
            == "1.235 kWh"
        )


    def test_update_data_rounds_maximum_to_three_decimals(self):

        self.project.statistics.statistics = {
            "total_consumption": 100.0,
            "mean_hourly": 1.0,
            "min_consumption": 0.0,
            "max_consumption": 12.34567,
            "std_consumption": 0.5,
            "max_consumption_time": pd.Timestamp(
                "2025-01-01 10:00"
            ),
            "min_consumption_time": pd.Timestamp(
                "2025-01-01 09:00"
            ),
        }

        self.page.update_data()

        assert (
            self.page.max_label.text()
            == "12.346 kWh"
        )


    def test_update_data_rounds_standard_deviation_to_three_decimals(self):

        self.project.statistics.statistics = {
            "total_consumption": 100.0,
            "mean_hourly": 1.0,
            "min_consumption": 0.0,
            "max_consumption": 2.0,
            "std_consumption": 3.45678,
            "max_consumption_time": pd.Timestamp(
                "2025-01-01 10:00"
            ),
            "min_consumption_time": pd.Timestamp(
                "2025-01-01 09:00"
            ),
        }

        self.page.update_data()

        assert (
            self.page.std_label.text()
            == "3.457 kWh"
        )


    # ==================================================
    # Unidades
    # ==================================================

    def test_update_data_adds_kwh_unit_to_consumption_values(self):

        self.project.statistics.statistics = {
            "total_consumption": 100.0,
            "mean_hourly": 2.0,
            "min_consumption": 0.5,
            "max_consumption": 10.0,
            "std_consumption": 2.5,
            "max_consumption_time": pd.Timestamp(
                "2025-01-01 10:00"
            ),
            "min_consumption_time": pd.Timestamp(
                "2025-01-01 09:00"
            ),
        }

        self.page.update_data()

        assert self.page.total_label.text().endswith(
            " kWh"
        )
        assert self.page.mean_label.text().endswith(
            " kWh"
        )
        assert self.page.min_label.text().endswith(
            " kWh"
        )
        assert self.page.max_label.text().endswith(
            " kWh"
        )
        assert self.page.std_label.text().endswith(
            " kWh"
        )


    # ==================================================
    # Valores cero
    # ==================================================

    def test_update_data_handles_zero_values(self):

        self.project.statistics.statistics = {
            "total_consumption": 0.0,
            "mean_hourly": 0.0,
            "min_consumption": 0.0,
            "max_consumption": 0.0,
            "std_consumption": 0.0,
            "max_consumption_time": pd.Timestamp(
                "2025-01-01 00:00"
            ),
            "min_consumption_time": pd.Timestamp(
                "2025-01-01 00:00"
            ),
        }

        self.page.update_data()

        assert self.page.total_label.text() == "0.00 kWh"
        assert self.page.mean_label.text() == "0.000 kWh"
        assert self.page.min_label.text() == "0.000 kWh"
        assert self.page.max_label.text() == "0.000 kWh"
        assert self.page.std_label.text() == "0.000 kWh"


    # ==================================================
    # Actualización completa
    # ==================================================

    def test_update_data_updates_all_labels_together(self):

        self.project.statistics.statistics = {
            "total_consumption": 9876.543,
            "mean_hourly": 1.23456,
            "min_consumption": 0.12345,
            "max_consumption": 67.89123,
            "std_consumption": 4.56789,
            "max_consumption_time": pd.Timestamp(
                "2026-07-20 22:45"
            ),
            "min_consumption_time": pd.Timestamp(
                "2024-03-11 04:15"
            ),
        }

        self.page.update_data()

        assert self.page.total_label.text() == "9876.54 kWh"
        assert self.page.mean_label.text() == "1.235 kWh"
        assert self.page.min_label.text() == "0.123 kWh"
        assert self.page.max_label.text() == "67.891 kWh"
        assert self.page.std_label.text() == "4.568 kWh"
        assert (
            self.page.max_time_label.text()
            == "20/07/2026 22:45"
        )
        assert (
            self.page.min_time_label.text()
            == "11/03/2024 04:15"
        )