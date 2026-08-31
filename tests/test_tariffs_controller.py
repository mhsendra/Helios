from unittest.mock import MagicMock, call

from helios.core.controllers.tariffs_controller import (
    TariffsController
)


class TestTariffsController:

    def setup_method(self):

        self.analyzer = MagicMock()

        self.analyzer.valid_dataset.return_value = (
            "valid_dataset"
        )

        self.analyzer.dataset = "dataset"

        self.controller = TariffsController(
            self.analyzer
        )

    # ==================================================
    # Estado
    # ==================================================

    def test_controller_stores_analyzer(self):

        assert self.controller.analyzer is self.analyzer

    def test_controller_does_not_store_tariff_state(self):

        assert not hasattr(
            self.controller,
            "period_consumption"
        )

        assert not hasattr(
            self.controller,
            "period_percentage"
        )

    # ==================================================
    # Cálculos individuales
    # ==================================================

    def test_calculate_tariff_periods_calls_steps_in_order(
        self
    ):

        engine = self.analyzer.tariff_engine

        self.controller.calculate_tariff_periods()

        assert engine.mock_calls == [
            call.calculate_period_consumption(
                self.analyzer.valid_dataset.return_value
            ),
            call.calculate_period_percentage(),
        ]

    def test_assign_buy_prices_uses_dataset(self):

        self.controller.assign_buy_prices()

        (
            self.analyzer.tariff_engine
            .assign_buy_prices
            .assert_called_once_with(
                self.analyzer.dataset
            )
        )

    def test_assign_sell_price_uses_dataset(self):

        self.controller.assign_sell_price()

        (
            self.analyzer.tariff_engine
            .assign_sell_price
            .assert_called_once_with(
                self.analyzer.dataset
            )
        )

    # ==================================================
    # calculate()
    # ==================================================

    def test_calculate_calls_all_steps_in_order(self):

        engine = self.analyzer.tariff_engine

        self.controller.calculate()

        assert engine.mock_calls == [
            call.calculate_period_consumption(
                self.analyzer.valid_dataset.return_value
            ),
            call.calculate_period_percentage(),
            call.assign_tariff_periods(
                self.analyzer.dataset
            ),
            call.assign_buy_prices(
                self.analyzer.dataset
            ),
            call.assign_sell_price(
                self.analyzer.dataset
            ),
        ]

    # ==================================================
    # Report individual
    # ==================================================

    def test_tariff_periods_report_uses_engine_results(
        self
    ):

        engine = self.analyzer.tariff_engine

        engine.period_consumption = (
            "period_consumption"
        )

        engine.period_percentage = (
            "period_percentage"
        )

        engine.PERIODS = "periods"

        self.controller.tariff_periods_report()

        (
            self.analyzer.tariff_reporter
            .tariff_periods
            .assert_called_once_with(
                engine.period_consumption,
                engine.period_percentage,
                engine.PERIODS
            )
        )

    # ==================================================
    # reports()
    # ==================================================

    def test_reports_calls_tariff_periods_report(self):

        self.controller.reports()

        reporter = self.analyzer.tariff_reporter
        engine = self.analyzer.tariff_engine

        assert reporter.mock_calls == [
            call.tariff_periods(
                engine.period_consumption,
                engine.period_percentage,
                engine.PERIODS
            )
        ]

        # ==================================================
    # Ampliación de cobertura
    # ==================================================

    def test_calculate_tariff_periods_requests_valid_dataset_once(self):

        engine = self.analyzer.tariff_engine

        self.controller.calculate_tariff_periods()

        self.analyzer.valid_dataset.assert_called_once_with()

        engine.calculate_period_consumption.assert_called_once_with(
            self.analyzer.valid_dataset.return_value
        )

        engine.calculate_period_percentage.assert_called_once_with()


    def test_calculate_uses_analyzer_dataset_for_assignments(self):

        engine = self.analyzer.tariff_engine

        self.controller.calculate()

        engine.assign_tariff_periods.assert_called_once_with(
            self.analyzer.dataset
        )

        engine.assign_buy_prices.assert_called_once_with(
            self.analyzer.dataset
        )

        engine.assign_sell_price.assert_called_once_with(
            self.analyzer.dataset
        )


    def test_calculate_does_not_replace_analyzer_dataset(self):

        original_dataset = self.analyzer.dataset

        self.controller.calculate()

        assert self.analyzer.dataset is original_dataset


    def test_assign_buy_prices_does_not_request_valid_dataset(self):

        self.controller.assign_buy_prices()

        self.analyzer.valid_dataset.assert_not_called()

        self.analyzer.tariff_engine.assign_buy_prices.assert_called_once_with(
            self.analyzer.dataset
        )


    def test_assign_sell_price_does_not_request_valid_dataset(self):

        self.controller.assign_sell_price()

        self.analyzer.valid_dataset.assert_not_called()

        self.analyzer.tariff_engine.assign_sell_price.assert_called_once_with(
            self.analyzer.dataset
        )


    def test_tariff_periods_report_does_not_request_dataset(self):

        self.controller.tariff_periods_report()

        self.analyzer.valid_dataset.assert_not_called()
        self.analyzer.tariff_engine.assign_tariff_periods.assert_not_called()
        self.analyzer.tariff_engine.assign_buy_prices.assert_not_called()
        self.analyzer.tariff_engine.assign_sell_price.assert_not_called()


    def test_reports_does_not_calculate(self):

        self.controller.reports()

        engine = self.analyzer.tariff_engine

        engine.calculate_period_consumption.assert_not_called()
        engine.calculate_period_percentage.assert_not_called()
        engine.assign_tariff_periods.assert_not_called()
        engine.assign_buy_prices.assert_not_called()
        engine.assign_sell_price.assert_not_called()


    def test_calculate_tariff_periods_preserves_engine_call_order(self):

        engine = self.analyzer.tariff_engine

        self.controller.calculate_tariff_periods()

        assert engine.mock_calls == [
            call.calculate_period_consumption(
                self.analyzer.valid_dataset.return_value
            ),
            call.calculate_period_percentage(),
        ]