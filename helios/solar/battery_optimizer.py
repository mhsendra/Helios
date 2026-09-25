from dataclasses import replace

from helios.core.consumption_scenario import ConsumptionScenario
from helios.solar.battery_configuration import BatteryConfiguration
from helios.solar.battery import BatteryEngine
from helios.solar.battery_economic_model import (
    BatteryEconomicConfiguration,
    BatteryEconomicModel,
)
from helios.solar.battery_recommendation import BatteryRecommendation
from helios.solar.production_profile import SolarProductionProfile


class BatteryOptimizer:

    def _evaluate_capacities(
        self,
        consumption_scenario: ConsumptionScenario,
        production_profile: SolarProductionProfile,
        candidate_capacities_kwh: list[float],
        *,
        max_charge_power_kw: float,
        max_discharge_power_kw: float,
        charge_efficiency: float = 0.95,
        discharge_efficiency: float = 0.95,
        min_soc: float = 0.10,
        max_soc: float = 0.90,
        initial_soc: float = 0.10,
        battery_cost_per_kwh_eur: float = 249.70,
        annual_cost_without_battery_eur: float | None = None,
        cost_calculator=None,
        economic_configuration: (
            BatteryEconomicConfiguration | None
        ) = None,
    ) -> list[BatteryRecommendation]:

        recommendations = []

        sorted_capacities = sorted(candidate_capacities_kwh)

        for capacity in sorted_capacities:

            battery_cost_eur = (
                capacity * battery_cost_per_kwh_eur
            )

            configuration = BatteryConfiguration(
                capacity_kwh=capacity,
                max_charge_power_kw=max_charge_power_kw,
                max_discharge_power_kw=max_discharge_power_kw,
                charge_efficiency=charge_efficiency,
                discharge_efficiency=discharge_efficiency,
                min_soc=min_soc,
                max_soc=max_soc,
                initial_soc=initial_soc,
            )

            result = BatteryEngine().calculate(
                consumption_scenario,
                production_profile,
                configuration,
            ).hourly_data

            if cost_calculator is not None:
                annual_cost_with_battery = float(
                    cost_calculator(result)
                )
            else:
                annual_cost_with_battery = 0.0

            if annual_cost_without_battery_eur is not None:
                annual_additional_savings = (
                    annual_cost_without_battery_eur
                    - annual_cost_with_battery
                )

                simple_payback_years = (
                    battery_cost_eur
                    / annual_additional_savings
                    if annual_additional_savings > 0
                    else float("inf")
                )

                annual_return_on_battery_cost = (
                    annual_additional_savings
                    / battery_cost_eur
                    if battery_cost_eur > 0
                    else 0.0
                )
            else:
                annual_additional_savings = 0.0

                simple_payback_years = float("inf")
                annual_return_on_battery_cost = 0.0

            annual_consumption = float(
                result["consumption_kwh"].sum()
            )

            annual_production = float(
                result["production_kwh"].sum()
            )

            annual_surplus = float(
                (
                    result["production_kwh"]
                    - result["direct_self_consumption_kwh"]
                ).sum()
            )

            annual_export = float(
                result["grid_export_kwh"].sum()
            )

            annual_grid_import = float(
                result["grid_import_kwh"].sum()
            )

            annual_charge = float(
                result["battery_charge_kwh"].sum()
            )

            annual_discharge = float(
                result["battery_discharge_kwh"].sum()
            )

            self_consumption = (
                annual_consumption
                - annual_grid_import
            )

            self_sufficiency = (
                self_consumption
                / annual_consumption
                * 100
                if annual_consumption > 0
                else 0.0
            )

            usable_capacity = (
                capacity
                * (max_soc - min_soc)
            )

            equivalent_cycles = (
                annual_discharge / usable_capacity
                if usable_capacity > 0
                else 0.0
            )

            # ---------------------------------------------------------
            # Incremental analysis
            # ---------------------------------------------------------

            incremental_battery_cost = 0.0
            incremental_savings = 0.0
            marginal_savings_per_kwh = 0.0
            marginal_payback_years = float("inf")

            if recommendations:
                previous = recommendations[-1]

                marginal_recovered = (
                    annual_discharge
                    - previous.annual_battery_discharge_kwh
                )

                capacity_increment = (
                    capacity
                    - previous.capacity_kwh
                )

                marginal_recovered_kwh_per_kwh = (
                    marginal_recovered / capacity_increment
                    if capacity_increment > 0
                    else 0.0
                )

                incremental_battery_cost = (
                    battery_cost_eur
                    - previous.capacity_kwh
                    * battery_cost_per_kwh_eur
                )

                incremental_savings = max(
                    0.0,
                    annual_additional_savings
                    - previous.annual_additional_savings_eur,
                )

                marginal_savings_per_kwh = (
                    incremental_savings
                    / capacity_increment
                    if capacity_increment > 0
                    else 0.0
                )

                marginal_payback_years = (
                    incremental_battery_cost
                    / incremental_savings
                    if incremental_savings > 0
                    else float("inf")
                )

            else:
                marginal_recovered_kwh_per_kwh = 0.0

            # ---------------------------------------------------------
            # Lifecycle economic analysis
            # ---------------------------------------------------------

            economic_npv_eur = 0.0
            economic_irr_percent = 0.0
            economic_payback_years = float("inf")

            if economic_configuration is not None:
                economic_configuration_for_capacity = replace(
                    economic_configuration,
                    battery_cost_eur=battery_cost_eur,
                    annual_savings_eur=(
                        annual_additional_savings
                    ),
                )

                economic_result = (
                    BatteryEconomicModel().calculate(
                        economic_configuration_for_capacity
                    )
                )

                economic_npv_eur = (
                    economic_result.npv_eur
                )

                economic_irr_percent = (
                    economic_result.irr_percent
                )

                economic_payback_years = (
                    economic_result.payback_years
                )

            recommendations.append(
                BatteryRecommendation(
                    capacity_kwh=capacity,
                    max_charge_power_kw=max_charge_power_kw,
                    max_discharge_power_kw=max_discharge_power_kw,
                    annual_consumption_kwh=annual_consumption,
                    annual_production_kwh=annual_production,
                    annual_surplus_kwh=annual_surplus,
                    annual_export_kwh=annual_export,
                    annual_grid_import_kwh=annual_grid_import,
                    annual_battery_charge_kwh=annual_charge,
                    annual_battery_discharge_kwh=annual_discharge,
                    self_consumption_kwh=self_consumption,
                    self_sufficiency_percent=self_sufficiency,
                    equivalent_cycles=equivalent_cycles,
                    annual_cost_with_battery_eur=(
                        annual_cost_with_battery
                    ),
                    annual_additional_savings_eur=(
                        annual_additional_savings
                    ),
                    marginal_recovered_kwh_per_kwh=(
                        marginal_recovered_kwh_per_kwh
                    ),
                    incremental_battery_cost_eur=(
                        incremental_battery_cost
                    ),
                    incremental_savings_eur=(
                        incremental_savings
                    ),
                    marginal_savings_per_kwh=(
                        marginal_savings_per_kwh
                    ),
                    marginal_payback_years=(
                        marginal_payback_years
                    ),
                    economic_npv_eur=(
                        economic_npv_eur
                    ),
                    economic_irr_percent=(
                        economic_irr_percent
                    ),
                    economic_payback_years=(
                        economic_payback_years
                    ),
                )
            )

        return recommendations

    def evaluate(
        self,
        consumption_scenario: ConsumptionScenario,
        production_profile: SolarProductionProfile,
        candidate_capacities_kwh: list[float],
        *,
        max_charge_power_kw: float,
        max_discharge_power_kw: float,
        charge_efficiency: float = 0.95,
        discharge_efficiency: float = 0.95,
        min_soc: float = 0.10,
        max_soc: float = 0.90,
        initial_soc: float = 0.10,
        annual_cost_without_battery_eur: float | None = None,
        cost_calculator=None,
        economic_configuration: (
            BatteryEconomicConfiguration | None
        ) = None,
    ) -> list[BatteryRecommendation]:

        if not isinstance(
            consumption_scenario,
            ConsumptionScenario,
        ):
            raise TypeError(
                "consumption_scenario must be a "
                "ConsumptionScenario."
            )

        if not isinstance(
            production_profile,
            SolarProductionProfile,
        ):
            raise TypeError(
                "production_profile must be a "
                "SolarProductionProfile."
            )

        if not candidate_capacities_kwh:
            raise ValueError(
                "candidate_capacities_kwh must not be empty."
            )

        if any(
            capacity <= 0
            for capacity in candidate_capacities_kwh
        ):
            raise ValueError(
                "Battery capacities must be greater than zero."
            )

        return self._evaluate_capacities(
            consumption_scenario,
            production_profile,
            candidate_capacities_kwh,
            max_charge_power_kw=max_charge_power_kw,
            max_discharge_power_kw=max_discharge_power_kw,
            charge_efficiency=charge_efficiency,
            discharge_efficiency=discharge_efficiency,
            min_soc=min_soc,
            max_soc=max_soc,
            initial_soc=initial_soc,
            annual_cost_without_battery_eur=(
                annual_cost_without_battery_eur
            ),
            cost_calculator=cost_calculator,
            economic_configuration=(
                economic_configuration
            ),
        )

    def optimize(
        self,
        consumption_scenario: ConsumptionScenario,
        production_profile: SolarProductionProfile,
        candidate_capacities_kwh: list[float],
        *,
        max_charge_power_kw: float,
        max_discharge_power_kw: float,
        charge_efficiency: float = 0.95,
        discharge_efficiency: float = 0.95,
        min_soc: float = 0.10,
        max_soc: float = 0.90,
        initial_soc: float = 0.10,
        annual_cost_without_battery_eur: float | None = None,
        cost_calculator=None,
        economic_configuration: (
            BatteryEconomicConfiguration | None
        ) = None,
    ) -> BatteryRecommendation:

        recommendations = self.evaluate(
            consumption_scenario,
            production_profile,
            candidate_capacities_kwh,
            max_charge_power_kw=max_charge_power_kw,
            max_discharge_power_kw=max_discharge_power_kw,
            charge_efficiency=charge_efficiency,
            discharge_efficiency=discharge_efficiency,
            min_soc=min_soc,
            max_soc=max_soc,
            initial_soc=initial_soc,
            annual_cost_without_battery_eur=(
                annual_cost_without_battery_eur
            ),
            cost_calculator=cost_calculator,
            economic_configuration=(
                economic_configuration
            ),
        )

        return max(
            recommendations,
            key=lambda recommendation: (
                recommendation.battery_energy_recovered_kwh,
                -recommendation.capacity_kwh,
            ),
        )