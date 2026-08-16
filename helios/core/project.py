from helios.core.analyzer import ConsumptionAnalyzer
from helios.core.economics_configuration import EconomicsConfiguration
from helios.core.tariffs_model import TariffPrices


class HeliosProject:

    def __init__(
        self,
        economics_configuration: EconomicsConfiguration
    ):

        self.analyzer = ConsumptionAnalyzer(
            economics_configuration
        )

        self.tariff_prices = TariffPrices()

    # ==================================================
    # Controllers
    # ==================================================

    @property
    def validation(self):
        return self.analyzer.validation

    @property
    def statistics(self):
        return self.analyzer.statistics

    @property
    def profiles(self):
        return self.analyzer.profiles

    @property
    def comparisons(self):
        return self.analyzer.comparisons

    @property
    def indicators(self):
        return self.analyzer.indicators

    @property
    def tariffs(self):
        return self.analyzer.tariffs

    @property
    def solar(self):
        return self.analyzer.solar

    @property
    def economics(self):
        return self.analyzer.economics

    @property
    def dataset(self):
        return self.analyzer.dataset

    @property
    def quality(self):
        return self.analyzer.quality

    # ==================================================
    # Carga y preparación de datos
    # ==================================================

    def load_data(self, path):

        self.analyzer.load_excel(path)
        self.analyzer.clean_data()
        self.analyzer.build_datetime()

    def analyze_data(self):

        self.analyzer.validation.calculate()
        self.analyzer.statistics.calculate()
        self.analyzer.profiles.calculate()
        self.analyzer.comparisons.calculate()
        self.analyzer.tariffs.calculate()