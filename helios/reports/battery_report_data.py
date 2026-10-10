from dataclasses import dataclass


@dataclass(frozen=True)
class BatteryReportData:
    """
    Datos de una capacidad de batería preparados para
    su representación en informes.

    No realiza cálculos. Contiene exclusivamente resultados
    producidos por BatteryOptimizer.
    """

    # ==================================================
    # Configuración física
    # ==================================================

    capacity_kwh: float
    max_charge_power_kw: float
    max_discharge_power_kw: float

    # ==================================================
    # Balance energético anual
    # ==================================================

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

    # ==================================================
    # Economía anual
    # ==================================================

    annual_cost_with_battery_eur: float
    annual_additional_savings_eur: float

    # ==================================================
    # Economía marginal
    # ==================================================

    marginal_recovered_kwh_per_kwh: float
    incremental_battery_cost_eur: float
    incremental_savings_eur: float
    marginal_savings_per_kwh: float
    marginal_payback_years: float

    # ==================================================
    # Economía de la batería
    # ==================================================

    economic_npv_eur: float
    economic_irr_percent: float
    economic_payback_years: float

    # ==================================================
    # Economía conjunta FV + batería
    # ==================================================

    combined_economic_npv_eur: float
    combined_economic_irr_percent: float
    combined_economic_payback_years: float

    # ==================================================
    # Desglose del ahorro incremental de la batería
    # ==================================================

    annual_import_savings_eur: float | None = None
    annual_export_compensation_lost_eur: float | None = None
