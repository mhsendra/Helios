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
        self.solar_statistics = {}
        self.hourly_profile = None
        self.energy_balance: pd.DataFrame | None = None
        self.daily_production: pd.Series | None = None
        self.monthly_production: pd.Series | None = None
        self.yearly_production: pd.Series | None = None
        self.energy_statistics = None

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
    
    def calculate_daily_production(self):

        """
        Calcula la producción diaria a partir de la producción horaria.
        """

        if self.hourly_production is None:

            raise RuntimeError(
                "Hourly production has not been calculated."
            )

        self.daily_production = (
            self.hourly_production["production_kwh"]
            .resample("D")
            .sum()
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

        dataframe["production_kwh"] = (
            dataframe["production_w"] / 1000
        )

        dataframe.drop(
            columns=["production_w"],
            inplace=True
        )

        return dataframe[
            [
                "production_kwh",
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

    if self.energy_balance is None:

        raise ValueError(
            "Energy balance has not been calculated."
        )

    production = self.hourly_production["production_kwh"]

    balance = self.energy_balance

    # ==========================================
    # Eliminar horas sin consumo válido
    # ==========================================

    valid_balance = balance.dropna(
        subset=["consumption_kwh"]
    )

    consumption = valid_balance["consumption_kwh"].sum()

    annual_production = production.sum()

    installed_power = self.configuration.installed_power_kwp

    productive_hours = (production > 0).sum()

    zero_production_hours = (production == 0).sum()

    hourly_average = production.mean()

    daily_average = annual_production / 365

    monthly_average = annual_production / 12

    equivalent_hours = (
        annual_production /
        installed_power
    )

    specific_yield = equivalent_hours

    capacity_factor = (
        annual_production /
        (installed_power * len(production))
    ) * 100

    maximum_power = production.max()

    if (production > 0).any():

        minimum_power = (
            production[production > 0].min()
        )

    else:

        minimum_power = 0.0

    # ==========================================
    # Balance energético (solo horas válidas)
    # ==========================================

    self_consumption = (
        valid_balance["self_consumption_kwh"].sum()
    )

    grid_import = (
        valid_balance["grid_import_kwh"].sum()
    )

    grid_export = (
        valid_balance["grid_export_kwh"].sum()
    )

    self_consumption_ratio = (
        self_consumption /
        annual_production
    ) * 100

    self_sufficiency = (
        self_consumption /
        consumption
    ) * 100

    coverage_ratio = (
        annual_production /
        consumption
    ) * 100

    surplus_ratio = (
        grid_export /
        annual_production
    ) * 100

    import_ratio = (
        grid_import /
        consumption
    ) * 100

    self.solar_statistics = {

        "hours": len(production),

        "productive_hours": productive_hours,

        "zero_production_hours": zero_production_hours,

        "annual_production": annual_production,

        "daily_average": daily_average,

        "monthly_average": monthly_average,

        "hourly_average": hourly_average,

        "maximum_power": maximum_power,

        "minimum_power": minimum_power,

        "equivalent_hours": equivalent_hours,

        "specific_yield": specific_yield,

        "capacity_factor": capacity_factor,

        "consumption": consumption,

        "self_consumption": self_consumption,

        "grid_import": grid_import,

        "grid_export": grid_export,

        "self_consumption_ratio": self_consumption_ratio,

        "self_sufficiency": self_sufficiency,

        "coverage_ratio": coverage_ratio,

        "surplus_ratio": surplus_ratio,

        "import_ratio": import_ratio

    }
    
    def calculate_monthly_production(self):

        """
        Calcula la producción mensual.
        """

        if self.daily_production is None:

            self.calculate_daily_production()

        self.monthly_production = (
                self.daily_production
                .resample("ME")
                .sum()
            )

    def calculate_yearly_production(self):

        """
        Calcula la producción anual.
        """

        if self.monthly_production is None:

            self.calculate_monthly_production()

        self.yearly_production = (
            self.monthly_production
            .resample("YE")
            .sum()
        )

    def calculate_energy_balance(
        self,
        consumption: pd.Series
    ):

        """
        Calcula el balance energético horario entre
        consumo y producción fotovoltaica.

        Parámetros
        ----------
        consumption
            Serie horaria de consumo (kWh).

        """

        if self.hourly_production is None:

            raise RuntimeError(
                "Hourly production has not been calculated."
            )
        
        # Producción horaria
        production = self.hourly_production["production_kwh"]

        # Clave MM-DD-HH de la producción
        production_lookup = production.copy()
        production_lookup.index = production_lookup.index.strftime("%m-%d-%H")

        # Balance con el índice REAL del consumo
        balance = pd.DataFrame(index=consumption.index)

        balance["consumption_kwh"] = consumption.values

        # Buscar la producción correspondiente al mismo perfil horario
        profile_key = balance.index.strftime("%m-%d-%H")

        balance["production_kwh"] = (
            pd.Series(profile_key, index=balance.index)
            .map(production_lookup)
            .fillna(0.0)
        )

        balance["self_consumption_kwh"] = (
            balance[
                [
                    "consumption_kwh",
                    "production_kwh"
                ]
            ].min(axis=1)
        )

        balance["grid_import_kwh"] = (
            balance["consumption_kwh"]
            - balance["self_consumption_kwh"]
        )

        balance["grid_export_kwh"] = (
            balance["production_kwh"]
            - balance["self_consumption_kwh"]
        )
        print(type(consumption.index))
        print(consumption.index[:5])

        print(consumption.head())

        print(consumption.isna().sum())

        print("Longitud consumo:", len(consumption))
        print("Longitud índice :", len(consumption.index))

        self.energy_balance = balance

        # Solo horas con consumo válido
        valid_balance = balance.dropna(subset=["consumption_kwh"])

        consumption = valid_balance["consumption_kwh"].sum()

    def monthly_production_report(self):

        print()

        print("=== PRODUCCIÓN MENSUAL FV ===")

        print()

        for month, value in self.monthly_production.items():

            value_text = (
                f"{value:,.2f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            )

            print(f"{month.strftime('%m-%Y')} : {value_text:>10} kWh")

    def statistics_report(self):

        if not self.solar_statistics:

            raise ValueError(
                "Solar statistics have not been calculated."
            )

        print()

        print("=========================================")
        print("PRODUCCIÓN FOTOVOLTAICA")
        print("=========================================")
        print()

        print(f"Potencia instalada      : {self.configuration.installed_power_kwp:.2f} kWp")
        print(f"Tecnología FV           : {self.configuration.pv_technology}")
        print(f"Inclinación             : {self.configuration.tilt}°")
        print(f"Orientación             : {self.configuration.azimuth}°")
        print(f"Pérdidas consideradas   : {self.configuration.losses:.1f} %")

        print()

        print("-----------------------------------------")
        print("PRODUCCIÓN")
        print("-----------------------------------------")

        print(f"Horas simuladas         : {self.solar_statistics['hours']}")
        print(f"Producción simulada     : {self.solar_statistics['annual_production']:.2f} kWh/año")
        print(f"Producción media diaria : {self.solar_statistics['daily_average']:.2f} kWh")
        print(f"Potencia máxima         : {self.solar_statistics['maximum_power']:.2f} kW")
        print(f"Potencia mínima (>0)    : {self.solar_statistics['minimum_power']:.2f} kW")
        print(f"Horas equivalentes      : {self.solar_statistics['equivalent_hours']:.2f} h")
        print(f"Factor de capacidad     : {self.solar_statistics['capacity_factor']:.2f} %")

    def energy_balance_report(self):

        if self.energy_balance is None:

            raise ValueError(
                "Energy balance has not been calculated."
            )

        if self.solar_statistics is None:

            raise ValueError(
                "Solar statistics have not been calculated."
            )

        stats = self.solar_statistics

        print()
        print("=" * 40)
        print("BALANCE ENERGÉTICO")
        print("=" * 40)
        print()

        print(f"Consumo total periodo  : {stats['consumption']:10.2f} kWh")
        print(f"Producción periodo     : {stats['annual_production']:10.2f} kWh")
        print()

        print(f"Autoconsumo total      : {stats['self_consumption']:10.2f} kWh")
        print(f"Importación de red     : {stats['grid_import']:10.2f} kWh")
        print(f"Exportación a red      : {stats['grid_export']:10.2f} kWh")
        print()

        print(f"Autosuficiencia        : {stats['self_sufficiency']:10.2f} %")
        print(f"Autoconsumo FV         : {stats['self_consumption_ratio']:10.2f} %")
        print(f"Cobertura FV           : {stats['coverage_ratio']:10.2f} %")
        print(f"Excedentes             : {stats['surplus_ratio']:10.2f} %")

    def calculate_energy_statistics(self):

        """
        Calcula los indicadores energéticos de la instalación FV.
        """

        if self.energy_balance is None:

            raise RuntimeError(
                "Energy balance has not been calculated."
            )

        balance = self.energy_balance

        consumption = balance["consumption_kwh"].sum()

        production = balance["production_kwh"].sum()

        self_consumption = balance["self_consumption_kwh"].sum()

        grid_import = balance["grid_import_kwh"].sum()

        grid_export = balance["grid_export_kwh"].sum()

        if consumption > 0:

            self_sufficiency = (
                self_consumption / consumption
            ) * 100

        else:

            self_sufficiency = 0

        if production > 0:

            self_consumption_ratio = (
                self_consumption / production
            ) * 100

        else:

            self_consumption_ratio = 0

        self.energy_statistics = {

            "consumption_kwh": consumption,

            "production_kwh": production,

            "self_consumption_kwh": self_consumption,

            "grid_import_kwh": grid_import,

            "grid_export_kwh": grid_export,

            "self_sufficiency": self_sufficiency,

            "self_consumption_ratio": self_consumption_ratio

        }

    def energy_statistics_report(self):

        if self.energy_statistics is None:

            raise RuntimeError(
                "Energy statistics have not been calculated."
            )

        s = self.energy_statistics

        print()

        print("=" * 41)
        print("BALANCE ENERGÉTICO")
        print("=" * 41)
        print()

        print(f"Consumo total periodo  : {s['consumption_kwh']:10.2f} kWh")
        print(f"Producción periodo     : {s['production_kwh']:10.2f} kWh")
        print()

        print(f"Autoconsumo total      : {s['self_consumption_kwh']:10.2f} kWh")
        print(f"Importación de red     : {s['grid_import_kwh']:10.2f} kWh")
        print(f"Exportación a red      : {s['grid_export_kwh']:10.2f} kWh")
        print()

        print(f"Autosuficiencia        : {s['self_sufficiency']:10.2f} %")
        print(f"Autoconsumo FV         : {s['self_consumption_ratio']:10.2f} %")