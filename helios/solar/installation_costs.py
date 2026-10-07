from dataclasses import dataclass

from helios.solar.battery_economic_model import (
    CombinedEconomicConfiguration,
)


@dataclass(frozen=True)
class InstallationCostConfiguration:
    """
    Configuración de costes unitarios de una instalación FV.

    Esta clase no conoce ninguna instalación concreta ni ningún
    número de paneles de referencia.

    Los costes adicionales se incorporarán posteriormente a medida
    que el modelo geométrico proporcione la información necesaria
    para calcularlos.
    """

    panel_unit_cost_eur: float

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

    def calculate_panel_cost(
        self,
        panel_count: int,
    ) -> float:
        """
        Calcula el coste de los paneles de un candidato.

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

    def calculate_installation_cost(
        self,
        panel_count: int,
    ) -> float:
        """
        Calcula el coste actualmente modelado de la instalación.

        En esta fase el único componente disponible es el coste
        de los paneles.

        Los demás componentes se añadirán posteriormente sin
        modificar la responsabilidad del candidato físico.
        """

        return self.calculate_panel_cost(
            panel_count
        )

    def build_economic_configuration(
        self,
        panel_count: int,
    ) -> CombinedEconomicConfiguration:
        """
        Construye la configuración económica base para un candidato.

        La batería se mantiene fuera de esta configuración porque
        su coste es añadido posteriormente por BatteryOptimizer.
        """

        return CombinedEconomicConfiguration(
            installation_cost_eur=(
                self.calculate_installation_cost(
                    panel_count
                )
            ),
            battery_cost_eur=0.0,
            annual_pv_savings_eur=0.0,
            annual_battery_additional_savings_eur=0.0,
        )