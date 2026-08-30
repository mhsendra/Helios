from unittest.mock import MagicMock

import pytest

from PySide6.QtWidgets import QApplication

from helios.gui.widgets.reports_page import ReportsPage


class TestReportsPage:

    @classmethod
    def setup_class(cls):

        cls.app = QApplication.instance()

        if cls.app is None:
            cls.app = QApplication([])

    def setup_method(self):

        self.project = MagicMock()

        self.page = ReportsPage(
            self.project
        )

    # ==================================================
    # Inicialización
    # ==================================================

    def test_page_stores_project(self):

        assert self.page.project is self.project

    def test_report_output_is_read_only(self):

        assert self.page.report_output.isReadOnly()

    # ==================================================
    # Botones
    # ==================================================

    def test_profile_buttons_exist(self):

        assert self.page.hourly_button is not None
        assert self.page.weekday_button is not None
        assert self.page.monthly_button is not None
        assert self.page.seasonal_button is not None

    def test_indicator_buttons_exist(self):

        assert self.page.mean_consumption_button is not None
        assert self.page.extremes_button is not None
        assert self.page.base_load_button is not None

    def test_comparison_buttons_exist(self):

        assert self.page.monthly_comparison_button is not None
        assert self.page.monthly_variation_button is not None
        assert self.page.weekly_comparison_button is not None
        assert self.page.weekly_variation_button is not None
        assert self.page.yearly_comparison_button is not None

    def test_statistics_buttons_exist(self):

        assert self.page.statistics_button is not None
        assert self.page.daily_statistics_button is not None
        assert self.page.monthly_statistics_button is not None
        assert self.page.yearly_statistics_button is not None

    def test_tariff_buttons_exist(self):

        assert self.page.tariff_periods_button is not None

    def test_economics_buttons_exist(self):

        assert self.page.annual_economics_button is not None
        assert self.page.economic_scenarios_button is not None

    # ==================================================
    # _show_report
    # ==================================================

    def test_show_report_captures_stdout(self):

        def report():

            print("Informe de prueba")

        self.page._show_report(report)

        assert (
            self.page.report_output.toPlainText()
            == "Informe de prueba\n"
        )

    # ==================================================
    # Informes de perfiles
    # ==================================================

    def test_show_hourly_report(self):

        self.page._show_report = MagicMock()

        self.page.show_hourly_report()

        self.page._show_report.assert_called_once_with(
            self.project.profiles.hourly_profile_report
        )

    def test_show_weekday_report(self):

        self.page._show_report = MagicMock()

        self.page.show_weekday_report()

        self.page._show_report.assert_called_once_with(
            self.project.profiles.weekday_profile_report
        )

    def test_show_monthly_report(self):

        self.page._show_report = MagicMock()

        self.page.show_monthly_report()

        self.page._show_report.assert_called_once_with(
            self.project.profiles.monthly_profile_report
        )

    def test_show_seasonal_report(self):

        self.page._show_report = MagicMock()

        self.page.show_seasonal_report()

        self.page._show_report.assert_called_once_with(
            self.project.profiles.seasonal_profile_report
        )

    # ==================================================
    # Informes de indicadores
    # ==================================================

    def test_show_mean_consumption_report(self):

        self.page._show_report = MagicMock()

        self.page.show_mean_consumption_report()

        self.page._show_report.assert_called_once_with(
            self.project.indicators.mean_consumption_report
        )

    def test_show_extremes_report(self):

        self.page._show_report = MagicMock()

        self.page.show_extremes_report()

        self.page._show_report.assert_called_once_with(
            self.project.indicators.extremes_report
        )

    def test_show_base_load_report(self):

        self.page._show_report = MagicMock()

        self.page.show_base_load_report()

        self.page._show_report.assert_called_once_with(
            self.project.indicators.base_load_report
        )

    # ==================================================
    # Informes de comparativas
    # ==================================================

    def test_show_monthly_comparison_report(self):

        self.page._show_report = MagicMock()

        self.page.show_monthly_comparison_report()

        self.page._show_report.assert_called_once_with(
            self.project.comparisons.monthly_comparison_report
        )

    def test_show_monthly_variation_report(self):

        self.page._show_report = MagicMock()

        self.page.show_monthly_variation_report()

        self.page._show_report.assert_called_once_with(
            self.project.comparisons.monthly_variation_report
        )

    def test_show_weekly_comparison_report(self):

        self.page._show_report = MagicMock()

        self.page.show_weekly_comparison_report()

        self.page._show_report.assert_called_once_with(
            self.project.comparisons.weekly_comparison_report
        )

    def test_show_weekly_variation_report(self):

        self.page._show_report = MagicMock()

        self.page.show_weekly_variation_report()

        self.page._show_report.assert_called_once_with(
            self.project.comparisons.weekly_variation_report
        )

    def test_show_yearly_comparison_report(self):

        self.page._show_report = MagicMock()

        self.page.show_yearly_comparison_report()

        self.page._show_report.assert_called_once_with(
            self.project.comparisons.yearly_comparison_report
        )

    # ==================================================
    # Informes de estadísticas
    # ==================================================

    def test_show_statistics_report(self):

        self.page._show_report = MagicMock()

        self.page.show_statistics_report()

        self.page._show_report.assert_called_once_with(
            self.project.statistics.statistics_report
        )

    def test_show_daily_statistics_report(self):

        self.page._show_report = MagicMock()

        self.page.show_daily_statistics_report()

        self.page._show_report.assert_called_once_with(
            self.project.statistics.daily_report
        )

    def test_show_monthly_statistics_report(self):

        self.page._show_report = MagicMock()

        self.page.show_monthly_statistics_report()

        self.page._show_report.assert_called_once_with(
            self.project.statistics.monthly_report
        )

    def test_show_yearly_statistics_report(self):

        self.page._show_report = MagicMock()

        self.page.show_yearly_statistics_report()

        self.page._show_report.assert_called_once_with(
            self.project.statistics.yearly_report
        )

    # ==================================================
    # Informes de tarifas
    # ==================================================

    def test_show_tariff_periods_report(self):

        self.page._show_report = MagicMock()

        self.page.show_tariff_periods_report()

        self.page._show_report.assert_called_once_with(
            self.project.tariffs.tariff_periods_report
        )

    # ==================================================
    # Informes de economía
    # ==================================================

    def test_show_annual_economics_report(self):

        self.page._show_report = MagicMock()

        self.page.show_annual_economics_report()

        self.page._show_report.assert_called_once_with(
            self.project.economics.annual_economics_report
        )

    def test_show_economic_scenarios_report(self):

        self.page._show_report = MagicMock()

        self.page.show_economic_scenarios_report()

        self.page._show_report.assert_called_once_with(
            self.project.economics.economic_scenarios_report
        )