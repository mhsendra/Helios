from dataclasses import dataclass


@dataclass
class EconomicScenario:

    name: str

    buy_price_factor: float = 1.0
    sell_price_factor: float = 1.0

    annual_maintenance: float | None = None
    annual_degradation: float | None = None
    discount_rate: float | None = None


@dataclass
class EconomicScenarioResult:

    name: str
    annual_savings: float
    payback_years: float
    npv: float
    irr: float