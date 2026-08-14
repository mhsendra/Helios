from unittest.mock import MagicMock

from helios.core.controllers.tariffs_controller import (
    TariffsController
)


def create_controller():

    analyzer = MagicMock()

    analyzer.tariff_engine = MagicMock()
    analyzer.tariff_reporter = MagicMock()

    analyzer.valid_dataset.return_value = "valid_dataset"
    analyzer.dataset = "dataset"

    return TariffsController(analyzer), analyzer


# ==========================================================
# Cálculos
# ==========================================================


def test_calculate_tariff_periods():

    controller, analyzer = create_controller()

    controller.calculate_tariff_periods()

    analyzer.tariff_engine.calculate_period_consumption.assert_called_once_with(
        "valid_dataset"
    )

    analyzer.tariff_engine.calculate_period_percentage.assert_called_once_with()


def test_assign_buy_prices():

    controller, analyzer = create_controller()

    controller.assign_buy_prices()

    analyzer.tariff_engine.assign_buy_prices.assert_called_once_with(
        "dataset"
    )


def test_assign_sell_price():

    controller, analyzer = create_controller()

    controller.assign_sell_price()

    analyzer.tariff_engine.assign_sell_price.assert_called_once_with(
        "dataset"
    )


def test_calculate():

    controller, analyzer = create_controller()

    controller.calculate_tariff_periods = MagicMock()
    controller.assign_buy_prices = MagicMock()
    controller.assign_sell_price = MagicMock()

    controller.calculate()

    controller.calculate_tariff_periods.assert_called_once_with()

    analyzer.tariff_engine.assign_tariff_periods.assert_called_once_with(
        "dataset"
    )

    controller.assign_buy_prices.assert_called_once_with()
    controller.assign_sell_price.assert_called_once_with()


# ==========================================================
# Reports
# ==========================================================


def test_tariff_periods_report():

    controller, analyzer = create_controller()

    analyzer.tariff_engine.period_consumption = "period_consumption"
    analyzer.tariff_engine.period_percentage = "period_percentage"
    analyzer.tariff_engine.PERIODS = "periods"

    controller.tariff_periods_report()

    analyzer.tariff_reporter.tariff_periods.assert_called_once_with(
        "period_consumption",
        "period_percentage",
        "periods"
    )


def test_reports():

    controller, _ = create_controller()

    controller.tariff_periods_report = MagicMock()

    controller.reports()

    controller.tariff_periods_report.assert_called_once_with()