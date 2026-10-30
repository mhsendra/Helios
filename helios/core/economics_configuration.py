from dataclasses import dataclass


@dataclass
class EconomicsConfiguration:

    # Solo se usa como presupuesto explícito introducido por el usuario.
    # La aplicación no debe establecer un presupuesto cerrado por defecto.
    installation_cost: float | None = None

    subsidies: float = 0.0

    tax_deductions: float = 0.0
    
    first_year_degradation: float = 0.01
    annual_degradation: float = 0.0035
    
    annual_electricity_price_growth: float = 0.02
    
    annual_export_price_growth: float = 0.0
    
    annual_maintenance_cost: float = 150.0
    annual_maintenance_growth: float = 0.02
    
    discount_rate: float = 0.05

    economic_horizon_years: int = 25