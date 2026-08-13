from helios.reports.economics import EconomicsReports
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
        self.calculate_annual_savings()
        self.calculate_net_investment()
        self.calculate_cash_flow()
        self.calculate_economic_indicators()
        
    def reports(self):

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