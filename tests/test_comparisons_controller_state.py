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