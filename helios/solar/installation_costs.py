from dataclasses import dataclass

from helios.solar.battery_economic_model import (
    CombinedEconomicConfiguration,
)
from helios.solar.installation_evaluation import (
    InstallationEvaluation,
)

import math

@dataclass(frozen=True)
class InstallationCostConfiguration:
    """
    Configuración de costes de una instalación fotovoltaica.

    Permite definir los costes unitarios de los paneles y la
    estructura, así como los costes fijos de instalación,
    inversor, protecciones eléctricas, cableado y legalización.

    La configuración permite calcular el coste de la instalación
    a partir de una InstallationEvaluation y construir la
    configuración económica inicial para evaluar su rentabilidad.

    Los costes de instalación incluyen paneles, estructura,
    mano de obra, inversor, protecciones eléctricas y cableado.
    El coste de legalización se calcula por separado y se añade
    al construir la configuración económica.

    Esta clase no calcula el ahorro energético ni el retorno
    económico: esos cálculos corresponden a las capas de
    análisis económico.
    """

    panel_unit_cost_eur: float

    structure_unit_cost_eur: float = 0.0

    installation_cost_eur: float = 0.0

    inverter_unit_cost_eur: float = 0.0

    electrical_protection_cost_eur: float = 0.0

    cabling_cost_eur: float = 0.0

    legalization_cost_eur: float = 0.0

    def __post_init__(self) -> None:
        fields = (
            ("panel_unit_cost_eur", self.panel_unit_cost_eur),
            ("structure_unit_cost_eur", self.structure_unit_cost_eur),
            ("installation_cost_eur", self.installation_cost_eur),
            ("inverter_unit_cost_eur", self.inverter_unit_cost_eur),
            (
                "electrical_protection_cost_eur",
                self.electrical_protection_cost_eur,
            ),
            ("cabling_cost_eur", self.cabling_cost_eur),
            ("legalization_cost_eur", self.legalization_cost_eur),
        )

        for name, value in fields:
            if isinstance(value, bool) or not isinstance(
                value,
                (int, float),
            ):
                raise TypeError(
                    f"{name} must be numeric."
                )

            if not math.isfinite(value):
                raise ValueError(
                    f"{name} must be finite."
                )

            if value < 0:
                raise ValueError(
                    f"{name} cannot be negative."
                )

    def calculate_panel_cost(
        self,
        panel_count: int,
    ) -> float:
        """
        Calcula el coste de los paneles.

        El coste depende exclusivamente del número de paneles
        y del precio unitario configurado.
        """

        if isinstance(panel_count, bool):
            raise TypeError(
                "panel_count must be an integer."
            )

        if not isinstance(panel_count, int):
            raise TypeError(
                "panel_count must be an integer."
            )

        if panel_count <= 0:
            raise ValueError(
                "panel_count must be greater than zero."
            )

        return float(
            panel_count * self.panel_unit_cost_eur
        )

    def calculate_structure_cost(
        self,
        evaluation: InstallationEvaluation,
    ) -> float:
        """
        Calcula el coste de la estructura y los soportes.

        El importe se obtiene multiplicando el número de paneles
        de la evaluación por el coste unitario de estructura.

        No incluye paneles, mano de obra, inversor, protecciones,
        cableado ni legalización.
        """

        if not isinstance(
            evaluation,
            InstallationEvaluation,
        ):
            raise TypeError(
                "evaluation must be an InstallationEvaluation."
            )

        return float(
            evaluation.panel_count
            * self.structure_unit_cost_eur
        )

    def calculate_installation_service_cost(
        self,
        evaluation: InstallationEvaluation,
    ) -> float:
        if not isinstance(
            evaluation,
            InstallationEvaluation,
        ):
            raise TypeError(
                "evaluation must be an InstallationEvaluation."
            )

        return float(
            self.installation_cost_eur
        )

    def calculate_inverter_cost(
        self,
        evaluation: InstallationEvaluation,
    ) -> float:
        if not isinstance(
            evaluation,
            InstallationEvaluation,
        ):
            raise TypeError(
                "evaluation must be an InstallationEvaluation."
            )

        return float(
            self.inverter_unit_cost_eur
        )

    def calculate_electrical_protection_cost(
        self,
        evaluation: InstallationEvaluation,
    ) -> float:
        if not isinstance(
            evaluation,
            InstallationEvaluation,
        ):
            raise TypeError(
                "evaluation must be an InstallationEvaluation."
            )

        return float(
            self.electrical_protection_cost_eur
        )

    def calculate_cabling_cost(
        self,
        evaluation: InstallationEvaluation,
    ) -> float:
        if not isinstance(
            evaluation,
            InstallationEvaluation,
        ):
            raise TypeError(
                "evaluation must be an InstallationEvaluation."
            )

        return float(
            self.cabling_cost_eur
        )

    def calculate_legalization_cost(
        self,
        evaluation: InstallationEvaluation,
    ) -> float:
        if not isinstance(
            evaluation,
            InstallationEvaluation,
        ):
            raise TypeError(
                "evaluation must be an InstallationEvaluation."
            )

        return float(
            self.legalization_cost_eur
        )

    def calculate_installation_cost(
        self,
        evaluation: InstallationEvaluation,
    ) -> float:
        """
        Calcula el coste total modelado de la instalación.

        Incluye:
        - paneles;
        - estructura y soportes;
        - mano de obra e instalación;
        - inversor;
        - protecciones eléctricas;
        - cableado.

        Excluye la legalización, que se calcula por separado
        mediante calculate_legalization_cost() y se añade al
        construir la configuración económica.

        Los importes dependen de InstallationCostConfiguration.
        """

        return (
            self.calculate_panel_cost(
                evaluation.panel_count
            )
            + self.calculate_structure_cost(
                evaluation
            )
            + self.calculate_installation_service_cost(
                evaluation
            )
            + self.calculate_inverter_cost(
                evaluation
            )
            + self.calculate_electrical_protection_cost(
                evaluation
            )
            + self.calculate_cabling_cost(
                evaluation
            )
        )

    def build_economic_configuration(
        self,
        evaluation: InstallationEvaluation,
    ) -> CombinedEconomicConfiguration:
        """
        Construye la configuración económica base para un candidato.

        El coste de batería se mantiene fuera de esta configuración
        porque BatteryOptimizer lo añade posteriormente.
        """

        if not isinstance(
            evaluation,
            InstallationEvaluation,
        ):
            raise TypeError(
                "evaluation must be an InstallationEvaluation."
            )

        return CombinedEconomicConfiguration(
            installation_cost_eur=(
                self.calculate_installation_cost(
                    evaluation
                )
                + self.calculate_legalization_cost(
                    evaluation
                )
            ),
            battery_cost_eur=0.0,
            annual_pv_savings_eur=0.0,
            annual_battery_additional_savings_eur=0.0,
        )