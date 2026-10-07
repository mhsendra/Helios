import pandas as pd
import pytest

from dataclasses import replace

from helios.core.consumption_scenario import ConsumptionScenario
from helios.core.energy_recommendation import EnergyRecommendation
from helios.core.energy_recommender import EnergyRecommender

from helios.ev.scenario import EVScenario

from helios.solar.battery_economic_model import (
    CombinedEconomicConfiguration,
)
from helios.solar.battery_recommendation import BatteryRecommendation

from helios.solar.installation_candidate import (
    InstallationCandidate,
)
from helios.solar.installation_evaluation import (
    InstallationEvaluation,
)

from helios.solar.production_profile import (
    SolarProductionProfile,
)

from helios.solar.installation_recommendation import (
    InstallationRecommendation,
)

def _consumption_scenario():
    index = pd.date_range(
        "2025-01-01 00:00:00",
        periods=8760,
        freq="h",
    )

    return ConsumptionScenario(
        hourly_consumption=pd.Series(
            1.0,
            index=index,
        ),
        reference_year=2025,
    )


def _production_profile(
    installed_power_kwp,
    annual_production_kwh,
):
    index = pd.date_range(
        "2025-01-01 00:00:00",
        periods=8760,
        freq="h",
    )

    hourly_value = (
        annual_production_kwh / 8760.0
    )

    return SolarProductionProfile(
        hourly_production=pd.Series(
            hourly_value,
            index=index,
        ),
        reference_year=2025,
        installed_power_kwp=installed_power_kwp,
    )


def _evaluation(panel_count, installed_power_kwp):
    candidate = InstallationCandidate(
        panel_count=panel_count,
        panel_power_wp=540,
        panel_area_m2=2.0,
    )
    return InstallationEvaluation(
        candidate=candidate,
        available_area_m2=100.0,
    )


class FakeBatteryOptimizer:
    def __init__(self, recommendations):
        self.recommendations = recommendations
        self.calls = []

    def optimize(
        self,
        consumption_scenario,
        production_profile,
        candidate_capacities_kwh,
        **kwargs,
    ):
        self.calls.append(
            {
                "production_profile": production_profile,
                "candidate_capacities_kwh": (
                    candidate_capacities_kwh
                ),
                "kwargs": kwargs,
            }
        )

        return self.recommendations[
            production_profile.installed_power_kwp
        ]


def _battery_recommendation(
    capacity_kwh,
    combined_npv_eur,
):
    return BatteryRecommendation(
        capacity_kwh=capacity_kwh,
        max_charge_power_kw=5.0,
        max_discharge_power_kw=5.0,
        annual_consumption_kwh=8760.0,
        annual_production_kwh=10000.0,
        annual_surplus_kwh=1000.0,
        annual_export_kwh=500.0,
        annual_grid_import_kwh=100.0,
        annual_battery_charge_kwh=500.0,
        annual_battery_discharge_kwh=450.0,
        self_consumption_kwh=8660.0,
        self_sufficiency_percent=98.85,
        equivalent_cycles=50.0,
        combined_economic_npv_eur=combined_npv_eur,
    )


