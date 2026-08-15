from unittest.mock import MagicMock, call

from helios.core.controllers.tariffs_controller import (
    TariffsController
)


class TestTariffsControllerState:

    def setup_method(self):

        self.analyzer = MagicMock()

        self.controller = TariffsController(
            self.analyzer
        )

    def test_controller_does_not_store_tariff_state(self):

        assert not hasattr(
            self.controller,
            "period_consumption"
        )

        assert not hasattr(
            self.controller,
            "period_percentage"
        )

    def test_calculate_tariff_periods_calls_steps_in_order(self):

        engine = self.analyzer.tariff_engine

        self.controller.calculate_tariff_periods()

        assert engine.mock_calls == [
            call.calculate_period_consumption(
                self.analyzer.valid_dataset.return_value
            ),
            call.calculate_period_percentage(),
        ]

    def test_calculate_calls_steps_in_order(self):

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

    def test_reports_calls_steps_in_order(self):

        reporter = self.analyzer.tariff_reporter
        engine = self.analyzer.tariff_engine

        self.controller.reports()

        assert reporter.mock_calls == [
            call.tariff_periods(
                engine.period_consumption,
                engine.period_percentage,
                engine.PERIODS
            )
        ]