# helios/core/controllers/solar_controller.py

class SolarController:

    def __init__(self, analyzer):
        """
        Controlador de producción solar.
        Encapsula cálculos, reportes y gráficas relacionadas
        con la producción fotovoltaica y el balance energético.
        """
        self.analyzer = analyzer

    # ==================================================
    # Cálculos de producción solar
    # ==================================================

    def calculate_hourly_production(self, configuration):
        self.analyzer.solar_engine.calculate_hourly_production(
            configuration
        )

    def calculate_daily_production(self):
        self.analyzer.solar_engine.calculate_daily_production()

    def calculate_monthly_production(self):
        self.analyzer.solar_engine.calculate_monthly_production()

    def calculate_yearly_production(self):
        self.analyzer.solar_engine.calculate_yearly_production()

    def calculate_energy_balance(self):
        consumption = self.analyzer.valid_dataset()["AE_kWh"]
        self.analyzer.solar_engine.calculate_energy_balance(consumption)

    def calculate_statistics(self):
        self.analyzer.solar_engine.calculate_statistics()

    def calculate(self, configuration):
        """
        Ejecuta todos los cálculos solares.
        """
        self.calculate_hourly_production(configuration)
        self.calculate_daily_production()
        self.calculate_monthly_production()
        self.calculate_yearly_production()
        self.calculate_energy_balance()
        self.calculate_statistics()

    # ==================================================
    # Reportes solares
    # ==================================================

    def production_statistics_report(self):
        self.analyzer.solar_engine.production_statistics_report()

    def monthly_production_report(self):
        self.analyzer.solar_engine.monthly_production_report()

    def energy_balance_report(self):
        self.analyzer.solar_engine.energy_balance_report()

    def reports(self):
        """
        Genera todos los informes solares.
        """
        self.production_statistics_report()
        self.monthly_production_report()
        self.energy_balance_report()
