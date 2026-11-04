
import requests

from helios.solar.configuration import SolarConfiguration
from helios.solar.cache import PVGISCache
from helios.utils.paths import user_data_path


class PVGISClient:

    def __init__(self):
        self.cache_directory = user_data_path("cache/solar")

    def fetch(
        self,
        configuration: SolarConfiguration
    ):

        cache_file = PVGISCache.build_filename(
            self.cache_directory,
            configuration
        )

        # ==========================================
        # CACHE
        # ==========================================

        if cache_file.exists():

            return PVGISCache.load(
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

            "peakpower": 1.0,

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

        response.raise_for_status()

        data = response.json()

        PVGISCache.save(
            cache_file,
            data
        )

        return data
