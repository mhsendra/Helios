# helios/solar/production_profile.py

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class SolarProductionProfile:
    """Perfil horario anual de producción fotovoltaica."""

    hourly_production: pd.Series
    reference_year: int
    installed_power_kwp: float

    def __post_init__(self):
        if not isinstance(self.hourly_production, pd.Series):
            raise TypeError(
                "hourly_production must be a pandas Series."
            )

        if not isinstance(
            self.hourly_production.index,
            pd.DatetimeIndex,
        ):
            raise TypeError(
                "hourly_production index must be a DatetimeIndex."
            )

        if len(self.hourly_production) != 8760:
            raise ValueError(
                "Solar production profile must contain exactly "
                "8760 hourly values."
            )

        if self.hourly_production.isna().any():
            raise ValueError(
                "Solar production profile cannot contain NaN values."
            )

        if not pd.api.types.is_numeric_dtype(
            self.hourly_production
        ):
            raise TypeError(
                "hourly_production must contain numeric values."
            )

        if (self.hourly_production < 0).any():
            raise ValueError(
                "Solar production profile cannot contain negative values."
            )

        expected_index = pd.date_range(
            start=f"{self.reference_year}-01-01 00:00:00",
            periods=8760,
            freq="h",
        )

        if not self.hourly_production.index.equals(expected_index):
            raise ValueError(
                "Solar production profile index must contain a complete "
                "8760-hour reference year."
            )

        if self.installed_power_kwp <= 0:
            raise ValueError(
                "Installed power must be greater than zero."
            )

    @property
    def annual_production(self) -> float:
        """Producción anual total en kWh."""
        return float(self.hourly_production.sum())


def scale_solar_production_profile(
    profile: SolarProductionProfile,
    installed_power_kwp: float,
) -> SolarProductionProfile:
    """Escala un perfil fotovoltaico a una potencia instalada."""

    if not isinstance(profile, SolarProductionProfile):
        raise TypeError(
            "profile must be a SolarProductionProfile."
        )

    if installed_power_kwp <= 0:
        raise ValueError(
            "Installed power must be greater than zero."
        )

    scaled_production = (
        profile.hourly_production
        * installed_power_kwp
        / profile.installed_power_kwp
    )

    return SolarProductionProfile(
        hourly_production=scaled_production,
        reference_year=profile.reference_year,
        installed_power_kwp=installed_power_kwp,
    )