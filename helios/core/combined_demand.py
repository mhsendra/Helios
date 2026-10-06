from dataclasses import dataclass

import pandas as pd

from helios.core.consumption_scenario import ConsumptionScenario
from helios.ev.scenario import EVScenario


@dataclass(frozen=True)
class CombinedDemandBuilder:
    """Construye la demanda horaria conjunta de vivienda + vehículo eléctrico."""

    @staticmethod
    def build(
        consumption_scenario: ConsumptionScenario,
        ev_scenario: EVScenario,
    ) -> ConsumptionScenario:
        if not isinstance(
            consumption_scenario,
            ConsumptionScenario,
        ):
            raise TypeError(
                "consumption_scenario must be a ConsumptionScenario."
            )

        if not isinstance(ev_scenario, EVScenario):
            raise TypeError(
                "ev_scenario must be an EVScenario."
            )

        if (
            consumption_scenario.reference_year
            != ev_scenario.reference_year
        ):
            raise ValueError(
                "Consumption and EV scenarios must use the same "
                "reference year."
            )

        if not consumption_scenario.hourly_consumption.index.equals(
            ev_scenario.hourly_consumption.index
        ):
            raise ValueError(
                "Consumption and EV scenarios must use the same "
                "hourly index."
            )

        combined_consumption = (
            consumption_scenario.hourly_consumption
            + ev_scenario.hourly_consumption
        )

        combined_consumption = pd.Series(
            combined_consumption.to_numpy(dtype=float),
            index=consumption_scenario.hourly_consumption.index,
            name="combined_consumption_kwh",
        )

        return ConsumptionScenario(
            hourly_consumption=combined_consumption,
            reference_year=consumption_scenario.reference_year,
        )