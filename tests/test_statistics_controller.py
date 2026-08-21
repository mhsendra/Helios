from unittest.mock import MagicMock, call

from helios.core.controllers.statistics_controller import (
    StatisticsController
)


def create_controller():

    analyzer = MagicMock()

    analyzer.statistics_engine = MagicMock()
    analyzer.statistics_reporter = MagicMock()

    analyzer.valid_dataset.return_value = "valid_dataset"

    return StatisticsController(analyzer), analyzer


# ==========================================================
# Cálculos
# ==========================================================


def test_calculate_statistics():

    controller, analyzer = create_controller()

    controller.calculate_statistics()

    analyzer.statistics_engine.calculate.assert_called_once_with(
        "valid_dataset"
    )


def test_calculate_daily_consumption():

    controller, analyzer = create_controller()

    controller.calculate_daily_consumption()

    analyzer.statistics_engine.calculate_daily_consumption.assert_called_once_with(
        "valid_dataset"
    )


def test_calculate_monthly_consumption():

    controller, analyzer = create_controller()

    controller.calculate_monthly_consumption()

    analyzer.statistics_engine.calculate_monthly_consumption.assert_called_once_with(
        "valid_dataset"
    )


def test_calculate_yearly_consumption():

    controller, analyzer = create_controller()

    controller.calculate_yearly_consumption()

    analyzer.statistics_engine.calculate_yearly_consumption.assert_called_once_with(
        "valid_dataset"
    )


def test_calculate_calls_steps_in_order():

    controller, _ = create_controller()

    calls = []

    controller.calculate_statistics = MagicMock(
        side_effect=lambda: calls.append("statistics")
    )
    controller.calculate_daily_consumption = MagicMock(
        side_effect=lambda: calls.append("daily")
    )
    controller.calculate_monthly_consumption = MagicMock(
        side_effect=lambda: calls.append("monthly")
    )
    controller.calculate_yearly_consumption = MagicMock(
        side_effect=lambda: calls.append("yearly")
    )

    controller.calculate()

    assert calls == [
        "statistics",
        "daily",
        "monthly",
        "yearly",
    ]

    controller.calculate_statistics.assert_called_once_with()
    controller.calculate_daily_consumption.assert_called_once_with()
    controller.calculate_monthly_consumption.assert_called_once_with()
    controller.calculate_yearly_consumption.assert_called_once_with()

# ==========================================================
# Reports
# ==========================================================


def test_statistics_report():

    controller, analyzer = create_controller()

    analyzer.statistics_engine.statistics = "statistics"

    controller.statistics_report()

    analyzer.statistics_reporter.statistics.assert_called_once_with(
        "statistics"
    )


def test_daily_report():

    controller, analyzer = create_controller()

    analyzer.statistics_engine.daily_consumption = "daily_consumption"

    controller.daily_report()

    analyzer.statistics_reporter.daily.assert_called_once_with(
        "daily_consumption"
    )


def test_monthly_report():

    controller, analyzer = create_controller()

    analyzer.statistics_engine.monthly_consumption = "monthly_consumption"

    controller.monthly_report()

    analyzer.statistics_reporter.monthly.assert_called_once_with(
        "monthly_consumption"
    )


def test_yearly_report():

    controller, analyzer = create_controller()

    analyzer.statistics_engine.yearly_consumption = "yearly_consumption"

    controller.yearly_report()

    analyzer.statistics_reporter.yearly.assert_called_once_with(
        "yearly_consumption"
    )


def test_reports_calls_steps_in_order():

    controller, _ = create_controller()

    controller.statistics_report = MagicMock()
    controller.daily_report = MagicMock()
    controller.monthly_report = MagicMock()
    controller.yearly_report = MagicMock()

    controller.reports()

    assert controller.statistics_report.mock_calls == [
        call()
    ]

    assert controller.daily_report.mock_calls == [
        call()
    ]

    assert controller.monthly_report.mock_calls == [
        call()
    ]

    assert controller.yearly_report.mock_calls == [
        call()
    ]


# ==========================================================
# Propiedades
# ==========================================================


def test_statistics_property():

    controller, analyzer = create_controller()

    analyzer.statistics_engine.statistics = "statistics"

    assert controller.statistics == "statistics"


def test_daily_consumption_property():

    controller, analyzer = create_controller()

    analyzer.statistics_engine.daily_consumption = "daily_consumption"

    assert controller.daily_consumption == "daily_consumption"


def test_monthly_consumption_property():

    controller, analyzer = create_controller()

    analyzer.statistics_engine.monthly_consumption = "monthly_consumption"

    assert controller.monthly_consumption == "monthly_consumption"


def test_yearly_consumption_property():

    controller, analyzer = create_controller()

    analyzer.statistics_engine.yearly_consumption = "yearly_consumption"

    assert controller.yearly_consumption == "yearly_consumption"