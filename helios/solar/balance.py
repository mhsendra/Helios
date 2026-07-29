import pandas as pd


class SolarBalanceEngine:

    @staticmethod
    def calculate(
        consumption: pd.Series,
        hourly_production: pd.DataFrame
    ) -> pd.DataFrame:

        production = hourly_production["production_kwh"]

        production_lookup = production.copy()
        production_lookup.index = (
            production_lookup.index.strftime("%m-%d-%H")
        )

        balance = pd.DataFrame(index=consumption.index)

        balance["consumption_kwh"] = consumption.values

        profile_key = balance.index.strftime("%m-%d-%H")

        balance["production_kwh"] = (
            pd.Series(profile_key, index=balance.index)
            .map(production_lookup)
            .fillna(0.0)
        )

        balance["self_consumption_kwh"] = (
            balance[
                [
                    "consumption_kwh",
                    "production_kwh"
                ]
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