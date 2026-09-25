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

    def calculate_cost_without_pv(self):
        if self._economic_data is None:
            self._economic_data = self._get_economic_data()

        consumption_scenario, tariff_data = self._economic_data

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

        self.analyzer.economics_engine.calculate_export_income(
            energy_balance,
            tariff_data,
        )

        return (
            self.analyzer.economics_engine
            .calculate_cost_with_pv(
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
        self._economic_data = self._get_economic_data()

        self.calculate_cost_without_pv()
        self.calculate_export_income()
        self.calculate_cost_with_pv()
        self.calculate_annual_savings()
        self.calculate_net_investment()
        self.calculate_cash_flow()
        self.calculate_economic_indicators()

        self._economic_data = None
        
    def reports(self):

        self.annual_economics_report()
        self.economic_scenarios_report()
        
    def calculate_net_investment(self):

        return (
            self.analyzer.economics_engine
            .calculate_net_investment(
                self.configuration
            )
        )
              
    def calculate_cash_flow(
        self,
        years: int = 25
    ):

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
    ):

        return (
            self.analyzer.economics_engine
            .calculate_scenario(
                scenario,
                self.configuration,
            )
        )

    def calculate_scenarios(
        self,
        scenarios,
        years: int = 25,
    ):
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