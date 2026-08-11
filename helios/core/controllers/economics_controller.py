from helios.reports.economics import EconomicsReports
class EconomicsController:

    def __init__(self, analyzer):

        self.analyzer = analyzer

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

    def reports(self):

        economics = self.analyzer.economics_engine

        self.reports_engine.annual_economics(
            economics.cost_without_pv,
            economics.grid_import_cost,
            economics.export_income,
            economics.cost_with_pv,
            economics.annual_savings
        )