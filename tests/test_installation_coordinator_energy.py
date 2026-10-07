import pandas as pd
import pytest

from helios.core.consumption_scenario import ConsumptionScenario
from helios.core.energy_recommendation import EnergyRecommendation
from helios.core.energy_recommender import EnergyRecommender
from helios.ev.scenario import EVScenario
from helios.solar.battery_economic_model import (
    CombinedEconomicConfiguration,
)
from helios.solar.installation_configuration import (
    InstallationConfiguration,
)
from helios.solar.installation_constraints import (
    InstallationConstraints,
)
from helios.solar.installation_coordinator import (
    InstallationCoordinator,
)
from helios.solar.installation_evaluation import (
    InstallationEvaluator,
)
from helios.solar.installation_optimizer import (
    InstallationOptimizer,
)
from helios.solar.installation_recommendation import (
    InstallationRecommendation,
)
from helios.solar.installation_recommendation import (
    InstallationRecommender,
)
from helios.solar.installation_candidate import (
    InstallationCandidate,
)
from helios.solar.production_profile import (
    SolarProductionProfile,
)

from helios.solar.installation_costs import (
    InstallationCostConfiguration,
)

def _configuration() -> InstallationConfiguration:
    return InstallationConfiguration(
        available_area_m2=100.0,
        panel_width_m=1.134,
        panel_height_m=2.278,
        panel_power_wp=540.0,
        min_panels=5,
        max_panels=10,
        panel_orientation="auto",
        maintenance_passage_required=False,
        maintenance_passage_width_m=0.45,
        maintenance_passage_orientation="auto",
    )


def _constraints() -> InstallationConstraints:
    return InstallationConstraints(
        available_area_m2=100.0,
        panel_width_m=1.134,
        panel_height_m=2.278,
        panel_power_wp=540.0,
        min_panels=5,
        max_panels=10,
        panel_orientation="auto",
        maintenance_passage_required=False,
        maintenance_passage_width_m=0.45,
        maintenance_passage_orientation="auto",
    )


def _coordinator(
    production_calculator,
    *,
    energy_recommender=None,
) -> InstallationCoordinator:
    constraints = _constraints()

    optimizer = InstallationOptimizer(
        constraints,
    )

    evaluator = InstallationEvaluator(
        constraints,
    )

    recommender = InstallationRecommender()

    return InstallationCoordinator(
        optimizer=optimizer,
        evaluator=evaluator,
        recommender=recommender,
        production_calculator=production_calculator,
        energy_recommender=energy_recommender,
    )


def _consumption_scenario() -> ConsumptionScenario:
    index = pd.date_range(
        "2025-01-01 00:00:00",
        periods=8760,
        freq="h",
    )

    consumption = pd.Series(
        1.0,
        index=index,
    )

    return ConsumptionScenario(
        hourly_consumption=consumption,
        reference_year=2025,
    )


def _production_profile(
    installed_power_kwp: float,
    annual_production_kwh: float,
) -> SolarProductionProfile:
    index = pd.date_range(
        "2025-01-01 00:00:00",
        periods=8760,
        freq="h",
    )

    hourly_value = annual_production_kwh / 8760.0

    return SolarProductionProfile(
        hourly_production=pd.Series(
            hourly_value,
            index=index,
        ),
        reference_year=2025,
        installed_power_kwp=installed_power_kwp,
    )


def _ev_scenario() -> EVScenario:
    index = pd.date_range(
        "2025-01-01 00:00:00",
        periods=8760,
        freq="h",
    )

    return EVScenario(
        hourly_consumption=pd.Series(
            0.0,
            index=index,
        ),
        reference_year=2025,
    )


def _economic_configuration_factory(
    installation_cost_eur: float = 12000.0,
):
    def factory(evaluation):
        return CombinedEconomicConfiguration(
            installation_cost_eur=installation_cost_eur,
            battery_cost_eur=2497.0,
            annual_pv_savings_eur=2000.0,
            annual_battery_additional_savings_eur=500.0,
        )

    return factory


def _production_calculator_factory(
    calls: list[int],
):
    def calculate(candidate: InstallationCandidate):
        calls.append(candidate.panel_count)

        return _production_profile(
            installed_power_kwp=candidate.installed_power_kwp,
            annual_production_kwh=(
                candidate.installed_power_kwp * 1400.0
            ),
        )

    return calculate


