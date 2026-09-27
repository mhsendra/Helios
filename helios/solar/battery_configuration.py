import math
from dataclasses import dataclass


@dataclass
class BatteryConfiguration:

    capacity_kwh: float

    max_charge_power_kw: float

    max_discharge_power_kw: float

    charge_efficiency: float = 0.95

    discharge_efficiency: float = 0.95

    min_soc: float = 0.10

    max_soc: float = 0.90

    initial_soc: float = 0.50

    def __post_init__(self) -> None:
        numeric_values = {
            "capacity_kwh": self.capacity_kwh,
            "max_charge_power_kw": self.max_charge_power_kw,
            "max_discharge_power_kw": self.max_discharge_power_kw,
            "charge_efficiency": self.charge_efficiency,
            "discharge_efficiency": self.discharge_efficiency,
            "min_soc": self.min_soc,
            "max_soc": self.max_soc,
            "initial_soc": self.initial_soc,
        }

        for name, value in numeric_values.items():
            if not math.isfinite(value):
                raise ValueError(
                    f"{name} must be finite."
                )

        if self.capacity_kwh <= 0:
            raise ValueError(
                "Battery capacity must be greater than zero."
            )

        if self.max_charge_power_kw < 0:
            raise ValueError(
                "Maximum charge power cannot be negative."
            )

        if self.max_discharge_power_kw < 0:
            raise ValueError(
                "Maximum discharge power cannot be negative."
            )

        if not 0 < self.charge_efficiency <= 1:
            raise ValueError(
                "Charge efficiency must be greater than zero "
                "and less than or equal to one."
            )

        if not 0 < self.discharge_efficiency <= 1:
            raise ValueError(
                "Discharge efficiency must be greater than zero "
                "and less than or equal to one."
            )

        if not 0 <= self.min_soc < self.max_soc <= 1:
            raise ValueError(
                "SOC limits must satisfy "
                "0 <= min_soc < max_soc <= 1."
            )

        if not self.min_soc <= self.initial_soc <= self.max_soc:
            raise ValueError(
                "Initial SOC must be between min_soc and max_soc."
            )