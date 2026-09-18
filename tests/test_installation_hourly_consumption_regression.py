import pandas as pd

import pytest

from helios.core.consumption_scenario import ConsumptionScenario
from helios.solar.installation_coordinator import InstallationCoordinator
from helios.solar.installation_constraints import InstallationConstraints
from helios.solar.installation_configuration import InstallationConfiguration
from helios.solar.installation_evaluation import InstallationEvaluator
from helios.solar.installation_optimizer import InstallationOptimizer
from helios.solar.installation_candidate import InstallationCandidate
from helios.solar.installation_evaluation import InstallationEvaluation
from helios.solar.installation_recommendation import (
    InstallationRecommendation,
    InstallationRecommender,
)
from helios.solar.production_profile import SolarProductionProfile

class CapturingRecommender(InstallationRecommender):
    """Captures the hourly inputs that sizing must evaluate."""

    def __init__(self):
        self.consumption_scenario = None
        self.production_profiles = None

    def recommend(
        self,
        evaluations,
        annual_consumption_kwh,
        annual_productions_kwh,
        *,
        consumption_scenario,
        production_profiles,
    ):
        self.consumption_scenario = consumption_scenario
        self.production_profiles = production_profiles
        return super().recommend(
            evaluations=evaluations,
            annual_consumption_kwh=annual_consumption_kwh,
            annual_productions_kwh=annual_productions_kwh,
        )


def _scenario(*, pv_aligned: bool) -> ConsumptionScenario:
    index = pd.date_range(
        start="2025-01-01 00:00:00",
        periods=8760,
        freq="h",
    )

    consumption = pd.Series(0.0, index=index)

    if pv_aligned:
        consumption.iloc[12::24] = 1.0
    else:
        consumption.iloc[0::24] = 1.0

    return ConsumptionScenario(
        hourly_consumption=consumption,
        reference_year=2025,
    )


def _production_profile() -> SolarProductionProfile:
    index = pd.date_range(
        start="2025-01-01 00:00:00",
        periods=8760,
        freq="h",
    )

    production = pd.Series(0.0, index=index)
    production.iloc[12::24] = 1.0

    return SolarProductionProfile(
        hourly_production=production,
        reference_year=2025,
        installed_power_kwp=1.0,
    )


def _configuration() -> InstallationConfiguration:
    return InstallationConfiguration(
        available_area_m2=100.0,
        panel_width_m=1.134,
        panel_height_m=1.762,
        panel_power_wp=540,
        min_panels=5,
        max_panels=5,
        maintenance_passage_required=False,
        maintenance_passage_width_m=0.45,
        maintenance_passage_orientation="auto",
    )


def test_installation_sizing_receives_complete_consumption_scenario():
    """
    El dimensionamiento automático debe recibir el año sintético completo,
    no solamente su suma anual.
    """
    recommender = CapturingRecommender()

    coordinator = InstallationCoordinator(
        optimizer=InstallationOptimizer(
            _configuration().to_constraints()
        ),
        evaluator=InstallationEvaluator(
            InstallationConstraints(
                available_area_m2=100.0,
                panel_width_m=1.134,
                panel_height_m=1.762,
                panel_power_wp=540,
                min_panels=5,
                max_panels=5,
            )
        ),
        recommender=recommender,
        production_calculator=lambda candidate: _production_profile(),
    )

    scenario = _scenario(pv_aligned=True)

    coordinator.recommend(
        configuration=_configuration(),
        annual_consumption_kwh=scenario.annual_consumption,
        consumption_scenario=scenario,
    )

    assert recommender.consumption_scenario is scenario
    assert recommender.production_profiles[5].hourly_production.equals(
        _production_profile().hourly_production
    )


def test_same_annual_consumption_does_not_hide_hourly_difference():
    """
    Dos años sintéticos con el mismo consumo anual deben conservar su
    distribución horaria, porque esa distribución determina la coincidencia
    real entre consumo y producción FV.
    """
    aligned = _scenario(pv_aligned=True)
    shifted = _scenario(pv_aligned=False)

    assert aligned.annual_consumption == shifted.annual_consumption
    assert not aligned.hourly_consumption.equals(
        shifted.hourly_consumption
    )

