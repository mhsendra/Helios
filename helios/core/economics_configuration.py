from dataclasses import dataclass


@dataclass
class EconomicsConfiguration:

    installation_cost: float

    subsidies: float = 0.0

    tax_deductions: float = 0.0
    
    first_year_degradation: float = 0.01
    annual_degradation: float = 0.0035
    