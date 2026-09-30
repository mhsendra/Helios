from __future__ import annotations

import pandas as pd

from helios.reports.battery_report_data import (
    BatteryReportData,
)
from helios.reports.solar_report_data import SolarReportData


class SolarReportDataBuilder:
    """
    Construye SolarReportData a partir del estado actual de un HeliosProject.

    El builder adapta las estructuras internas del proyecto al modelo
    específico utilizado por el generador de informes PDF.
    """

    @classmethod
    def from_project(cls, project) -> SolarReportData:
        solar = project.solar
        solar_configuration = project.solar_configuration
        economics = project.economics

        economics_engine = (
            project.analyzer.economics_engine
        )

        economics_configuration = (
            economics.configuration
        )

        # ---------------------------------------------------------
        # Instalación / modo de cálculo
        # ---------------------------------------------------------

        sizing_result = getattr(
            solar,
            "sizing_result",
            None,
        )

        if sizing_result is not None:
            calculation_mode = "automatic"

            installed_power_kwp = float(
                sizing_result.installed_power_kwp
            )

            panel_count = int(
                sizing_result.panel_count
            )

            installation_configuration = getattr(
                solar,
                "installation_configuration",
                None,
            )

            panel_power_wp = (
                float(
                    installation_configuration.panel_power_wp
                )
                if installation_configuration is not None
                else None
            )

        else:
            calculation_mode = "manual"

            simulation_installed_power_kwp = getattr(
                solar,
                "simulation_installed_power_kwp",
                None,
            )

            installed_power_kwp = (
                float(simulation_installed_power_kwp)
                if simulation_installed_power_kwp is not None
                else None
            )

            panel_count = None
            panel_power_wp = None

        # ---------------------------------------------------------
        # Producción
        # ---------------------------------------------------------

        if sizing_result is not None:
            yearly_production_kwh = float(
                sizing_result.annual_production_kwh
            )
        else:
            annual_production = solar.annual_production

            yearly_production_kwh = (
                float(annual_production)
                if annual_production is not None
                else 0.0
            )

        monthly_production = solar.monthly_production

        specific_production = solar.specific_production

        statistics = solar.statistics or {}

        productive_hours = int(
            statistics.get(
                "productive_hours",
                0,
            )
        )

        daily_average = float(
            statistics.get(
                "daily_average",
                0.0,
            )
        )

        monthly_average = float(
            statistics.get(
                "monthly_average",
                0.0,
            )
        )

        maximum_hourly_production = float(
            statistics.get(
                "maximum_hourly_production",
                0.0,
            )
        )

        capacity_factor = float(
            statistics.get(
                "capacity_factor",
                0.0,
            )
        )

        # ---------------------------------------------------------
        # Balance energético
        # ---------------------------------------------------------

        balance = solar.energy_balance

        if sizing_result is not None:
            yearly_consumption_kwh = float(
                sizing_result.annual_consumption_kwh
            )
        elif balance is not None and not balance.empty:
            yearly_consumption_kwh = float(
                statistics.get(
                    "consumption",
                    0.0,
                )
            )
        else:
            yearly_consumption_kwh = float(
                statistics.get(
                    "consumption",
                    0.0,
                )
            )

        if balance is not None and not balance.empty:
            if not isinstance(
                balance.index,
                pd.DatetimeIndex,
            ):
                raise TypeError(
                    "solar energy balance index must be a DatetimeIndex"
                )

            self_consumption = getattr(
                solar,
                "self_consumption",
                None,
            )
            if self_consumption is None:
                self_consumption_kwh = float(
                    balance["self_consumption_kwh"].sum()
                )
            else:
                self_consumption_kwh = float(
                    self_consumption
                )

            grid_export = getattr(
                solar,
                "grid_export",
                None,
            )
            if grid_export is None:
                grid_export_kwh = float(
                    balance["grid_export_kwh"].sum()
                )
            else:
                grid_export_kwh = float(
                    grid_export
                )

            grid_import = getattr(
                solar,
                "grid_import",
                None,
            )
            if grid_import is None:
                grid_import_kwh = float(
                    balance["grid_import_kwh"].sum()
                )
            else:
                grid_import_kwh = float(
                    grid_import
                )

            consumption_reference_year = int(
                balance.index[0].year
            )

            monthly_consumption = (
                balance["consumption_kwh"]
                .resample("ME")
                .sum()
            )

        else:
            self_consumption = getattr(
                solar,
                "self_consumption",
                None,
            )
            self_consumption_kwh = (
                float(self_consumption)
                if self_consumption is not None
                else float(
                    statistics.get(
                        "self_consumption",
                        0.0,
                    )
                )
            )

            grid_export = getattr(
                solar,
                "grid_export",
                None,
            )
            grid_export_kwh = (
                float(grid_export)
                if grid_export is not None
                else float(
                    statistics.get(
                        "grid_export",
                        0.0,
                    )
                )
            )

            grid_import = getattr(
                solar,
                "grid_import",
                None,
            )
            grid_import_kwh = (
                float(grid_import)
                if grid_import is not None
                else float(
                    statistics.get(
                        "grid_import",
                        0.0,
                    )
                )
            )

            consumption_reference_year = None

            monthly_consumption = pd.Series(
                dtype=float
            )

        # ---------------------------------------------------------
        # Ratios energéticos
        # ---------------------------------------------------------

        self_consumption_rate_percent = float(
            statistics.get(
                "self_consumption_ratio",
                0.0,
            )
        )

        if sizing_result is not None:
            self_sufficiency_rate_percent = float(
                sizing_result.self_sufficiency_percent
            )
        else:
            self_sufficiency_rate_percent = float(
                statistics.get(
                    "self_sufficiency",
                    0.0,
                )
            )

        # ---------------------------------------------------------
        # Economía
        # ---------------------------------------------------------

        cost_without_pv_eur = float(
            getattr(
                economics_engine,
                "cost_without_pv",
                0.0,
            )
        )

        grid_import_cost_eur = float(
            getattr(
                economics_engine,
                "grid_import_cost",
                0.0,
            )
        )

        export_income_eur = float(
            getattr(
                economics_engine,
                "export_income",
                0.0,
            )
        )

        cost_with_pv_eur = float(
            getattr(
                economics_engine,
                "cost_with_pv",
                0.0,
            )
        )

        self_consumption_savings_eur = float(
            getattr(
                economics_engine,
                "self_consumption_savings",
                0.0,
            )
        )

        investment_eur = float(
            getattr(
                economics_engine,
                "net_investment",
                economics_configuration.installation_cost,
            )
        )

        yearly_savings_eur = float(
            getattr(
                economics_engine,
                "annual_savings",
                0.0,
            )
        )

        payback_value = getattr(
            economics_engine,
            "payback_years",
            None,
        )

        payback_years = (
            float(payback_value)
            if payback_value is not None
            else None
        )

        net_present_value_eur = float(
            getattr(
                economics_engine,
                "npv",
                0.0,
            )
        )

        internal_rate_of_return = getattr(
            economics_engine,
            "irr",
            None,
        )

        if internal_rate_of_return is not None:
            internal_rate_of_return = (
                float(internal_rate_of_return) * 100
            )

        # ---------------------------------------------------------
        # Hipótesis económicas
        #
        # EconomicsConfiguration almacena estos valores como
        # fracciones. SolarReportData los expresa como porcentajes.
        # ---------------------------------------------------------

        first_year_degradation_percent = (
            float(
                economics_configuration.first_year_degradation
            )
            * 100
        )

        annual_degradation_percent = (
            float(
                economics_configuration.annual_degradation
            )
            * 100
        )

        annual_electricity_price_growth_percent = (
            float(
                economics_configuration.annual_electricity_price_growth
            )
            * 100
        )

        annual_export_price_growth_percent = (
            float(
                economics_configuration.annual_export_price_growth
            )
            * 100
        )

        annual_maintenance_cost_eur = float(
            economics_configuration.annual_maintenance_cost
        )

        annual_maintenance_growth_percent = (
            float(
                economics_configuration.annual_maintenance_growth
            )
            * 100
        )

        discount_rate_percent = (
            float(
                economics_configuration.discount_rate
            )
            * 100
        )

        # ---------------------------------------------------------
        # Resultados económicos y horizonte real
        # ---------------------------------------------------------

        scenario_results = list(
            getattr(
                economics_engine,
                "scenario_results",
                [],
            )
            or []
        )

        cash_flow = getattr(
            economics_engine,
            "cash_flow",
            None,
        )

        if (
            cash_flow is not None
            and not cash_flow.empty
            and "year" in cash_flow.columns
        ):
            economic_horizon_years = int(
                cash_flow["year"].max()
            )
        else:
            economic_horizon_years = 0

        # ---------------------------------------------------------
        # Configuración PVGIS
        # ---------------------------------------------------------

        latitude = None
        longitude = None
        tilt = None
        azimuth = None
        reference_year = None
        losses = None
        pv_technology = None
        mounting_place = None

        if solar_configuration is not None:
            latitude = float(
                solar_configuration.latitude
            )

            longitude = float(
                solar_configuration.longitude
            )

            tilt = int(
                solar_configuration.tilt
            )

            azimuth = int(
                solar_configuration.azimuth
            )

            reference_year = int(
                solar_configuration.reference_year
            )

            losses = float(
                solar_configuration.losses
            )

            pv_technology = (
                solar_configuration.pv_technology
            )

            mounting_place = (
                solar_configuration.mounting_place
            )

        # ---------------------------------------------------------
        # Recomendaciones de batería
        # ---------------------------------------------------------

        battery_recommendations = list(
            getattr(
                solar,
                "battery_recommendations",
                [],
            )
            or []
        )

        battery_report_data = [
            BatteryReportData(
                capacity_kwh=float(
                    recommendation.capacity_kwh
                ),
                max_charge_power_kw=float(
                    recommendation.max_charge_power_kw
                ),
                max_discharge_power_kw=float(
                    recommendation.max_discharge_power_kw
                ),
                annual_consumption_kwh=float(
                    recommendation.annual_consumption_kwh
                ),
                annual_production_kwh=float(
                    recommendation.annual_production_kwh
                ),
                annual_surplus_kwh=float(
                    recommendation.annual_surplus_kwh
                ),
                annual_export_kwh=float(
                    recommendation.annual_export_kwh
                ),
                annual_grid_import_kwh=float(
                    recommendation.annual_grid_import_kwh
                ),
                annual_battery_charge_kwh=float(
                    recommendation.annual_battery_charge_kwh
                ),
                annual_battery_discharge_kwh=float(
                    recommendation.annual_battery_discharge_kwh
                ),
                self_consumption_kwh=float(
                    recommendation.self_consumption_kwh
                ),
                self_sufficiency_percent=float(
                    recommendation.self_sufficiency_percent
                ),
                equivalent_cycles=float(
                    recommendation.equivalent_cycles
                ),
                annual_cost_with_battery_eur=float(
                    recommendation.annual_cost_with_battery_eur
                ),
                annual_additional_savings_eur=float(
                    recommendation.annual_additional_savings_eur
                ),
                marginal_recovered_kwh_per_kwh=float(
                    recommendation.marginal_recovered_kwh_per_kwh
                ),
                incremental_battery_cost_eur=float(
                    recommendation.incremental_battery_cost_eur
                ),
                incremental_savings_eur=float(
                    recommendation.incremental_savings_eur
                ),
                marginal_savings_per_kwh=float(
                    recommendation.marginal_savings_per_kwh
                ),
                marginal_payback_years=float(
                    recommendation.marginal_payback_years
                ),
                economic_npv_eur=float(
                    recommendation.economic_npv_eur
                ),
                economic_irr_percent=float(
                    recommendation.economic_irr_percent
                ),
                economic_payback_years=float(
                    recommendation.economic_payback_years
                ),
                combined_economic_npv_eur=float(
                    recommendation.combined_economic_npv_eur
                ),
                combined_economic_irr_percent=float(
                    recommendation.combined_economic_irr_percent
                ),
                combined_economic_payback_years=float(
                    recommendation.combined_economic_payback_years
                ),
            )
            for recommendation in battery_recommendations
        ]

        # ---------------------------------------------------------
        # Resultado final
        # ---------------------------------------------------------

        return SolarReportData(
            calculation_mode=calculation_mode,

            installed_power_kwp=installed_power_kwp,

            yearly_production_kwh=yearly_production_kwh,
            monthly_production=monthly_production,

            specific_production_kwh_kwp=(
                float(specific_production)
                if specific_production is not None
                else 0.0
            ),

            productive_hours=productive_hours,
            daily_average_kwh=daily_average,
            monthly_average_kwh=monthly_average,
            maximum_hourly_production_kwh=(
                maximum_hourly_production
            ),
            capacity_factor_percent=capacity_factor,

            yearly_consumption_kwh=yearly_consumption_kwh,
            consumption_reference_year=(
                consumption_reference_year
            ),
            monthly_consumption=monthly_consumption,

            self_consumption_kwh=self_consumption_kwh,
            grid_export_kwh=grid_export_kwh,
            grid_import_kwh=grid_import_kwh,

            self_consumption_rate_percent=(
                self_consumption_rate_percent
            ),

            self_sufficiency_rate_percent=(
                self_sufficiency_rate_percent
            ),

            cost_without_pv_eur=cost_without_pv_eur,
            grid_import_cost_eur=grid_import_cost_eur,
            export_income_eur=export_income_eur,
            cost_with_pv_eur=cost_with_pv_eur,
            self_consumption_savings_eur=(
                self_consumption_savings_eur
            ),

            investment_eur=investment_eur,
            yearly_savings_eur=yearly_savings_eur,
            payback_years=payback_years,
            net_present_value_eur=net_present_value_eur,
            internal_rate_of_return_percent=(
                internal_rate_of_return
            ),

            economic_horizon_years=economic_horizon_years,

            first_year_degradation_percent=(
                first_year_degradation_percent
            ),
            annual_degradation_percent=(
                annual_degradation_percent
            ),
            annual_electricity_price_growth_percent=(
                annual_electricity_price_growth_percent
            ),
            annual_export_price_growth_percent=(
                annual_export_price_growth_percent
            ),
            annual_maintenance_cost_eur=(
                annual_maintenance_cost_eur
            ),
            annual_maintenance_growth_percent=(
                annual_maintenance_growth_percent
            ),
            discount_rate_percent=discount_rate_percent,

            scenario_results=scenario_results,

            battery_recommendations=battery_report_data,

            panel_count=panel_count,
            panel_power_wp=panel_power_wp,

            latitude=latitude,
            longitude=longitude,
            tilt=tilt,
            azimuth=azimuth,
            reference_year=reference_year,
            losses=losses,
            pv_technology=pv_technology,
            mounting_place=mounting_place,
        )