from dataclasses import dataclass


@dataclass(frozen=True)
class BatteryEconomicParameters:
    """
    Parámetros económicos propios de la batería.

    No contiene parámetros físicos de operación ni parámetros
    económicos generales de la instalación.
    """

    cost_per_kwh_eur: float = 249.70

    lifetime_years: int = 25

    annual_degradation: float = 0.02

    annual_maintenance_eur: float = 0.0