def test_recommend_energy_returns_integral_recommendation():
    production_calls = []

    coordinator = _coordinator(
        _production_calculator_factory(production_calls),
    )

    result = coordinator.recommend_energy(
        configuration=_configuration(),
        annual_consumption_kwh=8760.0,
        consumption_scenario=_consumption_scenario(),
        candidate_capacities_kwh=[5.0],
        max_charge_power_kw=5.0,
        max_discharge_power_kw=5.0,
    )

    assert isinstance(
        result,
        EnergyRecommendation,
    )

    assert isinstance(
        result.installation_recommendation,
        InstallationRecommendation,
    )


def test_recommend_energy_calculates_production_for_each_candidate():
    production_calls = []

    coordinator = _coordinator(
        _production_calculator_factory(production_calls),
    )

    result = coordinator.recommend_energy(
        configuration=_configuration(),
        annual_consumption_kwh=8760.0,
        consumption_scenario=_consumption_scenario(),
        candidate_capacities_kwh=[5.0],
        max_charge_power_kw=5.0,
        max_discharge_power_kw=5.0,
    )

    assert result is not None
    assert production_calls
    assert len(production_calls) == len(set(production_calls))


def test_recommend_energy_propagates_ev_scenario():
    production_calls = []

    coordinator = _coordinator(
        _production_calculator_factory(production_calls),
    )

    ev_scenario = _ev_scenario()

    result = coordinator.recommend_energy(
        configuration=_configuration(),
        annual_consumption_kwh=8760.0,
        consumption_scenario=_consumption_scenario(),
        candidate_capacities_kwh=[5.0],
        max_charge_power_kw=5.0,
        max_discharge_power_kw=5.0,
        ev_scenario=ev_scenario,
    )

    assert result.ev_scenario is ev_scenario
    assert (
        result.battery_recommendation is not None
    )


def test_recommend_energy_defaults_to_combined_npv():
    production_calls = []

    coordinator = _coordinator(
        _production_calculator_factory(production_calls),
    )

    result = coordinator.recommend_energy(
        configuration=_configuration(),
        annual_consumption_kwh=8760.0,
        consumption_scenario=_consumption_scenario(),
        candidate_capacities_kwh=[5.0],
        max_charge_power_kw=5.0,
        max_discharge_power_kw=5.0,
    )

    assert result.optimization_criterion == "combined_npv"


def test_recommend_energy_accepts_combined_payback():
    production_calls = []

    coordinator = _coordinator(
        _production_calculator_factory(production_calls),
    )

    result = coordinator.recommend_energy(
        configuration=_configuration(),
        annual_consumption_kwh=8760.0,
        consumption_scenario=_consumption_scenario(),
        candidate_capacities_kwh=[5.0],
        max_charge_power_kw=5.0,
        max_discharge_power_kw=5.0,
        optimization_criterion="combined_payback",
    )

    assert result.optimization_criterion == "combined_payback"


def test_recommend_energy_passes_economic_configuration_factory():
    production_calls = []
    factory_calls = []

    def factory(evaluation, production_profile):
        factory_calls.append(
            (
                evaluation.panel_count,
                production_profile.installed_power_kwp,
            )
        )

        return CombinedEconomicConfiguration(
            installation_cost_eur=12000.0,
            battery_cost_eur=2497.0,
            annual_pv_savings_eur=2000.0,
            annual_battery_additional_savings_eur=500.0,
        )

    coordinator = _coordinator(
        _production_calculator_factory(production_calls),
    )

    result = coordinator.recommend_energy(
        configuration=_configuration(),
        annual_consumption_kwh=8760.0,
        consumption_scenario=_consumption_scenario(),
        candidate_capacities_kwh=[5.0],
        max_charge_power_kw=5.0,
        max_discharge_power_kw=5.0,
        economic_configuration_factory=factory,
    )

    assert result is not None
    assert factory_calls
    assert len(factory_calls) == len(set(factory_calls))


def test_existing_recommend_method_is_preserved():
    production_calls = []

    coordinator = _coordinator(
        _production_calculator_factory(production_calls),
    )

    result = coordinator.recommend(
        configuration=_configuration(),
        annual_consumption_kwh=8760.0,
    )

    assert isinstance(
        result,
        InstallationRecommendation,
    )


