from dataclasses import dataclass

from helios.solar.battery_economic_model import (
    CombinedEconomicConfiguration,
)
from helios.solar.installation_evaluation import (
    InstallationEvaluation,
)

@dataclass(frozen=True)
class InstallationCostConfiguration:
    """
    Configuración de costes unitarios de una instalación FV.

    Los costes se calculan a partir de la evaluación física del
    candidato optimizado.

    En esta fase se modelan:

    - paneles;
    - estructura/soportes.

    Los demás componentes se incorporarán posteriormente.
    """

    panel_unit_cost_eur: float

    structure_unit_cost_eur: float = 0.0

    installation_cost_eur: float = 0.0

    inverter_unit_cost_eur: float = 0.0

    electrical_protection_cost_eur: float = 0.0

    cabling_cost_eur: float = 0.0

    legalization_cost_eur: float = 0.0

    def __post_init__(self) -> None:

        if isinstance(self.panel_unit_cost_eur, bool):
            raise TypeError(
                "panel_unit_cost_eur must be numeric."
            )

        if not isinstance(
            self.panel_unit_cost_eur,
            (int, float),
        ):
            raise TypeError(
                "panel_unit_cost_eur must be numeric."
            )

        if self.panel_unit_cost_eur < 0:
            raise ValueError(
                "panel_unit_cost_eur cannot be negative."
            )

        if isinstance(self.structure_unit_cost_eur, bool):
            raise TypeError(
                "structure_unit_cost_eur must be numeric."
            )

        if not isinstance(
            self.structure_unit_cost_eur,
            (int, float),
        ):
            raise TypeError(
                "structure_unit_cost_eur must be numeric."
            )

        if self.structure_unit_cost_eur < 0:
            raise ValueError(
                "structure_unit_cost_eur cannot be negative."
            )

        if isinstance(self.installation_cost_eur, bool):
            raise TypeError(
                "installation_cost_eur must be numeric."
            )

        if not isinstance(
            self.installation_cost_eur,
            (int, float),
        ):
            raise TypeError(
                "installation_cost_eur must be numeric."
            )

        if self.installation_cost_eur < 0:
            raise ValueError(
                "installation_cost_eur cannot be negative."
            )

        if isinstance(self.inverter_unit_cost_eur, bool):
            raise TypeError(
                "inverter_unit_cost_eur must be numeric."
            )

        if not isinstance(
            self.inverter_unit_cost_eur,
            (int, float),
        ):
            raise TypeError(
                "inverter_unit_cost_eur must be numeric."
            )

        if self.inverter_unit_cost_eur < 0:
            raise ValueError(
                "inverter_unit_cost_eur cannot be negative."
            )

        if isinstance(self.electrical_protection_cost_eur, bool):
            raise TypeError(
                "electrical_protection_cost_eur must be numeric."
            )

        if not isinstance(
            self.electrical_protection_cost_eur,
            (int, float),
        ):
            raise TypeError(
                "electrical_protection_cost_eur must be numeric."
            )

        if self.electrical_protection_cost_eur < 0:
            raise ValueError(
                "electrical_protection_cost_eur cannot be negative."
            )

        if isinstance(self.cabling_cost_eur, bool):
            raise TypeError(
                "cabling_cost_eur must be numeric."
            )

        if not isinstance(
            self.cabling_cost_eur,
            (int, float),
        ):
            raise TypeError(
                "cabling_cost_eur must be numeric."
            )

        if self.cabling_cost_eur < 0:
            raise ValueError(
                "cabling_cost_eur cannot be negative."
            )

        if isinstance(self.legalization_cost_eur, bool):
            raise TypeError(
                "legalization_cost_eur must be numeric."
            )

        if not isinstance(
            self.legalization_cost_eur,
            (int, float),
        ):
            raise TypeError(
                "legalization_cost_eur must be numeric."
            )

        if self.legalization_cost_eur < 0:
            raise ValueError(
                "legalization_cost_eur cannot be negative."
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
        Calcula el coste de estructura/soportes.

        La evaluación física completa se recibe deliberadamente
        aunque la fórmula actual utilice únicamente el número de
        paneles.

        Esto permite sustituir posteriormente el modelo unitario
        por un modelo basado en la geometría real del layout
        sin modificar la interfaz económica.
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
        Calcula el coste actualmente modelado de la instalación.

        Incluye:

        - paneles;
        - estructura/soportes.

        Los demás componentes se añadirán posteriormente.
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