import requests
import pytest
from unittest.mock import MagicMock, patch

from helios.solar.pvgis import PVGISClient
from helios.solar.configuration import SolarConfiguration


class TestPVGISClient:

    def setup_method(self):

        self.configuration = SolarConfiguration(
            latitude=41.4,
            longitude=2.1,
            tilt=30,
            azimuth=0,
            reference_year=2025,
            losses=14,
            pv_technology="crystSi",
            mounting_place="building",
        )

    def test_fetch_requests_pvgis_with_correct_parameters(self):

        client = PVGISClient()

        response = MagicMock()

        response.url = "https://example.com"
        response.status_code = 200
        response.json.return_value = {
            "outputs": {
                "hourly": []
            }
        }

        with patch(
            "helios.solar.pvgis.PVGISCache.build_filename"
        ) as build_filename, patch(
            "helios.solar.pvgis.requests.get",
            return_value=response
        ) as get:

            cache_file = MagicMock()
            cache_file.exists.return_value = False

            build_filename.return_value = cache_file

            client.fetch(
                self.configuration
            )

            get.assert_called_once()

            _, kwargs = get.call_args

            assert kwargs["params"] == {
                "lat": 41.4,
                "lon": 2.1,
                "pvcalculation": 1,
                "peakpower": 1.0,
                "loss": 14,
                "angle": 30,
                "aspect": 0,
                "startyear": 2025,
                "endyear": 2025,
                "pvtechchoice": "crystSi",
                "mountingplace": "building",
                "outputformat": "json",
            }

            assert kwargs["timeout"] == 60

    def test_fetch_returns_pvgis_response(self):

        client = PVGISClient()

        expected = {
            "outputs": {
                "hourly": [
                    {
                        "time": "20250101:1000",
                        "P": 1500,
                    }
                ]
            }
        }

        response = MagicMock()

        response.url = "https://example.com"
        response.status_code = 200
        response.json.return_value = expected

        with patch(
            "helios.solar.pvgis.PVGISCache.build_filename"
        ) as build_filename, patch(
            "helios.solar.pvgis.requests.get",
            return_value=response
        ):

            cache_file = MagicMock()
            cache_file.exists.return_value = False

            build_filename.return_value = cache_file

            result = client.fetch(
                self.configuration
            )

            assert result == expected

    def test_fetch_saves_response_to_cache(self):

        client = PVGISClient()

        expected = {
            "outputs": {
                "hourly": []
            }
        }

        response = MagicMock()

        response.url = "https://example.com"
        response.status_code = 200
        response.json.return_value = expected

        with patch(
            "helios.solar.pvgis.PVGISCache.build_filename"
        ) as build_filename, patch(
            "helios.solar.pvgis.requests.get",
            return_value=response
        ), patch(
            "helios.solar.pvgis.PVGISCache.save"
        ) as save:

            cache_file = MagicMock()
            cache_file.exists.return_value = False

            build_filename.return_value = cache_file

            client.fetch(
                self.configuration
            )

            save.assert_called_once_with(
                cache_file,
                expected
            )

    def test_fetch_uses_cache_without_request(self):

        client = PVGISClient()

        cached_data = {
            "outputs": {
                "hourly": []
            }
        }

        with patch(
            "helios.solar.pvgis.PVGISCache.build_filename"
        ) as build_filename, patch(
            "helios.solar.pvgis.PVGISCache.load",
            return_value=cached_data
        ) as load, patch(
            "helios.solar.pvgis.requests.get"
        ) as get:

            cache_file = MagicMock()
            cache_file.exists.return_value = True

            build_filename.return_value = cache_file

            result = client.fetch(
                self.configuration
            )

            assert result == cached_data

            load.assert_called_once_with(
                cache_file
            )

            get.assert_not_called()

    def test_fetch_raises_on_http_error(self):

        client = PVGISClient()

        response = MagicMock()

        response.url = "https://example.com"
        response.status_code = 500

        error = requests.HTTPError("PVGIS error")
        response.raise_for_status.side_effect = error

        with patch(
            "helios.solar.pvgis.PVGISCache.build_filename"
        ) as build_filename, patch(
            "helios.solar.pvgis.requests.get",
            return_value=response,
        ) as get, patch(
            "helios.solar.pvgis.PVGISCache.save"
        ) as save:

            cache_file = MagicMock()
            cache_file.exists.return_value = False

            build_filename.return_value = cache_file

            with pytest.raises(
                requests.HTTPError,
                match="PVGIS error",
            ):
                client.fetch(self.configuration)

            get.assert_called_once()
            response.raise_for_status.assert_called_once_with()
            save.assert_not_called()