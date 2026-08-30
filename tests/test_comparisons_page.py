from unittest.mock import MagicMock

import pandas as pd

import pytest 
from PySide6.QtWidgets import QApplication

from helios.gui.widgets.comparisons_page import ComparisonsPage


class TestComparisonsPage:

    @classmethod
    def setup_class(cls):

        cls.app = QApplication.instance()

        if cls.app is None:
            cls.app = QApplication([])

    def setup_method(self):

        self.project = MagicMock()
        self.analyzer = self.project.analyzer

        self.page = ComparisonsPage(
            self.project
        )

    # ==================================================
    # Estado inicial
    # ==================================================

    def test_page_stores_project_and_analyzer(self):

        assert self.page.project is self.project
        assert self.page.analyzer is self.analyzer

    def test_page_has_five_tabs(self):

        assert self.page.tabs.count() == 5

        assert self.page.tabs.tabText(0) == "Resumen"
        assert self.page.tabs.tabText(1) == "Semanal"
        assert self.page.tabs.tabText(2) == "Mensual"
        assert self.page.tabs.tabText(3) == "Anual"
        assert self.page.tabs.tabText(4) == "Insights"

    def test_labels_start_with_dash(self):

        labels = [
            self.page.summary_year_max_label,
            self.page.summary_year_min_label,
            self.page.summary_stable_month_label,
            self.page.summary_volatile_month_label,
            self.page.summary_stable_week_label,
            self.page.summary_volatile_week_label,
            self.page.summary_anomalies_label,

            self.page.week_max_label,
            self.page.week_min_label,
            self.page.week_peak_label,
            self.page.week_valley_label,
            self.page.most_stable_week_label,
            self.page.most_volatile_week_label,

            self.page.month_max_label,
            self.page.month_min_label,
            self.page.anomalies_label,
            self.page.most_stable_month_label,
            self.page.most_volatile_month_label,

            self.page.year_max_label,
            self.page.year_min_label,
            self.page.trend_2024_label,
            self.page.trend_2025_label,
            self.page.trend_2026_label,
            self.page.stab_2024_label,
            self.page.stab_2025_label,
            self.page.stab_2026_label,

            self.page.insights_text_label,
        ]

        assert all(
            label.text() == "-"
            for label in labels
        )

    # ==================================================
    # update_data — datos no preparados
    # ==================================================

    def test_update_data_returns_when_comparisons_are_not_available(self):

        self.project.comparisons = None

        with pytest.raises(AttributeError):
            self.page.update_data()

    def test_update_data_returns_when_weekly_is_missing(self):

        comparisons = self.project.comparisons

        comparisons.get_weekly_comparison.return_value = None
        comparisons.get_monthly_comparison.return_value = (
            pd.DataFrame()
        )
        comparisons.get_yearly_comparison.return_value = (
            pd.Series(dtype=float)
        )

        self.page.update_data()

        assert self.page.week_max_label.text() == "-"

    def test_update_data_returns_when_monthly_is_missing(self):

        comparisons = self.project.comparisons

        comparisons.get_weekly_comparison.return_value = (
            pd.DataFrame()
        )
        comparisons.get_monthly_comparison.return_value = None
        comparisons.get_yearly_comparison.return_value = (
            pd.Series(dtype=float)
        )

        self.page.update_data()

        assert self.page.month_max_label.text() == "-"

    def test_update_data_returns_when_yearly_is_missing(self):

        comparisons = self.project.comparisons

        comparisons.get_weekly_comparison.return_value = (
            pd.DataFrame()
        )
        comparisons.get_monthly_comparison.return_value = (
            pd.DataFrame()
        )
        comparisons.get_yearly_comparison.return_value = None

        self.page.update_data()

        assert self.page.year_max_label.text() == "-"

    # ==================================================
    # Fixture común para update_data
    # ==================================================

    def _prepare_comparisons(self):

        comparisons = self.project.comparisons

        weekly = pd.DataFrame(
            {
                2024: [100.0, 200.0, 300.0],
                2025: [150.0, 250.0, 350.0],
            },
            index=[1, 2, 3],
        )

        monthly = pd.DataFrame(
            {
                2024: [1000.0, 2000.0, 3000.0],
                2025: [1500.0, 2500.0, 3500.0],
            },
            index=[1, 2, 3],
        )

        yearly = pd.Series(
            {
                2024: 10000.0,
                2025: 15000.0,
                2026: 12000.0,
            }
        )

        comparisons.get_weekly_comparison.return_value = weekly
        comparisons.get_monthly_comparison.return_value = monthly
        comparisons.get_yearly_comparison.return_value = yearly

        comparisons.detailed_weekly_insights.return_value = {
            "max": {
                "week": 3,
                "year": 2025,
                "value": 350.0,
                "variation_prev": 10.0,
                "variation_mean": 20.0,
            },
            "min": {
                "week": 1,
                "year": 2024,
                "value": 100.0,
            },
        }

        comparisons.weekly_stability_extremes.return_value = {
            "stable": {
                "week": "S01",
                "cv": 0.05,
                "std": 2.50,
                "classification": "Estable",
            },
            "volatile": {
                "week": "S35",
                "cv": 0.50,
                "std": 20.00,
                "classification": "Volátil",
            },
        }

        comparisons.detect_monthly_anomalies.return_value = [
            {
                "month": "Enero",
                "year": 2025,
                "detail": "Aumento extremo (+80.00%)",
            },
            {
                "month": "Febrero",
                "year": 2025,
                "detail": "Caída extrema (-40.00%)",
            },
        ]

        comparisons.monthly_stability_extremes.return_value = {
            "stable": {
                "month": "Marzo",
                "cv": 0.04,
                "std": 3.00,
                "classification": "Estable",
            },
            "volatile": {
                "month": "Julio",
                "cv": 0.45,
                "std": 25.00,
                "classification": "Volátil",
            },
        }

        comparisons.monthly_trends.return_value = {
            2024: {
                "classification": "Creciente",
                "positive_steps": 2,
                "negative_steps": 0,
                "max_increase": 30.0,
                "max_decrease": 0.0,
            },
            2025: {
                "classification": "Decreciente",
                "positive_steps": 1,
                "negative_steps": 2,
                "max_increase": 15.0,
                "max_decrease": -20.0,
            },
            2026: {
                "classification": "Irregular",
                "positive_steps": 1,
                "negative_steps": 1,
                "max_increase": 10.0,
                "max_decrease": -12.0,
            },
        }

        comparisons.yearly_trend.return_value = {
            "classification": "Creciente",
            "positive_steps": 2,
            "negative_steps": 1,
            "max_increase": 25.0,
            "max_decrease": -10.0,
        }

        comparisons.annual_stability.return_value = {
            2024: {
                "classification": "Estable",
                "range": 100.0,
                "std": 10.0,
                "cv": 0.10,
            },
            2025: {
                "classification": "Volátil",
                "range": 500.0,
                "std": 50.0,
                "cv": 0.30,
            },
            2026: {
                "classification": "Irregular",
                "range": 300.0,
                "std": 30.0,
                "cv": 0.20,
            },
        }

        return comparisons

    # ==================================================
    # Semanal
    # ==================================================

    def test_update_data_sets_weekly_comparison(self):

        self._prepare_comparisons()

        self.page.update_data()

        assert self.page.week_max_label.text() == (
            "Semana 3 del año 2025"
        )

        assert self.page.week_min_label.text() == (
            "Semana 1 del año 2024"
        )

    def test_update_data_sets_weekly_insights(self):

        self._prepare_comparisons()

        self.page.update_data()

        assert "Semana 3 del 2025" in (
            self.page.week_peak_label.text()
        )

        assert "350.00 kWh" in (
            self.page.week_peak_label.text()
        )

        assert "+10.00% vs año anterior" in (
            self.page.week_peak_label.text()
        )

        assert "+20.00% vs media anual" in (
            self.page.week_peak_label.text()
        )

        assert self.page.week_valley_label.text() == (
            "Semana 1 del 2024 — 100.00 kWh"
        )

    def test_update_data_weekly_insight_without_previous_year(self):

        comparisons = self._prepare_comparisons()

        comparisons.detailed_weekly_insights.return_value["max"][
            "variation_prev"
        ] = None

        self.page.update_data()

        assert "sin año anterior para comparar" in (
            self.page.week_peak_label.text()
        )

    def test_update_data_sets_weekly_stability(self):

        self._prepare_comparisons()

        self.page.update_data()

        assert self.page.most_stable_week_label.text() == (
            "S01 — CV 0.05, Desv. 2.50 (Estable)"
        )

        assert self.page.most_volatile_week_label.text() == (
            "S35 — CV 0.50, Desv. 20.00 (Volátil)"
        )

    # ==================================================
    # Mensual
    # ==================================================

    def test_update_data_sets_monthly_comparison(self):

        self._prepare_comparisons()

        self.page.update_data()

        assert self.page.month_max_label.text() == (
            "Mes 3 del año 2025"
        )

        assert self.page.month_min_label.text() == (
            "Mes 1 del año 2024"
        )

    def test_update_data_sets_monthly_anomalies(self):

        self._prepare_comparisons()

        self.page.update_data()

        text = self.page.anomalies_label.text()

        assert "Enero 2025" in text
        assert "Aumento extremo (+80.00%)" in text
        assert "Febrero 2025" in text
        assert "Caída extrema (-40.00%)" in text

        assert self.page.summary_anomalies_label.text() == text

    def test_update_data_without_monthly_anomalies(self):

        comparisons = self._prepare_comparisons()

        comparisons.detect_monthly_anomalies.return_value = []

        self.page.update_data()

        assert (
            self.page.anomalies_label.text()
            == "No se han detectado anomalías."
        )

        assert (
            self.page.summary_anomalies_label.text()
            == "No se han detectado anomalías."
        )

    def test_update_data_sets_monthly_stability(self):

        self._prepare_comparisons()

        self.page.update_data()

        assert self.page.most_stable_month_label.text() == (
            "Marzo — CV 0.04, Desv. 3.00 (Estable)"
        )

        assert self.page.most_volatile_month_label.text() == (
            "Julio — CV 0.45, Desv. 25.00 (Volátil)"
        )

    # ==================================================
    # Anual
    # ==================================================

    def test_update_data_sets_yearly_comparison(self):

        self._prepare_comparisons()

        self.page.update_data()

        assert self.page.year_max_label.text() == "2025"
        assert self.page.year_min_label.text() == "2024"

    def test_update_data_sets_yearly_trends(self):

        self._prepare_comparisons()

        self.page.update_data()

        assert self.page.trend_2024_label.text() == (
            "Creciente (+2 / -0) — "
            "Max ↑ 30.00, Max ↓ 0.00"
        )

        assert self.page.trend_2025_label.text() == (
            "Decreciente (+1 / -2) — "
            "Max ↑ 15.00, Max ↓ -20.00"
        )

        assert self.page.trend_2026_label.text() == (
            "Irregular (+1 / -1) — "
            "Max ↑ 10.00, Max ↓ -12.00"
        )

    def test_update_data_sets_annual_stability(self):

        self._prepare_comparisons()

        self.page.update_data()

        assert self.page.stab_2024_label.text() == (
            "Estable — Rango 100.00 kWh, "
            "Desv. 10.00, CV 0.10"
        )

        assert self.page.stab_2025_label.text() == (
            "Volátil — Rango 500.00 kWh, "
            "Desv. 50.00, CV 0.30"
        )

        assert self.page.stab_2026_label.text() == (
            "Irregular — Rango 300.00 kWh, "
            "Desv. 30.00, CV 0.20"
        )

    # ==================================================
    # Resumen e Insights
    # ==================================================

    def test_update_data_sets_summary(self):

        self._prepare_comparisons()

        self.page.update_data()

        assert self.page.summary_year_max_label.text() == "2025"
        assert self.page.summary_year_min_label.text() == "2024"

        assert self.page.summary_stable_month_label.text() == (
            "Marzo — CV 0.04"
        )

        assert self.page.summary_volatile_month_label.text() == (
            "Julio — CV 0.45"
        )

        assert self.page.summary_stable_week_label.text() == (
            "S01 — CV 0.05"
        )

        assert self.page.summary_volatile_week_label.text() == (
            "S35 — CV 0.50"
        )

    def test_update_data_sets_advanced_insights(self):

        self._prepare_comparisons()

        self.page.update_data()

        text = self.page.insights_text_label.text()

        assert "Año de mayor consumo:</b> 2025" in text
        assert "Año de menor consumo:</b> 2024" in text
        assert "Mes más estable:</b> Marzo — CV 0.04" in text
        assert "Mes más volátil:</b> Julio — CV 0.45" in text
        assert "Semana más tranquila:</b> S01 — CV 0.05" in text
        assert "Semana más crítica:</b> S35 — CV 0.50" in text
        assert "Tendencia anual:</b> Creciente (+2 / -1)" in text