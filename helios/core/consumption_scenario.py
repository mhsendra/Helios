from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ConsumptionScenario:
    """Escenario horario anual de consumo utilizado para simulación."""

    hourly_consumption: pd.Series
    reference_year: int = 2025

    def __post_init__(self):
        if not isinstance(self.hourly_consumption, pd.Series):
            raise TypeError("hourly_consumption must be a pandas Series.")

        if not isinstance(self.hourly_consumption.index, pd.DatetimeIndex):
            raise TypeError(
                "hourly_consumption index must be a DatetimeIndex."
            )

        if len(self.hourly_consumption) != 8760:
            raise ValueError(
                "Consumption scenario must contain exactly 8760 hourly values."
            )

        if self.hourly_consumption.isna().any():
            raise ValueError(
                "Consumption scenario cannot contain NaN values."
            )

        if not pd.api.types.is_numeric_dtype(self.hourly_consumption):
            raise TypeError(
                "hourly_consumption must contain numeric values."
            )

        if (self.hourly_consumption < 0).any():
            raise ValueError(
                "Consumption scenario cannot contain negative values."
            )

        expected_index = pd.date_range(
            start=f"{self.reference_year}-01-01 00:00:00",
            periods=8760,
            freq="h",
        )

        if not self.hourly_consumption.index.equals(expected_index):
            raise ValueError(
                "Consumption scenario index must contain a complete "
                "8760-hour reference year."
            )

    @property
    def annual_consumption(self) -> float:
        """Consumo anual total del escenario en kWh."""
        return float(self.hourly_consumption.sum())