from helios.solar.parser import PVGISParser
from helios.solar.pvgis import PVGISClient
from helios.solar.configuration import SolarConfiguration


class PVGISProductionService:
    """
    Servicio de alto nivel para obtener producción
    fotovoltaica específica a partir de PVGIS.

    PVGIS se consulta con una potencia de referencia
    de 1 kWp, por lo que la producción obtenida
    representa directamente:

        kWh / kWp / año
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

    def get_specific_production(
        self,
        configuration: SolarConfiguration,
    ) -> float:
        """
        Devuelve la producción específica estimada por PVGIS:

            kWh / kWp / año

        La consulta a PVGIS utiliza una potencia de
        referencia de 1 kWp.
        """

        if not isinstance(
            configuration,
            SolarConfiguration,
        ):
            raise TypeError(
                "configuration must be a SolarConfiguration."
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

        specific_production = float(
            dataframe["production_kwh"].sum()
        )

        if specific_production < 0:
            raise ValueError(
                "PVGIS specific production cannot be negative."
            )

        return specific_production