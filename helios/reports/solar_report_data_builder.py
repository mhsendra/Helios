from __future__ import annotations

from helios.reports.solar_report_data import SolarReportData


class SolarReportDataBuilder:
    """
    Construye SolarReportData a partir del estado actual de un HeliosProject.

    El builder adapta las estructuras internas del proyecto al modelo
    específico utilizado por el generador de informes PDF.
    """

    ECONOMIC_HORIZON_YEARS = 25

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
        # Instalación
        # ---------------------------------------------------------

        sizing_result = getattr(
            solar,
            "sizing_result",
            None,
        )

        installed_power_kwp = (
            float(sizing_result.installed_power_kwp)
            if sizing_result is not None
            else None
        )

        panel_count = (
            int(sizing_result.panel_count)
            if sizing_result is not None
            else None
        )

        installation_configuration = getattr(
            solar,
            "installation_configuration",
            None,
        )

        panel_power_wp = (
            float(installation_configuration.panel_power_wp)
            if installation_configuration is not None
            else None
        )

        # ---------------------------------------------------------
        # Producción
        # ---------------------------------------------------------

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
            statistics.get("productive_hours", 0)
        )

        daily_average = float(
            statistics.get("daily_average", 0.0)
        )

        monthly_average = float(
            statistics.get("monthly_average", 0.0)
        )

        maximum_power = float(
            statistics.get("maximum_power", 0.0)
        )

        capacity_factor = float(
            statistics.get("capacity_factor", 0.0)
        )

        # ---------------------------------------------------------
        # Balance energético
        # ---------------------------------------------------------

        balance = solar.energy_balance

        if balance is not None and not balance.empty:
            yearly_consumption_kwh = float(
                balance["consumption_kwh"].sum()
            )

            self_consumption_kwh = float(
                balance["self_consumption_kwh"].sum()
            )

            grid_export_kwh = float(
                balance["grid_export_kwh"].sum()
            )

            grid_import_kwh = float(
                balance["grid_import_kwh"].sum()
            )
        else:
            yearly_consumption_kwh = float(
                statistics.get("consumption", 0.0)
            )

            self_consumption_kwh = float(
                statistics.get("self_consumption", 0.0)
            )

            grid_export_kwh = float(
                statistics.get("grid_export", 0.0)
            )

            grid_import_kwh = float(
                statistics.get("grid_import", 0.0)
            )

        # ---------------------------------------------------------
        # Ratios energéticos
        # ---------------------------------------------------------

        self_consumption_rate_percent = float(
            statistics.get("self_consumption_ratio", 0.0)
        )

        self_sufficiency_rate_percent = float(
            statistics.get("self_sufficiency", 0.0)
        )

        # ---------------------------------------------------------
        # Economía
        # ---------------------------------------------------------

        cost_without_pv_eur = float(
            getattr(economics_engine, "cost_without_pv", 0.0)
        )

        grid_import_cost_eur = float(
            getattr(economics_engine, "grid_import_cost", 0.0)
        )

        export_income_eur = float(
            getattr(economics_engine, "export_income", 0.0)
        )

        cost_with_pv_eur = float(
            getattr(economics_engine, "cost_with_pv", 0.0)
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
            getattr(economics_engine, "annual_savings", 0.0)
        )

        payback_value = getattr(
            economics_engine,
            "payback_years",
            None,
        )

        if payback_value is not None:
            payback_years = float(payback_value)
        else:
            payback_years = None

        net_present_value_eur = float(
            getattr(economics_engine, "npv", 0.0)
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
            float(economics_configuration.first_year_degradation)
            * 100
        )

        annual_degradation_percent = (
            float(economics_configuration.annual_degradation)
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
            float(economics_configuration.discount_rate)
            * 100
        )

        scenario_results = list(
            getattr(
                economics_engine,
                "scenario_results",
                [],
            )
            or []
        )

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

        print(">>> REPORT DATA DEBUG")
        print("installed_power_kwp:", installed_power_kwp)
        print("panel_count:", panel_count)
        print("panel_power_wp:", panel_power_wp)
        print("yearly_production_kwh:", yearly_production_kwh)
        print("specific_production:", specific_production)
        print("productive_hours:", productive_hours)
        print("daily_average:", daily_average)
        print("monthly_average:", monthly_average)
        print("maximum_power:", maximum_power)
        print("capacity_factor:", capacity_factor)
        print("yearly_consumption_kwh:", yearly_consumption_kwh)
        print("self_consumption_kwh:", self_consumption_kwh)
        print("grid_export_kwh:", grid_export_kwh)
        print("grid_import_kwh:", grid_import_kwh)
        print("self_consumption_rate_percent:", self_consumption_rate_percent)
        print("self_sufficiency_rate_percent:", self_sufficiency_rate_percent)
        print("cost_without_pv_eur:", cost_without_pv_eur)
        print("grid_import_cost_eur:", grid_import_cost_eur)
        print("export_income_eur:", export_income_eur)
        print("cost_with_pv_eur:", cost_with_pv_eur)
        print("self_consumption_savings_eur:", self_consumption_savings_eur)
        print("investment_eur:", investment_eur)
        print("yearly_savings_eur:", yearly_savings_eur)
        print("payback_years:", payback_years)
        print("net_present_value_eur:", net_present_value_eur)
        print("internal_rate_of_return:", internal_rate_of_return)
        print("scenario_results:", scenario_results)

        # ---------------------------------------------------------
        # Resultado final
        # ---------------------------------------------------------

        return SolarReportData(
            calculation_mode="project",

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
            maximum_power_kw=maximum_power,
            capacity_factor_percent=capacity_factor,

            yearly_consumption_kwh=yearly_consumption_kwh,
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

            economic_horizon_years=(
                cls.ECONOMIC_HORIZON_YEARS
            ),

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