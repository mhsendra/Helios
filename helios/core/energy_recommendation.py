from dataclasses import dataclass

from helios.ev.scenario import EVScenario
from helios.solar.battery_recommendation import BatteryRecommendation
from helios.solar.installation_recommendation import (
    InstallationRecommendation,
)


@dataclass(frozen=True)
class EnergyRecommendation:
    """
    Recomendación energética integral del proyecto.

    Agrupa la instalación fotovoltaica, la batería y, si existe,
    el escenario de vehículo eléctrico que han sido considerados
    conjuntamente.

    ``evaluated_options`` contiene todas las combinaciones FV +
    batería evaluadas por el optimizador. La propia recomendación
    ganadora también forma parte de esta colección.
    """

    installation_recommendation: InstallationRecommendation
    battery_recommendation: BatteryRecommendation
    ev_scenario: EVScenario | None = None
    optimization_criterion: str = "combined_npv"
    evaluated_options: tuple["EnergyRecommendation", ...] = ()

    @property
    def panel_count(self) -> int:
        return self.installation_recommendation.panel_count

    @property
    def installed_power_kwp(self) -> float:
        return self.installation_recommendation.installed_power_kwp

    @property
    def battery_capacity_kwh(self) -> float:
        return self.battery_recommendation.capacity_kwh

    @property
    def annual_consumption_kwh(self) -> float:
        return self.battery_recommendation.annual_consumption_kwh

    @property
    def annual_production_kwh(self) -> float:
        return self.battery_recommendation.annual_production_kwh

    @property
    def annual_grid_import_kwh(self) -> float:
        return self.battery_recommendation.annual_grid_import_kwh

    @property
    def annual_export_kwh(self) -> float:
        return self.battery_recommendation.annual_export_kwh

    @property
    def annual_battery_charge_kwh(self) -> float:
        return self.battery_recommendation.annual_battery_charge_kwh

    @property
    def annual_battery_discharge_kwh(self) -> float:
        return self.battery_recommendation.annual_battery_discharge_kwh

    @property
    def self_consumption_kwh(self) -> float:
        return self.battery_recommendation.self_consumption_kwh

    @property
    def self_sufficiency_percent(self) -> float:
        return self.battery_recommendation.self_sufficiency_percent

    @property
    def equivalent_cycles(self) -> float:
        return self.battery_recommendation.equivalent_cycles

    @property
    def combined_economic_npv_eur(self) -> float:
        return self.battery_recommendation.combined_economic_npv_eur

    @property
    def combined_economic_irr_percent(self) -> float:
        return self.battery_recommendation.combined_economic_irr_percent

    @property
    def combined_economic_payback_years(self) -> float:
        return (
            self.battery_recommendation
            .combined_economic_payback_years
        )

    @property
    def candidate_count(self) -> int:
        """
        Número total de combinaciones FV + batería evaluadas.

        Antes de completar la recomendación integral puede ser 0
        en objetos construidos manualmente. Las recomendaciones
        producidas por EnergyRecommender contienen siempre todas
        las alternativas evaluadas.
        """
        if self.evaluated_options:
            return len(self.evaluated_options)

        return 1

    @property
    def alternatives(self) -> tuple["EnergyRecommendation", ...]:
        """
        Devuelve todas las alternativas evaluadas.

        La recomendación ganadora está incluida en la colección.
        """
        if self.evaluated_options:
            return self.evaluated_options

        return (self,)