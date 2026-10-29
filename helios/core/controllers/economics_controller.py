from helios.reports.economics import EconomicsReports
from helios.core.economic_scenarios import EconomicScenario
class EconomicsController:

    def __init__(self, analyzer, configuration):

        self.analyzer = analyzer

        self.configuration = configuration

        self.reports_engine = EconomicsReports()

        self._economic_data = None

    def _get_economic_data(self):
        consumption_scenario = (
            self.analyzer
            .calculate_representative_consumption_scenario()
        )

        if consumption_scenario is None:
            raise ValueError(
                "A representative consumption scenario is required "
                "for economic calculations."
            )

        tariff_data = (
            self.analyzer
            .tariff_engine
            .build_tariff_data(
                consumption_scenario.hourly_consumption.index
            )
        )

        return consumption_scenario, tariff_data

    def calculate_cost_without_pv(
        self,
        consumption_scenario=None,
    ):
        if self._economic_data is None:
            self._economic_data = self._get_economic_data()

        default_consumption_scenario, tariff_data = (
            self._economic_data
        )

        if consumption_scenario is None:
            consumption_scenario = default_consumption_scenario

        return (
            self.analyzer.economics_engine
            .calculate_cost_without_pv(
                consumption_scenario,
                tariff_data,
            )
        )

    def calculate_export_income(self):
        if self._economic_data is None:
            self._economic_data = self._get_economic_data()

        _, tariff_data = self._economic_data

        return (
            self.analyzer.economics_engine
            .calculate_export_income(
                self.analyzer.solar.energy_balance,
                tariff_data,
            )
        )

    def calculate_export_income_for_balance(
        self,
        energy_balance,
    ) -> float:
        """
        Calcula la compensación efectiva de excedentes para un
        balance arbitrario sin modificar el estado económico.
        """
        if self._economic_data is None:
            self._economic_data = self._get_economic_data()

        _, tariff_data = self._economic_data

        return (
            self.analyzer.economics_engine
            .calculate_export_income_for_balance(
                energy_balance,
                tariff_data,
            )
        )

    def calculate_cost_with_pv(self):
        if self._economic_data is None:
            self._economic_data = self._get_economic_data()

        _, tariff_data = self._economic_data

        return (
            self.analyzer.economics_engine
            .calculate_cost_with_pv(
                self.analyzer.solar.energy_balance,
                tariff_data,
            )
        )

    def calculate_cost_with_balance(self, energy_balance):
        if self._economic_data is None:
            self._economic_data = self._get_economic_data()

        _, tariff_data = self._economic_data

        return (
            self.analyzer.economics_engine
            .calculate_cost_with_balance(
                energy_balance,
                tariff_data,
            )
        )

    def calculate_annual_savings(self):

        return (
            self.analyzer.economics_engine
            .calculate_annual_savings()
        )

    def calculate(self):
        economics = self.analyzer.economics_engine

        # Invalidar primero el estado anterior. Si cualquier etapa falla,
        # no se conservará un indicador de cálculo completado.
        economics.economic_analysis_calculated = False

        self._economic_data = None

        try:
            self._economic_data = self._get_economic_data()

            self.calculate_cost_without_pv()
            self.calculate_export_income()
            self.calculate_cost_with_pv()
            self.calculate_annual_savings()
            self.calculate_net_investment()
            self.calculate_cash_flow()
            self.calculate_economic_indicators()

            # Este es el único punto donde se confirma el cálculo.
            economics.economic_analysis_calculated = True

        finally:
            self._economic_data = None
        
    def reports(self):

        self.annual_economics_report()
        self.economic_scenarios_report()
        
    def calculate_net_investment(self):
        """Calcula la inversión usando la instalación seleccionada.

        Prioriza el desglose de costes de la instalación dimensionada.
        Un presupuesto explícito solo se acepta si no hay una instalación
        dimensionada con costes de catálogo configurados.
        """
        project = getattr(self.analyzer, "project", None)
        solar_controller = getattr(self.analyzer, "solar", None)

        sizing_result = getattr(
            solar_controller,
            "sizing_result",
            None,
        )
        installation_cost_configuration = getattr(
            project,
            "installation_cost_configuration",
            None,
        )

        if (
            sizing_result is not None
            and installation_cost_configuration is not None
        ):
            installation_cost = (
                solar_controller._calculate_combined_installation_cost(
                    evaluation=sizing_result.evaluation,
                    installation_cost_configuration=(
                        installation_cost_configuration
                    ),
                )
            )
        else:
            installation_cost = self.configuration.installation_cost

        if installation_cost is None:
            raise ValueError(
                "No se puede calcular el VAN/TIR: configura los costes "
                "del catálogo para la instalación dimensionada o introduce "
                "un presupuesto explícito."
            )

        from dataclasses import replace

        configuration = replace(
            self.configuration,
            installation_cost=float(installation_cost),
        )

        return (
            self.analyzer.economics_engine
            .calculate_net_investment(
                configuration
            )
        )
              
    def calculate_cash_flow(
        self,
        years: int | None = None,
    ):
        if years is None:
            years = self.configuration.economic_horizon_years

        return (
            self.analyzer.economics_engine
            .calculate_cash_flow(
                self.configuration,
                years
            )
        )
        
    def calculate_economic_indicators(self):

        return (
            self.analyzer.economics_engine
            .calculate_economic_indicators(
                self.configuration.discount_rate
            )
        )

    def economic_summary(self):

        return (
            self.analyzer.economics_engine
            .economic_summary()
        )

    def calculate_scenario(
        self,
        scenario: EconomicScenario,
        years: int | None = None,
    ):
        if years is None:
            years = self.configuration.economic_horizon_years

        return self.analyzer.economics_engine.calculate_scenario(
            scenario,
            self.configuration,
            years,
        )

    def calculate_scenarios(
        self,
        scenarios,
        years: int | None = None,
    ):
        if years is None:
            years = self.configuration.economic_horizon_years
            
        return (
            self.analyzer.economics_engine
            .calculate_scenarios(
                scenarios,
                self.configuration,
                years,
            )
        )

    def scenarios_report(self):

        self.reports_engine.economic_scenarios(
            self.analyzer.economics_engine.scenario_results
        )

    def annual_economics_report(self):

        economics = self.analyzer.economics_engine

        self.reports_engine.annual_economics(
            economics.cost_without_pv,
            economics.grid_import_cost,
            economics.export_income,
            economics.cost_with_pv,
            economics.annual_savings,
            economics.net_investment,
            economics.payback_years,
            economics.cash_flow,
            economics.npv,
            self.configuration.discount_rate,
            economics.irr
        )

    def economic_scenarios_report(self):

        self.reports_engine.economic_scenarios(
            self.analyzer.economics_engine.scenario_results
        )