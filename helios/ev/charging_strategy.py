from abc import ABC, abstractmethod

from helios.ev.scenario import EVScenario


class EVChargingStrategy(ABC):
    """Contrato común para las estrategias de carga del vehículo eléctrico."""

    @abstractmethod
    def apply(self, scenario: EVScenario) -> EVScenario:
        """Aplica la estrategia y devuelve el escenario resultante."""
        raise NotImplementedError