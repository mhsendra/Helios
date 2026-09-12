from helios.solar.installation_candidate import InstallationCandidate
from helios.solar.production_profile import (
    SolarProductionProfile,
    scale_solar_production_profile,
)


def calculate_candidate_solar_production(
    candidate: InstallationCandidate,
    base_profile: SolarProductionProfile,
) -> SolarProductionProfile:
    """Calcula el perfil horario de producción de una instalación candidata."""

    if not isinstance(candidate, InstallationCandidate):
        raise TypeError(
            "candidate must be an InstallationCandidate."
        )

    if not isinstance(base_profile, SolarProductionProfile):
        raise TypeError(
            "base_profile must be a SolarProductionProfile."
        )

    return scale_solar_production_profile(
        base_profile,
        installed_power_kwp=candidate.installed_power_kwp,
    )