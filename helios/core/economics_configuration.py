from dataclasses import dataclass


@dataclass
class EconomicsConfiguration:

    installation_cost: float

    subsidies: float = 0.0

    tax_deductions: float = 0.0
    
    first_year_degradation: float = 0.01
    annual_degradation: float = 0.0035
    
    annual_electricity_price_growth: float = 0.02
    
    annual_export_price_growth: float = 0.0
    
    annual_maintenance_cost: float = 0.0
    annual_maintenance_growth: float = 0.02