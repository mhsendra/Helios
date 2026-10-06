import pytest

from helios.core.diagnostics.battery_economics import (
    BatteryEconomicAnalyzer,
)
from helios.solar.battery_recommendation import BatteryRecommendation


def make_recommendation(
    capacity_kwh: float,
    *,
    economic_npv_eur: float = 0.0,
    economic_irr_percent: float = 0.0,
    economic_payback_years: float = float("inf"),
    annual_additional_savings_eur: float = 0.0,
    incremental_battery_cost_eur: float = 0.0,
) -> BatteryRecommendation:
    return BatteryRecommendation(
        capacity_kwh=capacity_kwh,
        max_charge_power_kw=8.0,
        max_discharge_power_kw=8.0,
        annual_consumption_kwh=10000.0,
        annual_production_kwh=12000.0,
        annual_surplus_kwh=7000.0,
        annual_export_kwh=5000.0,
        annual_grid_import_kwh=3000.0,
        annual_battery_charge_kwh=2500.0,
        annual_battery_discharge_kwh=2200.0,
        self_consumption_kwh=9000.0,
        self_sufficiency_percent=70.0,
        equivalent_cycles=130.0,
        annual_additional_savings_eur=annual_additional_savings_eur,
        incremental_battery_cost_eur=incremental_battery_cost_eur,
        economic_npv_eur=economic_npv_eur,
        economic_irr_percent=economic_irr_percent,
        economic_payback_years=economic_payback_years,
    )


