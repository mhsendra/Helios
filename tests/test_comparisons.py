import pandas as pd

from helios.core.comparisons import ConsumptionComparisons

from helios.plots.comparisons import ComparisonPlots

from unittest.mock import MagicMock, patch

import pytest

class TestConsumptionComparisons:

    def setup_method(self):

        self.comparisons = ConsumptionComparisons()

    # ==================================================
    # Estado inicial
    # ==================================================

    def test_initial_state(self):

        assert self.comparisons.monthly_comparison is None
        assert self.comparisons.monthly_variation is None

        assert self.comparisons.weekly_comparison is None
        assert self.comparisons.weekly_variation is None

        assert self.comparisons.yearly_comparison is None

    # ==================================================
    # Comparación mensual
    # ==================================================

    def test_compare_months_by_year(self):

        index = pd.to_datetime([
            "2024-01-15",
            "2024-01-20",
            "2024-02-10",
            "2025-01-10",
            "2025-02-15",
        ])

        dataset = pd.DataFrame(
            {
                "AE_kWh": [
                    10.0,
                    20.0,
                    30.0,
                    40.0,
                    50.0,
                ]
            },
            index=index
        )

        result = self.comparisons.compare_months_by_year(
            dataset
        )

        assert result.loc["Enero", 2024] == 30.0
        assert result.loc["Febrero", 2024] == 30.0

        assert result.loc["Enero", 2025] == 40.0
        assert result.loc["Febrero", 2025] == 50.0

        assert result.index.name is None
        assert result.columns.name is None

        assert self.comparisons.monthly_comparison is result

    # ==================================================
    # Comparación anual
    # ==================================================

    def test_compare_years(self):

        index = pd.to_datetime([
            "2024-01-01",
            "2024-06-01",
            "2025-01-01",
            "2025-06-01",
        ])

        df = pd.DataFrame(
            {
                "AE_kWh": [
                    100.0,
                    150.0,
                    200.0,
                    250.0,
                ]
            },
            index=index
        )

        result = self.comparisons.compare_years(df)

        assert result.loc[2024] == 250.0
        assert result.loc[2025] == 450.0

        assert self.comparisons.yearly_comparison is result

    # ==================================================
    # Comparación semanal
    # ==================================================

    def test_compare_weeks_by_year(self):

        index = pd.to_datetime([
            "2024-01-01",
            "2024-01-03",
            "2024-01-08",
            "2025-01-01",
            "2025-01-08",
        ])

        df = pd.DataFrame(
            {
                "AE_kWh": [
                    10.0,
                    20.0,
                    30.0,
                    40.0,
                    50.0,
                ]
            },
            index=index
        )

        result = self.comparisons.compare_weeks_by_year(df)

        assert result.loc["S01", 2024] == 30.0
        assert result.loc["S02", 2024] == 30.0

        assert result.loc["S01", 2025] == 40.0
        assert result.loc["S02", 2025] == 50.0

        assert result.index.name is None
        assert result.columns.name is None

        assert self.comparisons.weekly_comparison is result

    def test_compare_months_by_year_always_contains_12_months(self):

        index = pd.to_datetime([
            "2024-01-15",
            "2024-02-15",
        ])

        dataset = pd.DataFrame(
            {
                "AE_kWh": [
                    10.0,
                    20.0,
                ]
            },
            index=index
        )

        result = self.comparisons.compare_months_by_year(
            dataset
        )

        assert len(result) == 12

        assert list(result.index) == [
            "Enero", "Febrero", "Marzo", "Abril",
            "Mayo", "Junio", "Julio", "Agosto",
            "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        assert result.loc["Enero", 2024] == 10.0
        assert result.loc["Febrero", 2024] == 20.0

        assert pd.isna(result.loc["Marzo", 2024])
        assert pd.isna(result.loc["Diciembre", 2024])

    # ==================================================
    # Variaciones
    # ==================================================

    def test_calculate_variation(self):

        comparison = pd.DataFrame(
            {
                2024: [100.0, 200.0],
                2025: [120.0, 150.0],
                2026: [180.0, 180.0],
            },
            index=["Enero", "Febrero"]
        )

        result = self.comparisons.calculate_variation(
            comparison
        )

        assert list(result.columns) == [
            "2025 vs 2024",
            "2026 vs 2025",
        ]

        assert result.loc[
            "Enero", "2025 vs 2024"
        ] == pytest.approx(20.0)

        assert result.loc[
            "Febrero", "2025 vs 2024"
        ] == pytest.approx(-25.0)

        assert result.loc[
            "Enero", "2026 vs 2025"
        ] == pytest.approx(50.0)

        assert result.loc[
            "Febrero", "2026 vs 2025"
        ] == pytest.approx(20.0)

    def test_calculate_monthly_variation(self):

        self.comparisons.monthly_comparison = pd.DataFrame(
            {
                2024: [100.0, 200.0],
                2025: [120.0, 150.0],
            },
            index=["Enero", "Febrero"]
        )

        result = self.comparisons.calculate_monthly_variation()

        assert result is self.comparisons.monthly_variation

        assert list(result.columns) == [
            "2025 vs 2024"
        ]

        assert result.loc[
            "Enero", "2025 vs 2024"
        ] == pytest.approx(20.0)

        assert result.loc[
            "Febrero", "2025 vs 2024"
        ] == pytest.approx(-25.0)

    def test_calculate_weekly_variation(self):

        self.comparisons.weekly_comparison = pd.DataFrame(
            {
                2024: [100.0, 200.0],
                2025: [110.0, 150.0],
            },
            index=["S01", "S02"]
        )

        result = self.comparisons.calculate_weekly_variation()

        assert result is self.comparisons.weekly_variation

        assert list(result.columns) == [
            "2025 vs 2024"
        ]

        assert result.loc[
            "S01", "2025 vs 2024"
        ] == pytest.approx(10.0)

        assert result.loc[
            "S02", "2025 vs 2024"
        ] == pytest.approx(-25.0)

    # ==================================================
    # Tendencias
    # ==================================================

    def test_yearly_trend_increasing(self):

        self.comparisons.yearly_comparison = pd.Series(
            {
                2024: 100.0,
                2025: 120.0,
                2026: 150.0,
            }
        )

        result = self.comparisons.yearly_trend()

        assert result["classification"] == "Creciente"
        assert result["positive_steps"] == 2
        assert result["negative_steps"] == 0
        assert result["max_increase"] == pytest.approx(30.0)
        assert result["max_decrease"] == pytest.approx(20.0)

    def test_yearly_trend_decreasing(self):

        self.comparisons.yearly_comparison = pd.Series(
            {
                2024: 150.0,
                2025: 120.0,
                2026: 100.0,
            }
        )

        result = self.comparisons.yearly_trend()

        assert result["classification"] == "Decreciente"
        assert result["positive_steps"] == 0
        assert result["negative_steps"] == 2
        assert result["max_increase"] == pytest.approx(-20.0)
        assert result["max_decrease"] == pytest.approx(-30.0)


    def test_yearly_trend_irregular(self):

        self.comparisons.yearly_comparison = pd.Series(
            {
                2024: 100.0,
                2025: 150.0,
                2026: 120.0,
            }
        )

        result = self.comparisons.yearly_trend()

        assert result["classification"] == "Irregular"
        assert result["positive_steps"] == 1
        assert result["negative_steps"] == 1
        assert result["max_increase"] == pytest.approx(50.0)
        assert result["max_decrease"] == pytest.approx(-30.0)

# ==================================================
# Tendencias mensuales
# ==================================================

    def test_monthly_trends_increasing(self):

        self.comparisons.monthly_comparison = pd.DataFrame(
            {
                2024: [100.0, 120.0, 150.0],
            },
            index=["Enero", "Febrero", "Marzo"]
        )

        result = self.comparisons.monthly_trends()

        assert result[2024]["classification"] == "Creciente"
        assert result[2024]["positive_steps"] == 2
        assert result[2024]["negative_steps"] == 0
        assert result[2024]["max_increase"] == pytest.approx(30.0)
        assert result[2024]["max_decrease"] == pytest.approx(20.0)


    def test_monthly_trends_decreasing(self):

        self.comparisons.monthly_comparison = pd.DataFrame(
            {
                2024: [150.0, 120.0, 100.0],
            },
            index=["Enero", "Febrero", "Marzo"]
        )

        result = self.comparisons.monthly_trends()

        assert result[2024]["classification"] == "Decreciente"
        assert result[2024]["positive_steps"] == 0
        assert result[2024]["negative_steps"] == 2
        assert result[2024]["max_increase"] == pytest.approx(-20.0)
        assert result[2024]["max_decrease"] == pytest.approx(-30.0)


    def test_monthly_trends_irregular(self):

        self.comparisons.monthly_comparison = pd.DataFrame(
            {
                2024: [100.0, 150.0, 120.0],
            },
            index=["Enero", "Febrero", "Marzo"]
        )

        result = self.comparisons.monthly_trends()

        assert result[2024]["classification"] == "Irregular"
        assert result[2024]["positive_steps"] == 1
        assert result[2024]["negative_steps"] == 1
        assert result[2024]["max_increase"] == pytest.approx(50.0)
        assert result[2024]["max_decrease"] == pytest.approx(-30.0)

    # ==================================================
    # Tendencias semanales
    # ==================================================

    def test_weekly_trends(self):

        self.comparisons.weekly_comparison = pd.DataFrame(
            {
                2024: [100.0, 150.0, 120.0],
                2025: [200.0, 180.0, 220.0],
            },
            index=["S01", "S02", "S03"]
        )

        result = self.comparisons.weekly_trends()

        assert set(result.keys()) == {2024, 2025}

        assert result[2024]["classification"] == "Irregular"
        assert result[2024]["positive_steps"] == 1
        assert result[2024]["negative_steps"] == 1
        assert result[2024]["max_increase"] == pytest.approx(50.0)
        assert result[2024]["max_decrease"] == pytest.approx(-30.0)

        assert result[2025]["classification"] == "Irregular"
        assert result[2025]["positive_steps"] == 1
        assert result[2025]["negative_steps"] == 1
        assert result[2025]["max_increase"] == pytest.approx(40.0)
        assert result[2025]["max_decrease"] == pytest.approx(-20.0)

    # ==================================================
    # Weekly insights
    # ==================================================

    def test_detailed_weekly_insights_with_previous_year(self):

        self.comparisons.weekly_comparison = pd.DataFrame(
            {
                2024: [100.0, 200.0, 150.0],
                2025: [120.0, 300.0, 180.0],
            },
            index=["S01", "S02", "S03"]
        )

        result = self.comparisons.detailed_weekly_insights()

        assert result["max"]["week"] == "S02"
        assert result["max"]["year"] == 2025
        assert result["max"]["value"] == pytest.approx(300.0)

        assert result["max"]["variation_prev"] == pytest.approx(50.0)

        mean_2025 = (120.0 + 300.0 + 180.0) / 3

        expected_variation = (
            (300.0 - mean_2025) / mean_2025
        ) * 100

        assert result["max"]["variation_mean"] == pytest.approx(
            expected_variation
        )

        assert result["min"]["week"] == "S01"
        assert result["min"]["year"] == 2024
        assert result["min"]["value"] == pytest.approx(100.0)

    def test_detailed_weekly_insights_without_previous_year(self):

        self.comparisons.weekly_comparison = pd.DataFrame(
            {
                2025: [120.0, 300.0, 180.0],
            },
            index=["S01", "S02", "S03"]
        )

        result = self.comparisons.detailed_weekly_insights()

        assert result["max"]["week"] == "S02"
        assert result["max"]["year"] == 2025
        assert result["max"]["value"] == pytest.approx(300.0)

        assert result["max"]["variation_prev"] is None

        mean_2025 = (120.0 + 300.0 + 180.0) / 3

        expected_variation = (
            (300.0 - mean_2025) / mean_2025
        ) * 100

        assert result["max"]["variation_mean"] == pytest.approx(
            expected_variation
        )

    def test_detailed_weekly_insights_previous_year_zero(self):

        self.comparisons.weekly_comparison = pd.DataFrame(
            {
                2024: [0.0, 100.0],
                2025: [150.0, 50.0],
            },
            index=["S01", "S02"]
        )

        result = self.comparisons.detailed_weekly_insights()

        assert result["max"]["week"] == "S01"
        assert result["max"]["year"] == 2025
        assert result["max"]["value"] == pytest.approx(150.0)

        assert result["max"]["variation_prev"] is None

    def test_detailed_weekly_insights_mean_zero(self):

        self.comparisons.weekly_comparison = pd.DataFrame(
            {
                2024: [0.0, 0.0],
                2025: [0.0, 0.0],
            },
            index=["S01", "S02"]
        )

        result = self.comparisons.detailed_weekly_insights()

        assert result["max"]["value"] == pytest.approx(0.0)
        assert result["max"]["variation_mean"] is None
        
    # ==================================================
    # Anomalías mensuales
    # ==================================================

    def test_detect_monthly_anomalies_detects_missing_and_extreme_variations(self):

        self.comparisons.monthly_comparison = pd.DataFrame(
            {
                2024: [100.0, 100.0, 100.0],
                2025: [None, 200.0, 40.0],
            },
            index=["Enero", "Febrero", "Marzo"]
        )

        self.comparisons.monthly_variation = pd.DataFrame(
            {
                "2025 vs 2024": [
                    None,
                    100.0,
                    -60.0,
                ]
            },
            index=["Enero", "Febrero", "Marzo"]
        )

        result = self.comparisons.detect_monthly_anomalies()

        assert {
            "type": "missing",
            "month": "Enero",
            "year": "2024",
            "detail": "Valor faltante",
        } in result

        assert {
            "type": "extreme_increase",
            "month": "Febrero",
            "year": "2024",
            "value": 100.0,
            "detail": "Aumento extremo (+100.00%)",
        } in result

        assert {
            "type": "extreme_decrease",
            "month": "Marzo",
            "year": "2024",
            "value": -60.0,
            "detail": "Caída extrema (-60.00%)",
        } in result

    def test_detect_monthly_anomalies_detects_statistical_peak(self):

        self.comparisons.monthly_comparison = pd.DataFrame(
            {
                2024: [
                    100.0,
                    100.0,
                    100.0,
                    100.0,
                    100.0,
                    100.0,
                    100.0,
                    100.0,
                    100.0,
                    100.0,
                    100.0,
                    1000.0,
                ]
            },
            index=[
                "Enero", "Febrero", "Marzo", "Abril",
                "Mayo", "Junio", "Julio", "Agosto",
                "Septiembre", "Octubre", "Noviembre", "Diciembre",
            ]
        )

        self.comparisons.monthly_variation = pd.DataFrame(
            columns=[]
        )

        result = self.comparisons.detect_monthly_anomalies()

        peaks = [
            anomaly
            for anomaly in result
            if anomaly["type"] == "statistical_peak"
        ]

        assert len(peaks) == 1

        assert peaks[0]["month"] == "Diciembre"
        assert peaks[0]["year"] == 2024
        assert peaks[0]["value"] == pytest.approx(1000.0)

    def test_detect_monthly_anomalies_detects_statistical_valley(self):

        self.comparisons.monthly_comparison = pd.DataFrame(
            {
                2024: [
                    100.0,
                    100.0,
                    100.0,
                    100.0,
                    100.0,
                    100.0,
                    100.0,
                    100.0,
                    100.0,
                    100.0,
                    100.0,
                    0.0,
                ]
            },
            index=[
                "Enero", "Febrero", "Marzo", "Abril",
                "Mayo", "Junio", "Julio", "Agosto",
                "Septiembre", "Octubre", "Noviembre", "Diciembre",
            ]
        )

        self.comparisons.monthly_variation = pd.DataFrame(
            columns=[]
        )

        result = self.comparisons.detect_monthly_anomalies()

        valleys = [
            anomaly
            for anomaly in result
            if anomaly["type"] == "statistical_valley"
        ]

        assert len(valleys) == 1

        assert valleys[0]["month"] == "Diciembre"
        assert valleys[0]["year"] == 2024
        assert valleys[0]["value"] == pytest.approx(0.0)

    # ==================================================
    # Estabilidad anual
    # ==================================================

    def test_annual_stability_classifies_years(self):

        self.comparisons.monthly_comparison = pd.DataFrame(
            {
                2024: [
                    100.0, 100.0, 100.0, 100.0,
                    100.0, 100.0, 100.0, 100.0,
                    100.0, 100.0, 100.0, 100.0,
                ],
                2025: [
                    80.0, 120.0, 80.0, 120.0,
                    80.0, 120.0, 80.0, 120.0,
                    80.0, 120.0, 80.0, 120.0,
                ],
            },
            index=[
                "Enero", "Febrero", "Marzo", "Abril",
                "Mayo", "Junio", "Julio", "Agosto",
                "Septiembre", "Octubre", "Noviembre", "Diciembre",
            ]
        )

        result = self.comparisons.annual_stability()

        assert result[2024]["classification"] == "Muy estable"
        assert result[2024]["cv"] == pytest.approx(0.0)

        assert result[2025]["classification"] == "Estable"

        assert result[2024]["min"] == pytest.approx(100.0)
        assert result[2024]["max"] == pytest.approx(100.0)
        assert result[2024]["range"] == pytest.approx(0.0)

    def test_annual_stability_handles_zero_mean(self):

        self.comparisons.monthly_comparison = pd.DataFrame(
            {
                2024: [
                    0.0, 0.0, 0.0, 0.0,
                ],
            },
            index=[
                "Enero",
                "Febrero",
                "Marzo",
                "Abril",
            ]
        )

        result = self.comparisons.annual_stability()

        assert result[2024]["cv"] is None
        assert result[2024]["classification"] == "Indeterminado"

    def test_annual_stability_classifies_all_ranges(self):

        self.comparisons.monthly_comparison = pd.DataFrame(
            {
                2024: [100.0, 100.0, 100.0, 100.0],
                2025: [90.0, 110.0, 90.0, 110.0],
                2026: [70.0, 130.0, 70.0, 130.0],
                2027: [50.0, 150.0, 50.0, 150.0],
            },
            index=[
                "Enero",
                "Febrero",
                "Marzo",
                "Abril",
            ]
        )

        result = self.comparisons.annual_stability()

        assert result[2024]["classification"] == "Muy estable"
        assert result[2025]["classification"] == "Estable"
        assert result[2026]["classification"] == "Moderadamente inestable"
        assert result[2027]["classification"] == "Muy inestable"

    # ==================================================
    # Estabilidad mensual
    # ==================================================

    def test_monthly_stability_with_single_year_is_indeterminate(self):

        self.comparisons.monthly_comparison = pd.DataFrame(
            {
                2024: [100.0],
            },
            index=["Enero"]
        )

        result = self.comparisons.monthly_stability()

        assert result["Enero"]["std"] is None
        assert result["Enero"]["cv"] is None
        assert result["Enero"]["classification"] == "Indeterminado"

    def test_monthly_stability_calculates_cv_and_classification(self):

        self.comparisons.monthly_comparison = pd.DataFrame(
            {
                2024: [100.0],
                2025: [120.0],
                2026: [140.0],
            },
            index=["Enero"]
        )

        result = self.comparisons.monthly_stability()

        assert result["Enero"]["std"] == pytest.approx(20.0)
        assert result["Enero"]["cv"] == pytest.approx(20.0 / 120.0)
        assert result["Enero"]["classification"] == "Estable"

    def test_monthly_stability_handles_zero_mean(self):

        self.comparisons.monthly_comparison = pd.DataFrame(
            {
                2024: [0.0],
                2025: [0.0],
            },
            index=["Enero"]
        )

        result = self.comparisons.monthly_stability()

        assert result["Enero"]["std"] == pytest.approx(0.0)
        assert result["Enero"]["cv"] is None
        assert result["Enero"]["classification"] == "Indeterminado"

        # ==================================================
    # Extremos de estabilidad mensual
    # ==================================================

    def test_monthly_stability_extremes_returns_stable_and_volatile(self):

        self.comparisons.monthly_comparison = pd.DataFrame(
            {
                2024: [100.0, 100.0],
                2025: [105.0, 150.0],
                2026: [110.0, 200.0],
            },
            index=["Enero", "Febrero"]
        )

        result = self.comparisons.monthly_stability_extremes()

        assert result["stable"]["month"] == "Enero"
        assert result["volatile"]["month"] == "Febrero"

        assert result["stable"]["cv"] < result["volatile"]["cv"]

        assert "std" in result["stable"]
        assert "classification" in result["stable"]

        assert "std" in result["volatile"]
        assert "classification" in result["volatile"]

    def test_monthly_stability_extremes_returns_none_without_valid_cv(self):

        self.comparisons.monthly_comparison = pd.DataFrame(
            {
                2024: [0.0],
                2025: [0.0],
            },
            index=["Enero"]
        )

        result = self.comparisons.monthly_stability_extremes()

        assert result is None

    def test_monthly_stability_classifies_all_ranges(self):

        self.comparisons.monthly_comparison = pd.DataFrame(
            {
                2024: [100.0, 100.0, 100.0, 100.0],
                2025: [105.0, 120.0, 140.0, 200.0],
            },
            index=[
                "Enero",
                "Febrero",
                "Marzo",
                "Abril",
            ]
        )

        result = self.comparisons.monthly_stability()

        assert result["Enero"]["classification"] == "Muy estable"
        assert result["Febrero"]["classification"] == "Estable"
        assert result["Marzo"]["classification"] == "Moderadamente volátil"
        assert result["Abril"]["classification"] == "Muy volátil"

    # ==================================================
    # Estabilidad semanal
    # ==================================================

    def test_weekly_stability_with_single_year_is_indeterminate(self):

        self.comparisons.weekly_comparison = pd.DataFrame(
            {
                2024: [100.0],
            },
            index=["S01"]
        )

        result = self.comparisons.weekly_stability()

        assert result["S01"]["std"] is None
        assert result["S01"]["cv"] is None
        assert result["S01"]["classification"] == "Indeterminado"

    def test_weekly_stability_calculates_cv_and_classification(self):

        self.comparisons.weekly_comparison = pd.DataFrame(
            {
                2024: [100.0],
                2025: [120.0],
                2026: [140.0],
            },
            index=["S01"]
        )

        result = self.comparisons.weekly_stability()

        assert result["S01"]["std"] == pytest.approx(20.0)
        assert result["S01"]["cv"] == pytest.approx(20.0 / 120.0)
        assert result["S01"]["classification"] == "Tranquila"

    def test_weekly_stability_handles_zero_mean(self):

        self.comparisons.weekly_comparison = pd.DataFrame(
            {
                2024: [0.0],
                2025: [0.0],
            },
            index=["S01"]
        )

        result = self.comparisons.weekly_stability()

        assert result["S01"]["std"] == pytest.approx(0.0)
        assert result["S01"]["cv"] is None
        assert result["S01"]["classification"] == "Indeterminado"

    def test_weekly_stability_classifies_all_ranges(self):

        self.comparisons.weekly_comparison = pd.DataFrame(
            {
                2024: [100.0, 100.0, 100.0, 100.0],
                2025: [105.0, 120.0, 140.0, 200.0],
            },
            index=[
                "S01",
                "S02",
                "S03",
                "S04",
            ]
        )

        result = self.comparisons.weekly_stability()

        assert result["S01"]["classification"] == "Muy tranquila"
        assert result["S02"]["classification"] == "Tranquila"
        assert result["S03"]["classification"] == "Moderadamente crítica"
        assert result["S04"]["classification"] == "Muy crítica"

    # ==================================================
    # Extremos de estabilidad semanal
    # ==================================================

    def test_weekly_stability_extremes_returns_stable_and_volatile(self):

        self.comparisons.weekly_comparison = pd.DataFrame(
            {
                2024: [100.0, 100.0],
                2025: [105.0, 150.0],
                2026: [110.0, 200.0],
            },
            index=["S01", "S02"]
        )

        result = self.comparisons.weekly_stability_extremes()

        assert result["stable"]["week"] == "S01"
        assert result["volatile"]["week"] == "S02"

        assert result["stable"]["cv"] < result["volatile"]["cv"]

        assert "std" in result["stable"]
        assert "classification" in result["stable"]

        assert "std" in result["volatile"]
        assert "classification" in result["volatile"]

    def test_weekly_stability_extremes_returns_none_without_valid_cv(self):

        self.comparisons.weekly_comparison = pd.DataFrame(
            {
                2024: [0.0],
                2025: [0.0],
            },
            index=["S01"]
        )

        result = self.comparisons.weekly_stability_extremes()

        assert result is None

    # ==================================================
    # Reports
    # ==================================================

    @patch("helios.core.comparisons.ReportPrinter")
    def test_monthly_comparison_report(self, printer):

        comparison = pd.DataFrame(
            {
                2024: [100.0, float("nan")],
                2025: [120.5, 150.0],
            },
            index=["Enero", "Febrero"]
        )

        self.comparisons.monthly_comparison_report(
            comparison
        )

        printer.title.assert_called_once_with(
            "MONTHLY YEAR COMPARISON"
        )

        printer.blank.assert_called_once()

        assert printer.table_header.called

        assert printer.table_row.call_count == 2

        first_row = printer.table_row.call_args_list[0]

        assert first_row.args[0] == [
            "Enero",
            "100.00",
            "120.50",
        ]

        second_row = printer.table_row.call_args_list[1]

        assert second_row.args[0] == [
            "Febrero",
            "---",
            "150.00",
        ]

    @patch("helios.core.comparisons.ReportPrinter")
    def test_monthly_variation_report(self, printer):

        variation = pd.DataFrame(
            {
                "2025 vs 2024": [20.0, float("nan")],
                "2026 vs 2025": [-5.5, 10.25],
            },
            index=["Enero", "Febrero"]
        )

        self.comparisons.monthly_variation_report(
            variation
        )

        printer.title.assert_called_once_with(
            "MONTHLY VARIATION REPORT"
        )

        printer.blank.assert_called_once()

        assert printer.table_header.called

        assert printer.table_row.call_count == 2

        first_row = printer.table_row.call_args_list[0]

        assert first_row.args[0] == [
            "Enero",
            "20.00 %",
            "-5.50 %",
        ]

        second_row = printer.table_row.call_args_list[1]

        assert second_row.args[0] == [
            "Febrero",
            "---",
            "10.25 %",
        ]

    @patch("helios.core.comparisons.ReportPrinter")
    def test_yearly_comparison_report(self, printer):

        yearly = pd.Series(
            {
                2024: 1234.567,
                2025: 2500.0,
            }
        )

        self.comparisons.yearly_comparison_report(
            yearly
        )

        printer.title.assert_called_once_with(
            "YEARLY COMPARISON"
        )

        printer.blank.assert_called_once()

        printer.table_header.assert_called_once_with(
            ["Año", "Consumo"],
            [10, 18],
            ["left", "right"]
        )

        assert printer.table_row.call_count == 2

        first_row = printer.table_row.call_args_list[0]

        assert first_row.args[0] == [
            "2024",
            "1234.57 kWh",
        ]

        second_row = printer.table_row.call_args_list[1]

        assert second_row.args[0] == [
            "2025",
            "2500.00 kWh",
        ]

    @patch("helios.core.comparisons.ReportPrinter")
    def test_weekly_comparison_report(self, printer):

        comparison = pd.DataFrame(
            {
                2024: [100.0, float("nan")],
                2025: [120.5, 150.0],
            },
            index=["S01", "S02"]
        )

        self.comparisons.weekly_comparison_report(
            comparison
        )

        printer.title.assert_called_once_with(
            "WEEKLY YEAR COMPARISON"
        )

        printer.blank.assert_called_once()

        assert printer.table_header.called

        assert printer.table_row.call_count == 2

        first_row = printer.table_row.call_args_list[0]

        assert first_row.args[0] == [
            "S01",
            "100.00",
            "120.50",
        ]

        second_row = printer.table_row.call_args_list[1]

        assert second_row.args[0] == [
            "S02",
            "---",
            "150.00",
        ]

    @patch("helios.core.comparisons.ReportPrinter")
    def test_weekly_variation_report(self, printer):

        variation = pd.DataFrame(
            {
                "2025 vs 2024": [10.0, float("nan")],
                "2026 vs 2025": [-5.5, 12.25],
            },
            index=["S01", "S02"]
        )

        self.comparisons.weekly_variation_report(
            variation
        )

        printer.title.assert_called_once_with(
            "WEEKLY VARIATION REPORT"
        )

        printer.blank.assert_called_once()

        assert printer.table_header.called

        assert printer.table_row.call_count == 2

        first_row = printer.table_row.call_args_list[0]

        assert first_row.args[0] == [
            "S01",
            "10.00 %",
            "-5.50 %",
        ]

        second_row = printer.table_row.call_args_list[1]

        assert second_row.args[0] == [
            "S02",
            "---",
            "12.25 %",
        ]

    def test_weekly_trends_increasing(self):

        self.comparisons.weekly_comparison = pd.DataFrame(
            {
                2024: [100.0, 120.0, 140.0],
            },
            index=["S01", "S02", "S03"]
        )

        result = self.comparisons.weekly_trends()

        assert result[2024]["classification"] == "Creciente"
        assert result[2024]["positive_steps"] == 2
        assert result[2024]["negative_steps"] == 0

    def test_weekly_trends_decreasing(self):

        self.comparisons.weekly_comparison = pd.DataFrame(
            {
                2024: [140.0, 120.0, 100.0],
            },
            index=["S01", "S02", "S03"]
        )

        result = self.comparisons.weekly_trends()

        assert result[2024]["classification"] == "Decreciente"
        assert result[2024]["positive_steps"] == 0
        assert result[2024]["negative_steps"] == 2

    # ==================================================
    # Comparison plots
    # ==================================================

# ==================================================
# Comparison plots
# ==================================================

class TestComparisonPlots:

    def setup_method(self):

        self.plotter = MagicMock()

        self.plots = ComparisonPlots(
            self.plotter
        )

    # ==================================================
    # Comparación mensual
    # ==================================================

    def test_plot_monthly_comparison(self):

        comparison = pd.DataFrame(
            {
                2024: [100.0, 120.0],
                2025: [110.0, 130.0],
            },
            index=["Enero", "Febrero"]
        )

        self.plots.plot_monthly_comparison(
            comparison
        )

        self.plotter.plot_comparison_lines.assert_called_once_with(
            dataframe=comparison,
            title="Comparativa mensual",
            xlabel="Mes",
            ylabel="Consumo (kWh)"
        )

    # ==================================================
    # Comparación semanal
    # ==================================================

    def test_plot_weekly_comparison(self):

        comparison = pd.DataFrame(
            {
                2024: [100.0, 120.0],
                2025: [110.0, 130.0],
            },
            index=["S01", "S02"]
        )

        self.plots.plot_weekly_comparison(
            comparison
        )

        self.plotter.plot_comparison_lines.assert_called_once_with(
            dataframe=comparison,
            title="Comparativa semanal",
            xlabel="Semana",
            ylabel="Consumo (kWh)"
        )

    # ==================================================
    # Comparación anual
    # ==================================================

    def test_plot_yearly_comparison(self):

        comparison = pd.Series(
            {
                2024: 1200.0,
                2025: 1500.0,
            }
        )

        self.plots.plot_yearly_comparison(
            comparison
        )

        self.plotter.plot_series.assert_called_once_with(
            series=comparison,
            title="Comparativa anual",
            xlabel="Año",
            ylabel="Consumo (kWh)"
        )