from unittest.mock import MagicMock, call

from helios.core.controllers.comparisons_controller import (
    ComparisonsController
)


class TestComparisonsControllerState:

    def setup_method(self):

        self.analyzer = MagicMock()

        self.controller = ComparisonsController(
            self.analyzer
        )

    def test_controller_does_not_store_comparison_state(self):

        assert not hasattr(
            self.controller,
            "monthly_comparison"
        )

        assert not hasattr(
            self.controller,
            "monthly_variation"
        )

        assert not hasattr(
            self.controller,
            "weekly_comparison"
        )

        assert not hasattr(
            self.controller,
            "weekly_variation"
        )

        assert not hasattr(
            self.controller,
            "yearly_comparison"
        )

    def test_calculate_calls_steps_in_order(self):

        engine = self.analyzer.comparisons_engine

        self.controller.calculate()

        assert engine.mock_calls == [
            call.compare_months_by_year(
                self.analyzer.valid_dataset.return_value
            ),
            call.calculate_monthly_variation(),
            call.compare_weeks_by_year(
                self.analyzer.valid_dataset.return_value
            ),
            call.calculate_weekly_variation(),
            call.compare_years(
                self.analyzer.valid_dataset.return_value
            ),
        ]

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

    def test_plots_calls_steps_in_order(self):

        plotter = self.analyzer.plotter

        self.controller.plots()

        assert plotter.mock_calls == [
            call.comparisons.plot_monthly_comparison(
                self.analyzer.comparisons_engine.monthly_comparison
            ),
            call.variations.plot_monthly_variation(
                self.analyzer.comparisons_engine.monthly_variation
            ),
            call.comparisons.plot_weekly_comparison(
                self.analyzer.comparisons_engine.weekly_comparison
            ),
            call.variations.plot_weekly_variation(
                self.analyzer.comparisons_engine.weekly_variation
            ),
            call.comparisons.plot_yearly_comparison(
                self.analyzer.comparisons_engine.yearly_comparison
            ),
        ]
    def test_get_comparisons_returns_engine_state(self):

        engine = self.analyzer.comparisons_engine

        assert (
            self.controller.get_monthly_comparison()
            is engine.monthly_comparison
        )

        assert (
            self.controller.get_monthly_variation()
            is engine.monthly_variation
        )

        assert (
            self.controller.get_weekly_comparison()
            is engine.weekly_comparison
        )

        assert (
            self.controller.get_weekly_variation()
            is engine.weekly_variation
        )

        assert (
            self.controller.get_yearly_comparison()
            is engine.yearly_comparison
        )

    def test_detailed_weekly_insights_delegates_to_engine(self):

        engine = self.analyzer.comparisons_engine

        expected = object()

        engine.detailed_weekly_insights.return_value = expected

        result = self.controller.detailed_weekly_insights()

        engine.detailed_weekly_insights.assert_called_once_with()

        assert result is expected

    def test_weekly_stability_extremes_delegates_to_engine(self):

        engine = self.analyzer.comparisons_engine

        expected = object()

        engine.weekly_stability_extremes.return_value = expected

        result = self.controller.weekly_stability_extremes()

        engine.weekly_stability_extremes.assert_called_once_with()

        assert result is expected

    def test_detect_monthly_anomalies_delegates_to_engine(self):

        engine = self.analyzer.comparisons_engine

        expected = object()

        engine.detect_monthly_anomalies.return_value = expected

        result = self.controller.detect_monthly_anomalies()

        engine.detect_monthly_anomalies.assert_called_once_with()

        assert result is expected

    def test_monthly_stability_extremes_delegates_to_engine(self):

        engine = self.analyzer.comparisons_engine

        expected = object()

        engine.monthly_stability_extremes.return_value = expected

        result = self.controller.monthly_stability_extremes()

        engine.monthly_stability_extremes.assert_called_once_with()

        assert result is expected

    def test_monthly_trends_delegates_to_engine(self):

        engine = self.analyzer.comparisons_engine

        expected = object()

        engine.monthly_trends.return_value = expected

        result = self.controller.monthly_trends()

        engine.monthly_trends.assert_called_once_with()

        assert result is expected

    def test_yearly_trend_delegates_to_engine(self):

        engine = self.analyzer.comparisons_engine

        expected = object()

        engine.yearly_trend.return_value = expected

        result = self.controller.yearly_trend()

        engine.yearly_trend.assert_called_once_with()

        assert result is expected

    def test_annual_stability_delegates_to_engine(self):

        engine = self.analyzer.comparisons_engine

        expected = object()

        engine.annual_stability.return_value = expected

        result = self.controller.annual_stability()

        engine.annual_stability.assert_called_once_with()

        assert result is expected