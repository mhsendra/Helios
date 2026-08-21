from unittest.mock import MagicMock, call

from helios.core.controllers.indicators_controller import (
    IndicatorsController,
)


class TestIndicatorsControllerState:

    def setup_method(self):

        self.analyzer = MagicMock()

        self.controller = IndicatorsController(
            self.analyzer
        )

    # ==================================================
    # Estado
    # ==================================================

    def test_controller_does_not_store_indicator_state(self):

        assert not hasattr(
            self.controller,
            "mean_consumption",
        )

        assert not hasattr(
            self.controller,
            "extremes",
        )

        assert not hasattr(
            self.controller,
            "base_load",
        )

    # ==================================================
    # Cálculos individuales
    # ==================================================

    def test_calculate_mean_consumption(self):

        dataset = MagicMock()

        self.analyzer.valid_dataset.return_value = dataset

        self.controller.calculate_mean_consumption()

        self.analyzer.valid_dataset.assert_called_once_with()

        self.analyzer.indicators_engine.calculate_mean_consumption.assert_called_once_with(
            dataset
        )

    def test_calculate_extremes(self):

        dataset = MagicMock()
        daily = MagicMock()
        monthly = MagicMock()
        weekly = MagicMock()

        self.analyzer.valid_dataset.return_value = dataset
        self.analyzer.statistics_engine.daily_consumption = daily
        self.analyzer.statistics_engine.monthly_consumption = monthly
        self.analyzer.comparisons.get_weekly_comparison.return_value = weekly

        self.controller.calculate_extremes()

        self.analyzer.valid_dataset.assert_called_once_with()

        self.analyzer.comparisons.get_weekly_comparison.assert_called_once_with()

        self.analyzer.indicators_engine.calculate_extremes.assert_called_once_with(
            dataset=dataset,
            daily=daily,
            monthly=monthly,
            weekly=weekly,
        )

    def test_calculate_base_load(self):

        dataset = MagicMock()

        self.analyzer.valid_dataset.return_value = dataset

        self.controller.calculate_base_load()

        self.analyzer.valid_dataset.assert_called_once_with()

        self.analyzer.indicators_engine.calculate_base_load.assert_called_once_with(
            dataset
        )

    # ==================================================
    # Calculate completo
    # ==================================================

    def test_calculate_calls_steps_in_order(self):

        dataset = MagicMock()
        daily = MagicMock()
        monthly = MagicMock()
        weekly = MagicMock()

        self.analyzer.valid_dataset.return_value = dataset
        self.analyzer.statistics_engine.daily_consumption = daily
        self.analyzer.statistics_engine.monthly_consumption = monthly
        self.analyzer.comparisons.get_weekly_comparison.return_value = weekly

        engine = self.analyzer.indicators_engine

        self.controller.calculate()

        assert engine.mock_calls == [
            call.calculate_mean_consumption(
                dataset
            ),
            call.calculate_extremes(
                dataset=dataset,
                daily=daily,
                monthly=monthly,
                weekly=weekly,
            ),
            call.calculate_base_load(
                dataset
            ),
        ]

    # ==================================================
    # Reportes individuales
    # ==================================================

    def test_mean_consumption_report(self):

        value = MagicMock()

        self.analyzer.indicators_engine.mean_consumption = value

        self.controller.mean_consumption_report()

        self.analyzer.indicator_reporter.mean_consumption.assert_called_once_with(
            value
        )

    def test_extremes_report(self):

        value = MagicMock()

        self.analyzer.indicators_engine.extremes = value

        self.controller.extremes_report()

        self.analyzer.indicator_reporter.extremes.assert_called_once_with(
            value
        )

    def test_base_load_report(self):

        value = MagicMock()

        self.analyzer.indicators_engine.base_load = value

        self.controller.base_load_report()

        self.analyzer.indicator_reporter.base_load.assert_called_once_with(
            value
        )

    # ==================================================
    # Reports completo
    # ==================================================

    def test_reports_calls_steps_in_order(self):

        reporter = self.analyzer.indicator_reporter
        engine = self.analyzer.indicators_engine

        mean = MagicMock()
        extremes = MagicMock()
        base_load = MagicMock()

        engine.mean_consumption = mean
        engine.extremes = extremes
        engine.base_load = base_load

        self.controller.reports()

        assert reporter.mock_calls == [
            call.mean_consumption(mean),
            call.extremes(extremes),
            call.base_load(base_load),
        ]

    def test_reports_does_not_calculate(self):

        self.controller.reports()

        self.analyzer.indicators_engine.calculate_mean_consumption.assert_not_called()
        self.analyzer.indicators_engine.calculate_extremes.assert_not_called()
        self.analyzer.indicators_engine.calculate_base_load.assert_not_called()