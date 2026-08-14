from unittest.mock import MagicMock, call

from helios.core.controllers.indicators_controller import (
IndicatorsController
)

class TestIndicatorsControllerState:

    def setup_method(self):

        self.analyzer = MagicMock()

        self.controller = IndicatorsController(
            self.analyzer
        )

    def test_controller_does_not_store_indicator_state(self):

        assert not hasattr(
            self.controller,
            "mean_consumption"
        )

        assert not hasattr(
            self.controller,
            "extremes"
        )

        assert not hasattr(
            self.controller,
            "base_load"
        )

    def test_calculate_calls_steps_in_order(self):

        engine = self.analyzer.indicators_engine

        self.controller.calculate()

        assert engine.mock_calls == [
            call.calculate_mean_consumption(
                self.analyzer.valid_dataset.return_value
            ),
            call.calculate_extremes(
                dataset=self.analyzer.valid_dataset.return_value,
                daily=(
                    self.analyzer.statistics_engine
                    .daily_consumption
                ),
                monthly=(
                    self.analyzer.statistics_engine
                    .monthly_consumption
                ),
                weekly=(
                    self.analyzer.comparisons_engine
                    .weekly_comparison
                )
            ),
            call.calculate_base_load(
                self.analyzer.valid_dataset.return_value
            ),
        ]

    def test_reports_calls_steps_in_order(self):

        reporter = self.analyzer.indicator_reporter

        self.controller.reports()

        assert reporter.mock_calls == [
            call.mean_consumption(
                self.analyzer.indicators_engine.mean_consumption
            ),
            call.extremes(
                self.analyzer.indicators_engine.extremes
            ),
            call.base_load(
                self.analyzer.indicators_engine.base_load
            ),
        ]