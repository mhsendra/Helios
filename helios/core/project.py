from helios.core.analyzer import ConsumptionAnalyzer
from helios.core.controllers.solar_controller import SolarController

from helios.core.controllers.validation_controller import ValidationController
from helios.core.controllers.profiles_controller import ProfilesController
from helios.core.controllers.comparisons_controller import ComparisonsController
from helios.core.controllers.indicators_controller import IndicatorsController
from helios.core.controllers.tariffs_controller import TariffsController
from helios.core.controllers.solar_controller import SolarController


class HeliosProject:

    def __init__(self):

        self.analyzer = ConsumptionAnalyzer()

        self.validation = ValidationController(self.analyzer)
        self.profiles = ProfilesController(self.analyzer)
        self.comparisons = ComparisonsController(self.analyzer)
        self.indicators = IndicatorsController(self.analyzer)
        self.tariffs = TariffsController(self.analyzer)

        self.solar = SolarController(self.analyzer)