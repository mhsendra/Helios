import json

from helios.solar.cache import PVGISCache
from helios.solar.configuration import SolarConfiguration


class TestPVGISCache:

    def setup_method(self):

        self.configuration = SolarConfiguration(
            installed_power_kwp=8.1,
            latitude=41.4,
            longitude=2.1,
            tilt=30,
            azimuth=0,
            losses=14,
        )

    def test_build_filename(self, tmp_path):

        result = PVGISCache.build_filename(
            tmp_path,
            self.configuration
        )

        assert result == (
            tmp_path
            / "pvgis_41.40000_2.10000_8.10_30_0_14.0.json"
        )

    def test_save(self, tmp_path):

        cache_file = tmp_path / "test.json"

        data = {
            "outputs": {
                "hourly": [
                    {
                        "time": "20250101:1000",
                        "P": 1500,
                    }
                ]
            }
        }

        PVGISCache.save(
            cache_file,
            data
        )

        assert cache_file.exists()

        with open(
            cache_file,
            "r",
            encoding="utf-8"
        ) as file:

            saved_data = json.load(file)

        assert saved_data == data

    def test_load(self, tmp_path):

        cache_file = tmp_path / "test.json"

        data = {
            "outputs": {
                "hourly": [
                    {
                        "time": "20250101:1000",
                        "P": 1500,
                    }
                ]
            }
        }

        with open(
            cache_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file
            )

        result = PVGISCache.load(
            cache_file
        )

        assert result == data