def test_hourly_coincidence_changes_self_consumption():
    """
    La misma producción anual puede generar distinto autoconsumo según
    su coincidencia horaria con el consumo sintético.
    """
    scenario = _scenario(pv_aligned=True)

    aligned_profile = _production_profile()

    shifted_index = aligned_profile.hourly_production.index
    shifted_production = pd.Series(
        0.0,
        index=shifted_index,
    )
    shifted_production.iloc[0::24] = 1.0

    shifted_profile = SolarProductionProfile(
        hourly_production=shifted_production,
        reference_year=2025,
        installed_power_kwp=1.0,
    )

    aligned_recommendation = InstallationRecommendation(
        evaluation=None,
        annual_consumption_kwh=scenario.annual_consumption,
        annual_production_kwh=aligned_profile.hourly_production.sum(),
        consumption_scenario=scenario,
        production_profile=aligned_profile,
    )

    shifted_recommendation = InstallationRecommendation(
        evaluation=None,
        annual_consumption_kwh=scenario.annual_consumption,
        annual_production_kwh=shifted_profile.hourly_production.sum(),
        consumption_scenario=scenario,
        production_profile=shifted_profile,
    )

    assert (
        aligned_recommendation.annual_production_kwh
        == shifted_recommendation.annual_production_kwh
    )

    assert (
        aligned_recommendation.self_consumption_kwh
        > shifted_recommendation.self_consumption_kwh
    )

def test_recommendation_aligns_different_reference_years_by_month_day_hour():
    """
    El consumo representativo y el perfil solar pueden pertenecer a años
    de referencia distintos, pero deben alinearse por mes, día y hora.
    """
    consumption_index = pd.date_range(
        start="2025-01-01 00:00:00",
        periods=8760,
        freq="h",
    )

    solar_index = pd.date_range(
        start="2023-01-01 00:00:00",
        periods=8760,
        freq="h",
    )

    consumption = pd.Series(
        0.0,
        index=consumption_index,
    )

    # 12:00 de cada día del año 2025
    consumption.iloc[12::24] = 1.0

    scenario = ConsumptionScenario(
        hourly_consumption=consumption,
        reference_year=2025,
    )

    production = pd.Series(
        0.0,
        index=solar_index,
    )

    # 12:00 de cada día del año 2023
    production.iloc[12::24] = 1.0

    profile = SolarProductionProfile(
        hourly_production=production,
        reference_year=2023,
        installed_power_kwp=1.0,
    )

    recommendation = InstallationRecommendation(
        evaluation=None,
        annual_consumption_kwh=scenario.annual_consumption,
        annual_production_kwh=profile.hourly_production.sum(),
        consumption_scenario=scenario,
        production_profile=profile,
    )

    assert recommendation.self_consumption_kwh == pytest.approx(
        365.0
    )

def test_recommendation_can_distinguish_hourly_coincidence():
    """
    Dos instalaciones con la misma producción anual pueden tener distinto
    autoconsumo según la distribución horaria de su producción.
    """
    scenario = _scenario(pv_aligned=True)

    aligned_profile = _production_profile()

    shifted_production = pd.Series(
        0.0,
        index=aligned_profile.hourly_production.index,
    )
    shifted_production.iloc[0::24] = 1.0

    shifted_profile = SolarProductionProfile(
        hourly_production=shifted_production,
        reference_year=2025,
        installed_power_kwp=1.0,
    )

    assert (
        aligned_profile.hourly_production.sum()
        == shifted_profile.hourly_production.sum()
    )

    aligned_candidate = InstallationCandidate(
        panel_count=5,
        panel_power_wp=540,
        panel_area_m2=1.134 * 1.762,
    )

    shifted_candidate = InstallationCandidate(
        panel_count=6,
        panel_power_wp=450,
        panel_area_m2=1.134 * 1.762,
    )

    aligned_evaluation = InstallationEvaluation(
        candidate=aligned_candidate,
        available_area_m2=100.0,
    )

    shifted_evaluation = InstallationEvaluation(
        candidate=shifted_candidate,
        available_area_m2=100.0,
    )

    recommender = InstallationRecommender()

    aligned_recommendation = recommender.recommend(
        evaluations=[aligned_evaluation],
        annual_consumption_kwh=scenario.annual_consumption,
        annual_productions_kwh={
            5: aligned_profile.hourly_production.sum(),
        },
        consumption_scenario=scenario,
        production_profiles={
            5: aligned_profile,
        },
    )

    shifted_recommendation = recommender.recommend(
        evaluations=[shifted_evaluation],
        annual_consumption_kwh=scenario.annual_consumption,
        annual_productions_kwh={
            6: shifted_profile.hourly_production.sum(),
        },
        consumption_scenario=scenario,
        production_profiles={
            6: shifted_profile,
        },
    )

    assert (
        aligned_recommendation.self_consumption_kwh
        > shifted_recommendation.self_consumption_kwh
    )

