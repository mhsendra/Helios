from dataclasses import dataclass


@dataclass(frozen=True)
class EVConfiguration:
    """Configuración básica de demanda anual de un vehículo eléctrico."""

    annual_consumption_kwh: float
    reference_year: int = 2025

    def __post_init__(self):
        if self.annual_consumption_kwh < 0:
            raise ValueError(
                "annual_consumption_kwh cannot be negative."
            )

        if self.reference_year < 1:
            raise ValueError(
                "reference_year must be a positive integer."
            )

    @property
    def average_daily_consumption_kwh(self) -> float:
        """Consumo medio diario del vehículo en kWh/día."""
        return self.annual_consumption_kwh / 365.0