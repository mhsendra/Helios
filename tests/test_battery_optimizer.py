import pandas as pd
import pytest

from helios.core.consumption_scenario import ConsumptionScenario
from helios.solar.battery_optimizer import BatteryOptimizer
from helios.solar.battery_recommendation import BatteryRecommendation
from helios.solar.battery_economic_model import BatteryEconomicConfiguration
from helios.solar.production_profile import SolarProductionProfile
from helios.solar.battery_economic_model import CombinedEconomicConfiguration


REFERENCE_YEAR = 2025


def make_index():
    return pd.date_range(
        start=f"{REFERENCE_YEAR}-01-01",
        periods=8760,
        freq="h",
    )


def make_scenario(values):
    index = make_index()

    return ConsumptionScenario(
        hourly_consumption=pd.Series(
            values,
            index=index,
            dtype=float,
        )
    )


def make_profile(values):
    index = make_index()

    return SolarProductionProfile(
        hourly_production=pd.Series(
            values,
            index=index,
            dtype=float,
        ),
        reference_year=REFERENCE_YEAR,
        installed_power_kwp=1.0,
    )


def make_optimizer():
    return BatteryOptimizer()


class TestBatteryOptimizer:

    def test_evaluate_returns_recommendations_for_all_capacities(self):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        recommendations = make_optimizer().evaluate(
            consumption,
            production,
            [5.0, 8.3, 16.6],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
        )

        assert len(recommendations) == 3

        assert [
            recommendation.capacity_kwh
            for recommendation in recommendations
        ] == [5.0, 8.3, 16.6]

        assert all(
            isinstance(
                recommendation,
                BatteryRecommendation,
            )
            for recommendation in recommendations
        )

    def test_evaluate_sorts_capacities(self):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        recommendations = make_optimizer().evaluate(
            consumption,
            production,
            [16.6, 5.0, 8.3],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
        )

        assert [
            recommendation.capacity_kwh
            for recommendation in recommendations
        ] == [5.0, 8.3, 16.6]

    def test_evaluate_rejects_invalid_consumption_scenario(self):
        production = make_profile([1.0] * 8760)

        with pytest.raises(
            TypeError,
            match="consumption_scenario must be a ConsumptionScenario",
        ):
            make_optimizer().evaluate(
                "invalid",
                production,
                [5.0],
                max_charge_power_kw=5.0,
                max_discharge_power_kw=5.0,
            )

    def test_evaluate_rejects_invalid_production_profile(self):
        consumption = make_scenario([1.0] * 8760)

        with pytest.raises(
            TypeError,
            match="production_profile must be a SolarProductionProfile",
        ):
            make_optimizer().evaluate(
                consumption,
                "invalid",
                [5.0],
                max_charge_power_kw=5.0,
                max_discharge_power_kw=5.0,
            )

    def test_evaluate_rejects_empty_capacities(self):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        with pytest.raises(
            ValueError,
            match="candidate_capacities_kwh must not be empty",
        ):
            make_optimizer().evaluate(
                consumption,
                production,
                [],
                max_charge_power_kw=5.0,
                max_discharge_power_kw=5.0,
            )

    def test_evaluate_rejects_non_positive_capacities(self):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        with pytest.raises(
            ValueError,
            match="Battery capacities must be greater than zero",
        ):
            make_optimizer().evaluate(
                consumption,
                production,
                [0.0, 5.0],
                max_charge_power_kw=5.0,
                max_discharge_power_kw=5.0,
            )

    def test_evaluate_calculates_annual_metrics(self):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        recommendations = make_optimizer().evaluate(
            consumption,
            production,
            [5.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
        )

        recommendation = recommendations[0]

        assert recommendation.annual_consumption_kwh == pytest.approx(
            8760.0
        )

        assert recommendation.annual_production_kwh == pytest.approx(
            8760.0
        )

        assert recommendation.annual_surplus_kwh >= 0.0
        assert recommendation.annual_export_kwh >= 0.0
        assert recommendation.annual_grid_import_kwh >= 0.0
        assert recommendation.annual_battery_charge_kwh >= 0.0
        assert recommendation.annual_battery_discharge_kwh >= 0.0

    def test_evaluate_calculates_self_consumption_and_self_sufficiency(
        self,
    ):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        recommendation = make_optimizer().evaluate(
            consumption,
            production,
            [5.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
        )[0]

        assert recommendation.self_consumption_kwh >= 0.0
        assert 0.0 <= recommendation.self_sufficiency_percent <= 100.0

    def test_evaluate_calculates_equivalent_cycles(self):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        recommendation = make_optimizer().evaluate(
            consumption,
            production,
            [5.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
        )[0]

        assert recommendation.equivalent_cycles >= 0.0

    def test_evaluate_calculates_annual_additional_savings(self):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        recommendation = make_optimizer().evaluate(
            consumption,
            production,
            [5.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            annual_cost_without_battery_eur=1000.0,
            cost_calculator=lambda result: 400.0,
        )[0]

        assert recommendation.annual_cost_with_battery_eur == pytest.approx(
            400.0
        )

        assert recommendation.annual_additional_savings_eur == pytest.approx(
            600.0
        )

    def test_evaluate_calculates_incremental_battery_cost(self):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        recommendations = make_optimizer().evaluate(
            consumption,
            production,
            [5.0, 10.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
        )

        assert recommendations[0].incremental_battery_cost_eur == pytest.approx(
            0.0
        )

        assert recommendations[1].incremental_battery_cost_eur == pytest.approx(
            (10.0 - 5.0) * 249.70
        )

    def test_evaluate_calculates_incremental_savings(self):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        recommendations = make_optimizer().evaluate(
            consumption,
            production,
            [5.0, 10.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            annual_cost_without_battery_eur=1000.0,
            cost_calculator=lambda result: 400.0,
        )

        assert recommendations[0].incremental_savings_eur == pytest.approx(
            0.0
        )

        assert recommendations[1].incremental_savings_eur == pytest.approx(
            0.0
        )

    def test_evaluate_preserves_negative_incremental_savings(self):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        calls = 0

        def cost_calculator(result):
            nonlocal calls
            calls += 1

            if calls == 1:
                return 400.0

            return 450.0

        recommendations = make_optimizer().evaluate(
            consumption,
            production,
            [5.0, 10.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            annual_cost_without_battery_eur=1000.0,
            cost_calculator=cost_calculator,
        )

        assert recommendations[0].annual_additional_savings_eur == pytest.approx(
            600.0
        )

        assert recommendations[1].annual_additional_savings_eur == pytest.approx(
            550.0
        )

        assert recommendations[1].incremental_savings_eur == pytest.approx(
            -50.0
        )

        assert recommendations[1].marginal_savings_per_kwh == pytest.approx(
            -10.0
        )

        assert recommendations[1].marginal_payback_years == float("inf")

    def test_evaluate_calculates_marginal_savings_per_kwh(self):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        recommendations = make_optimizer().evaluate(
            consumption,
            production,
            [5.0, 10.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            annual_cost_without_battery_eur=1000.0,
            cost_calculator=lambda result: 400.0,
        )

        assert recommendations[0].marginal_savings_per_kwh == pytest.approx(
            0.0
        )

        assert recommendations[1].marginal_savings_per_kwh == pytest.approx(
            0.0
        )

    def test_evaluate_calculates_marginal_payback(self):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        recommendations = make_optimizer().evaluate(
            consumption,
            production,
            [5.0, 10.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            annual_cost_without_battery_eur=1000.0,
            cost_calculator=lambda result: 400.0,
        )

        assert recommendations[0].marginal_payback_years == float("inf")
        assert recommendations[1].marginal_payback_years == float("inf")

    def test_evaluate_calculates_economic_npv(self):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        economic_configuration = BatteryEconomicConfiguration(
            battery_cost_eur=1.0,
            annual_savings_eur=1.0,
            years=2,
            electricity_price_growth=0.0,
            pv_degradation=0.0,
            battery_degradation=0.0,
            annual_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        recommendation = make_optimizer().evaluate(
            consumption,
            production,
            [1.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            annual_cost_without_battery_eur=1000.0,
            cost_calculator=lambda result: 400.0,
            economic_configuration=economic_configuration,
        )[0]

        assert recommendation.economic_npv_eur == pytest.approx(
            -249.70 + 600.0 + 600.0
        )

    def test_evaluate_calculates_economic_irr(self):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        economic_configuration = BatteryEconomicConfiguration(
            battery_cost_eur=1.0,
            annual_savings_eur=1.0,
            years=2,
            electricity_price_growth=0.0,
            pv_degradation=0.0,
            battery_degradation=0.0,
            annual_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        recommendation = make_optimizer().evaluate(
            consumption,
            production,
            [1.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            annual_cost_without_battery_eur=1000.0,
            cost_calculator=lambda result: 400.0,
            economic_configuration=economic_configuration,
        )[0]

        assert recommendation.economic_irr_percent == pytest.approx(
            216.2652,
            rel=1e-4,
        )

    def test_evaluate_calculates_economic_payback(self):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        economic_configuration = BatteryEconomicConfiguration(
            battery_cost_eur=1.0,
            annual_savings_eur=1.0,
            years=2,
            electricity_price_growth=0.0,
            pv_degradation=0.0,
            battery_degradation=0.0,
            annual_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        recommendation = make_optimizer().evaluate(
            consumption,
            production,
            [1.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            annual_cost_without_battery_eur=1000.0,
            cost_calculator=lambda result: 400.0,
            economic_configuration=economic_configuration,
        )[0]

        assert recommendation.economic_payback_years == pytest.approx(
            249.70 / 600.0
        )

    def test_evaluate_calculates_economic_metrics_for_each_capacity(self):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        economic_configuration = BatteryEconomicConfiguration(
            battery_cost_eur=1.0,
            annual_savings_eur=1.0,
            years=2,
            electricity_price_growth=0.0,
            pv_degradation=0.0,
            battery_degradation=0.0,
            annual_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        recommendations = make_optimizer().evaluate(
            consumption,
            production,
            [1.0, 2.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            annual_cost_without_battery_eur=1000.0,
            cost_calculator=lambda result: 400.0,
            economic_configuration=economic_configuration,
        )

        assert len(recommendations) == 2

        first = recommendations[0]
        second = recommendations[1]

        assert first.capacity_kwh == pytest.approx(1.0)
        assert second.capacity_kwh == pytest.approx(2.0)

        assert first.economic_npv_eur == pytest.approx(
            -249.70 + 600.0 + 600.0
        )

        assert second.economic_npv_eur == pytest.approx(
            -499.40 + 600.0 + 600.0
        )

    def test_evaluate_does_not_mutate_economic_configuration(self):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        economic_configuration = BatteryEconomicConfiguration(
            battery_cost_eur=1234.0,
            annual_savings_eur=567.0,
            years=30,
            electricity_price_growth=0.02,
            pv_degradation=0.0035,
            battery_degradation=0.02,
            annual_maintenance_eur=10.0,
            maintenance_growth=0.02,
            discount_rate=0.05,
        )

        make_optimizer().evaluate(
            consumption,
            production,
            [1.0, 2.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            annual_cost_without_battery_eur=1000.0,
            cost_calculator=lambda result: 400.0,
            economic_configuration=economic_configuration,
        )

        assert economic_configuration.battery_cost_eur == 1234.0
        assert economic_configuration.annual_savings_eur == 567.0

    def test_evaluate_without_economic_configuration_keeps_default_metrics(
        self,
    ):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        recommendation = make_optimizer().evaluate(
            consumption,
            production,
            [1.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            annual_cost_without_battery_eur=1000.0,
            cost_calculator=lambda result: 400.0,
        )[0]

        assert recommendation.economic_npv_eur == 0.0
        assert recommendation.economic_irr_percent == 0.0
        assert recommendation.economic_payback_years == float("inf")

    def test_optimize_returns_best_technical_recommendation(self):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        recommendation = make_optimizer().optimize(
            consumption,
            production,
            [5.0, 8.3, 16.6],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
        )

        assert isinstance(
            recommendation,
            BatteryRecommendation,
        )

        assert recommendation.capacity_kwh > 0.0

    def test_optimize_keeps_smaller_capacity_on_energy_tie(self):
        consumption = make_scenario([0.0] * 8760)
        production = make_profile([0.0] * 8760)

        recommendation = make_optimizer().optimize(
            consumption,
            production,
            [5.0, 8.3],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
        )

        assert recommendation.capacity_kwh == pytest.approx(5.0)

    def test_optimize_uses_default_battery_cost_per_kwh(
        self,
    ):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        economic_configuration = BatteryEconomicConfiguration(
            battery_cost_eur=1.0,
            annual_savings_eur=1.0,
            years=2,
            electricity_price_growth=0.0,
            pv_degradation=0.0,
            battery_degradation=0.0,
            annual_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        recommendation = make_optimizer().optimize(
            consumption,
            production,
            [1.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            annual_cost_without_battery_eur=1000.0,
            cost_calculator=lambda result: 400.0,
            economic_configuration=economic_configuration,
        )

        assert recommendation.economic_npv_eur == pytest.approx(
            -249.70 + 600.0 + 600.0
        )


    def test_optimize_uses_custom_battery_cost_per_kwh(
        self,
    ):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        economic_configuration = BatteryEconomicConfiguration(
            battery_cost_eur=1.0,
            annual_savings_eur=1.0,
            years=2,
            electricity_price_growth=0.0,
            pv_degradation=0.0,
            battery_degradation=0.0,
            annual_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        recommendation = make_optimizer().optimize(
            consumption,
            production,
            [1.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            annual_cost_without_battery_eur=1000.0,
            cost_calculator=lambda result: 400.0,
            economic_configuration=economic_configuration,
            battery_cost_per_kwh_eur=300.0,
        )

        assert recommendation.economic_npv_eur == pytest.approx(
            -300.0 + 600.0 + 600.0
        )

    @pytest.mark.parametrize(
        "capacity",
        [float("nan"), float("inf"), float("-inf")],
    )
    def test_evaluate_rejects_non_finite_capacities(
        self,
        capacity,
    ):

        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        with pytest.raises(
            ValueError,
            match="Battery capacities must be greater than zero",
        ):
            make_optimizer().evaluate(
                consumption,
                production,
                [capacity],
                max_charge_power_kw=5.0,
                max_discharge_power_kw=5.0,
            )

    def test_select_recommendation_by_energy(self):
        recommendations = [
            BatteryRecommendation(
                capacity_kwh=5.0,
                max_charge_power_kw=5.0,
                max_discharge_power_kw=5.0,
                annual_consumption_kwh=1000.0,
                annual_production_kwh=1000.0,
                annual_surplus_kwh=500.0,
                annual_export_kwh=100.0,
                annual_grid_import_kwh=100.0,
                annual_battery_charge_kwh=200.0,
                annual_battery_discharge_kwh=150.0,
                self_consumption_kwh=900.0,
                self_sufficiency_percent=90.0,
                equivalent_cycles=30.0,
            ),
            BatteryRecommendation(
                capacity_kwh=10.0,
                max_charge_power_kw=5.0,
                max_discharge_power_kw=5.0,
                annual_consumption_kwh=1000.0,
                annual_production_kwh=1000.0,
                annual_surplus_kwh=500.0,
                annual_export_kwh=50.0,
                annual_grid_import_kwh=50.0,
                annual_battery_charge_kwh=300.0,
                annual_battery_discharge_kwh=250.0,
                self_consumption_kwh=950.0,
                self_sufficiency_percent=95.0,
                equivalent_cycles=27.0,
            ),
        ]

        result = BatteryOptimizer._select_recommendation(
            recommendations,
            "energy",
        )

        assert result.capacity_kwh == 10.0

    def test_select_recommendation_by_combined_npv(self):
        recommendations = [
            BatteryRecommendation(
                capacity_kwh=5.0,
                max_charge_power_kw=5.0,
                max_discharge_power_kw=5.0,
                annual_consumption_kwh=1000.0,
                annual_production_kwh=1000.0,
                annual_surplus_kwh=500.0,
                annual_export_kwh=100.0,
                annual_grid_import_kwh=100.0,
                annual_battery_charge_kwh=200.0,
                annual_battery_discharge_kwh=150.0,
                self_consumption_kwh=900.0,
                self_sufficiency_percent=90.0,
                equivalent_cycles=30.0,
                combined_economic_npv_eur=2500.0,
            ),
            BatteryRecommendation(
                capacity_kwh=10.0,
                max_charge_power_kw=5.0,
                max_discharge_power_kw=5.0,
                annual_consumption_kwh=1000.0,
                annual_production_kwh=1000.0,
                annual_surplus_kwh=500.0,
                annual_export_kwh=50.0,
                annual_grid_import_kwh=50.0,
                annual_battery_charge_kwh=300.0,
                annual_battery_discharge_kwh=250.0,
                self_consumption_kwh=950.0,
                self_sufficiency_percent=95.0,
                equivalent_cycles=27.0,
                combined_economic_npv_eur=1800.0,
            ),
        ]

        result = BatteryOptimizer._select_recommendation(
            recommendations,
            "combined_npv",
        )

        assert result.capacity_kwh == 5.0

    def test_select_recommendation_rejects_invalid_criterion(self):
        recommendation = BatteryRecommendation(
            capacity_kwh=5.0,
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            annual_consumption_kwh=1000.0,
            annual_production_kwh=1000.0,
            annual_surplus_kwh=500.0,
            annual_export_kwh=100.0,
            annual_grid_import_kwh=100.0,
            annual_battery_charge_kwh=200.0,
            annual_battery_discharge_kwh=150.0,
            self_consumption_kwh=900.0,
            self_sufficiency_percent=90.0,
            equivalent_cycles=30.0,
        )

        with pytest.raises(
            ValueError,
            match="optimization_criterion must be one of",
        ):
            BatteryOptimizer._select_recommendation(
                [recommendation],
                "invalid",
            )

    def test_optimize_uses_selected_optimization_criterion(
        self,
        monkeypatch,
    ):
        recommendations = [
            BatteryRecommendation(
                capacity_kwh=5.0,
                max_charge_power_kw=5.0,
                max_discharge_power_kw=5.0,
                annual_consumption_kwh=1000.0,
                annual_production_kwh=1500.0,
                annual_surplus_kwh=500.0,
                annual_export_kwh=400.0,
                annual_grid_import_kwh=100.0,
                annual_battery_charge_kwh=100.0,
                annual_battery_discharge_kwh=90.0,
                self_consumption_kwh=1100.0,
                self_sufficiency_percent=90.0,
                equivalent_cycles=18.0,
                combined_economic_npv_eur=3500.0,
            ),
            BatteryRecommendation(
                capacity_kwh=10.0,
                max_charge_power_kw=10.0,
                max_discharge_power_kw=10.0,
                annual_consumption_kwh=1000.0,
                annual_production_kwh=1500.0,
                annual_surplus_kwh=500.0,
                annual_export_kwh=300.0,
                annual_grid_import_kwh=50.0,
                annual_battery_charge_kwh=150.0,
                annual_battery_discharge_kwh=140.0,
                self_consumption_kwh=1200.0,
                self_sufficiency_percent=95.0,
                equivalent_cycles=14.0,
                combined_economic_npv_eur=2500.0,
            ),
        ]

        monkeypatch.setattr(
            BatteryOptimizer,
            "evaluate",
            lambda self, *args, **kwargs: recommendations,
        )

        optimizer = BatteryOptimizer()

        result = optimizer.optimize(
            consumption_scenario=object(),
            production_profile=object(),
            candidate_capacities_kwh=[5.0, 10.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            optimization_criterion="combined_npv",
        )
        assert result.capacity_kwh == pytest.approx(5.0)
        assert result.combined_economic_npv_eur == pytest.approx(3500.0)

    def test_evaluate_calculates_combined_economics_with_battery_cost(
        self,
    ):
        consumption = make_scenario([1.0] * 8760)
        production = make_profile([1.0] * 8760)

        combined_configuration = CombinedEconomicConfiguration(
            installation_cost_eur=10000.0,
            battery_cost_eur=0.0,
            annual_pv_savings_eur=1000.0,
            annual_battery_additional_savings_eur=600.0,
            years=2,
            electricity_price_growth=0.0,
            pv_initial_degradation=0.0,
            pv_degradation=0.0,
            battery_degradation=0.0,
            annual_pv_maintenance_eur=0.0,
            annual_battery_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        recommendations = make_optimizer().evaluate(
            consumption,
            production,
            [5.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            annual_cost_without_battery_eur=1000.0,
            cost_calculator=lambda result: 400.0,
            combined_economic_configuration=combined_configuration,
        )

        recommendation = recommendations[0]

        expected_battery_cost = 5.0 * 249.70

        expected_npv = (
            -10000.0
            - expected_battery_cost
            + 1600.0
            + 1600.0
        )

        assert recommendation.combined_economic_npv_eur == pytest.approx(
            expected_npv
        )

        assert combined_configuration.installation_cost_eur == pytest.approx(
            10000.0
        )

        assert combined_configuration.battery_cost_eur == pytest.approx(
            0.0
        )