from unittest.mock import MagicMock

from helios.core.controllers.profiles_controller import (
    ProfilesController
)


def create_controller():

    analyzer = MagicMock()

    analyzer.statistics_engine = MagicMock()
    analyzer.profile_reporter = MagicMock()
    analyzer.plotter = MagicMock()
    analyzer.plotter.profiles = MagicMock()

    analyzer.valid_dataset.return_value = "valid_dataset"

    return ProfilesController(analyzer), analyzer


# ==========================================================
# Cálculos
# ==========================================================


def test_calculate_hourly_profile():

    controller, analyzer = create_controller()

    controller.calculate_hourly_profile()

    analyzer.statistics_engine.calculate_hourly_profile.assert_called_once_with(
        "valid_dataset"
    )


def test_calculate_weekday_profile():

    controller, analyzer = create_controller()

    controller.calculate_weekday_profile()

    analyzer.statistics_engine.calculate_weekday_profile.assert_called_once_with(
        "valid_dataset"
    )


def test_calculate_monthly_profile():

    controller, analyzer = create_controller()

    controller.calculate_monthly_profile()

    analyzer.statistics_engine.calculate_monthly_profile.assert_called_once_with(
        "valid_dataset"
    )


def test_calculate_seasonal_profile():

    controller, analyzer = create_controller()

    controller.calculate_seasonal_profile()

    analyzer.statistics_engine.calculate_seasonal_profile.assert_called_once_with()


def test_calculate_workday_vs_weekend_profile():

    controller, analyzer = create_controller()

    controller.calculate_workday_vs_weekend_profile()

    analyzer.statistics_engine.calculate_workday_vs_weekend_profile.assert_called_once_with(
        "valid_dataset"
    )


def test_calculate():

    controller, _ = create_controller()

    controller.calculate_hourly_profile = MagicMock()
    controller.calculate_weekday_profile = MagicMock()
    controller.calculate_monthly_profile = MagicMock()
    controller.calculate_seasonal_profile = MagicMock()
    controller.calculate_workday_vs_weekend_profile = MagicMock()

    controller.calculate()

    controller.calculate_hourly_profile.assert_called_once_with()
    controller.calculate_weekday_profile.assert_called_once_with()
    controller.calculate_monthly_profile.assert_called_once_with()
    controller.calculate_seasonal_profile.assert_called_once_with()
    controller.calculate_workday_vs_weekend_profile.assert_called_once_with()


# ==========================================================
# Reports
# ==========================================================


def test_hourly_profile_report():

    controller, analyzer = create_controller()

    analyzer.statistics_engine.hourly_profile = "hourly_profile"

    controller.hourly_profile_report()

    analyzer.profile_reporter.hourly_profile.assert_called_once_with(
        "hourly_profile"
    )


def test_weekday_profile_report():

    controller, analyzer = create_controller()

    analyzer.statistics_engine.weekday_profile = "weekday_profile"

    controller.weekday_profile_report()

    analyzer.profile_reporter.weekday_profile.assert_called_once_with(
        "weekday_profile"
    )


def test_monthly_profile_report():

    controller, analyzer = create_controller()

    analyzer.statistics_engine.monthly_profile = "monthly_profile"

    controller.monthly_profile_report()

    analyzer.profile_reporter.monthly_profile.assert_called_once_with(
        "monthly_profile"
    )


def test_seasonal_profile_report():

    controller, analyzer = create_controller()

    analyzer.statistics_engine.seasonal_profile = "seasonal_profile"

    controller.seasonal_profile_report()

    analyzer.profile_reporter.seasonal_profile.assert_called_once_with(
        "seasonal_profile"
    )


def test_reports():

    controller, _ = create_controller()

    controller.hourly_profile_report = MagicMock()
    controller.weekday_profile_report = MagicMock()
    controller.monthly_profile_report = MagicMock()
    controller.seasonal_profile_report = MagicMock()

    controller.reports()

    controller.hourly_profile_report.assert_called_once_with()
    controller.weekday_profile_report.assert_called_once_with()
    controller.monthly_profile_report.assert_called_once_with()
    controller.seasonal_profile_report.assert_called_once_with()


# ==========================================================
# Gráficas
# ==========================================================


def test_plot_hourly_profile():

    controller, analyzer = create_controller()

    analyzer.statistics_engine.hourly_profile = "hourly_profile"

    controller.plot_hourly_profile()

    analyzer.plotter.profiles.plot_hourly_profile.assert_called_once_with(
        "hourly_profile"
    )


def test_plot_weekday_profile():

    controller, analyzer = create_controller()

    analyzer.statistics_engine.weekday_profile = "weekday_profile"

    controller.plot_weekday_profile()

    analyzer.plotter.profiles.plot_weekday_profile.assert_called_once_with(
        "weekday_profile"
    )


def test_plot_monthly_profile():

    controller, analyzer = create_controller()

    analyzer.statistics_engine.monthly_profile = "monthly_profile"

    controller.plot_monthly_profile()

    analyzer.plotter.profiles.plot_monthly_profile.assert_called_once_with(
        "monthly_profile"
    )


def test_plot_seasonal_profile():

    controller, analyzer = create_controller()

    analyzer.statistics_engine.seasonal_profile = "seasonal_profile"

    controller.plot_seasonal_profile()

    analyzer.plotter.profiles.plot_seasonal_profile.assert_called_once_with(
        "seasonal_profile"
    )


def test_plot_workday_vs_weekend_profile():

    controller, analyzer = create_controller()

    analyzer.statistics_engine.workday_vs_weekend_profile = (
        "workday_vs_weekend_profile"
    )

    controller.plot_workday_vs_weekend_profile()

    analyzer.plotter.profiles.plot_workday_vs_weekend_profile.assert_called_once_with(
        "workday_vs_weekend_profile"
    )


def test_plots():

    controller, _ = create_controller()

    controller.plot_hourly_profile = MagicMock()
    controller.plot_workday_vs_weekend_profile = MagicMock()
    controller.plot_weekday_profile = MagicMock()
    controller.plot_monthly_profile = MagicMock()
    controller.plot_seasonal_profile = MagicMock()

    controller.plots()

    controller.plot_hourly_profile.assert_called_once_with()
    controller.plot_workday_vs_weekend_profile.assert_called_once_with()
    controller.plot_weekday_profile.assert_called_once_with()
    controller.plot_monthly_profile.assert_called_once_with()
    controller.plot_seasonal_profile.assert_called_once_with()