from dataclasses import dataclass
from pathlib import Path
import json
import requests

import pandas as pd


@dataclass
class SolarConfiguration:

    installed_power_kwp: float

    latitude: float

    longitude: float

    tilt: int

    azimuth: int

    reference_year: int = 2023

    losses: float = 14

    pv_technology: str = "crystSi"

    mounting_place: str = "building"


class SolarEngine:

    def __init__(self):

        self.hourly_production = None
        self.statistics = {}
        self.monthly_production = None
        self.hourly_profile = None

        self.cache_directory = (
            Path("data")
            / "cache"
            / "solar"
        )

        self.cache_directory.mkdir(
            parents=True,
            exist_ok=True
        )

    def calculate_hourly_production(
        self,
        configuration: SolarConfiguration
    ) -> pd.DataFrame:
        
        self.configuration = configuration

        cache_file = self._build_cache_filename(
            configuration
        )

        if cache_file.exists():

            response = self._load_cache(
                cache_file
            )

        else:

            response = self._fetch_pvgis(
                configuration
            )

            self._save_cache(
                cache_file,
                response
            )

        dataframe = self._parse_pvgis_response(
            response
        )

        self.hourly_production = dataframe

        return self.hourly_production

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

    def _fetch_pvgis(
        self,
        configuration: SolarConfiguration
    ):

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

        print("======================================")
        print("PVGIS REQUEST")
        print("======================================")
        print(response.url)
        print()
        print("Status:", response.status_code)

        response.raise_for_status()

        return response.json()

    def _parse_pvgis_response(self, response):

        hourly = response["outputs"]["hourly"]

        dataframe = pd.DataFrame(hourly)

        dataframe["datetime"] = pd.to_datetime(
            dataframe["time"],
            format="%Y%m%d:%H%M"
        )

        dataframe = dataframe.set_index("datetime")

        dataframe.index = dataframe.index.floor("h")

        dataframe = dataframe.rename(
            columns={
                "P": "production_w",
                "G(i)": "irradiance",
                "T2m": "temperature",
                "WS10m": "wind_speed",
                "Int": "interpolated"
            }
        )

        dataframe["production_kw"] = (
            dataframe["production_w"] / 1000
        )

        return dataframe[
            [
                "production_kw",
                "irradiance",
                "temperature",
                "wind_speed",
                "interpolated"
            ]
        ]
    def calculate_statistics(self):

        if self.hourly_production is None:

            raise ValueError(
                "Hourly production has not been calculated."
            )

        production = self.hourly_production["production_kw"]

        annual_production = production.sum()

        installed_power = self.configuration.installed_power_kwp

        equivalent_hours = (
            annual_production /
            installed_power
        )

        capacity_factor = (
            annual_production /
            (installed_power * len(production))
        ) * 100

        self.statistics = {

            "hours": len(production),

            "annual_production": annual_production,

            "daily_average": annual_production / 365,

            "maximum_power": production.max(),

            "minimum_power": production[production > 0].min(),

            "equivalent_hours": equivalent_hours,

            "capacity_factor": capacity_factor

        }