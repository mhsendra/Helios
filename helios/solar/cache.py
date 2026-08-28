from pathlib import Path
import json

from helios.solar.configuration import SolarConfiguration


class PVGISCache:

    @staticmethod
    def build_filename(
        cache_directory: Path,
        configuration: SolarConfiguration,
    ) -> Path:

        filename = (
            "pvgis_"
            f"{configuration.latitude:.5f}_"
            f"{configuration.longitude:.5f}_"
            f"{configuration.tilt}_"
            f"{configuration.azimuth}_"
            f"{configuration.losses:.1f}_"
            f"{configuration.reference_year}_"
            f"{configuration.pv_technology}_"
            f"{configuration.mounting_place}.json"
        )

        filename = filename.replace("-", "m")

        return cache_directory / filename

    @staticmethod
    def load(cache_file: Path):

        with open(
            cache_file,
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    @staticmethod
    def save(
        cache_file: Path,
        data,
    ):

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