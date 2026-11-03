from unittest.mock import MagicMock

from helios.solar.PVGIS_production import (
    PVGISProductionService,
)


class TestPVGISProductionService:

    def test_constructor_creates_default_dependencies(self):
        service = PVGISProductionService()

        assert service.client is not None
        assert service.parser is not None

    def test_constructor_accepts_custom_dependencies(self):
        client = MagicMock()
        parser = MagicMock()

        service = PVGISProductionService(
            client=client,
            parser=parser,
        )

        assert service.client is client
        assert service.parser is parser