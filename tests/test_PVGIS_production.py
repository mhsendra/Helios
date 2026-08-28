import pytest
import pandas as pd

from unittest.mock import MagicMock

from helios.solar.configuration import SolarConfiguration
from helios.solar.PVGIS_production import (
    PVGISProductionService,
)


class TestPVGISProductionService:

    # ==================================================
    # Helpers
    # ==================================================

    @staticmethod
    def configuration():
        return SolarConfiguration(
            latitude=41.6167,
            longitude=2.0833,
            tilt=30,
            azimuth=0,
        )

    @staticmethod
    def response():
        return {
            "outputs": {
                "hourly": []
            }
        }

    @staticmethod
    def dataframe():
        return pd.DataFrame(
            {
                "production_kwh": [
                    1.0,
                    2.0,
                    3.0,
                    4.0,
                ]
            }
        )

    @staticmethod
    def service(
        client=None,
        parser=None,
    ):
        return PVGISProductionService(
            client=client,
            parser=parser,
        )

    # ==================================================
    # Constructor
    # ==================================================

    def test_constructor_creates_default_dependencies(self):

        service = PVGISProductionService()

        assert service.client is not None
        assert service.parser is not None

    def test_constructor_accepts_custom_dependencies(self):

        client = MagicMock()
        parser = MagicMock()

        service = self.service(
            client=client,
            parser=parser,
        )

        assert service.client is client
        assert service.parser is parser

    # ==================================================
    # Configuration validation
    # ==================================================

    @pytest.mark.parametrize(
        "configuration",
        [
            None,
            object(),
            "configuration",
            123,
        ],
    )
    def test_get_specific_production_rejects_invalid_configuration(
        self,
        configuration,
    ):

        service = self.service(
            client=MagicMock(),
            parser=MagicMock(),
        )

        with pytest.raises(
            TypeError,
            match="configuration must be a SolarConfiguration.",
        ):
            service.get_specific_production(
                configuration
            )

    # ==================================================
    # Specific production
    # ==================================================

    def test_get_specific_production_returns_sum_of_production(
        self,
    ):

        client = MagicMock()
        parser = MagicMock()

        client.fetch.return_value = self.response()
        parser.parse.return_value = self.dataframe()

        service = self.service(
            client=client,
            parser=parser,
        )

        configuration = self.configuration()

        result = service.get_specific_production(
            configuration
        )

        assert result == pytest.approx(10.0)
        assert isinstance(result, float)

        client.fetch.assert_called_once_with(
            configuration
        )

        parser.parse.assert_called_once_with(
            client.fetch.return_value
        )

    def test_get_specific_production_accepts_integer_values(
        self,
    ):

        client = MagicMock()
        parser = MagicMock()

        client.fetch.return_value = self.response()

        parser.parse.return_value = pd.DataFrame(
            {
                "production_kwh": [
                    100,
                    200,
                    300,
                ]
            }
        )

        service = self.service(
            client=client,
            parser=parser,
        )

        result = service.get_specific_production(
            self.configuration()
        )

        assert result == 600.0
        assert isinstance(result, float)

    def test_get_specific_production_rejects_empty_dataframe(
        self,
    ):

        client = MagicMock()
        parser = MagicMock()

        client.fetch.return_value = self.response()
        parser.parse.return_value = pd.DataFrame()

        service = self.service(
            client=client,
            parser=parser,
        )

        with pytest.raises(
            ValueError,
            match="PVGIS returned no production data.",
        ):
            service.get_specific_production(
                self.configuration()
            )

    def test_get_specific_production_rejects_negative_production(
        self,
    ):

        client = MagicMock()
        parser = MagicMock()

        client.fetch.return_value = self.response()

        parser.parse.return_value = pd.DataFrame(
            {
                "production_kwh": [
                    100.0,
                    -101.0,
                ]
            }
        )

        service = self.service(
            client=client,
            parser=parser,
        )

        with pytest.raises(
            ValueError,
            match="PVGIS specific production cannot be negative.",
        ):
            service.get_specific_production(
                self.configuration()
            )

    # ==================================================
    # Dependency propagation
    # ==================================================

    def test_client_exception_is_propagated(self):

        client = MagicMock()
        parser = MagicMock()

        client.fetch.side_effect = RuntimeError(
            "PVGIS unavailable"
        )

        service = self.service(
            client=client,
            parser=parser,
        )

        with pytest.raises(
            RuntimeError,
            match="PVGIS unavailable",
        ):
            service.get_specific_production(
                self.configuration()
            )

        parser.parse.assert_not_called()

    def test_parser_exception_is_propagated(self):

        client = MagicMock()
        parser = MagicMock()

        client.fetch.return_value = self.response()

        parser.parse.side_effect = RuntimeError(
            "Invalid PVGIS response"
        )

        service = self.service(
            client=client,
            parser=parser,
        )

        with pytest.raises(
            RuntimeError,
            match="Invalid PVGIS response",
        ):
            service.get_specific_production(
                self.configuration()
            )

    # ==================================================
    # End-to-end service flow
    # ==================================================

    def test_service_executes_client_parser_and_calculation_in_order(
        self,
    ):

        calls = []

        client = MagicMock()
        parser = MagicMock()

        def fetch(configuration):

            calls.append("fetch")

            return self.response()

        def parse(response):

            calls.append("parse")

            return self.dataframe()

        client.fetch.side_effect = fetch
        parser.parse.side_effect = parse

        service = self.service(
            client=client,
            parser=parser,
        )

        result = service.get_specific_production(
            self.configuration()
        )

        assert calls == [
            "fetch",
            "parse",
        ]

        assert result == pytest.approx(10.0)

    # ==================================================
    # Configuration propagation
    # ==================================================

    def test_configuration_is_passed_unchanged_to_client(
        self,
    ):

        client = MagicMock()
        parser = MagicMock()

        client.fetch.return_value = self.response()
        parser.parse.return_value = self.dataframe()

        service = self.service(
            client=client,
            parser=parser,
        )

        configuration = self.configuration()

        service.get_specific_production(
            configuration
        )

        assert client.fetch.call_args.args[0] is configuration