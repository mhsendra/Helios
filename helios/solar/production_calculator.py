from helios.solar.installation_candidate import InstallationCandidate
from helios.solar.production_profile import (
    SolarProductionProfile,
    scale_solar_production_profile,
)


class SolarProductionCalculator:
    """Calcula la producción solar de una instalación candidata."""

    def __init__(
        self,
        base_profile: SolarProductionProfile,
    ) -> None:
        if not isinstance(base_profile, SolarProductionProfile):
            raise TypeError(
                "base_profile must be a SolarProductionProfile."
            )

        self.base_profile = base_profile

    def calculate(
        self,
        candidate: InstallationCandidate,
    ) -> SolarProductionProfile:
        """Escala el perfil base a la potencia de la instalación candidata."""

        if not isinstance(candidate, InstallationCandidate):
            raise TypeError(
                "candidate must be an InstallationCandidate."
            )

        installed_power_kwp = (
            candidate.panel_count
            * candidate.panel_power_wp
            / 1000
        )

        return scale_solar_production_profile(
            self.base_profile,
            installed_power_kwp,
        )