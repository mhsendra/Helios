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
                    self.analyzer.comparisons_controller
                    .get_weekly_comparison.return_value
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

    # ==========================================================
# Cálculos individuales
# ==========================================================

    def test_calculate_mean_consumption(self):

        self.controller.calculate_mean_consumption()

        self.analyzer.indicators_engine.calculate_mean_consumption.assert_called_once_with(
            self.analyzer.valid_dataset.return_value
        )


    def test_calculate_extremes(self):

        self.controller.calculate_extremes()

        self.analyzer.indicators_engine.calculate_extremes.assert_called_once_with(
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
                self.analyzer.comparisons_controller
                .get_weekly_comparison.return_value
            )
        )


    def test_calculate_base_load(self):

        self.controller.calculate_base_load()

        self.analyzer.indicators_engine.calculate_base_load.assert_called_once_with(
            self.analyzer.valid_dataset.return_value
        )


# ==========================================================
# Reportes individuales
# ==========================================================

    def test_mean_consumption_report(self):

        self.controller.mean_consumption_report()

        self.analyzer.indicator_reporter.mean_consumption.assert_called_once_with(
            self.analyzer.indicators_engine.mean_consumption
        )


    def test_extremes_report(self):

        self.controller.extremes_report()

        self.analyzer.indicator_reporter.extremes.assert_called_once_with(
            self.analyzer.indicators_engine.extremes
        )


    def test_base_load_report(self):

        self.controller.base_load_report()

        self.analyzer.indicator_reporter.base_load.assert_called_once_with(
            self.analyzer.indicators_engine.base_load
        )