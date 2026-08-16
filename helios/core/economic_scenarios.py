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

    def default_economic_scenarios():
        return [
            EconomicScenario(
                name="Conservador",
                buy_price_factor=0.90,
                sell_price_factor=0.90,
                annual_maintenance=200.0,
                annual_degradation=0.005,
            ),
            EconomicScenario(
                name="Base",
            ),
            EconomicScenario(
                name="Optimista",
                buy_price_factor=1.10,
                sell_price_factor=1.10,
                annual_maintenance=100.0,
                annual_degradation=0.0025,
            ),
        ]