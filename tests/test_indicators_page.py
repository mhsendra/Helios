from unittest.mock import MagicMock

from PySide6.QtWidgets import QApplication

from helios.gui.widgets.indicators_page import IndicatorsPage


class TestIndicatorsPage:

    @classmethod
    def setup_class(cls):

        cls.app = QApplication.instance()

        if cls.app is None:
            cls.app = QApplication([])

    def setup_method(self):

        self.project = MagicMock()
        self.analyzer = self.project.analyzer

        self.page = IndicatorsPage(
            self.project
        )

    # ==================================================
    # Estado inicial
    # ==================================================

    def test_page_stores_project_and_analyzer(self):

        assert self.page.project is self.project
        assert self.page.analyzer is self.analyzer

    def test_kpi_labels_start_with_dash(self):

        labels = [
            self.page.kpi_total_year_label,
            self.page.kpi_avg_month_label,
            self.page.kpi_avg_day_label,
            self.page.kpi_max_day_label,
            self.page.kpi_min_day_label,
            self.page.kpi_stable_month_label,
            self.page.kpi_volatile_month_label,
            self.page.kpi_stable_week_label,
            self.page.kpi_volatile_week_label,
            self.page.kpi_anomaly_count_label,
            self.page.kpi_worst_anomaly_label,
            self.page.kpi_max_anomaly_pct_label,
            self.page.kpi_year_trend_label,
            self.page.kpi_max_increase_label,
            self.page.kpi_max_decrease_label,
        ]

        assert all(
            label.text() == "-"
            for label in labels
        )

    # ==================================================
    # update_data — datos no preparados
    # ==================================================

    def test_update_data_returns_when_daily_consumption_is_missing(self):

        self.analyzer.statistics_engine.daily_consumption = None

        self.page.update_data()

        assert self.page.kpi_total_year_label.text() == "-"

    def test_update_data_returns_when_daily_consumption_is_empty(self):

        self.analyzer.statistics_engine.daily_consumption = []

        self.page.update_data()

        assert self.page.kpi_total_year_label.text() == "-"

    def test_update_data_returns_when_comparisons_are_not_ready(self):

        self.analyzer.statistics_engine.daily_consumption = MagicMock(
            __len__=lambda self: 1
        )

        comparisons = self.analyzer.comparisons

        comparisons.get_weekly_comparison.return_value = None
        comparisons.get_monthly_comparison.return_value = None
        comparisons.get_yearly_comparison.return_value = None

        self.page.update_data()

        assert self.page.kpi_total_year_label.text() == "-"

    # ==================================================
    # update_data — KPIs de consumo
    # ==================================================

    def test_update_data_sets_consumption_kpis(self):

        import pandas as pd

        daily = pd.Series(
            [10.0, 20.0, 30.0],
            index=pd.to_datetime([
                "2025-01-01",
                "2025-01-02",
                "2025-01-03",
            ])
        )

        self.analyzer.statistics_engine.daily_consumption = daily

        comparisons = self.analyzer.comparisons

        comparisons.get_weekly_comparison.return_value = MagicMock()
        comparisons.get_monthly_comparison.return_value = MagicMock()
        comparisons.get_yearly_comparison.return_value = MagicMock()

        comparisons.monthly_stability_extremes.return_value = None
        comparisons.weekly_stability_extremes.return_value = None
        comparisons.detect_monthly_anomalies.return_value = []
        comparisons.yearly_trend.return_value = {
            "classification": "Creciente",
            "positive_steps": 2,
            "negative_steps": 0,
            "max_increase": 20.0,
            "max_decrease": 10.0,
        }

        self.page.update_data()

        assert (
            self.page.kpi_total_year_label.text()
            == "60.00 kWh"
        )

        assert (
            self.page.kpi_avg_day_label.text()
            == "20.00 kWh"
        )

        assert "2025-01-03" in (
            self.page.kpi_max_day_label.text()
        )

        assert "30.00 kWh" in (
            self.page.kpi_max_day_label.text()
        )

        assert "2025-01-01" in (
            self.page.kpi_min_day_label.text()
        )

        assert "10.00 kWh" in (
            self.page.kpi_min_day_label.text()
        )

    # ==================================================
    # update_data — estabilidad
    # ==================================================

    def test_update_data_sets_stability_kpis(self):

        import pandas as pd

        daily = pd.Series(
            [10.0, 20.0],
            index=pd.to_datetime([
                "2025-01-01",
                "2025-01-02",
            ])
        )

        self.analyzer.statistics_engine.daily_consumption = daily

        comparisons = self.analyzer.comparisons

        comparisons.weekly_comparison = MagicMock()
        comparisons.monthly_comparison = MagicMock()
        comparisons.yearly_comparison = MagicMock()

        comparisons.monthly_stability_extremes.return_value = {
            "stable": {
                "month": "Enero",
                "cv": 0.05,
            },
            "volatile": {
                "month": "Julio",
                "cv": 0.42,
            },
        }

        comparisons.weekly_stability_extremes.return_value = {
            "stable": {
                "week": "S03",
                "cv": 0.08,
            },
            "volatile": {
                "week": "S35",
                "cv": 0.51,
            },
        }

        comparisons.detect_monthly_anomalies.return_value = []

        comparisons.yearly_trend.return_value = {
            "classification": "Irregular",
            "positive_steps": 1,
            "negative_steps": 1,
            "max_increase": 20.0,
            "max_decrease": -15.0,
        }

        self.page.update_data()

        assert (
            self.page.kpi_stable_month_label.text()
            == "Enero — CV 0.05"
        )

        assert (
            self.page.kpi_volatile_month_label.text()
            == "Julio — CV 0.42"
        )

        assert (
            self.page.kpi_stable_week_label.text()
            == "S03 — CV 0.08"
        )

        assert (
            self.page.kpi_volatile_week_label.text()
            == "S35 — CV 0.51"
        )

    # ==================================================
    # update_data — anomalías
    # ==================================================

    def test_update_data_without_anomalies(self):

        import pandas as pd

        daily = pd.Series(
            [10.0, 20.0],
            index=pd.to_datetime([
                "2025-01-01",
                "2025-01-02",
            ])
        )

        self.analyzer.statistics_engine.daily_consumption = daily

        comparisons = self.analyzer.comparisons

        comparisons.weekly_comparison = MagicMock()
        comparisons.monthly_comparison = MagicMock()
        comparisons.yearly_comparison = MagicMock()

        comparisons.monthly_stability_extremes.return_value = None
        comparisons.weekly_stability_extremes.return_value = None
        comparisons.detect_monthly_anomalies.return_value = []

        comparisons.yearly_trend.return_value = {
            "classification": "Creciente",
            "positive_steps": 1,
            "negative_steps": 0,
            "max_increase": 20.0,
            "max_decrease": 0.0,
        }

        self.page.update_data()

        assert (
            self.page.kpi_anomaly_count_label.text()
            == "0"
        )

        assert (
            self.page.kpi_worst_anomaly_label.text()
            == "Ninguna"
        )

        assert (
            self.page.kpi_max_anomaly_pct_label.text()
            == "0%"
        )

    def test_update_data_sets_worst_anomaly(self):

        import pandas as pd

        daily = pd.Series(
            [10.0, 20.0],
            index=pd.to_datetime([
                "2025-01-01",
                "2025-01-02",
            ])
        )

        self.analyzer.statistics_engine.daily_consumption = daily

        comparisons = self.analyzer.comparisons

        comparisons.weekly_comparison = MagicMock()
        comparisons.monthly_comparison = MagicMock()
        comparisons.yearly_comparison = MagicMock()

        comparisons.monthly_stability_extremes.return_value = None
        comparisons.weekly_stability_extremes.return_value = None

        comparisons.detect_monthly_anomalies.return_value = [
            {
                "type": "extreme_increase",
                "month": "Enero",
                "year": "2025",
                "value": 80.0,
                "detail": "Aumento extremo (+80.00%)",
            },
            {
                "type": "extreme_decrease",
                "month": "Febrero",
                "year": "2025",
                "value": -40.0,
                "detail": "Caída extrema (-40.00%)",
            },
        ]

        comparisons.yearly_trend.return_value = {
            "classification": "Creciente",
            "positive_steps": 1,
            "negative_steps": 0,
            "max_increase": 20.0,
            "max_decrease": 0.0,
        }

        self.page.update_data()

        assert (
            self.page.kpi_anomaly_count_label.text()
            == "2"
        )

        assert (
            self.page.kpi_worst_anomaly_label.text()
            == "Enero 2025 — Aumento extremo (+80.00%)"
        )

        assert (
            self.page.kpi_max_anomaly_pct_label.text()
            == "80.00%"
        )

    # ==================================================
    # update_data — tendencias
    # ==================================================

    def test_update_data_sets_trend_kpis(self):

        import pandas as pd

        daily = pd.Series(
            [10.0, 20.0],
            index=pd.to_datetime([
                "2025-01-01",
                "2025-01-02",
            ])
        )

        self.analyzer.statistics_engine.daily_consumption = daily

        comparisons = self.analyzer.comparisons

        comparisons.weekly_comparison = MagicMock()
        comparisons.monthly_comparison = MagicMock()
        comparisons.yearly_comparison = MagicMock()

        comparisons.monthly_stability_extremes.return_value = None
        comparisons.weekly_stability_extremes.return_value = None
        comparisons.detect_monthly_anomalies.return_value = []

        comparisons.yearly_trend.return_value = {
            "classification": "Decreciente",
            "positive_steps": 1,
            "negative_steps": 2,
            "max_increase": 25.50,
            "max_decrease": -40.25,
        }

        self.page.update_data()

        assert (
            self.page.kpi_year_trend_label.text()
            == "Decreciente (+1 / -2)"
        )

        assert (
            self.page.kpi_max_increase_label.text()
            == "25.50%"
        )

        assert (
            self.page.kpi_max_decrease_label.text()
            == "-40.25%"
        )