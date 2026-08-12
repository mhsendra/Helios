from dataclasses import dataclass


@dataclass
class EconomicsConfiguration:

    installation_cost: float

    subsidies: float = 0.0

    tax_deductions: float = 0.0