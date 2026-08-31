from unittest.mock import MagicMock, call

import pytest

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

class TestIndicatorsController:

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

    # ==================================================
    # Ampliación de cobertura
    # ==================================================

    def test_calculate_mean_consumption_uses_valid_dataset(self):

        dataset = object()

        self.analyzer.valid_dataset.return_value = dataset

        self.controller.calculate_mean_consumption()

        self.analyzer.valid_dataset.assert_called_once_with()

        self.analyzer.indicators_engine.calculate_mean_consumption.assert_called_once_with(
            dataset
        )

    def test_calculate_extremes_uses_required_sources(self):

        dataset = object()
        daily = object()
        monthly = object()
        weekly = object()

        self.analyzer.valid_dataset.return_value = dataset

        self.analyzer.statistics_engine.daily_consumption = daily
        self.analyzer.statistics_engine.monthly_consumption = monthly

        self.analyzer.comparisons.get_weekly_comparison.return_value = weekly

        engine = self.analyzer.indicators_engine

        self.controller.calculate_extremes()

        self.analyzer.valid_dataset.assert_called_once_with()

        self.analyzer.comparisons.get_weekly_comparison.assert_called_once_with()

        engine.calculate_extremes.assert_called_once_with(
            dataset=dataset,
            daily=daily,
            monthly=monthly,
            weekly=weekly,
        )

    def test_calculate_base_load_uses_valid_dataset(self):

        dataset = object()

        self.analyzer.valid_dataset.return_value = dataset

        self.controller.calculate_base_load()

        self.analyzer.valid_dataset.assert_called_once_with()

        self.analyzer.indicators_engine.calculate_base_load.assert_called_once_with(
            dataset
        )

    def test_calculate_calls_all_indicator_steps_in_order(self):

        dataset = object()
        daily = object()
        monthly = object()
        weekly = object()

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
    # Excepciones durante el cálculo
    # ==================================================

    def test_calculate_propagates_mean_consumption_exception(self):

        dataset = object()

        self.analyzer.valid_dataset.return_value = dataset

        error = RuntimeError(
            "mean consumption failed"
        )

        engine = self.analyzer.indicators_engine

        engine.calculate_mean_consumption.side_effect = error

        with pytest.raises(
            RuntimeError,
            match="mean consumption failed",
        ):
            self.controller.calculate()

        engine.calculate_extremes.assert_not_called()

        engine.calculate_base_load.assert_not_called()

    def test_calculate_stops_when_extremes_fail(self):

        dataset = object()

        self.analyzer.valid_dataset.return_value = dataset

        error = RuntimeError(
            "extremes failed"
        )

        engine = self.analyzer.indicators_engine

        engine.calculate_extremes.side_effect = error

        with pytest.raises(
            RuntimeError,
            match="extremes failed",
        ):
            self.controller.calculate()

        engine.calculate_mean_consumption.assert_called_once_with(
            dataset
        )

        engine.calculate_base_load.assert_not_called()

    def test_calculate_propagates_base_load_exception(self):

        dataset = object()
        daily = object()
        monthly = object()
        weekly = object()

        self.analyzer.valid_dataset.return_value = dataset

        self.analyzer.statistics_engine.daily_consumption = daily
        self.analyzer.statistics_engine.monthly_consumption = monthly

        self.analyzer.comparisons.get_weekly_comparison.return_value = weekly

        error = RuntimeError(
            "base load failed"
        )

        engine = self.analyzer.indicators_engine

        engine.calculate_base_load.side_effect = error

        with pytest.raises(
            RuntimeError,
            match="base load failed",
        ):
            self.controller.calculate()

        engine.calculate_mean_consumption.assert_called_once_with(
            dataset
        )

        engine.calculate_extremes.assert_called_once_with(
            dataset=dataset,
            daily=daily,
            monthly=monthly,
            weekly=weekly,
        )

        engine.calculate_base_load.assert_called_once_with(
            dataset
        )

    # ==================================================
    # Reports delegados al engine
    # ==================================================

    def test_reports_calls_all_reports_in_order(self):

        reporter = self.analyzer.indicator_reporter

        engine = self.analyzer.indicators_engine

        mean = object()
        extremes = object()
        base_load = object()

        engine.mean_consumption = mean
        engine.extremes = extremes
        engine.base_load = base_load

        self.controller.reports()

        assert reporter.mock_calls == [
            call.mean_consumption(mean),
            call.extremes(extremes),
            call.base_load(base_load),
        ]

    def test_mean_consumption_report_delegates_to_reporter(self):

        value = object()

        reporter = self.analyzer.indicator_reporter

        self.analyzer.indicators_engine.mean_consumption = value

        self.controller.mean_consumption_report()

        reporter.mean_consumption.assert_called_once_with(
            value
        )


    def test_extremes_report_delegates_to_reporter(self):

        value = object()

        reporter = self.analyzer.indicator_reporter

        self.analyzer.indicators_engine.extremes = value

        self.controller.extremes_report()

        reporter.extremes.assert_called_once_with(
            value
        )


    def test_base_load_report_delegates_to_reporter(self):

        value = object()

        reporter = self.analyzer.indicator_reporter

        self.analyzer.indicators_engine.base_load = value

        self.controller.base_load_report()

        reporter.base_load.assert_called_once_with(
            value
        )


    def test_controller_does_not_expose_engine_state_as_properties(self):

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