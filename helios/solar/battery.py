from dataclasses import dataclass

import pandas as pd

from helios.solar.battery_configuration import BatteryConfiguration
from helios.solar.production_profile import SolarProductionProfile
from helios.core.consumption_scenario import ConsumptionScenario


@dataclass
class BatteryResult:
    hourly_data: pd.DataFrame


class BatteryEngine:

    def calculate(
        self,
        consumption_scenario: ConsumptionScenario,
        production_profile: SolarProductionProfile,
        configuration: BatteryConfiguration,
    ) -> BatteryResult:
        consumption = consumption_scenario.hourly_consumption
        production = production_profile.hourly_production

        if len(consumption) != 8760:
            raise ValueError("Consumption profile must contain 8760 hours.")

        if len(production) != 8760:
            raise ValueError("Production profile must contain 8760 hours.")

        production_lookup = production.copy()
        production_lookup.index = (
            production_lookup.index.strftime("%m-%d-%H")
        )

        profile_key = consumption.index.strftime("%m-%d-%H")

        aligned_production = (
            pd.Series(
                profile_key,
                index=consumption.index,
            )
            .map(production_lookup)
            .fillna(0.0)
        )

        min_energy = configuration.capacity_kwh * configuration.min_soc
        max_energy = configuration.capacity_kwh * configuration.max_soc
        stored_energy = configuration.capacity_kwh * configuration.initial_soc

        rows = []

        for timestamp in consumption.index:
            consumption_kwh = consumption.loc[timestamp]
            production_kwh = aligned_production.loc[timestamp]

            direct_self_consumption = min(
                consumption_kwh,
                production_kwh,
            )

            surplus = production_kwh - direct_self_consumption
            deficit = consumption_kwh - direct_self_consumption

            battery_charge = 0.0
            battery_discharge = 0.0
            grid_export = 0.0
            grid_import = 0.0
            battery_losses = 0.0

            if surplus > 0:
                available_capacity = max_energy - stored_energy

                requested_charge = min(
                    surplus,
                    configuration.max_charge_power_kw,
                )

                energy_stored = min(
                    requested_charge * configuration.charge_efficiency,
                    available_capacity,
                )

                battery_charge = (
                    energy_stored / configuration.charge_efficiency
                )

                battery_losses += battery_charge - energy_stored
                stored_energy += energy_stored

                grid_export = surplus - battery_charge

            elif deficit > 0:
                available_energy = max(
                    stored_energy - min_energy,
                    0.0,
                )

                requested_discharge = min(
                    deficit,
                    configuration.max_discharge_power_kw,
                )

                energy_delivered = min(
                    requested_discharge,
                    available_energy * configuration.discharge_efficiency,
                )

                battery_discharge = (
                    energy_delivered / configuration.discharge_efficiency
                )

                battery_losses += battery_discharge - energy_delivered
                stored_energy -= battery_discharge

                grid_import = deficit - energy_delivered

            soc = stored_energy / configuration.capacity_kwh

            rows.append(
                {
                    "consumption_kwh": consumption_kwh,
                    "production_kwh": production_kwh,
                    "direct_self_consumption_kwh": direct_self_consumption,
                    "battery_charge_kwh": battery_charge,
                    "battery_discharge_kwh": battery_discharge,
                    "grid_import_kwh": grid_import,
                    "grid_export_kwh": grid_export,
                    "battery_soc": soc,
                    "battery_losses_kwh": battery_losses,
                }
            )

        return BatteryResult(
            hourly_data=pd.DataFrame(
                rows,
                index=consumption.index,
            )
        )