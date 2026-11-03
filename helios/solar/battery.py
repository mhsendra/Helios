
from dataclasses import dataclass

import numpy as np
import pandas as pd

from helios.core.consumption_scenario import ConsumptionScenario
from helios.solar.battery_configuration import BatteryConfiguration
from helios.solar.production_profile import SolarProductionProfile

from helios.solar.temporal_alignment import (
    align_hourly_series_by_month_day_hour,
)


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
            raise ValueError(
                "Consumption profile must contain 8760 hours."
            )

        if len(production) != 8760:
            raise ValueError(
                "Production profile must contain 8760 hours."
            )

        aligned_production = (
            align_hourly_series_by_month_day_hour(
                consumption.index,
                production,
            )
        )

        consumption_values = consumption.to_numpy(
            dtype=float,
            copy=False,
        )
        production_values = aligned_production.to_numpy(
            dtype=float,
            copy=False,
        )

        min_energy = (
            configuration.capacity_kwh * configuration.min_soc
        )
        max_energy = (
            configuration.capacity_kwh * configuration.max_soc
        )
        stored_energy = (
            configuration.capacity_kwh * configuration.initial_soc
        )

        hour_count = len(consumption_values)

        direct_self_consumption_values = np.zeros(
            hour_count,
            dtype=float,
        )
        self_consumption_values = np.zeros(
            hour_count,
            dtype=float,
        )
        battery_charge_values = np.zeros(
            hour_count,
            dtype=float,
        )
        battery_discharge_values = np.zeros(
            hour_count,
            dtype=float,
        )
        grid_import_values = np.zeros(
            hour_count,
            dtype=float,
        )
        grid_export_values = np.zeros(
            hour_count,
            dtype=float,
        )
        battery_soc_values = np.zeros(
            hour_count,
            dtype=float,
        )
        battery_losses_values = np.zeros(
            hour_count,
            dtype=float,
        )

        for hour in range(hour_count):
            consumption_kwh = consumption_values[hour]
            production_kwh = production_values[hour]

            direct_self_consumption = min(
                consumption_kwh,
                production_kwh,
            )

            surplus = production_kwh - direct_self_consumption
            deficit = consumption_kwh - direct_self_consumption

            battery_charge = 0.0
            battery_discharge = 0.0
            energy_delivered = 0.0
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
                    requested_charge
                    * configuration.charge_efficiency,
                    available_capacity,
                )

                battery_charge = (
                    energy_stored
                    / configuration.charge_efficiency
                )

                battery_losses += (
                    battery_charge - energy_stored
                )
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
                    available_energy
                    * configuration.discharge_efficiency,
                )

                battery_discharge = (
                    energy_delivered
                    / configuration.discharge_efficiency
                )

                battery_losses += (
                    battery_discharge - energy_delivered
                )
                stored_energy -= battery_discharge

                grid_import = deficit - energy_delivered

            self_consumption = (
                direct_self_consumption + energy_delivered
            )

            soc = (
                stored_energy / configuration.capacity_kwh
            )

            direct_self_consumption_values[hour] = (
                direct_self_consumption
            )
            self_consumption_values[hour] = self_consumption
            battery_charge_values[hour] = battery_charge
            battery_discharge_values[hour] = battery_discharge
            grid_import_values[hour] = grid_import
            grid_export_values[hour] = grid_export
            battery_soc_values[hour] = soc
            battery_losses_values[hour] = battery_losses

        hourly_data = pd.DataFrame(
            {
                "consumption_kwh": consumption_values,
                "production_kwh": production_values,
                "direct_self_consumption_kwh": (
                    direct_self_consumption_values
                ),
                "self_consumption_kwh": self_consumption_values,
                "battery_charge_kwh": battery_charge_values,
                "battery_discharge_kwh": battery_discharge_values,
                "grid_import_kwh": grid_import_values,
                "grid_export_kwh": grid_export_values,
                "battery_soc": battery_soc_values,
                "battery_losses_kwh": battery_losses_values,
            },
            index=consumption.index,
        )

        return BatteryResult(hourly_data=hourly_data)