class TestBatteryEconomicAnalyzer:

    def test_empty_recommendations_return_empty_result(self):
        assert BatteryEconomicAnalyzer.analyze([]) == []

    def test_selects_highest_positive_npv(self):
        recommendations = [
            make_recommendation(
                5.0,
                economic_npv_eur=500.0,
            ),
            make_recommendation(
                8.3,
                economic_npv_eur=1200.0,
            ),
            make_recommendation(
                16.6,
                economic_npv_eur=900.0,
            ),
        ]

        result = BatteryEconomicAnalyzer.analyze(
            recommendations
        )

        assert len(result) == 1
        assert result[0].capacity_kwh == pytest.approx(8.3)
        assert result[0].criterion == "positive_npv"

    def test_positive_npv_has_expected_evidence(self):
        recommendation = make_recommendation(
            8.3,
            economic_npv_eur=1200.0,
            economic_irr_percent=11.5,
            economic_payback_years=7.2,
            annual_additional_savings_eur=450.0,
            incremental_battery_cost_eur=2072.51,
        )

        result = BatteryEconomicAnalyzer.analyze(
            [recommendation]
        )[0]

        assert result.evidence["capacity_kwh"] == pytest.approx(8.3)
        assert result.evidence["economic_npv_eur"] == pytest.approx(
            1200.0
        )
        assert result.evidence["economic_irr_percent"] == pytest.approx(
            11.5
        )
        assert result.evidence["economic_payback_years"] == pytest.approx(
            7.2
        )
        assert result.evidence[
            "annual_additional_savings_eur"
        ] == pytest.approx(450.0)
        assert result.evidence[
            "incremental_battery_cost_eur"
        ] == pytest.approx(2072.51)

    def test_positive_npv_includes_marginal_economic_evidence(self):
        recommendation = make_recommendation(
            8.3,
            economic_npv_eur=1200.0,
            economic_irr_percent=11.5,
            economic_payback_years=7.2,
            annual_additional_savings_eur=450.0,
            incremental_battery_cost_eur=2072.51,
        )

        recommendation = BatteryRecommendation(
            **{
                **recommendation.__dict__,
                "incremental_savings_eur": 180.0,
                "marginal_savings_per_kwh": 54.5454545,
                "marginal_payback_years": 11.5139444,
            }
        )

        result = BatteryEconomicAnalyzer.analyze(
            [recommendation]
        )[0]

        assert result.evidence[
            "incremental_savings_eur"
        ] == pytest.approx(180.0)

        assert result.evidence[
            "marginal_savings_per_kwh"
        ] == pytest.approx(54.5454545)

        assert result.evidence[
            "marginal_payback_years"
        ] == pytest.approx(11.5139444)

        assert "ahorro" in result.description
        assert "marginal" in result.description

    def test_no_positive_npv_includes_marginal_economic_evidence(self):
        recommendation = make_recommendation(
            16.6,
            economic_npv_eur=-800.0,
            economic_irr_percent=2.5,
            economic_payback_years=18.4,
            annual_additional_savings_eur=600.0,
            incremental_battery_cost_eur=2072.51,
        )

        recommendation = BatteryRecommendation(
            **{
                **recommendation.__dict__,
                "incremental_savings_eur": -35.0,
                "marginal_savings_per_kwh": -4.2168675,
                "marginal_payback_years": float("inf"),
            }
        )

        result = BatteryEconomicAnalyzer.analyze(
            [recommendation]
        )[0]

        assert result.evidence[
            "incremental_savings_eur"
        ] == pytest.approx(-35.0)

        assert result.evidence[
            "marginal_savings_per_kwh"
        ] == pytest.approx(-4.2168675)

        assert result.evidence[
            "marginal_payback_years"
        ] == float("inf")

        assert "ahorro" in result.description
        assert "marginal" in result.description

    def test_when_no_npv_is_positive_selects_best_npv(self):
        recommendations = [
            make_recommendation(
                5.0,
                economic_npv_eur=-1500.0,
            ),
            make_recommendation(
                8.3,
                economic_npv_eur=-800.0,
            ),
            make_recommendation(
                16.6,
                economic_npv_eur=-1100.0,
            ),
        ]

        result = BatteryEconomicAnalyzer.analyze(
            recommendations
        )

        assert len(result) == 1
        assert result[0].capacity_kwh == pytest.approx(8.3)
        assert result[0].criterion == "no_positive_npv"
        assert result[0].title == (
            "La batería no resulta económicamente viable"
        )

    def test_zero_npv_is_not_considered_economically_viable(self):
        recommendations = [
            make_recommendation(
                5.0,
                economic_npv_eur=0.0,
            ),
            make_recommendation(
                8.3,
                economic_npv_eur=-100.0,
            ),
        ]

        result = BatteryEconomicAnalyzer.analyze(
            recommendations
        )[0]

        assert result.criterion == "no_positive_npv"
        assert result.capacity_kwh == pytest.approx(5.0)

    def test_tie_on_npv_selects_smaller_capacity(self):
        recommendations = [
            make_recommendation(
                8.3,
                economic_npv_eur=1000.0,
            ),
            make_recommendation(
                16.6,
                economic_npv_eur=1000.0,
            ),
        ]

        result = BatteryEconomicAnalyzer.analyze(
            recommendations
        )[0]

        assert result.capacity_kwh == pytest.approx(8.3)

    def test_non_finite_npv_candidates_are_ignored(self):
        recommendations = [
            make_recommendation(
                5.0,
                economic_npv_eur=float("nan"),
            ),
            make_recommendation(
                8.3,
                economic_npv_eur=1000.0,
            ),
        ]

        result = BatteryEconomicAnalyzer.analyze(
            recommendations
        )[0]

        assert result.capacity_kwh == pytest.approx(8.3)

    def test_all_non_finite_npv_returns_empty(self):
        recommendations = [
            make_recommendation(
                5.0,
                economic_npv_eur=float("nan"),
            ),
            make_recommendation(
                8.3,
                economic_npv_eur=float("inf"),
            ),
            make_recommendation(
                16.6,
                economic_npv_eur=float("-inf"),
            ),
        ]

        assert BatteryEconomicAnalyzer.analyze(
            recommendations
        ) == []

    def test_infinite_payback_is_reported_as_unrecovered(self):
        recommendation = make_recommendation(
            8.3,
            economic_npv_eur=-500.0,
            economic_payback_years=float("inf"),
        )

        result = BatteryEconomicAnalyzer.analyze(
            [recommendation]
        )[0]

        assert "no se alcanza" in result.description

    def test_selects_best_economic_capacity_from_realistic_candidates(self):
        recommendations = [
            make_recommendation(
                5.0,
                economic_npv_eur=850.0,
                economic_irr_percent=8.2,
                economic_payback_years=9.4,
                annual_additional_savings_eur=320.0,
                incremental_battery_cost_eur=1248.50,
            ),
            make_recommendation(
                8.3,
                economic_npv_eur=1250.0,
                economic_irr_percent=10.7,
                economic_payback_years=7.8,
                annual_additional_savings_eur=455.0,
                incremental_battery_cost_eur=2072.51,
            ),
            make_recommendation(
                16.6,
                economic_npv_eur=980.0,
                economic_irr_percent=7.1,
                economic_payback_years=10.2,
                annual_additional_savings_eur=590.0,
                incremental_battery_cost_eur=2072.51,
            ),
            make_recommendation(
                24.9,
                economic_npv_eur=420.0,
                economic_irr_percent=4.8,
                economic_payback_years=14.1,
                annual_additional_savings_eur=650.0,
                incremental_battery_cost_eur=2072.51,
            ),
            make_recommendation(
                30.0,
                economic_npv_eur=-150.0,
                economic_irr_percent=3.4,
                economic_payback_years=17.8,
                annual_additional_savings_eur=675.0,
                incremental_battery_cost_eur=1271.97,
            ),
        ]

        recommendations[1] = BatteryRecommendation(
            **{
                **recommendations[1].__dict__,
                "incremental_savings_eur": 135.0,
                "marginal_savings_per_kwh": 40.9090909,
                "marginal_payback_years": 15.352,
            }
        )

        result = BatteryEconomicAnalyzer.analyze(
            recommendations
        )

        assert len(result) == 1

        recommendation = result[0]

        assert recommendation.capacity_kwh == pytest.approx(8.3)
        assert recommendation.criterion == (
            BatteryEconomicAnalyzer.CRITERION_POSITIVE_NPV
        )

        assert recommendation.evidence[
            "economic_npv_eur"
        ] == pytest.approx(1250.0)

        assert recommendation.evidence[
            "annual_additional_savings_eur"
        ] == pytest.approx(455.0)

        assert recommendation.evidence[
            "incremental_savings_eur"
        ] == pytest.approx(135.0)

        assert recommendation.evidence[
            "marginal_savings_per_kwh"
        ] == pytest.approx(40.9090909)

        assert recommendation.evidence[
            "marginal_payback_years"
        ] == pytest.approx(15.352)