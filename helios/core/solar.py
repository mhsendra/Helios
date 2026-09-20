from helios.solar.configuration import SolarConfiguration
from helios.solar.manager import SolarManager
from helios.core.consumption_scenario import ConsumptionScenario

class SolarEngine:

    def __init__(self):

        self.manager = SolarManager()

    @property
    def configuration(self):

        return self.manager.configuration

    # ==================================================
    # Métodos de cálculo
    # ==================================================

    def calculate_hourly_production(
        self,
        configuration: SolarConfiguration,
        installed_power_kwp: float = 1.0,
    ):
        self.manager.calculate_hourly_production(
            configuration,
            installed_power_kwp,
        )

    def calculate_daily_production(self):

        self.manager.calculate_daily_production()

    def calculate_monthly_production(self):

        self.manager.calculate_monthly_production()

    def calculate_yearly_production(self):

        self.manager.calculate_yearly_production()

    def calculate_energy_balance(
        self,
        consumption_scenario: ConsumptionScenario,
    ):

        self.manager.calculate_energy_balance(
            consumption_scenario
        )

    def calculate_statistics(self):

        self.manager.calculate_statistics()

    # ==================================================
    # Propiedades de acceso al estado
    # ==================================================

    @property
    def hourly_production(self):

        return self.manager.hourly_production

    @property
    def daily_production(self):

        return self.manager.daily_production

    @property
    def monthly_production(self):

        return self.manager.monthly_production

    @property
    def yearly_production(self):

        return self.manager.yearly_production

    @property
    def statistics(self):

        return self.manager.statistics

    @property
    def energy_balance(self):

        return self.manager.energy_balance

    def set_energy_balance(self, energy_balance):
        self.manager.energy_balance = energy_balance

    @property
    def installed_power_kwp(self):
        return self.manager.installed_power_kwp

    # ==================================================
    # Informes
    # ==================================================

    def monthly_production_report(self):

        return self.manager.monthly_production_report()

    def production_statistics_report(self):

        return self.manager.production_statistics_report()

    def energy_balance_report(self):

        return self.manager.energy_balance_report()

    # ==================================================
    # Configuración
    # ==================================================

    def set_configuration(
        self,
        configuration,
    ):

        self.manager.set_configuration(
            configuration
        )

    def reset(self):

        self.manager.reset()