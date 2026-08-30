from helios.solar.configuration import SolarConfiguration
from helios.solar.manager import SolarManager


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

        if installed_power_kwp == 1.0:
            self.manager.calculate_hourly_production(
                configuration
            )
        else:
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
        consumption,
    ):

        self.manager.calculate_energy_balance(
            consumption
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

    # ==================================================
    # Informes
    # ==================================================

    def monthly_production_report(self):

        return self.manager.monthly_production_report()

    def production_statistics_report(self):

        return self.manager.production_statistics_report()

    def energy_balance_report(self):

        return self.manager.energy_balance_report()

    def installation_simulation_report(
        self,
        configuration,
        recommendation,
        specific_production=None,
    ):

        return self.manager.installation_simulation_report(
            configuration=configuration,
            recommendation=recommendation,
            specific_production=specific_production,
        )

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