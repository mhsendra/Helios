from helios.solar.parser import PVGISParser
from helios.solar.pvgis import PVGISClient


class PVGISProductionService:
    """
    Servicio que proporciona los componentes de adquisición
    y análisis de respuestas de PVGIS.

    La obtención y normalización de perfiles horarios
    corresponde a PVGISProductionProfileService.
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