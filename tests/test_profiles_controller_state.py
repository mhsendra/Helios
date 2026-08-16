from unittest.mock import MagicMock

import pandas as pd

from helios.core.controllers.profiles_controller import ProfilesController


class TestProfilesControllerState:

    def setup_method(self):

        self.analyzer = MagicMock()

        self.analyzer.statistics_engine.hourly_profile = pd.Series(
            [1, 2, 3]
        )

        self.analyzer.statistics_engine.weekday_profile = pd.Series(
            [1, 2, 3]
        )

        self.analyzer.statistics_engine.monthly_profile = pd.Series(
            [1, 2, 3]
        )

        self.analyzer.statistics_engine.seasonal_profile = pd.Series(
            [1, 2, 3]
        )

        self.analyzer.statistics_engine.workday_vs_weekend_profile = {
            "workdays": 10,
            "weekend": 12
        }

        self.analyzer.valid_dataset.return_value = pd.DataFrame()

        self.controller = ProfilesController(
            self.analyzer
        )

    # ==================================================
    # Estado
    # ==================================================

    def test_initial_state(self):

        assert self.controller.hourly_profile.equals(
            self.analyzer.statistics_engine.hourly_profile
        )

        assert self.controller.weekday_profile.equals(
            self.analyzer.statistics_engine.weekday_profile
        )

        assert self.controller.monthly_profile.equals(
            self.analyzer.statistics_engine.monthly_profile
        )

        assert self.controller.seasonal_profile.equals(
            self.analyzer.statistics_engine.seasonal_profile
        )

    # ==================================================
    # Cálculos individuales
    # ==================================================

    def test_calculate_hourly_profile(self):

        self.controller.calculate_hourly_profile()

        self.analyzer.statistics_engine.calculate_hourly_profile.assert_called_once_with(
            self.analyzer.valid_dataset.return_value
        )

    def test_calculate_weekday_profile(self):

        self.controller.calculate_weekday_profile()

        self.analyzer.statistics_engine.calculate_weekday_profile.assert_called_once_with(
            self.analyzer.valid_dataset.return_value
        )

    def test_calculate_monthly_profile(self):

        self.controller.calculate_monthly_profile()

        self.analyzer.statistics_engine.calculate_monthly_profile.assert_called_once_with(
            self.analyzer.valid_dataset.return_value
        )

    def test_calculate_seasonal_profile(self):

        self.controller.calculate_seasonal_profile()

        self.analyzer.statistics_engine.calculate_seasonal_profile.assert_called_once_with()

    def test_calculate_workday_vs_weekend_profile(self):

        self.controller.calculate_workday_vs_weekend_profile()

        self.analyzer.statistics_engine.calculate_workday_vs_weekend_profile.assert_called_once_with(
            self.analyzer.valid_dataset.return_value
        )

    # ==================================================
    # calculate()
    # ==================================================

    def test_calculate_calls_all_steps_in_order(self):

        self.controller.calculate()

        engine = self.analyzer.statistics_engine

        assert engine.calculate_hourly_profile.call_count == 1
        assert engine.calculate_weekday_profile.call_count == 1
        assert engine.calculate_monthly_profile.call_count == 1
        assert engine.calculate_seasonal_profile.call_count == 1
        assert engine.calculate_workday_vs_weekend_profile.call_count == 1

        # ==================================================
    # Reportes
    # ==================================================

    def test_hourly_profile_report(self):

        self.controller.hourly_profile_report()

        self.analyzer.profile_reporter.hourly_profile.assert_called_once_with(
            self.analyzer.statistics_engine.hourly_profile
        )

    def test_weekday_profile_report(self):

        self.controller.weekday_profile_report()

        self.analyzer.profile_reporter.weekday_profile.assert_called_once_with(
            self.analyzer.statistics_engine.weekday_profile
        )

    def test_monthly_profile_report(self):

        self.controller.monthly_profile_report()

        self.analyzer.profile_reporter.monthly_profile.assert_called_once_with(
            self.analyzer.statistics_engine.monthly_profile
        )

    def test_seasonal_profile_report(self):

        self.controller.seasonal_profile_report()

        self.analyzer.profile_reporter.seasonal_profile.assert_called_once_with(
            self.analyzer.statistics_engine.seasonal_profile
        )

    def test_reports_calls_all_reports(self):

        self.controller.reports()

        reporter = self.analyzer.profile_reporter

        reporter.hourly_profile.assert_called_once_with(
            self.analyzer.statistics_engine.hourly_profile
        )

        reporter.weekday_profile.assert_called_once_with(
            self.analyzer.statistics_engine.weekday_profile
        )

        reporter.monthly_profile.assert_called_once_with(
            self.analyzer.statistics_engine.monthly_profile
        )

        reporter.seasonal_profile.assert_called_once_with(
            self.analyzer.statistics_engine.seasonal_profile
        )

    # ==================================================
    # Gráficas
    # ==================================================

    def test_plot_hourly_profile(self):

        self.controller.plot_hourly_profile()

        self.analyzer.plotter.profiles.plot_hourly_profile.assert_called_once_with(
            self.analyzer.statistics_engine.hourly_profile
        )

    def test_plot_weekday_profile(self):

        self.controller.plot_weekday_profile()

        self.analyzer.plotter.profiles.plot_weekday_profile.assert_called_once_with(
            self.analyzer.statistics_engine.weekday_profile
        )

    def test_plot_monthly_profile(self):

        self.controller.plot_monthly_profile()

        self.analyzer.plotter.profiles.plot_monthly_profile.assert_called_once_with(
            self.analyzer.statistics_engine.monthly_profile
        )

    def test_plot_seasonal_profile(self):

        self.controller.plot_seasonal_profile()

        self.analyzer.plotter.profiles.plot_seasonal_profile.assert_called_once_with(
            self.analyzer.statistics_engine.seasonal_profile
        )

    def test_plot_workday_vs_weekend_profile(self):

        self.controller.plot_workday_vs_weekend_profile()

        self.analyzer.plotter.profiles.plot_workday_vs_weekend_profile.assert_called_once_with(
            self.analyzer.statistics_engine.workday_vs_weekend_profile
        )

    def test_plots_calls_all_plots(self):

        self.controller.plots()

        plots = self.analyzer.plotter.profiles

        plots.plot_hourly_profile.assert_called_once_with(
            self.analyzer.statistics_engine.hourly_profile
        )

        plots.plot_workday_vs_weekend_profile.assert_called_once_with(
            self.analyzer.statistics_engine.workday_vs_weekend_profile
        )

        plots.plot_weekday_profile.assert_called_once_with(
            self.analyzer.statistics_engine.weekday_profile
        )

        plots.plot_monthly_profile.assert_called_once_with(
            self.analyzer.statistics_engine.monthly_profile
        )

        plots.plot_seasonal_profile.assert_called_once_with(
            self.analyzer.statistics_engine.seasonal_profile
        )