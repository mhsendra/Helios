from helios.solar.manager import SolarManager

class SolarEngine:

    def __init__(self):

        self.manager = SolarManager()

    def calculate_hourly_production(
        self,
        configuration
    ):

        return self.manager.calculate_hourly_production(
            configuration
        )
    
    def calculate_daily_production(self):

        return self.manager.calculate_daily_production()

    def calculate_statistics(self):

        return self.manager.calculate_statistics()

    def calculate_monthly_production(self):

        return self.manager.calculate_monthly_production()

    def calculate_yearly_production(self):

        return self.manager.calculate_yearly_production()

    def calculate_energy_balance(
        self,
        consumption
    ):

        return self.manager.calculate_energy_balance(
            consumption
    )

    def monthly_production_report(self):

        return self.manager.monthly_production_report()

    def production_statistics_report(self):

        return self.manager.production_statistics_report()

    def energy_balance_report(self):

        return self.manager.energy_balance_report()