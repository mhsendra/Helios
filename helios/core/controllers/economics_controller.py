from helios.reports.economics import EconomicsReports
from helios.core.economic_scenarios import EconomicScenario
class EconomicsController:

    def __init__(self, analyzer, configuration):

        self.analyzer = analyzer

        self.configuration = configuration

        self.reports_engine = EconomicsReports()

    def calculate_cost_without_pv(self):

        return (
            self.analyzer.economics_engine
            .calculate_cost_without_pv(
                self.analyzer.dataset
            )
        )

    def calculate_export_income(self):

        return (
            self.analyzer.economics_engine
            .calculate_export_income(
                self.analyzer.solar.energy_balance,
                self.analyzer.dataset,
            )
        )

    def calculate_cost_with_pv(self):

        return (
            self.analyzer.economics_engine
            .calculate_cost_with_pv(
                self.analyzer.solar.energy_balance,
                self.analyzer.dataset,
            )
        )

    def calculate_annual_savings(self):

        return (
            self.analyzer.economics_engine
            .calculate_annual_savings()
        )

    def calculate(self):

        self.calculate_cost_without_pv()
        self.calculate_export_income()
        self.calculate_cost_with_pv()
        economics = self.analyzer.economics_engine
        balance = self.analyzer.solar.energy_balance

        print(
            ">>> BALANCE CONSUMPTION:",
            balance["consumption_kwh"].sum()
        )

        print(
            ">>> BALANCE PRODUCTION:",
            balance["production_kwh"].sum()
        )

        print(
            ">>> BALANCE SELF CONSUMPTION:",
            balance["self_consumption_kwh"].sum()
        )

        print(
            ">>> BALANCE GRID IMPORT:",
            balance["grid_import_kwh"].sum()
        )

        print(
            ">>> BALANCE GRID EXPORT:",
            balance["grid_export_kwh"].sum()
        )

        print(
            ">>> COST WITHOUT PV:",
            economics.cost_without_pv
        )

        print(
            ">>> GRID IMPORT COST:",
            economics.grid_import_cost
        )

        print(
            ">>> EXPORT INCOME:",
            economics.export_income
        )

        print(
            ">>> SELF-CONSUMPTION SAVINGS:",
            economics.self_consumption_savings
        )

        print(
            ">>> ANNUAL SAVINGS:",
            economics.annual_savings
        )
        self.calculate_annual_savings()
        self.calculate_net_investment()
        self.calculate_cash_flow()
        print(">>> NET INVESTMENT:", self.analyzer.economics_engine.net_investment)
        print(
            ">>> SELF-CONSUMPTION SAVINGS:",
            self.analyzer.economics_engine.self_consumption_savings,
        )
        print(
            ">>> EXPORT INCOME:",
            self.analyzer.economics_engine.export_income,
        )
        print(
            ">>> CASH FLOW:",
            self.analyzer.economics_engine.cash_flow
        )
        self.calculate_economic_indicators()
        
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
                self.analyzer.dataset,
                self.analyzer.solar.energy_balance,
                self.analyzer.dataset,
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
                self.analyzer.dataset,
                self.analyzer.solar.energy_balance,
                self.analyzer.dataset,
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