def test_recommend_energy_rejects_invalid_production_profile():
    def invalid_production_calculator(candidate):
        return object()

    coordinator = _coordinator(
        invalid_production_calculator,
    )

    with pytest.raises(
        TypeError,
        match="SolarProductionProfile",
    ):
        coordinator.recommend_energy(
            configuration=_configuration(),
            annual_consumption_kwh=8760.0,
            consumption_scenario=_consumption_scenario(),
            candidate_capacities_kwh=[5.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
        )


@pytest.mark.parametrize(
    "candidate_capacities",
    [
        [],
        [-1.0],
    ],
)
def test_recommend_energy_rejects_invalid_battery_capacities(
    candidate_capacities,
):
    production_calls = []

    coordinator = _coordinator(
        _production_calculator_factory(production_calls),
    )

    with pytest.raises(
        ValueError,
    ):
        coordinator.recommend_energy(
            configuration=_configuration(),
            annual_consumption_kwh=8760.0,
            consumption_scenario=_consumption_scenario(),
            candidate_capacities_kwh=candidate_capacities,
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
        )


@pytest.mark.parametrize(
    "min_soc,max_soc",
    [
        (0.90, 0.10),
        (-0.10, 0.90),
        (0.10, 1.10),
    ],
)
def test_recommend_energy_rejects_invalid_soc_configuration(
    min_soc,
    max_soc,
):
    production_calls = []

    coordinator = _coordinator(
        _production_calculator_factory(production_calls),
    )

    with pytest.raises(
        ValueError,
    ):
        coordinator.recommend_energy(
            configuration=_configuration(),
            annual_consumption_kwh=8760.0,
            consumption_scenario=_consumption_scenario(),
            candidate_capacities_kwh=[5.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            min_soc=min_soc,
            max_soc=max_soc,
        )

def test_recommend_energy_accepts_installation_cost_configuration():
    production_calls = []

    coordinator = _coordinator(
        _production_calculator_factory(production_calls),
    )

    cost_configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
    )

    result = coordinator.recommend_energy(
        configuration=_configuration(),
        annual_consumption_kwh=8760.0,
        consumption_scenario=_consumption_scenario(),
        candidate_capacities_kwh=[5.0],
        max_charge_power_kw=5.0,
        max_discharge_power_kw=5.0,
        installation_cost_configuration=cost_configuration,
    )

    assert isinstance(
        result,
        EnergyRecommendation,
    )

def test_recommend_energy_rejects_invalid_installation_cost_configuration():
    production_calls = []

    coordinator = _coordinator(
        _production_calculator_factory(production_calls),
    )

    with pytest.raises(
        TypeError,
        match="InstallationCostConfiguration",
    ):
        coordinator.recommend_energy(
            configuration=_configuration(),
            annual_consumption_kwh=8760.0,
            consumption_scenario=_consumption_scenario(),
            candidate_capacities_kwh=[5.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            installation_cost_configuration=100.0,
        )


def test_recommend_energy_rejects_both_cost_configuration_and_factory():
    production_calls = []

    coordinator = _coordinator(
        _production_calculator_factory(production_calls),
    )

    cost_configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
    )

    with pytest.raises(
        ValueError,
        match="mutually exclusive",
    ):
        coordinator.recommend_energy(
            configuration=_configuration(),
            annual_consumption_kwh=8760.0,
            consumption_scenario=_consumption_scenario(),
            candidate_capacities_kwh=[5.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            installation_cost_configuration=cost_configuration,
            economic_configuration_factory=(
                _economic_configuration_factory()
            ),
        )

def test_recommend_energy_uses_panel_count_for_installation_cost():
    production_calls = []
    captured_configurations = []

    class CapturingEnergyRecommender(EnergyRecommender):
        def recommend(self, **kwargs):
            economic_factory = kwargs[
                "economic_configuration_factory"
            ]

            for evaluation in kwargs["evaluations"]:
                production_profile = kwargs[
                    "production_profiles"
                ][evaluation.panel_count]

                configuration = economic_factory(
                    evaluation,
                    production_profile,
                )

                captured_configurations.append(
                    (
                        evaluation.panel_count,
                        configuration.installation_cost_eur,
                    )
                )

            return super().recommend(
                **kwargs,
            )

    coordinator = _coordinator(
        _production_calculator_factory(
            production_calls,
        ),
        energy_recommender=CapturingEnergyRecommender(),
    )

    cost_configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
    )

    coordinator.recommend_energy(
        configuration=_configuration(),
        annual_consumption_kwh=8760.0,
        consumption_scenario=_consumption_scenario(),
        candidate_capacities_kwh=[5.0],
        max_charge_power_kw=5.0,
        max_discharge_power_kw=5.0,
        installation_cost_configuration=cost_configuration,
    )

    assert captured_configurations == [
        (panel_count, panel_count * 100.0)
        for panel_count in range(5, 11)
    ]