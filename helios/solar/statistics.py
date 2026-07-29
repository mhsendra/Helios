import pandas as pd

from helios.solar.configuration import SolarConfiguration


class SolarStatisticsEngine:

    @staticmethod
    def calculate(
        hourly_production: pd.DataFrame,
        energy_balance: pd.DataFrame,
        configuration: SolarConfiguration
    ) -> dict:

        # ==========================================
        # Balance energético del periodo analizado
        # ==========================================

        balance = energy_balance

        valid_balance = balance.dropna(
            subset=["consumption_kwh"]
        )

        # ==========================================
        # Producción anual de referencia (PVGIS)
        # ==========================================

        reference_production = (
            hourly_production["production_kwh"]
            .sum()
        )

        production = valid_balance["production_kwh"]

        consumption = (
            valid_balance["consumption_kwh"]
            .sum()
        )

        period_production = (
            production.sum()
        )

        number_of_days = (
            valid_balance.index
            .normalize()
            .nunique()
        )

        number_of_months = (
            valid_balance.index
            .to_period("M")
            .nunique()
        )

        # ==========================================
        # Producción fotovoltaica
        # ==========================================

        installed_power = (
            configuration.installed_power_kwp
        )

        productive_hours = (
            production > 0
        ).sum()

        zero_production_hours = (
            production == 0
        ).sum()

        hourly_average = (
            production.mean()
        )

        daily_average = (
            period_production /
            number_of_days
        )

        monthly_average = (
            period_production /
            number_of_months
        )

        equivalent_hours = (
            period_production /
            installed_power
        )

        specific_yield = (
            period_production /
            installed_power
        )

        capacity_factor = (
            period_production /
            (
                installed_power *
                len(valid_balance)
            )
        ) * 100

        maximum_power = (
            production.max()
        )

        if productive_hours > 0:

            minimum_power = (
                production[
                    production > 0
                ].min()
            )

        else:

            minimum_power = 0.0

        # ==========================================
        # Balance energético
        # ==========================================

        self_consumption = (
            valid_balance["self_consumption_kwh"]
            .sum()
        )

        grid_import = (
            valid_balance["grid_import_kwh"]
            .sum()
        )

        grid_export = (
            valid_balance["grid_export_kwh"]
            .sum()
        )

        self_consumption_ratio = (
            self_consumption /
            period_production
        ) * 100

        self_sufficiency = (
            self_consumption /
            consumption
        ) * 100

        coverage_ratio = (
            period_production /
            consumption
        ) * 100

        surplus_ratio = (
            grid_export /
            period_production
        ) * 100

        import_ratio = (
            grid_import /
            consumption
        ) * 100

        # ==========================================
        # Resultados
        # ==========================================

        statistics = {

            "hours": len(valid_balance),

            "productive_hours": productive_hours,

            "zero_production_hours": zero_production_hours,

            "period_production": period_production,

            "annual_production": reference_production,

            "daily_average": daily_average,

            "monthly_average": monthly_average,

            "hourly_average": hourly_average,

            "maximum_power": maximum_power,

            "minimum_power": minimum_power,

            "equivalent_hours": equivalent_hours,

            "specific_yield": specific_yield,

            "capacity_factor": capacity_factor,

            "consumption": consumption,

            "self_consumption": self_consumption,

            "grid_import": grid_import,

            "grid_export": grid_export,

            "self_consumption_ratio": self_consumption_ratio,

            "self_sufficiency": self_sufficiency,

            "coverage_ratio": coverage_ratio,

            "surplus_ratio": surplus_ratio,

            "import_ratio": import_ratio

        }

        return statistics
