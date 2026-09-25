import pandas as pd

from helios.core.consumption_scenario import ConsumptionScenario
from helios.solar.production_profile import SolarProductionProfile
from helios.solar.battery import BatteryEngine
from helios.solar.battery_configuration import BatteryConfiguration


class SolarBalanceEngine:
    @staticmethod
    def calculate(
        consumption_scenario: ConsumptionScenario,
        production_profile: SolarProductionProfile,
        battery_configuration: BatteryConfiguration | None = None,
    ) -> pd.DataFrame:
        if not isinstance(
            consumption_scenario,
            ConsumptionScenario,
        ):
            raise TypeError(
                "consumption_scenario must be a ConsumptionScenario."
            )

        if not isinstance(
            production_profile,
            SolarProductionProfile,
        ):
            raise TypeError(
                "production_profile must be a SolarProductionProfile."
            )

        if battery_configuration is not None:
            if not isinstance(
                battery_configuration,
                BatteryConfiguration,
            ):
                raise TypeError(
                    "battery_configuration must be a "
                    "BatteryConfiguration."
                )

            return BatteryEngine().calculate(
                consumption_scenario,
                production_profile,
                battery_configuration,
            ).hourly_data

        consumption = consumption_scenario.hourly_consumption

        production = production_profile.hourly_production

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

        balance = pd.DataFrame(
            index=consumption.index,
        )

        balance["consumption_kwh"] = consumption.values
        balance["production_kwh"] = aligned_production.values

        balance["self_consumption_kwh"] = (
            balance[
                ["consumption_kwh", "production_kwh"]
            ].min(axis=1)
        )

        balance["grid_import_kwh"] = (
            balance["consumption_kwh"]
            - balance["self_consumption_kwh"]
        )

        balance["grid_export_kwh"] = (
            balance["production_kwh"]
            - balance["self_consumption_kwh"]
        )

        return balance