from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class SolarReportData:

    # ==================================================
    # Installation
    # ==================================================

    installed_power_kwp: float

    panel_count: int

    panel_power_wp: float

    # ==================================================
    # Solar production
    # ==================================================

    yearly_production_kwh: float

    monthly_production: pd.Series

    specific_production_kwh_kwp: float

    # ==================================================
    # Energy balance
    # ==================================================

    yearly_consumption_kwh: float

    self_consumption_kwh: float

    grid_export_kwh: float

    grid_import_kwh: float

    self_consumption_rate_percent: float

    self_sufficiency_rate_percent: float

    # ==================================================
    # Economics
    # ==================================================

    investment_eur: float

    yearly_savings_eur: float

    payback_years: float

    net_present_value_eur: float

    internal_rate_of_return_percent: float