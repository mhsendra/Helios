from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence

from helios.solar.battery_recommendation import BatteryRecommendation


@dataclass(frozen=True)
class BatteryEconomicRecommendation:
    """
    Interpretación económica de una capacidad de batería evaluada.

    Los datos económicos originales permanecen en BatteryRecommendation.
    Esta clase únicamente contiene la conclusión derivada de ellos.
    """

    capacity_kwh: float
    criterion: str
    title: str
    description: str
    evidence: Mapping[str, float | str]


class BatteryEconomicAnalyzer:
    """
    Analiza económicamente las capacidades de batería ya calculadas.

    No realiza simulaciones ni recalcula NPV, IRR o payback.
    """

    CRITERION_POSITIVE_NPV = "positive_npv"
    CRITERION_NO_POSITIVE_NPV = "no_positive_npv"

    @classmethod
    def analyze(
        cls,
        recommendations: Sequence[BatteryRecommendation],
    ) -> list[BatteryEconomicRecommendation]:
        """
        Devuelve la recomendación económica principal.

        El criterio principal es el NPV incremental de la batería.

        Si existe al menos una capacidad con NPV positivo, se selecciona
        la que maximiza dicho NPV.

        Si ninguna capacidad tiene NPV positivo, se devuelve la capacidad
        con el NPV más alto, indicando que ninguna resulta económicamente
        viable bajo las hipótesis utilizadas.
        """
        valid_recommendations = [
            recommendation
            for recommendation in recommendations
            if isfinite(recommendation.economic_npv_eur)
        ]

        if not valid_recommendations:
            return []

        positive_npv = [
            recommendation
            for recommendation in valid_recommendations
            if recommendation.economic_npv_eur > 0.0
        ]

        if positive_npv:
            selected = max(
                positive_npv,
                key=lambda recommendation: (
                    recommendation.economic_npv_eur,
                    -recommendation.capacity_kwh,
                ),
            )

            return [
                cls._build_positive_npv_recommendation(
                    selected,
                )
            ]

        selected = max(
            valid_recommendations,
            key=lambda recommendation: (
                recommendation.economic_npv_eur,
                -recommendation.capacity_kwh,
            ),
        )

        return [
            cls._build_no_positive_npv_recommendation(
                selected,
            )
        ]

    @staticmethod
    def _build_positive_npv_recommendation(
        recommendation: BatteryRecommendation,
    ) -> BatteryEconomicRecommendation:
        payback = recommendation.economic_payback_years
        irr = recommendation.economic_irr_percent

        payback_text = (
            f"{payback:.2f} años"
            if isfinite(payback)
            else "no se alcanza durante el horizonte analizado"
        )

        description = (
            f"La capacidad de {recommendation.capacity_kwh:.1f} kWh "
            f"presenta el mayor NPV incremental entre las capacidades "
            f"económicamente viables, con un NPV de "
            f"{recommendation.economic_npv_eur:.2f} €. "
            f"El ahorro anual adicional es de "
            f"{recommendation.annual_additional_savings_eur:.2f} €. "
            f"El payback económico es {payback_text} "
            f"y la TIR es {irr:.2f} %. "
            f"El incremento marginal respecto a la capacidad anterior "
            f"supone un ahorro de "
            f"{recommendation.incremental_savings_eur:.2f} € "
            f"por año, equivalente a "
            f"{recommendation.marginal_savings_per_kwh:.2f} €/kWh "
            f"de capacidad adicional."
        )

        return BatteryEconomicRecommendation(
            capacity_kwh=recommendation.capacity_kwh,
            criterion=BatteryEconomicAnalyzer.CRITERION_POSITIVE_NPV,
            title="Capacidad de batería económicamente óptima",
            description=description,
            evidence={
                "capacity_kwh": recommendation.capacity_kwh,
                "economic_npv_eur": recommendation.economic_npv_eur,
                "economic_irr_percent": recommendation.economic_irr_percent,
                "economic_payback_years": (
                    recommendation.economic_payback_years
                ),
                "annual_additional_savings_eur": (
                    recommendation.annual_additional_savings_eur
                ),
                "incremental_battery_cost_eur": (
                    recommendation.incremental_battery_cost_eur
                ),
                "incremental_savings_eur": (
                    recommendation.incremental_savings_eur
                ),
                "marginal_savings_per_kwh": (
                    recommendation.marginal_savings_per_kwh
                ),
                "marginal_payback_years": (
                    recommendation.marginal_payback_years
                ),
            },
        )

    @staticmethod
    def _build_no_positive_npv_recommendation(
        recommendation: BatteryRecommendation,
    ) -> BatteryEconomicRecommendation:
        payback = recommendation.economic_payback_years
        irr = recommendation.economic_irr_percent

        payback_text = (
            f"{payback:.2f} años"
            if isfinite(payback)
            else "no se alcanza durante el horizonte analizado"
        )

        description = (
            "Ninguna de las capacidades evaluadas presenta un NPV "
            "incremental positivo bajo las hipótesis económicas "
            "actuales. La capacidad con mejor resultado es "
            f"{recommendation.capacity_kwh:.1f} kWh, con un NPV de "
            f"{recommendation.economic_npv_eur:.2f} €. "
            f"Su ahorro anual adicional es de "
            f"{recommendation.annual_additional_savings_eur:.2f} €. "
            f"El payback económico es {payback_text} "
            f"y la TIR es {irr:.2f} %. "
            f"El incremento marginal respecto a la capacidad anterior "
            f"supone un ahorro de "
            f"{recommendation.incremental_savings_eur:.2f} € "
            f"por año, equivalente a "
            f"{recommendation.marginal_savings_per_kwh:.2f} €/kWh "
            f"de capacidad adicional."
        )

        return BatteryEconomicRecommendation(
            capacity_kwh=recommendation.capacity_kwh,
            criterion=BatteryEconomicAnalyzer.CRITERION_NO_POSITIVE_NPV,
            title="La batería no resulta económicamente viable",
            description=description,
            evidence={
                "capacity_kwh": recommendation.capacity_kwh,
                "economic_npv_eur": recommendation.economic_npv_eur,
                "economic_irr_percent": recommendation.economic_irr_percent,
                "economic_payback_years": (
                    recommendation.economic_payback_years
                ),
                "annual_additional_savings_eur": (
                    recommendation.annual_additional_savings_eur
                ),
                "incremental_battery_cost_eur": (
                    recommendation.incremental_battery_cost_eur
                ),
                "incremental_savings_eur": (
                    recommendation.incremental_savings_eur
                ),
                "marginal_savings_per_kwh": (
                    recommendation.marginal_savings_per_kwh
                ),
                "marginal_payback_years": (
                    recommendation.marginal_payback_years
                ),
            },
        )