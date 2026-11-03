
import pandas as pd

from helios.solar.PVGIS_production import PVGISProductionService
from helios.solar.configuration import SolarConfiguration
from helios.solar.production_profile import SolarProductionProfile


class PVGISProductionProfileService:
    """Construye un perfil solar horario de 8760 horas a partir de PVGIS."""

    def __init__(
        self,
        production_service: PVGISProductionService | None = None,
    ) -> None:
        self.production_service = (
            production_service
            if production_service is not None
            else PVGISProductionService()
        )

        # DataFrame completo de PVGIS, conservado para reutilizar
        # las columnas meteorológicas junto con la producción.
        self.hourly_dataframe: pd.DataFrame | None = None

    def get_production_profile(
        self,
        configuration: SolarConfiguration,
    ) -> SolarProductionProfile:
        """Obtiene un perfil horario normalizado a 1 kWp."""

        self.hourly_dataframe = None

        if not isinstance(
            configuration,
            SolarConfiguration,
        ):
            raise TypeError(
                "configuration must be a SolarConfiguration."
            )

        response = self.production_service.client.fetch(
            configuration
        )

        hourly = response.get("outputs", {}).get("hourly", [])

        if not hourly:
            raise ValueError(
                "PVGIS returned no production data."
            )

        dataframe = self.production_service.parser.parse(
            response
        )

        if dataframe.empty:
            raise ValueError(
                "PVGIS returned no production data."
            )

        if "production_kwh" not in dataframe.columns:
            raise ValueError(
                "PVGIS response does not contain production data."
            )

        hourly_production = dataframe[
            "production_kwh"
        ].copy()

        if hourly_production.isna().any():
            raise ValueError(
                "PVGIS production profile contains NaN values."
            )

        if (hourly_production < 0).any():
            raise ValueError(
                "PVGIS production profile cannot contain negative values."
            )

        if len(hourly_production) != 8760:
            raise ValueError(
                "PVGIS production profile must contain exactly "
                "8760 hourly values."
            )

        reference_year = configuration.reference_year

        expected_index = pd.date_range(
            start=f"{reference_year}-01-01 00:00:00",
            end=f"{reference_year}-12-31 23:00:00",
            freq="h",
        )

        if pd.Timestamp(
            f"{reference_year}-12-31"
        ).is_leap_year:
            expected_index = expected_index[
                ~(
                    (expected_index.month == 2)
                    & (expected_index.day == 29)
                )
            ]

        # Normalizar el índice del DataFrame completo, no solo
        # el de la serie de producción.
        dataframe = dataframe.copy()
        dataframe.index = expected_index

        hourly_production = dataframe[
            "production_kwh"
        ].copy()

        self.hourly_dataframe = dataframe.copy()

        return SolarProductionProfile(
            hourly_production=hourly_production,
            reference_year=reference_year,
            installed_power_kwp=1.0,
        )
