from pathlib import Path
import json

from helios.solar.cache import PVGISCache
from helios.solar.configuration import SolarConfiguration


class TestPVGISCache:

    def setup_method(self):

        self.configuration = SolarConfiguration(
            latitude=41.4,
            longitude=2.1,
            tilt=30,
            azimuth=0,
            reference_year=2023,
            losses=14,
            pv_technology="crystSi",
            mounting_place="building",
        )

    # ==================================================
    # build_filename
    # ==================================================

    def test_build_filename(self, tmp_path):

        result = PVGISCache.build_filename(
            tmp_path,
            self.configuration,
        )

        assert result == (
            tmp_path
            / (
                "pvgis_"
                "41.40000_"
                "2.10000_"
                "30_"
                "0_"
                "14.0_"
                "2023_"
                "crystSi_"
                "building.json"
            )
        )

    def test_build_filename_replaces_negative_coordinates(
        self,
        tmp_path,
    ):

        configuration = SolarConfiguration(
            latitude=-33.45,
            longitude=-70.66,
            tilt=30,
            azimuth=0,
            reference_year=2023,
            losses=14,
            pv_technology="crystSi",
            mounting_place="building",
        )

        result = PVGISCache.build_filename(
            tmp_path,
            configuration,
        )

        assert result == (
            tmp_path
            / (
                "pvgis_"
                "m33.45000_"
                "m70.66000_"
                "30_"
                "0_"
                "14.0_"
                "2023_"
                "crystSi_"
                "building.json"
            )
        )

    def test_build_filename_includes_reference_year(
        self,
        tmp_path,
    ):

        configuration = SolarConfiguration(
            latitude=41.4,
            longitude=2.1,
            tilt=30,
            azimuth=0,
            reference_year=2025,
            losses=14,
            pv_technology="crystSi",
            mounting_place="building",
        )

        result = PVGISCache.build_filename(
            tmp_path,
            configuration,
        )

        assert result.name == (
            "pvgis_"
            "41.40000_"
            "2.10000_"
            "30_"
            "0_"
            "14.0_"
            "2025_"
            "crystSi_"
            "building.json"
        )

    def test_build_filename_includes_pv_technology(
        self,
        tmp_path,
    ):

        configuration = SolarConfiguration(
            latitude=41.4,
            longitude=2.1,
            tilt=30,
            azimuth=0,
            reference_year=2023,
            losses=14,
            pv_technology="CdTe",
            mounting_place="building",
        )

        result = PVGISCache.build_filename(
            tmp_path,
            configuration,
        )

        assert result.name == (
            "pvgis_"
            "41.40000_"
            "2.10000_"
            "30_"
            "0_"
            "14.0_"
            "2023_"
            "CdTe_"
            "building.json"
        )

    def test_build_filename_includes_mounting_place(
        self,
        tmp_path,
    ):

        configuration = SolarConfiguration(
            latitude=41.4,
            longitude=2.1,
            tilt=30,
            azimuth=0,
            reference_year=2023,
            losses=14,
            pv_technology="crystSi",
            mounting_place="free",
        )

        result = PVGISCache.build_filename(
            tmp_path,
            configuration,
        )

        assert result.name == (
            "pvgis_"
            "41.40000_"
            "2.10000_"
            "30_"
            "0_"
            "14.0_"
            "2023_"
            "crystSi_"
            "free.json"
        )

    # ==================================================
    # save
    # ==================================================

    def test_save(self, tmp_path):

        cache_file = tmp_path / "cache.json"

        data = {
            "outputs": {
                "hourly": [
                    {
                        "time": "20250101:0000",
                        "P": 100,
                    }
                ]
            }
        }

        PVGISCache.save(
            cache_file,
            data,
        )

        assert cache_file.exists()

        with open(
            cache_file,
            "r",
            encoding="utf-8",
        ) as file:

            stored_data = json.load(file)

        assert stored_data == data

    # ==================================================
    # load
    # ==================================================

    def test_load(self, tmp_path):

        cache_file = tmp_path / "cache.json"

        data = {
            "outputs": {
                "hourly": [
                    {
                        "time": "20250101:0000",
                        "P": 100,
                    }
                ]
            }
        }

        with open(
            cache_file,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

        result = PVGISCache.load(
            cache_file
        )

        assert result == data