from helios.solar.parser import PVGISParser
from helios.solar.pvgis import PVGISClient
from helios.solar.configuration import SolarConfiguration


class PVGISProductionService:
    """
    Servicio de alto nivel para obtener producción
    fotovoltaica a partir de PVGIS.

    Encapsula:
        PVGISClient
            ↓
        PVGISParser
            ↓
        producción anual
            ↓
        producción específica
    """

    def __init__(
        self,
        client: PVGISClient | None = None,
        parser: PVGISParser | None = None,
    ):

        self.client = (
            client
            if client is not None
            else PVGISClient()
        )

        self.parser = (
            parser
            if parser is not None
            else PVGISParser()
        )

    def get_annual_production(
        self,
        configuration: SolarConfiguration,
    ) -> float:
        """
        Obtiene la producción anual estimada por PVGIS
        para la potencia indicada en la configuración.
        """

        if not isinstance(
            configuration,
            SolarConfiguration,
        ):
            raise TypeError(
                "configuration must be a SolarConfiguration."
            )

        if configuration.installed_power_kwp <= 0:
            raise ValueError(
                "installed_power_kwp must be greater than zero."
            )

        response = self.client.fetch(
            configuration
        )

        dataframe = self.parser.parse(
            response
        )

        if dataframe.empty:
            raise ValueError(
                "PVGIS returned no production data."
            )

        production = float(
            dataframe["production_kwh"].sum()
        )

        if production < 0:
            raise ValueError(
                "PVGIS annual production cannot be negative."
            )

        return production

    def get_specific_production(
        self,
        configuration: SolarConfiguration,
    ) -> float:
        """
        Devuelve la producción específica:

            kWh / kWp / año
        """

        annual_production = (
            self.get_annual_production(
                configuration
            )
        )

        return (
            annual_production
            / configuration.installed_power_kwp
        )