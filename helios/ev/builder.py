from dataclasses import dataclass

import pandas as pd

from helios.ev.configuration import EVConfiguration
from helios.ev.scenario import EVScenario


@dataclass(frozen=True)
class EVScenarioBuilder:
    """Construye un escenario horario EV neutro a partir de su configuración."""

    @staticmethod
    def build(configuration: EVConfiguration) -> EVScenario:
        if not isinstance(configuration, EVConfiguration):
            raise TypeError(
                "configuration must be an EVConfiguration."
            )

        index = pd.date_range(
            start=f"{configuration.reference_year}-01-01 00:00:00",
            end=f"{configuration.reference_year}-12-31 23:00:00",
            freq="h",
        )

        if pd.Timestamp(
            f"{configuration.reference_year}-12-31"
        ).is_leap_year:
            index = index[
                ~(
                    (index.month == 2)
                    & (index.day == 29)
                )
            ]

        hourly_consumption = pd.Series(
            configuration.annual_consumption_kwh / 8760.0,
            index=index,
            dtype=float,
        )

        return EVScenario(
            hourly_consumption=hourly_consumption,
            reference_year=configuration.reference_year,
        )