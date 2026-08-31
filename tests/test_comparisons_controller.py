from unittest.mock import MagicMock, call

import pytest

from helios.core.controllers.comparisons_controller import (
    ComparisonsController,
)


class TestComparisonsController:

    def setup_method(self):

        self.analyzer = MagicMock()

        self.controller = ComparisonsController(
            self.analyzer
        )

    # ==================================================
    # Cálculos
    # ==================================================

    def test_compare_months_by_year(self):

        dataset = self.analyzer.valid_dataset.return_value

        self.controller.compare_months_by_year()

        self.analyzer.comparisons_engine.compare_months_by_year.assert_called_once_with(
            dataset
        )

    def test_calculate_monthly_variation(self):

        self.controller.calculate_monthly_variation()

        self.analyzer.comparisons_engine.calculate_monthly_variation.assert_called_once_with()

    def test_compare_weeks_by_year(self):

        dataset = self.analyzer.valid_dataset.return_value

        self.controller.compare_weeks_by_year()

        self.analyzer.comparisons_engine.compare_weeks_by_year.assert_called_once_with(
            dataset
        )

    def test_calculate_weekly_variation(self):

        self.controller.calculate_weekly_variation()

        self.analyzer.comparisons_engine.calculate_weekly_variation.assert_called_once_with()

    def test_compare_years(self):

        dataset = self.analyzer.valid_dataset.return_value

        self.controller.compare_years()

        self.analyzer.comparisons_engine.compare_years.assert_called_once_with(
            dataset
        )

    def test_calculate_calls_steps_in_order(self):

        engine = self.analyzer.comparisons_engine
        dataset = self.analyzer.valid_dataset.return_value

        self.controller.calculate()

        assert engine.mock_calls == [
            call.compare_months_by_year(dataset),
            call.calculate_monthly_variation(),
            call.compare_weeks_by_year(dataset),
            call.calculate_weekly_variation(),
            call.compare_years(dataset),
        ]

    # ==================================================
    # Reports
    # ==================================================

    def test_monthly_comparison_report(self):

        engine = self.analyzer.comparisons_engine
        value = MagicMock()

        engine.monthly_comparison = value

        self.controller.monthly_comparison_report()

        engine.monthly_comparison_report.assert_called_once_with(
            value
        )

    def test_monthly_variation_report(self):

        engine = self.analyzer.comparisons_engine
        value = MagicMock()

        engine.monthly_variation = value

        self.controller.monthly_variation_report()

        engine.monthly_variation_report.assert_called_once_with(
            value
        )

    def test_weekly_comparison_report(self):

        engine = self.analyzer.comparisons_engine
        value = MagicMock()

        engine.weekly_comparison = value

        self.controller.weekly_comparison_report()

        engine.weekly_comparison_report.assert_called_once_with(
            value
        )

    def test_weekly_variation_report(self):

        engine = self.analyzer.comparisons_engine
        value = MagicMock()

        engine.weekly_variation = value

        self.controller.weekly_variation_report()

        engine.weekly_variation_report.assert_called_once_with(
            value
        )

    def test_yearly_comparison_report(self):

        engine = self.analyzer.comparisons_engine
        value = MagicMock()

        engine.yearly_comparison = value

        self.controller.yearly_comparison_report()

        engine.yearly_comparison_report.assert_called_once_with(
            value
        )

    def test_reports_calls_steps_in_order(self):

        engine = self.analyzer.comparisons_engine

        self.controller.reports()

        assert engine.mock_calls == [
            call.monthly_comparison_report(
                engine.monthly_comparison
            ),
            call.monthly_variation_report(
                engine.monthly_variation
            ),
            call.weekly_comparison_report(
                engine.weekly_comparison
            ),
            call.weekly_variation_report(
                engine.weekly_variation
            ),
            call.yearly_comparison_report(
                engine.yearly_comparison
            ),
        ]

    # ==================================================
    # Gráficas
    # ==================================================

    def test_plot_monthly_comparison(self):

        engine = self.analyzer.comparisons_engine
        plots = self.analyzer.plotter.comparisons
        value = MagicMock()

        engine.monthly_comparison = value

        self.controller.plot_monthly_comparison()

        plots.plot_monthly_comparison.assert_called_once_with(
            value
        )

    def test_plot_monthly_variation(self):

        engine = self.analyzer.comparisons_engine
        plots = self.analyzer.plotter.variations
        value = MagicMock()

        engine.monthly_variation = value

        self.controller.plot_monthly_variation()

        plots.plot_monthly_variation.assert_called_once_with(
            value
        )

    def test_plot_weekly_comparison(self):

        engine = self.analyzer.comparisons_engine
        plots = self.analyzer.plotter.comparisons
        value = MagicMock()

        engine.weekly_comparison = value

        self.controller.plot_weekly_comparison()

        plots.plot_weekly_comparison.assert_called_once_with(
            value
        )

    def test_plot_weekly_variation(self):

        engine = self.analyzer.comparisons_engine
        plots = self.analyzer.plotter.variations
        value = MagicMock()

        engine.weekly_variation = value

        self.controller.plot_weekly_variation()

        plots.plot_weekly_variation.assert_called_once_with(
            value
        )

    def test_plot_yearly_comparison(self):

        engine = self.analyzer.comparisons_engine
        plots = self.analyzer.plotter.comparisons
        value = MagicMock()

        engine.yearly_comparison = value

        self.controller.plot_yearly_comparison()

        plots.plot_yearly_comparison.assert_called_once_with(
            value
        )

    def test_plots_calls_steps_in_order(self):

        engine = self.analyzer.comparisons_engine
        comparison_plots = self.analyzer.plotter.comparisons
        variation_plots = self.analyzer.plotter.variations

        self.controller.plots()

        assert comparison_plots.mock_calls == [
            call.plot_monthly_comparison(
                engine.monthly_comparison
            ),
            call.plot_weekly_comparison(
                engine.weekly_comparison
            ),
            call.plot_yearly_comparison(
                engine.yearly_comparison
            ),
        ]

        assert variation_plots.mock_calls == [
            call.plot_monthly_variation(
                engine.monthly_variation
            ),
            call.plot_weekly_variation(
                engine.weekly_variation
            ),
        ]

    # ==================================================
    # Insights
    # ==================================================

    def test_detailed_weekly_insights(self):

        expected = MagicMock()

        self.analyzer.comparisons_engine.detailed_weekly_insights.return_value = (
            expected
        )

        result = self.controller.detailed_weekly_insights()

        assert result is expected

    def test_weekly_stability_extremes(self):

        expected = MagicMock()

        self.analyzer.comparisons_engine.weekly_stability_extremes.return_value = (
            expected
        )

        result = self.controller.weekly_stability_extremes()

        assert result is expected

    def test_detect_monthly_anomalies(self):

        expected = MagicMock()

        self.analyzer.comparisons_engine.detect_monthly_anomalies.return_value = (
            expected
        )

        result = self.controller.detect_monthly_anomalies()

        assert result is expected

    def test_monthly_stability_extremes(self):

        expected = MagicMock()

        self.analyzer.comparisons_engine.monthly_stability_extremes.return_value = (
            expected
        )

        result = self.controller.monthly_stability_extremes()

        assert result is expected

    def test_monthly_trends(self):

        expected = MagicMock()

        self.analyzer.comparisons_engine.monthly_trends.return_value = (
            expected
        )

        result = self.controller.monthly_trends()

        assert result is expected

    def test_yearly_trend(self):

        expected = MagicMock()

        self.analyzer.comparisons_engine.yearly_trend.return_value = (
            expected
        )

        result = self.controller.yearly_trend()

        assert result is expected

    def test_annual_stability(self):

        expected = MagicMock()

        self.analyzer.comparisons_engine.annual_stability.return_value = (
            expected
        )

        result = self.controller.annual_stability()

        assert result is expected

    # ==================================================
    # Getters
    # ==================================================

    def test_get_monthly_comparison(self):

        value = MagicMock()

        self.analyzer.comparisons_engine.monthly_comparison = value

        assert (
            self.controller.get_monthly_comparison()
            is value
        )

    def test_get_monthly_variation(self):

        value = MagicMock()

        self.analyzer.comparisons_engine.monthly_variation = value

        assert (
            self.controller.get_monthly_variation()
            is value
        )

    def test_get_weekly_comparison(self):

        value = MagicMock()

        self.analyzer.comparisons_engine.weekly_comparison = value

        assert (
            self.controller.get_weekly_comparison()
            is value
        )

    def test_get_weekly_variation(self):

        value = MagicMock()

        self.analyzer.comparisons_engine.weekly_variation = value

        assert (
            self.controller.get_weekly_variation()
            is value
        )

    def test_get_yearly_comparison(self):

        value = MagicMock()

        self.analyzer.comparisons_engine.yearly_comparison = value

        assert (
            self.controller.get_yearly_comparison()
            is value
        )

    # ==================================================
    # Validación de delegación y comportamiento
    # ==================================================

    def test_compare_months_by_year_uses_valid_dataset_once(self):

        dataset = object()

        self.analyzer.valid_dataset.return_value = dataset

        self.controller.compare_months_by_year()

        self.analyzer.valid_dataset.assert_called_once_with()

        self.analyzer.comparisons_engine.compare_months_by_year.assert_called_once_with(
            dataset
        )


    def test_compare_weeks_by_year_uses_valid_dataset_once(self):

        dataset = object()

        self.analyzer.valid_dataset.return_value = dataset

        self.controller.compare_weeks_by_year()

        self.analyzer.valid_dataset.assert_called_once_with()

        self.analyzer.comparisons_engine.compare_weeks_by_year.assert_called_once_with(
            dataset
        )


    def test_compare_years_uses_valid_dataset_once(self):

        dataset = object()

        self.analyzer.valid_dataset.return_value = dataset

        self.controller.compare_years()

        self.analyzer.valid_dataset.assert_called_once_with()

        self.analyzer.comparisons_engine.compare_years.assert_called_once_with(
            dataset
        )


    def test_calculate_monthly_variation_does_not_request_dataset(self):

        self.controller.calculate_monthly_variation()

        self.analyzer.valid_dataset.assert_not_called()

        self.analyzer.comparisons_engine.calculate_monthly_variation.assert_called_once_with()


    def test_calculate_weekly_variation_does_not_request_dataset(self):

        self.controller.calculate_weekly_variation()

        self.analyzer.valid_dataset.assert_not_called()

        self.analyzer.comparisons_engine.calculate_weekly_variation.assert_called_once_with()


    def test_calculate_requests_valid_dataset_for_each_comparison(self):

        dataset = object()

        self.analyzer.valid_dataset.return_value = dataset

        self.controller.calculate()

        assert self.analyzer.valid_dataset.call_count == 3

        self.analyzer.comparisons_engine.compare_months_by_year.assert_called_once_with(
            dataset
        )

        self.analyzer.comparisons_engine.compare_weeks_by_year.assert_called_once_with(
            dataset
        )

        self.analyzer.comparisons_engine.compare_years.assert_called_once_with(
            dataset
        )


    def test_calculate_stops_when_monthly_comparison_fails(self):

        error = RuntimeError(
            "monthly comparison failed"
        )

        engine = self.analyzer.comparisons_engine

        engine.compare_months_by_year.side_effect = error

        with pytest.raises(
            RuntimeError,
            match="monthly comparison failed",
        ):
            self.controller.calculate()

        engine.compare_months_by_year.assert_called_once_with(
            self.analyzer.valid_dataset.return_value
        )

        engine.calculate_monthly_variation.assert_not_called()
        engine.compare_weeks_by_year.assert_not_called()
        engine.calculate_weekly_variation.assert_not_called()
        engine.compare_years.assert_not_called()


    def test_calculate_stops_when_monthly_variation_fails(self):

        error = RuntimeError(
            "monthly variation failed"
        )

        engine = self.analyzer.comparisons_engine

        engine.calculate_monthly_variation.side_effect = error

        with pytest.raises(
            RuntimeError,
            match="monthly variation failed",
        ):
            self.controller.calculate()

        engine.compare_months_by_year.assert_called_once_with(
            self.analyzer.valid_dataset.return_value
        )

        engine.calculate_monthly_variation.assert_called_once_with()

        engine.compare_weeks_by_year.assert_not_called()
        engine.calculate_weekly_variation.assert_not_called()
        engine.compare_years.assert_not_called()


    def test_reports_does_not_request_valid_dataset(self):

        self.controller.reports()

        self.analyzer.valid_dataset.assert_not_called()


    def test_plots_does_not_request_valid_dataset(self):

        self.controller.plots()

        self.analyzer.valid_dataset.assert_not_called()


    def test_insight_methods_return_exact_engine_result(self):

        engine = self.analyzer.comparisons_engine

        weekly_insights = object()
        weekly_extremes = object()
        monthly_anomalies = object()
        monthly_extremes = object()
        monthly_trends = object()
        yearly_trend = object()
        annual_stability = object()

        engine.detailed_weekly_insights.return_value = (
            weekly_insights
        )

        engine.weekly_stability_extremes.return_value = (
            weekly_extremes
        )

        engine.detect_monthly_anomalies.return_value = (
            monthly_anomalies
        )

        engine.monthly_stability_extremes.return_value = (
            monthly_extremes
        )

        engine.monthly_trends.return_value = (
            monthly_trends
        )

        engine.yearly_trend.return_value = (
            yearly_trend
        )

        engine.annual_stability.return_value = (
            annual_stability
        )

        assert (
            self.controller.detailed_weekly_insights()
            is weekly_insights
        )

        assert (
            self.controller.weekly_stability_extremes()
            is weekly_extremes
        )

        assert (
            self.controller.detect_monthly_anomalies()
            is monthly_anomalies
        )

        assert (
            self.controller.monthly_stability_extremes()
            is monthly_extremes
        )

        assert (
            self.controller.monthly_trends()
            is monthly_trends
        )

        assert (
            self.controller.yearly_trend()
            is yearly_trend
        )

        assert (
            self.controller.annual_stability()
            is annual_stability
        )


    def test_getters_return_current_engine_state(self):

        engine = self.analyzer.comparisons_engine

        monthly_comparison = object()
        monthly_variation = object()
        weekly_comparison = object()
        weekly_variation = object()
        yearly_comparison = object()

        engine.monthly_comparison = monthly_comparison
        engine.monthly_variation = monthly_variation
        engine.weekly_comparison = weekly_comparison
        engine.weekly_variation = weekly_variation
        engine.yearly_comparison = yearly_comparison

        assert (
            self.controller.get_monthly_comparison()
            is monthly_comparison
        )

        assert (
            self.controller.get_monthly_variation()
            is monthly_variation
        )

        assert (
            self.controller.get_weekly_comparison()
            is weekly_comparison
        )

        assert (
            self.controller.get_weekly_variation()
            is weekly_variation
        )

        assert (
            self.controller.get_yearly_comparison()
            is yearly_comparison
        )