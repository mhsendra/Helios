from abc import ABC, abstractmethod

from helios.core.consumption_scenario import ConsumptionScenario
from helios.ev.scenario import EVScenario
from helios.solar.production_profile import SolarProductionProfile


class SolarChargingStrategy(ABC):
    """Contrato para estrategias de carga basadas en producción solar."""

    @abstractmethod
    def apply(
        self,
        ev_scenario: EVScenario,
        consumption_scenario: ConsumptionScenario,
        production_profile: SolarProductionProfile,
    ) -> EVScenario:
        """Distribuye la demanda EV considerando consumo doméstico y FV."""
        raise NotImplementedError