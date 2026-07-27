from pathlib import Path

import requests
import json

from helios.solar.configuration import SolarConfiguration
from helios.reports.printer import ReportPrinter 


class PVGISClient:

    def __init__(self):

        self.cache_directory = (
            Path("data")
            / "cache"
            / "solar"
        )

        self.cache_directory.mkdir(
            parents=True,
            exist_ok=True
        )

    def _build_cache_filename(
        self,
        configuration: SolarConfiguration
    ) -> Path:

        filename = (
            f"pvgis_"
            f"{configuration.latitude:.5f}_"
            f"{configuration.longitude:.5f}_"
            f"{configuration.installed_power_kwp:.2f}_"
            f"{configuration.tilt}_"
            f"{configuration.azimuth}_"
            f"{configuration.losses:.1f}.json"
        )

        filename = filename.replace("-", "m")

        return self.cache_directory / filename


    def _load_cache(
        self,
        cache_file: Path
    ):

        with open(
            cache_file,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)


    def _save_cache(
        self,
        cache_file: Path,
        data
    ):

        with open(
            cache_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )
        
    def fetch(
        self,
        configuration: SolarConfiguration
    ):

        cache_file = self._build_cache_filename(
            configuration
        )

        # ==========================================
        # CACHE
        # ==========================================

        if cache_file.exists():

            ReportPrinter.title("PVGIS CACHE")

            ReportPrinter.text(
                "Archivo",
                cache_file.name
            )

            ReportPrinter.blank()

            return self._load_cache(
                cache_file
            )

        # ==========================================
        # PVGIS
        # ==========================================

        url = (
            "https://re.jrc.ec.europa.eu/api/v5_3/seriescalc"
        )

        params = {

            "lat": configuration.latitude,

            "lon": configuration.longitude,

            "pvcalculation": 1,

            "peakpower": configuration.installed_power_kwp,

            "loss": configuration.losses,

            "angle": configuration.tilt,

            "aspect": configuration.azimuth,

            "startyear": configuration.reference_year,

            "endyear": configuration.reference_year,

            "pvtechchoice": configuration.pv_technology,

            "mountingplace": configuration.mounting_place,

            "outputformat": "json"

        }

        response = requests.get(
            url,
            params=params,
            timeout=60
        )

        ReportPrinter.title("PVGIS REQUEST")

        ReportPrinter.text(
            "URL",
            response.url
        )

        ReportPrinter.text(
            "Status",
            response.status_code
        )

        ReportPrinter.blank()

        response.raise_for_status()

        data = response.json()

        self._save_cache(
            cache_file,
            data
        )

        return data