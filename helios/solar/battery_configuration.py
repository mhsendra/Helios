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