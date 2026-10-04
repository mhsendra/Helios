from dataclasses import dataclass
from typing import Mapping

from helios.core.diagnostics import DiagnosticResult

from helios.core.diagnostics.battery_economics import (
    BatteryEconomicRecommendation,
)

@dataclass(frozen=True)
class RecommendationResult:
    """
    Recomendación derivada de uno o varios diagnósticos.

    La recomendación no realiza cálculos de dimensionamiento ni económicos.
    Esos cálculos pertenecen a las capas de optimización y economía.
    """

    code: str
    title: str
    description: str
    supporting_diagnostics: tuple[str, ...]
    evidence: Mapping[str, float | str]

    def __post_init__(self) -> None:
        if not self.code:
            raise ValueError("Recommendation code cannot be empty.")

        if not self.title:
            raise ValueError("Recommendation title cannot be empty.")

        if not self.description:
            raise ValueError(
                "Recommendation description cannot be empty."
            )

        if not self.supporting_diagnostics:
            raise ValueError(
                "Recommendation must reference at least one diagnostic."
            )


class EnergyRecommendations:
    """
    Genera recomendaciones energéticas a partir de diagnósticos existentes.

    Esta capa no recalcula el balance ni realiza dimensionamiento económico.
    """

    @classmethod
    def recommend(
        cls,
        diagnostics: list[DiagnosticResult],
        battery_economic_recommendations: (
            list[BatteryEconomicRecommendation] | None
        ) = None,
    ) -> list[RecommendationResult]:

        if not diagnostics:
            return []

        by_code = {
            diagnostic.code: diagnostic
            for diagnostic in diagnostics
        }

        recommendations: list[RecommendationResult] = []

        surplus = by_code.get("HIGH_SOLAR_SURPLUS")
        mismatch = by_code.get("HIGH_HOURLY_MISMATCH")

        battery_economic = (
            battery_economic_recommendations[0]
            if battery_economic_recommendations
            else None
        )

        if surplus is not None and mismatch is not None:
            description = (
                "Existe un excedente fotovoltaico significativo "
                "y, simultáneamente, un desacoplamiento horario "
                "entre producción y demanda. Esta situación "
                "justifica evaluar una solución de almacenamiento "
                "para desplazar parte de la energía solar "
                "excedentaria hacia periodos de demanda."
            )

            evidence: dict[str, float | str] = {
                "export_ratio_percent": float(
                    surplus.evidence["export_ratio_percent"]
                ),
                "excess_energy_kwh": float(
                    mismatch.evidence["excess_energy_kwh"]
                ),
                "deficit_energy_kwh": float(
                    mismatch.evidence["deficit_energy_kwh"]
                ),
            }

            if battery_economic is not None:
                description = (
                    f"{description} "
                    f"{battery_economic.description}"
                )

                evidence.update(
                    {
                        "battery_capacity_kwh": (
                            battery_economic.capacity_kwh
                        ),
                        "battery_economic_criterion": (
                            battery_economic.criterion
                        ),
                        "battery_economic_npv_eur": float(
                            battery_economic.evidence[
                                "economic_npv_eur"
                            ]
                        ),
                        "battery_economic_irr_percent": float(
                            battery_economic.evidence[
                                "economic_irr_percent"
                            ]
                        ),
                        "battery_economic_payback_years": float(
                            battery_economic.evidence[
                                "economic_payback_years"
                            ]
                        ),
                    }
                )

            recommendations.append(
                RecommendationResult(
                    code="CONSIDER_ENERGY_STORAGE",
                    title="Valorar almacenamiento energético",
                    description=description,
                    supporting_diagnostics=(
                        "HIGH_SOLAR_SURPLUS",
                        "HIGH_HOURLY_MISMATCH",
                    ),
                    evidence=evidence,
                )
            )

        elif surplus is not None:
            recommendations.append(
                RecommendationResult(
                    code="CONSIDER_SELF_CONSUMPTION_IMPROVEMENT",
                    title="Mejorar el aprovechamiento de la producción solar",
                    description=(
                        "Una proporción elevada de la producción "
                        "fotovoltaica se vierte a la red. Conviene evaluar "
                        "medidas que permitan aumentar el aprovechamiento "
                        "directo de la energía generada."
                    ),
                    supporting_diagnostics=(
                        "HIGH_SOLAR_SURPLUS",
                    ),
                    evidence={
                        "export_ratio_percent": float(
                            surplus.evidence["export_ratio_percent"]
                        ),
                        "grid_export_kwh": float(
                            surplus.evidence["grid_export_kwh"]
                        ),
                    },
                )
            )

        grid_dependence = by_code.get("HIGH_GRID_DEPENDENCE")

        if grid_dependence is not None:
            recommendations.append(
                RecommendationResult(
                    code="REVIEW_GRID_DEPENDENCE",
                    title="Revisar la dependencia de la red",
                    description=(
                        "Una proporción elevada de la demanda continúa "
                        "siendo cubierta mediante energía importada de "
                        "la red. Conviene evaluar medidas adicionales "
                        "de gestión de la demanda, almacenamiento o "
                        "adaptación de los consumos."
                    ),
                    supporting_diagnostics=(
                        "HIGH_GRID_DEPENDENCE",
                    ),
                    evidence={
                        "grid_import_ratio_percent": float(
                            grid_dependence.evidence[
                                "grid_import_ratio_percent"
                            ]
                        ),
                        "grid_import_kwh": float(
                            grid_dependence.evidence[
                                "grid_import_kwh"
                            ]
                        ),
                    },
                )
            )

        return recommendations