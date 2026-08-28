import pandas as pd

from helios.reports.solar_reports import SolarReports

from helios.solar.balance import SolarBalanceEngine
from helios.solar.configuration import SolarConfiguration
from helios.solar.parser import PVGISParser
from helios.solar.production import SolarProductionEngine
from helios.solar.pvgis import PVGISClient
from helios.solar.statistics import SolarStatisticsEngine


class SolarManager:

    def __init__(self):

        self.client = PVGISClient()

        self.parser = PVGISParser()

        self.production_engine = SolarProductionEngine()

        self.balance_engine = SolarBalanceEngine()

        self.statistics_engine = SolarStatisticsEngine()

        self.reporter = SolarReports()

        self.configuration = None

        self.hourly_production = None

        self.daily_production = None

        self.monthly_production = None

        self.yearly_production = None

        self.energy_balance = None

        self.statistics = None

    def calculate_hourly_production(
        self,
        configuration: SolarConfiguration
    ) -> pd.DataFrame:

        self.configuration = configuration

        self.daily_production = None
        self.monthly_production = None
        self.yearly_production = None
        self.energy_balance = None
        self.statistics = None

        response = self.client.fetch(
            configuration
        )

        self.hourly_production = self.parser.parse(
            response
        )

    def calculate_daily_production(self):
    
            if self.hourly_production is None:
    
                raise RuntimeError(
                    "Hourly production has not been calculated."
                )
    
            self.daily_production = (
                self.production_engine.daily(
                    self.hourly_production
                )
            )
    
    def calculate_monthly_production(self):

        if self.daily_production is None:

            self.calculate_daily_production()

        self.monthly_production = (
            self.production_engine.monthly(
                self.daily_production
            )
        )

    def calculate_yearly_production(self):
    
            if self.monthly_production is None:
    
                self.calculate_monthly_production()
    
            self.yearly_production = (
                self.production_engine.yearly(
                    self.monthly_production
                )
            )
    
    def calculate_energy_balance(
        self,
        consumption: pd.Series
    ):

        if self.hourly_production is None:

            raise RuntimeError(
                "Hourly production has not been calculated."
            )

        self.energy_balance = (
            self.balance_engine.calculate(
                consumption,
                self.hourly_production
            )
        )

    def calculate_statistics(self):

        if self.hourly_production is None:

            raise RuntimeError(
                "Hourly production has not been calculated."
            )

        if self.energy_balance is None:

            raise RuntimeError(
                "Energy balance has not been calculated."
            )

        self.statistics = (
            self.statistics_engine.calculate(
                self.hourly_production,
                self.energy_balance,
                self.configuration
            )
        )

    def production_statistics_report(self):

        if self.statistics is None:

            raise RuntimeError(
                "Solar statistics have not been calculated."
            )

        self.reporter.production_statistics(
            self.statistics,
            self.configuration
        )

    def energy_balance_report(self):

        if self.statistics is None:

            raise RuntimeError(
                "Energy statistics have not been calculated."
            )

        self.reporter.energy_balance(
            self.statistics
        )

    def monthly_production_report(self):

        if self.monthly_production is None:

            raise RuntimeError(
                "Monthly production has not been calculated."
            )

        self.reporter.monthly_production(
            self.monthly_production
        )

    def installation_simulation_report(
        self,
        configuration,
        recommendation,
        solar_configuration=None,
        specific_production=None,
    ):
        """
        Genera el informe de una simulación de instalación
        fotovoltaica.

        El Manager coordina los datos necesarios y delega
        la presentación en SolarReports.
        """

        if configuration is None:

            raise ValueError(
                "Installation configuration is not available."
            )

        if recommendation is None:

            raise ValueError(
                "Solar installation simulation "
                "has not been calculated."
            )

        if solar_configuration is None:

            solar_configuration = self.configuration

        if specific_production is None:

            if self.yearly_production is None:
                raise RuntimeError(
                    "Yearly production has not been calculated."
                )

            if recommendation.installed_power_kwp <= 0:
                raise ValueError(
                    "Installed power must be greater than zero."
                )

            specific_production = (
                self.yearly_production.sum()
                / recommendation.installed_power_kwp
            )

        return self.reporter.installation_simulation(
            configuration=configuration,
            recommendation=recommendation,
            solar_configuration=solar_configuration,
            specific_production=specific_production,
        )

    def reset(self):

        self.configuration = None
        self.hourly_production = None
        self.daily_production = None
        self.monthly_production = None
        self.yearly_production = None
        self.energy_balance = None
        self.statistics = None

    def set_configuration(
        self,
        configuration: SolarConfiguration,
    ):
        if not isinstance(
            configuration,
            SolarConfiguration,
        ):
            raise TypeError(
                "configuration must be a SolarConfiguration."
            )

        self.configuration = configuration