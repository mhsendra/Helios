from collections.abc import Callable
from dataclasses import replace
import math

from helios.core.consumption_scenario import ConsumptionScenario
from helios.core.energy_recommendation import EnergyRecommendation
from helios.ev.scenario import EVScenario
from helios.solar.battery_economic_model import CombinedEconomicConfiguration
from helios.solar.battery_optimizer import BatteryOptimizer
from helios.solar.installation_evaluation import InstallationEvaluation
from helios.solar.installation_recommendation import InstallationRecommendation
from helios.solar.production_profile import SolarProductionProfile


class EnergyRecommender:
    """
    Coordina la recomendación integral FV + batería + EV.

    No implementa simulación energética ni económica propia.
    Delega el balance y la optimización de batería a los
    componentes especializados existentes.
    """

    def __init__(
        self,
        battery_optimizer: BatteryOptimizer | None = None,
    ):
        if battery_optimizer is None:
            battery_optimizer = BatteryOptimizer()
        elif not callable(
            getattr(battery_optimizer, "optimize", None)
        ):
            raise TypeError(
                "battery_optimizer must provide an optimize() method."
            )

        self.battery_optimizer = battery_optimizer

    def recommend(
        self,
        evaluations: list[InstallationEvaluation],
        annual_consumption_kwh: float,
        consumption_scenario: ConsumptionScenario,
        production_profiles: dict[int, SolarProductionProfile],
        candidate_capacities_kwh: list[float],
        *,
        max_charge_power_kw: float,
        max_discharge_power_kw: float,
        battery_cost_per_kwh_eur: float = 249.70,
        economic_configuration_factory: (
            Callable[
                [
                    InstallationEvaluation,
                    SolarProductionProfile,
                ],
                CombinedEconomicConfiguration,
            ]
            | None
        ) = None,
        ev_scenario: EVScenario | None = None,
        optimization_criterion: str = "combined_npv",
        charge_efficiency: float = 0.95,
        discharge_efficiency: float = 0.95,
        min_soc: float = 0.10,
        max_soc: float = 0.90,
        initial_soc: float = 0.10,
    ) -> EnergyRecommendation:
        self._validate_inputs(
            evaluations,
            annual_consumption_kwh,
            consumption_scenario,
            production_profiles,
            candidate_capacities_kwh,
            ev_scenario,
            optimization_criterion,
        )

        evaluated_options: list[EnergyRecommendation] = []

        for evaluation in evaluations:
            panel_count = evaluation.panel_count
            production_profile = production_profiles[panel_count]

            combined_economic_configuration = None

            if economic_configuration_factory is not None:
                combined_economic_configuration = (
                    economic_configuration_factory(
                        evaluation,
                        production_profile,
                    )
                )

                if not isinstance(
                    combined_economic_configuration,
                    CombinedEconomicConfiguration,
                ):
                    raise TypeError(
                        "economic_configuration_factory must return "
                        "a CombinedEconomicConfiguration."
                    )

            battery_recommendation = (
                self.battery_optimizer.optimize(
                    consumption_scenario,
                    production_profile,
                    candidate_capacities_kwh,
                    optimization_criterion=optimization_criterion,
                    max_charge_power_kw=max_charge_power_kw,
                    max_discharge_power_kw=max_discharge_power_kw,
                    charge_efficiency=charge_efficiency,
                    discharge_efficiency=discharge_efficiency,
                    min_soc=min_soc,
                    max_soc=max_soc,
                    initial_soc=initial_soc,
                    battery_cost_per_kwh_eur=battery_cost_per_kwh_eur,
                    combined_economic_configuration=(
                        combined_economic_configuration
                    ),
                    ev_scenario=ev_scenario,
                )
            )

            installation_recommendation = InstallationRecommendation(
                evaluation=evaluation,
                annual_consumption_kwh=annual_consumption_kwh,
                annual_production_kwh=production_profile.annual_production,
                consumption_scenario=consumption_scenario,
                production_profile=production_profile,
            )

            evaluated_options.append(
                EnergyRecommendation(
                    installation_recommendation=(
                        installation_recommendation
                    ),
                    battery_recommendation=battery_recommendation,
                    ev_scenario=ev_scenario,
                    optimization_criterion=optimization_criterion,
                )
            )

        if not evaluated_options:
            raise ValueError(
                "No valid energy recommendation could be generated."
            )

        best_energy_recommendation = evaluated_options[0]

        for candidate in evaluated_options[1:]:
            if self._is_better(
                candidate,
                best_energy_recommendation,
                optimization_criterion,
            ):
                best_energy_recommendation = candidate

        return replace(
            best_energy_recommendation,
            evaluated_options=tuple(evaluated_options),
        )

    @staticmethod
    def _is_better(
        candidate: EnergyRecommendation,
        current: EnergyRecommendation,
        optimization_criterion: str,
    ) -> bool:
        candidate_battery = candidate.battery_recommendation
        current_battery = current.battery_recommendation

        if optimization_criterion == "energy":
            candidate_key = (
                candidate_battery.battery_energy_recovered_kwh,
                -candidate.battery_capacity_kwh,
                -candidate.panel_count,
            )
            current_key = (
                current_battery.battery_energy_recovered_kwh,
                -current.battery_capacity_kwh,
                -current.panel_count,
            )
            return candidate_key > current_key

        if optimization_criterion == "npv":
            candidate_key = (
                candidate_battery.economic_npv_eur,
                -candidate.battery_capacity_kwh,
                -candidate.panel_count,
            )
            current_key = (
                current_battery.economic_npv_eur,
                -current.battery_capacity_kwh,
                -current.panel_count,
            )
            return candidate_key > current_key

        if optimization_criterion == "combined_npv":
            candidate_key = (
                candidate_battery.combined_economic_npv_eur,
                -candidate.battery_capacity_kwh,
                -candidate.panel_count,
            )
            current_key = (
                current_battery.combined_economic_npv_eur,
                -current.battery_capacity_kwh,
                -current.panel_count,
            )
            return candidate_key > current_key

        if optimization_criterion == "payback":
            candidate_key = (
                candidate_battery.economic_payback_years,
                candidate.battery_capacity_kwh,
                candidate.panel_count,
            )
            current_key = (
                current_battery.economic_payback_years,
                current.battery_capacity_kwh,
                current.panel_count,
            )
            return candidate_key < current_key

        if optimization_criterion == "combined_payback":
            candidate_key = (
                candidate_battery.combined_economic_payback_years,
                candidate.battery_capacity_kwh,
                candidate.panel_count,
            )
            current_key = (
                current_battery.combined_economic_payback_years,
                current.battery_capacity_kwh,
                current.panel_count,
            )
            return candidate_key < current_key

        raise ValueError(
            "optimization_criterion must be one of: "
            "'energy', 'npv', 'combined_npv', "
            "'payback', 'combined_payback'."
        )

    @staticmethod
    def _validate_inputs(
        evaluations: list[InstallationEvaluation],
        annual_consumption_kwh: float,
        consumption_scenario: ConsumptionScenario,
        production_profiles: dict[int, SolarProductionProfile],
        candidate_capacities_kwh: list[float],
        ev_scenario: EVScenario | None,
        optimization_criterion: str,
    ) -> None:
        if not evaluations:
            raise ValueError(
                "At least one installation evaluation is required."
            )

        if not all(
            isinstance(evaluation, InstallationEvaluation)
            for evaluation in evaluations
        ):
            raise TypeError(
                "evaluations must contain only "
                "InstallationEvaluation instances."
            )

        if not isinstance(
            consumption_scenario,
            ConsumptionScenario,
        ):
            raise TypeError(
                "consumption_scenario must be a ConsumptionScenario."
            )

        if (
            isinstance(annual_consumption_kwh, bool)
            or not isinstance(
                annual_consumption_kwh,
                (int, float),
            )
        ):
            raise TypeError(
                "annual_consumption_kwh must be a number."
            )

        if (
            not math.isfinite(annual_consumption_kwh)
            or annual_consumption_kwh < 0
        ):
            raise ValueError(
                "annual_consumption_kwh must be a "
                "finite non-negative number."
            )

        if not isinstance(
            production_profiles,
            dict,
        ):
            raise TypeError(
                "production_profiles must be a dictionary."
            )

        for evaluation in evaluations:
            if evaluation.panel_count not in production_profiles:
                raise ValueError(
                    "Missing production profile for "
                    f"{evaluation.panel_count} panels."
                )

            if not isinstance(
                production_profiles[evaluation.panel_count],
                SolarProductionProfile,
            ):
                raise TypeError(
                    "production_profiles must contain only "
                    "SolarProductionProfile instances."
                )

        if not isinstance(candidate_capacities_kwh, list):
            raise TypeError(
                "candidate_capacities_kwh must be a list."
            )

        if not candidate_capacities_kwh:
            raise ValueError(
                "candidate_capacities_kwh must not be empty."
            )

        for capacity in candidate_capacities_kwh:
            if (
                isinstance(capacity, bool)
                or not isinstance(capacity, (int, float))
            ):
                raise TypeError(
                    "Battery capacities must be numeric."
                )

            if (
                not math.isfinite(capacity)
                or capacity <= 0
            ):
                raise ValueError(
                    "Battery capacities must be finite "
                    "and greater than zero."
                )

        if ev_scenario is not None and not isinstance(
            ev_scenario,
            EVScenario,
        ):
            raise TypeError(
                "ev_scenario must be an EVScenario."
            )

        if optimization_criterion not in {
            "energy",
            "npv",
            "combined_npv",
            "payback",
            "combined_payback",
        }:
            raise ValueError(
                "optimization_criterion must be one of: "
                "'energy', 'npv', 'combined_npv', "
                "'payback', 'combined_payback'."
            )