def test_recommendation_prefers_hourly_coincidence_over_annual_production():
    """
    El dimensionamiento debe considerar la coincidencia horaria:
    una instalación que produce menos anualmente puede ser preferible
    si su producción coincide con el consumo.
    """
    scenario = _scenario(pv_aligned=True)

    aligned_production = pd.Series(
        0.0,
        index=scenario.hourly_consumption.index,
    )
    aligned_production.iloc[12::24] = 0.8

    shifted_production = pd.Series(
        0.0,
        index=scenario.hourly_consumption.index,
    )
    shifted_production.iloc[0::24] = 1.1

    aligned_profile = SolarProductionProfile(
        hourly_production=aligned_production,
        reference_year=2025,
        installed_power_kwp=1.0,
    )

    shifted_profile = SolarProductionProfile(
        hourly_production=shifted_production,
        reference_year=2025,
        installed_power_kwp=1.0,
    )

    aligned_candidate = InstallationCandidate(
        panel_count=5,
        panel_power_wp=540,
        panel_area_m2=1.134 * 1.762,
    )

    shifted_candidate = InstallationCandidate(
        panel_count=6,
        panel_power_wp=540,
        panel_area_m2=1.134 * 1.762,
    )

    aligned_evaluation = InstallationEvaluation(
        candidate=aligned_candidate,
        available_area_m2=100.0,
    )

    shifted_evaluation = InstallationEvaluation(
        candidate=shifted_candidate,
        available_area_m2=100.0,
    )

    recommender = InstallationRecommender()

    recommendation = recommender.recommend(
        evaluations=[
            aligned_evaluation,
            shifted_evaluation,
        ],
        annual_consumption_kwh=scenario.annual_consumption,
        annual_productions_kwh={
            5: aligned_profile.hourly_production.sum(),
            6: shifted_profile.hourly_production.sum(),
        },
        consumption_scenario=scenario,
        production_profiles={
            5: aligned_profile,
            6: shifted_profile,
        },
    )

    assert recommendation.panel_count == 5

def test_consumption_scenario_bissextile_reference_year_uses_8760_hour_contract():
    """
    El contrato de ConsumptionScenario es siempre de 8760 horas,
    eliminando el 29 de febrero cuando reference_year es bisiesto.
    """
    
    expected_index = pd.date_range(
        start="2024-01-01 00:00:00",
        end="2024-12-31 23:00:00",
        freq="h",
    )

    expected_index = expected_index[
        ~(
            (expected_index.month == 2)
            & (expected_index.day == 29)
        )
    ]

    consumption = pd.Series(
        1.0,
        index=expected_index,
    )

    scenario = ConsumptionScenario(
        hourly_consumption=consumption,
        reference_year=2024,
    )

    assert len(scenario.hourly_consumption) == 8760
    assert scenario.hourly_consumption.index.equals(
        expected_index
    )
    assert scenario.hourly_consumption.index[0] == pd.Timestamp(
        "2024-01-01 00:00:00"
    )
    assert scenario.hourly_consumption.index[-1] == pd.Timestamp(
        "2024-12-31 23:00:00"
    )