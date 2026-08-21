from unittest.mock import MagicMock, call

from helios.core.controllers.profiles_controller import (
    ProfilesController,
)


def create_controller():
    analyzer = MagicMock()

    analyzer.statistics_engine = MagicMock()
    analyzer.profile_reporter = MagicMock()
    analyzer.plotter = MagicMock()
    analyzer.plotter.profiles = MagicMock()

    analyzer.valid_dataset.return_value = "valid_dataset"

    return ProfilesController(analyzer), analyzer


class TestProfilesController:

    # ==========================================================
    # Properties
    # ==========================================================

    def test_hourly_profile_property(self):

        controller, analyzer = create_controller()

        expected = object()
        analyzer.statistics_engine.hourly_profile = expected

        assert controller.hourly_profile is expected

    def test_weekday_profile_property(self):

        controller, analyzer = create_controller()

        expected = object()
        analyzer.statistics_engine.weekday_profile = expected

        assert controller.weekday_profile is expected

    def test_monthly_profile_property(self):

        controller, analyzer = create_controller()

        expected = object()
        analyzer.statistics_engine.monthly_profile = expected

        assert controller.monthly_profile is expected

    def test_seasonal_profile_property(self):

        controller, analyzer = create_controller()

        expected = object()
        analyzer.statistics_engine.seasonal_profile = expected

        assert controller.seasonal_profile is expected

    # ==========================================================
    # Cálculos individuales
    # ==========================================================

    def test_calculate_hourly_profile(self):

        controller, analyzer = create_controller()

        controller.calculate_hourly_profile()

        analyzer.statistics_engine.calculate_hourly_profile.assert_called_once_with(
            analyzer.valid_dataset.return_value
        )

    def test_calculate_weekday_profile(self):

        controller, analyzer = create_controller()

        controller.calculate_weekday_profile()

        analyzer.statistics_engine.calculate_weekday_profile.assert_called_once_with(
            analyzer.valid_dataset.return_value
        )

    def test_calculate_monthly_profile(self):

        controller, analyzer = create_controller()

        controller.calculate_monthly_profile()

        analyzer.statistics_engine.calculate_monthly_profile.assert_called_once_with(
            analyzer.valid_dataset.return_value
        )

    def test_calculate_seasonal_profile(self):

        controller, analyzer = create_controller()

        controller.calculate_seasonal_profile()

        analyzer.statistics_engine.calculate_seasonal_profile.assert_called_once_with()

    def test_calculate_workday_vs_weekend_profile(self):

        controller, analyzer = create_controller()

        controller.calculate_workday_vs_weekend_profile()

        analyzer.statistics_engine.calculate_workday_vs_weekend_profile.assert_called_once_with(
            analyzer.valid_dataset.return_value
        )

    # ==========================================================
    # calculate()
    # ==========================================================

    def test_calculate_calls_all_steps_in_order(self):

        controller, analyzer = create_controller()

        controller.calculate()

        assert analyzer.statistics_engine.mock_calls == [
            call.calculate_hourly_profile(
                analyzer.valid_dataset.return_value
            ),
            call.calculate_weekday_profile(
                analyzer.valid_dataset.return_value
            ),
            call.calculate_monthly_profile(
                analyzer.valid_dataset.return_value
            ),
            call.calculate_seasonal_profile(),
            call.calculate_workday_vs_weekend_profile(
                analyzer.valid_dataset.return_value
            ),
        ]

    # ==========================================================
    # Reportes individuales
    # ==========================================================

    def test_hourly_profile_report(self):

        controller, analyzer = create_controller()

        profile = object()
        analyzer.statistics_engine.hourly_profile = profile

        controller.hourly_profile_report()

        analyzer.profile_reporter.hourly_profile.assert_called_once_with(
            profile
        )

    def test_weekday_profile_report(self):

        controller, analyzer = create_controller()

        profile = object()
        analyzer.statistics_engine.weekday_profile = profile

        controller.weekday_profile_report()

        analyzer.profile_reporter.weekday_profile.assert_called_once_with(
            profile
        )

    def test_monthly_profile_report(self):

        controller, analyzer = create_controller()

        profile = object()
        analyzer.statistics_engine.monthly_profile = profile

        controller.monthly_profile_report()

        analyzer.profile_reporter.monthly_profile.assert_called_once_with(
            profile
        )

    def test_seasonal_profile_report(self):

        controller, analyzer = create_controller()

        profile = object()
        analyzer.statistics_engine.seasonal_profile = profile

        controller.seasonal_profile_report()

        analyzer.profile_reporter.seasonal_profile.assert_called_once_with(
            profile
        )

    # ==========================================================
    # reports()
    # ==========================================================

    def test_reports_calls_all_reports_in_order(self):

        controller, analyzer = create_controller()

        controller.reports()

        assert analyzer.profile_reporter.mock_calls == [
            call.hourly_profile(
                analyzer.statistics_engine.hourly_profile
            ),
            call.weekday_profile(
                analyzer.statistics_engine.weekday_profile
            ),
            call.monthly_profile(
                analyzer.statistics_engine.monthly_profile
            ),
            call.seasonal_profile(
                analyzer.statistics_engine.seasonal_profile
            ),
        ]

    # ==========================================================
    # Gráficas individuales
    # ==========================================================

    def test_plot_hourly_profile(self):

        controller, analyzer = create_controller()

        profile = object()
        analyzer.statistics_engine.hourly_profile = profile

        controller.plot_hourly_profile()

        analyzer.plotter.profiles.plot_hourly_profile.assert_called_once_with(
            profile
        )

    def test_plot_weekday_profile(self):

        controller, analyzer = create_controller()

        profile = object()
        analyzer.statistics_engine.weekday_profile = profile

        controller.plot_weekday_profile()

        analyzer.plotter.profiles.plot_weekday_profile.assert_called_once_with(
            profile
        )

    def test_plot_monthly_profile(self):

        controller, analyzer = create_controller()

        profile = object()
        analyzer.statistics_engine.monthly_profile = profile

        controller.plot_monthly_profile()

        analyzer.plotter.profiles.plot_monthly_profile.assert_called_once_with(
            profile
        )

    def test_plot_seasonal_profile(self):

        controller, analyzer = create_controller()

        profile = object()
        analyzer.statistics_engine.seasonal_profile = profile

        controller.plot_seasonal_profile()

        analyzer.plotter.profiles.plot_seasonal_profile.assert_called_once_with(
            profile
        )

    def test_plot_workday_vs_weekend_profile(self):

        controller, analyzer = create_controller()

        profile = object()
        analyzer.statistics_engine.workday_vs_weekend_profile = profile

        controller.plot_workday_vs_weekend_profile()

        analyzer.plotter.profiles.plot_workday_vs_weekend_profile.assert_called_once_with(
            profile
        )

    # ==========================================================
    # plots()
    # ==========================================================

    def test_plots_calls_all_plots_in_order(self):

        controller, analyzer = create_controller()

        controller.plots()

        assert analyzer.plotter.profiles.mock_calls == [
            call.plot_hourly_profile(
                analyzer.statistics_engine.hourly_profile
            ),
            call.plot_workday_vs_weekend_profile(
                analyzer.statistics_engine.workday_vs_weekend_profile
            ),
            call.plot_weekday_profile(
                analyzer.statistics_engine.weekday_profile
            ),
            call.plot_monthly_profile(
                analyzer.statistics_engine.monthly_profile
            ),
            call.plot_seasonal_profile(
                analyzer.statistics_engine.seasonal_profile
            ),
        ]