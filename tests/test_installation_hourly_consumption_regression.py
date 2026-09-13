import pandas as pd

from helios.core.consumption_scenario import ConsumptionScenario
from helios.solar.installation_coordinator import InstallationCoordinator
from helios.solar.installation_constraints import InstallationConstraints
from helios.solar.installation_configuration import InstallationConfiguration
from helios.solar.installation_evaluation import InstallationEvaluator
from helios.solar.installation_optimizer import InstallationOptimizer
from helios.solar.installation_recommendation import InstallationRecommender
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