class TestEnergyRecommender:

    def test_selects_best_combination_by_combined_npv(
        self,
    ):
        consumption = _consumption_scenario()

        evaluation_5 = _evaluation(
            panel_count=10,
            installed_power_kwp=5.4,
        )
        evaluation_10 = _evaluation(
            panel_count=15,
            installed_power_kwp=8.1,
        )

        profiles = {
            10: _production_profile(
                5.4,
                8000.0,
            ),
            15: _production_profile(
                8.1,
                12000.0,
            ),
        }

        optimizer = FakeBatteryOptimizer(
            {
                5.4: _battery_recommendation(
                    8.3,
                    2500.0,
                ),
                8.1: _battery_recommendation(
                    8.3,
                    4200.0,
                ),
            }
        )

        recommender = EnergyRecommender(
            battery_optimizer=optimizer,
        )

        result = recommender.recommend(
            evaluations=[
                evaluation_5,
                evaluation_10,
            ],
            annual_consumption_kwh=8760.0,
            consumption_scenario=consumption,
            production_profiles=profiles,
            candidate_capacities_kwh=[
                5.0,
                8.3,
                16.6,
            ],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
        )

        assert isinstance(
            result,
            EnergyRecommendation,
        )

        assert result.panel_count == 15
        assert result.installed_power_kwp == pytest.approx(
            8.1
        )
        assert result.battery_capacity_kwh == pytest.approx(
            8.3
        )
        assert result.combined_economic_npv_eur == pytest.approx(
            4200.0
        )
        assert result.optimization_criterion == "combined_npv"

        assert len(optimizer.calls) == 2

    def test_passes_ev_to_battery_optimizer(
        self,
    ):
        consumption = _consumption_scenario()

        index = consumption.hourly_consumption.index

        ev = EVScenario(
            hourly_consumption=pd.Series(
                1.0 / 8760.0 * 1000.0,
                index=index,
            ),
            reference_year=2025,
        )

        evaluation = _evaluation(
            panel_count=15,
            installed_power_kwp=8.1,
        )

        profiles = {
            15: _production_profile(
                8.1,
                12000.0,
            ),
        }

        optimizer = FakeBatteryOptimizer(
            {
                8.1: _battery_recommendation(
                    8.3,
                    4200.0,
                )
            }
        )

        recommender = EnergyRecommender(
            battery_optimizer=optimizer,
        )

        result = recommender.recommend(
            evaluations=[evaluation],
            annual_consumption_kwh=8760.0,
            consumption_scenario=consumption,
            production_profiles=profiles,
            candidate_capacities_kwh=[8.3],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            ev_scenario=ev,
        )

        assert result.ev_scenario is ev

        assert optimizer.calls[0]["kwargs"][
            "ev_scenario"
        ] is ev

    def test_uses_installation_specific_economic_configuration(
        self,
    ):
        consumption = _consumption_scenario()

        evaluation = _evaluation(
            panel_count=15,
            installed_power_kwp=8.1,
        )

        profiles = {
            15: _production_profile(
                8.1,
                12000.0,
            ),
        }

        optimizer = FakeBatteryOptimizer(
            {
                8.1: _battery_recommendation(
                    8.3,
                    4200.0,
                )
            }
        )

        recommender = EnergyRecommender(
            battery_optimizer=optimizer,
        )

        def economic_configuration_factory(
            candidate_evaluation,
            production_profile,
        ):
            assert candidate_evaluation is evaluation
            assert production_profile is profiles[15]

            return CombinedEconomicConfiguration(
                installation_cost_eur=12000.0,
                battery_cost_eur=0.0,
                annual_pv_savings_eur=2500.0,
                annual_battery_additional_savings_eur=0.0,
            )

        recommender.recommend(
            evaluations=[evaluation],
            annual_consumption_kwh=8760.0,
            consumption_scenario=consumption,
            production_profiles=profiles,
            candidate_capacities_kwh=[8.3],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            economic_configuration_factory=(
                economic_configuration_factory
            ),
        )

        configuration = optimizer.calls[0][
            "kwargs"
        ][
            "combined_economic_configuration"
        ]

        assert isinstance(
            configuration,
            CombinedEconomicConfiguration,
        )

        assert configuration.installation_cost_eur == pytest.approx(
            12000.0
        )

    def test_rejects_invalid_optimization_criterion(
        self,
    ):
        consumption = _consumption_scenario()

        evaluation = _evaluation(
            panel_count=15,
            installed_power_kwp=8.1,
        )

        profiles = {
            15: _production_profile(
                8.1,
                12000.0,
            ),
        }

        recommender = EnergyRecommender(
            battery_optimizer=FakeBatteryOptimizer(
                {
                    8.1: _battery_recommendation(
                        8.3,
                        4200.0,
                    )
                }
            )
        )

        with pytest.raises(
            ValueError,
            match=(
                "optimization_criterion must be one of"
            ),
        ):
            recommender.recommend(
                evaluations=[evaluation],
                annual_consumption_kwh=8760.0,
                consumption_scenario=consumption,
                production_profiles=profiles,
                candidate_capacities_kwh=[8.3],
                max_charge_power_kw=5.0,
                max_discharge_power_kw=5.0,
                optimization_criterion="invalid",
            )

    def test_recommend_selects_installation_by_combined_npv(self):
        evaluations = [
            _evaluation(
                panel_count=10,
                installed_power_kwp=5.4,
            ),
            _evaluation(
                panel_count=15,
                installed_power_kwp=8.1,
            ),
        ]

        production_profiles = {
            10: _production_profile(
                installed_power_kwp=5.4,
                annual_production_kwh=8_000.0,
            ),
            15: _production_profile(
                installed_power_kwp=8.1,
                annual_production_kwh=12_000.0,
            ),
        }

        recommendations = {
            5.4: _battery_recommendation(
                capacity_kwh=8.3,
                combined_npv_eur=1_000.0,
            ),
            8.1: _battery_recommendation(
                capacity_kwh=8.3,
                combined_npv_eur=2_000.0,
            ),
        }

        class FakeBatteryOptimizer:
            def optimize(self, *args, **kwargs):
                production_profile = args[1]

                return recommendations[
                    production_profile.installed_power_kwp
                ]

        recommender = EnergyRecommender(
            battery_optimizer=FakeBatteryOptimizer()
        )

        result = recommender.recommend(
            evaluations=evaluations,
            annual_consumption_kwh=10_000.0,
            consumption_scenario=_consumption_scenario(),
            production_profiles=production_profiles,
            candidate_capacities_kwh=[5.0, 8.3],
            max_charge_power_kw=8.0,
            max_discharge_power_kw=8.0,
            optimization_criterion="combined_npv",
        )

        assert result.panel_count == 15
        assert result.installed_power_kwp == 8.1
        assert result.combined_economic_npv_eur == 2_000.0

    def test_is_better_combined_payback_prefers_shorter_payback(self):
        evaluation = _evaluation(
            panel_count=15,
            installed_power_kwp=8.1,
        )

        installation = InstallationRecommendation(
            evaluation=evaluation,
            annual_consumption_kwh=10_000.0,
            annual_production_kwh=12_000.0,
            consumption_scenario=_consumption_scenario(),
            production_profile=_production_profile(
                installed_power_kwp=8.1,
                annual_production_kwh=12_000.0,
            ),
        )

        current_battery = replace(
            _battery_recommendation(
                capacity_kwh=8.3,
                combined_npv_eur=2_000.0,
            ),
            combined_economic_payback_years=8.0,
        )

        candidate_battery = replace(
            _battery_recommendation(
                capacity_kwh=8.3,
                combined_npv_eur=1_500.0,
            ),
            combined_economic_payback_years=5.0,
        )

        current = EnergyRecommendation(
            installation_recommendation=installation,
            battery_recommendation=current_battery,
        )

        candidate = EnergyRecommendation(
            installation_recommendation=installation,
            battery_recommendation=candidate_battery,
        )

        assert EnergyRecommender._is_better(
            candidate,
            current,
            "combined_payback",
        )

    def test_is_better_combined_npv_prefers_lower_battery_capacity(self):
        evaluation = _evaluation(
            panel_count=15,
            installed_power_kwp=8.1,
        )

        installation = InstallationRecommendation(
            evaluation=evaluation,
            annual_consumption_kwh=10_000.0,
            annual_production_kwh=12_000.0,
            consumption_scenario=_consumption_scenario(),
            production_profile=_production_profile(
                installed_power_kwp=8.1,
                annual_production_kwh=12_000.0,
            ),
        )

        current = EnergyRecommendation(
            installation_recommendation=installation,
            battery_recommendation=_battery_recommendation(
                capacity_kwh=8.3,
                combined_npv_eur=2_000.0,
            ),
        )

        candidate = EnergyRecommendation(
            installation_recommendation=installation,
            battery_recommendation=_battery_recommendation(
                capacity_kwh=5.0,
                combined_npv_eur=2_000.0,
            ),
        )

        assert EnergyRecommender._is_better(
            candidate,
            current,
            "combined_npv",
        )

    def test_recommend_calls_economic_configuration_factory_for_each_installation(
        self,
    ):
        evaluations = [
            _evaluation(
                panel_count=10,
                installed_power_kwp=5.4,
            ),
            _evaluation(
                panel_count=15,
                installed_power_kwp=8.1,
            ),
        ]

        production_profiles = {
            10: _production_profile(
                installed_power_kwp=5.4,
                annual_production_kwh=8_000.0,
            ),
            15: _production_profile(
                installed_power_kwp=8.1,
                annual_production_kwh=12_000.0,
            ),
        }

        received_evaluations = []

        class FakeBatteryOptimizer:
            def optimize(self, *args, **kwargs):
                return _battery_recommendation(
                    capacity_kwh=8.3,
                    combined_npv_eur=1_000.0,
                )

        def economic_configuration_factory(
            evaluation,
            production_profile,
        ):
            received_evaluations.append(
                (
                    evaluation,
                    production_profile,
                )
            )

            return CombinedEconomicConfiguration(
                installation_cost_eur=10_000.0,
                battery_cost_eur=2_000.0,
                annual_pv_savings_eur=1_500.0,
                annual_battery_additional_savings_eur=200.0,
            )

        recommender = EnergyRecommender(
            battery_optimizer=FakeBatteryOptimizer()
        )

        recommender.recommend(
            evaluations=evaluations,
            annual_consumption_kwh=10_000.0,
            consumption_scenario=_consumption_scenario(),
            production_profiles=production_profiles,
            candidate_capacities_kwh=[5.0, 8.3],
            max_charge_power_kw=8.0,
            max_discharge_power_kw=8.0,
            economic_configuration_factory=(
                economic_configuration_factory
            ),
            optimization_criterion="combined_npv",
        )

        assert received_evaluations == [
            (
                evaluations[0],
                production_profiles[10],
            ),
            (
                evaluations[1],
                production_profiles[15],
            ),
        ]

    def test_recommend_passes_ev_scenario_to_battery_optimizer(self):
        evaluation = _evaluation(
            panel_count=15,
            installed_power_kwp=8.1,
        )

        production_profile = _production_profile(
            installed_power_kwp=8.1,
            annual_production_kwh=12_000.0,
        )

        consumption_scenario = _consumption_scenario()

        ev_scenario = EVScenario(
            hourly_consumption=(
                consumption_scenario.hourly_consumption.copy()
            ),
            reference_year=2025,
        )

        received_ev_scenarios = []

        class FakeBatteryOptimizer:
            def optimize(self, *args, **kwargs):
                received_ev_scenarios.append(
                    kwargs["ev_scenario"]
                )

                return _battery_recommendation(
                    capacity_kwh=8.3,
                    combined_npv_eur=1_000.0,
                )

        recommender = EnergyRecommender(
            battery_optimizer=FakeBatteryOptimizer()
        )

        result = recommender.recommend(
            evaluations=[evaluation],
            annual_consumption_kwh=10_000.0,
            consumption_scenario=consumption_scenario,
            production_profiles={
                15: production_profile,
            },
            candidate_capacities_kwh=[5.0, 8.3],
            max_charge_power_kw=8.0,
            max_discharge_power_kw=8.0,
            ev_scenario=ev_scenario,
            optimization_criterion="combined_npv",
        )

        assert received_ev_scenarios == [ev_scenario]
        assert result.ev_scenario is ev_scenario

    def test_recommend_rejects_missing_production_profile(self):
        evaluation = _evaluation(
            panel_count=15,
            installed_power_kwp=8.1,
        )

        with pytest.raises(
            ValueError,
            match="Missing production profile",
        ):
            EnergyRecommender().recommend(
                evaluations=[evaluation],
                annual_consumption_kwh=10_000.0,
                consumption_scenario=_consumption_scenario(),
                production_profiles={},
                candidate_capacities_kwh=[5.0, 8.3],
                max_charge_power_kw=8.0,
                max_discharge_power_kw=8.0,
            )

    def test_recommendation_exposes_all_evaluated_options(self):
        evaluations = [
            _evaluation(5, 2.7),
            _evaluation(8, 4.32),
        ]

        production_profiles = {
            5: _production_profile(
                installed_power_kwp=2.7,
                annual_production_kwh=4000.0,
            ),
            8: _production_profile(
                installed_power_kwp=4.32,
                annual_production_kwh=7000.0,
            ),
        }

        recommender = EnergyRecommender(
            battery_optimizer=FakeBatteryOptimizer(
                {
                    2.7: _battery_recommendation(
                        capacity_kwh=5.0,
                        combined_npv_eur=1000.0,
                    ),
                    4.32: _battery_recommendation(
                        capacity_kwh=8.0,
                        combined_npv_eur=2000.0,
                    ),
                }
            )
        )

        result = recommender.recommend(
            evaluations=evaluations,
            annual_consumption_kwh=8760.0,
            consumption_scenario=_consumption_scenario(),
            production_profiles=production_profiles,
            candidate_capacities_kwh=[5.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
        )

        assert result.candidate_count == 2
        assert len(result.alternatives) == 2

        assert {
            option.panel_count
            for option in result.alternatives
        } == {5, 8}


    def test_best_recommendation_is_included_in_evaluated_options(self):
        evaluations = [
            _evaluation(5, 2.7),
            _evaluation(8, 4.32),
        ]

        production_profiles = {
            5: _production_profile(
                installed_power_kwp=2.7,
                annual_production_kwh=4000.0,
            ),
            8: _production_profile(
                installed_power_kwp=4.32,
                annual_production_kwh=7000.0,
            ),
        }

        recommender = EnergyRecommender(
            battery_optimizer=FakeBatteryOptimizer(
                {
                    2.7: _battery_recommendation(
                        capacity_kwh=5.0,
                        combined_npv_eur=1000.0,
                    ),
                    4.32: _battery_recommendation(
                        capacity_kwh=8.0,
                        combined_npv_eur=2000.0,
                    ),
                }
            )
        )

        result = recommender.recommend(
            evaluations=evaluations,
            annual_consumption_kwh=8760.0,
            consumption_scenario=_consumption_scenario(),
            production_profiles=production_profiles,
            candidate_capacities_kwh=[5.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
        )

        assert result.panel_count == 8
        assert result.battery_capacity_kwh == 8.0

        assert any(
            option.panel_count == result.panel_count
            and (
                option.battery_recommendation.capacity_kwh
                == result.battery_recommendation.capacity_kwh
            )
            for option in result.evaluated_options
        )

    def test_recommend_passes_matching_production_profile_to_economic_configuration_factory(
        self,
    ):
        evaluations = [
            _evaluation(
                panel_count=10,
                installed_power_kwp=5.4,
            ),
            _evaluation(
                panel_count=15,
                installed_power_kwp=8.1,
            ),
        ]

        production_profiles = {
            10: _production_profile(
                installed_power_kwp=5.4,
                annual_production_kwh=8_000.0,
            ),
            15: _production_profile(
                installed_power_kwp=8.1,
                annual_production_kwh=12_000.0,
            ),
        }

        received = []

        class FakeBatteryOptimizer:
            def optimize(self, *args, **kwargs):
                return _battery_recommendation(
                    capacity_kwh=8.3,
                    combined_npv_eur=1_000.0,
                )

        def economic_configuration_factory(
            evaluation,
            production_profile,
        ):
            received.append(
                (
                    evaluation,
                    production_profile,
                )
            )

            return CombinedEconomicConfiguration(
                installation_cost_eur=10_000.0,
                battery_cost_eur=0.0,
                annual_pv_savings_eur=2_000.0,
                annual_battery_additional_savings_eur=0.0,
            )

        recommender = EnergyRecommender(
            battery_optimizer=FakeBatteryOptimizer()
        )

        recommender.recommend(
            evaluations=evaluations,
            annual_consumption_kwh=10_000.0,
            consumption_scenario=_consumption_scenario(),
            production_profiles=production_profiles,
            candidate_capacities_kwh=[
                5.0,
                8.3,
            ],
            max_charge_power_kw=8.0,
            max_discharge_power_kw=8.0,
            economic_configuration_factory=(
                economic_configuration_factory
            ),
            optimization_criterion="combined_npv",
        )

        assert len(received) == 2

        assert received[0][0] is evaluations[0]
        assert received[0][1] is production_profiles[10]

        assert received[1][0] is evaluations[1]
        assert received[1][1] is production_profiles[15]

    def test_passes_installation_specific_economic_configuration_to_battery_optimizer(self):
        evaluations = [
            _evaluation(
                panel_count=10,
                installed_power_kwp=5.4,
            ),
            _evaluation(
                panel_count=15,
                installed_power_kwp=8.1,
            ),
        ]

        production_profiles = {
            10: _production_profile(
                installed_power_kwp=5.4,
                annual_production_kwh=8000.0,
            ),
            15: _production_profile(
                installed_power_kwp=8.1,
                annual_production_kwh=12000.0,
            ),
        }

        battery_recommendations = {
            5.4: BatteryRecommendation(
                capacity_kwh=5.0,
                max_charge_power_kw=5.0,
                max_discharge_power_kw=5.0,
                annual_consumption_kwh=10000.0,
                annual_production_kwh=8000.0,
                annual_surplus_kwh=1000.0,
                annual_export_kwh=500.0,
                annual_grid_import_kwh=3000.0,
                annual_battery_charge_kwh=500.0,
                annual_battery_discharge_kwh=450.0,
                self_consumption_kwh=7500.0,
                self_sufficiency_percent=75.0,
                equivalent_cycles=90.0,
                annual_additional_savings_eur=100.0,
            ),
            8.1: BatteryRecommendation(
                capacity_kwh=8.3,
                max_charge_power_kw=5.0,
                max_discharge_power_kw=5.0,
                annual_consumption_kwh=10000.0,
                annual_production_kwh=12000.0,
                annual_surplus_kwh=2000.0,
                annual_export_kwh=1000.0,
                annual_grid_import_kwh=2000.0,
                annual_battery_charge_kwh=1000.0,
                annual_battery_discharge_kwh=900.0,
                self_consumption_kwh=11000.0,
                self_sufficiency_percent=90.0,
                equivalent_cycles=108.4,
                annual_additional_savings_eur=200.0,
            ),
        }

        battery_optimizer = FakeBatteryOptimizer(
            battery_recommendations
        )

        economic_configurations = {
            5.4: CombinedEconomicConfiguration(
                installation_cost_eur=10000.0,
                battery_cost_eur=0.0,
                annual_pv_savings_eur=1000.0,
                annual_battery_additional_savings_eur=0.0,
            ),
            8.1: CombinedEconomicConfiguration(
                installation_cost_eur=14000.0,
                battery_cost_eur=0.0,
                annual_pv_savings_eur=1800.0,
                annual_battery_additional_savings_eur=0.0,
            ),
        }

        def economic_configuration_factory(
            evaluation,
            production_profile,
        ):
            return economic_configurations[
                production_profile.installed_power_kwp
            ]

        recommender = EnergyRecommender(
            battery_optimizer=battery_optimizer,
        )

        recommender.recommend(
            evaluations=evaluations,
            annual_consumption_kwh=10000.0,
            consumption_scenario=_consumption_scenario(),
            production_profiles=production_profiles,
            candidate_capacities_kwh=[5.0, 8.3],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            economic_configuration_factory=(
                economic_configuration_factory
            ),
        )

        assert len(battery_optimizer.calls) == 2

        assert (
            battery_optimizer.calls[0]["kwargs"][
                "combined_economic_configuration"
            ]
            == economic_configurations[5.4]
        )

        assert (
            battery_optimizer.calls[1]["kwargs"][
                "combined_economic_configuration"
            ]
            == economic_configurations[8.1]
        )