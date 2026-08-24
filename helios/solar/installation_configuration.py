from dataclasses import dataclass

from helios.solar.installation_constraints import (
    InstallationConstraints,
)


@dataclass(frozen=True)
class InstallationConfiguration:
    """
    Configuración física de la instalación fotovoltaica
    utilizada por el proceso de optimización.

    Esta clase representa las condiciones de partida
    proporcionadas por el usuario o por la aplicación.

    No realiza optimización ni simulación de producción.
    """

    available_area_m2: float

    panel_width_m: float
    panel_height_m: float
    panel_power_wp: float

    min_panels: int = 1
    max_panels: int | None = None

    # ==================================================
    # Panel orientation
    # ==================================================

    panel_orientation: str = "auto"

    # ==================================================
    # Maintenance passage
    # ==================================================

    maintenance_passage_required: bool = False

    maintenance_passage_width_m: float = 0.45

    maintenance_passage_orientation: str = "auto"

    # ==================================================
    # Roof geometry
    # ==================================================

    roof_width_m: float | None = None
    roof_height_m: float | None = None

    # ==================================================
    # Conversion
    # ==================================================

    def to_constraints(self) -> InstallationConstraints:
        """
        Convierte la configuración de instalación en
        restricciones operativas para el optimizador.
        """

        return InstallationConstraints(
            available_area_m2=self.available_area_m2,

            panel_width_m=self.panel_width_m,
            panel_height_m=self.panel_height_m,
            panel_power_wp=self.panel_power_wp,

            panel_orientation=self.panel_orientation,

            min_panels=self.min_panels,
            max_panels=self.max_panels,

            maintenance_passage_required=(
                self.maintenance_passage_required
            ),

            maintenance_passage_width_m=(
                self.maintenance_passage_width_m
            ),

            maintenance_passage_orientation=(
                self.maintenance_passage_orientation
            ),

            roof_width_m=self.roof_width_m,
            roof_height_m=self.roof_height_m,
        )