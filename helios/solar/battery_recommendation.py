from dataclasses import dataclass


@dataclass(frozen=True)
class BatteryRecommendation:
    capacity_kwh: float
    max_charge_power_kw: float
    max_discharge_power_kw: float

    annual_consumption_kwh: float
    annual_production_kwh: float

    annual_surplus_kwh: float
    annual_export_kwh: float
    annual_grid_import_kwh: float

    annual_battery_charge_kwh: float
    annual_battery_discharge_kwh: float

    self_consumption_kwh: float
    self_sufficiency_percent: float

    equivalent_cycles: float

    annual_cost_with_battery_eur: float = 0.0
    annual_additional_savings_eur: float = 0.0

    marginal_recovered_kwh_per_kwh: float = 0.0

    incremental_battery_cost_eur: float = 0.0
    incremental_savings_eur: float = 0.0
    marginal_savings_per_kwh: float = 0.0
    marginal_payback_years: float = float("inf")

    economic_npv_eur: float = 0.0
    economic_irr_percent: float = 0.0
    economic_payback_years: float = float("inf")

    @property
    def battery_energy_stored_kwh(self) -> float:
        return self.annual_battery_charge_kwh

    @property
    def battery_energy_recovered_kwh(self) -> float:
        return self.annual_battery_discharge_kwh

    @property
    def solar_energy_used_kwh(self) -> float:
        return (
            self.annual_production_kwh
            - self.annual_export_kwh
        )