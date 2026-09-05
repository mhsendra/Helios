from helios.reports.solar_report_data import SolarReportData


class SolarReportDataFactory:
    """
    Construye los datos necesarios para el informe solar.

    No realiza cálculos de producción ni económicos.
    Recoge resultados ya calculados por los engines.

    Soporta dos modos:

    - automatic: existe un SolarSizingResult procedente
      del dimensionamiento físico.
    - manual: existe una SolarConfiguration y una potencia
      de simulación, pero no existe SolarSizingResult.
    """

    @staticmethod
    def create(
        solar_controller,
        economics_controller,
    ) -> SolarReportData:

        if solar_controller is None:
            raise ValueError(
                "solar controller is required"
            )

        if economics_controller is None:
            raise ValueError(
                "economics controller is required"
            )

        statistics = (
            solar_controller.statistics
        )

        if statistics is None:
            raise ValueError(
                "solar statistics are required"
            )

        configuration = (
            solar_controller.configuration
        )

        if configuration is None:
            raise ValueError(
                "solar configuration is required"
            )

        sizing_result = (
            solar_controller.sizing_result
        )

        # ==================================================
        # Calculation mode
        # ==================================================

        if sizing_result is not None:

            calculation_mode = "automatic"

            installed_power_kwp = (
                sizing_result.installed_power_kwp
            )

            panel_count = (
                sizing_result.panel_count
            )

            panel_power_wp = (
                sizing_result
                .evaluation
                .candidate
                .panel_power_wp
            )

            yearly_production_kwh = (
                sizing_result.annual_production_kwh
            )

            yearly_consumption_kwh = (
                sizing_result.annual_consumption_kwh
            )

            self_sufficiency_rate_percent = (
                sizing_result.self_sufficiency_percent
            )

        else:

            calculation_mode = "manual"

            installed_power_kwp = (
                solar_controller
                .simulation_installed_power_kwp
            )

            if installed_power_kwp is None:
                raise ValueError(
                    "simulation installed power is required"
                )

            panel_count = None
            panel_power_wp = None

            yearly_production_kwh = (
                solar_controller.annual_production
            )

            if yearly_production_kwh is None:
                raise ValueError(
                    "solar annual production is required"
                )

            yearly_consumption_kwh = (
                statistics["consumption"]
            )

            self_sufficiency_rate_percent = (
                statistics["self_sufficiency"]
            )

        # ==================================================
        # Economics
        # ==================================================

        economics = (
            economics_controller
            .analyzer
            .economics_engine
        )

        scenario_results = (
            economics.scenario_results
        )

        if not scenario_results:
            raise ValueError(
                "economic scenario results are required"
            )

        cash_flow = economics.cash_flow

        if cash_flow is None:
            raise ValueError(
                "economic cash flow is required"
            )

        if "year" not in cash_flow.columns:
            raise ValueError(
                "economic cash flow year column is required"
            )

        if cash_flow.empty:
            raise ValueError(
                "economic cash flow cannot be empty"
            )

        economic_horizon_years = int(
            cash_flow["year"].max()
        )

        economic_configuration = (
            economics_controller.configuration
        )

        if economic_configuration is None:
            raise ValueError(
                "economic configuration is required"
            )

        # ==================================================
        # Report data
        # ==================================================

        return SolarReportData(

            # ==================================================
            # Calculation mode
            # ==================================================

            calculation_mode=(
                calculation_mode
            ),

            # ==================================================
            # Installation / simulation
            # ==================================================

            installed_power_kwp=(
                installed_power_kwp
            ),

            # ==================================================
            # Solar production
            # ==================================================

            yearly_production_kwh=(
                yearly_production_kwh
            ),

            monthly_production=(
                solar_controller.monthly_production
            ),

            specific_production_kwh_kwp=(
                solar_controller.specific_production
            ),

            # ==================================================
            # Solar statistics
            # ==================================================

            productive_hours=(
                statistics["productive_hours"]
            ),

            daily_average_kwh=(
                statistics["daily_average"]
            ),

            monthly_average_kwh=(
                statistics["monthly_average"]
            ),

            maximum_power_kw=(
                statistics["maximum_power"]
            ),

            capacity_factor_percent=(
                statistics["capacity_factor"]
            ),

            # ==================================================
            # Energy balance
            # ==================================================

            yearly_consumption_kwh=(
                yearly_consumption_kwh
            ),

            self_consumption_kwh=(
                solar_controller.self_consumption
            ),

            grid_export_kwh=(
                solar_controller.grid_export
            ),

            grid_import_kwh=(
                solar_controller.grid_import
            ),

            self_consumption_rate_percent=(
                solar_controller.coverage
            ),

            self_sufficiency_rate_percent=(
                self_sufficiency_rate_percent
            ),

            # ==================================================
            # Economics
            # ==================================================

            cost_without_pv_eur=(
                economics.cost_without_pv
            ),

            grid_import_cost_eur=(
                economics.grid_import_cost
            ),

            export_income_eur=(
                economics.export_income
            ),

            cost_with_pv_eur=(
                economics.cost_with_pv
            ),

            self_consumption_savings_eur=(
                economics.self_consumption_savings
            ),

            investment_eur=(
                economics.net_investment
            ),

            yearly_savings_eur=(
                economics.annual_savings
            ),

            payback_years=(
                economics.payback_years
            ),

            net_present_value_eur=(
                economics.npv
            ),

            internal_rate_of_return_percent=(
                economics.irr * 100
                if economics.irr is not None
                else None
            ),

            # ==================================================
            # Economic scenarios
            # ==================================================

            scenario_results=(
                scenario_results
            ),

            # ==================================================
            # Economic assumptions
            # ==================================================

            economic_horizon_years=(
                economic_horizon_years
            ),

            first_year_degradation_percent=(
                economic_configuration
                .first_year_degradation
                * 100
            ),

            annual_degradation_percent=(
                economic_configuration
                .annual_degradation
                * 100
            ),

            annual_electricity_price_growth_percent=(
                economic_configuration
                .annual_electricity_price_growth
                * 100
            ),

            annual_export_price_growth_percent=(
                economic_configuration
                .annual_export_price_growth
                * 100
            ),

            annual_maintenance_cost_eur=(
                economic_configuration
                .annual_maintenance_cost
            ),

            annual_maintenance_growth_percent=(
                economic_configuration
                .annual_maintenance_growth
                * 100
            ),

            discount_rate_percent=(
                economic_configuration
                .discount_rate
                * 100
            ),

            # ==================================================
            # Automatic dimensioning
            # ==================================================

            panel_count=(
                panel_count
            ),

            panel_power_wp=(
                panel_power_wp
            ),

            # ==================================================
            # Manual simulation configuration
            # ==================================================

            latitude=(
                configuration.latitude
            ),

            longitude=(
                configuration.longitude
            ),

            tilt=(
                configuration.tilt
            ),

            azimuth=(
                configuration.azimuth
            ),

            reference_year=(
                configuration.reference_year
            ),

            losses=(
                configuration.losses
            ),

            pv_technology=(
                configuration.pv_technology
            ),

            mounting_place=(
                configuration.mounting_place
            ),
        )