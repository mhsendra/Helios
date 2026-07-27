from dataclasses import dataclass
from pathlib import Path
import json
import requests

import pandas as pd
from helios.reports.printer import ReportPrinter
from helios.solar.configuration import SolarConfiguration
from helios.solar.production import SolarProductionEngine

class SolarEngine:

    def __init__(self):

        self.hourly_production = None
        self.solar_statistics = None
        self.hourly_profile = None
        self.energy_balance: pd.DataFrame | None = None
        self.daily_production: pd.Series | None = None
        self.monthly_production: pd.Series | None = None
        self.yearly_production: pd.Series | None = None
        
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

        if self.hourly_production is None:

            raise RuntimeError(
                "Hourly production has not been calculated."
            )

        self.daily_production = (
            SolarProductionEngine.daily(
                self.hourly_production
            )
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

        # ==========================================
        # Balance energético del periodo analizado
        # ==========================================

        balance = self.energy_balance

        valid_balance = balance.dropna(
            subset=["consumption_kwh"]
        )

        # ==========================================
        # Producción anual de referencia (PVGIS)
        # ==========================================

        reference_production = (
            self.hourly_production["production_kwh"]
            .sum()
        )

        production = valid_balance["production_kwh"]

        consumption = (
            valid_balance["consumption_kwh"]
            .sum()
        )

        period_production = (
            production.sum()
        )

        number_of_days = (
            valid_balance.index
            .normalize()
            .nunique()
        )

        number_of_months = (
            valid_balance.index
            .to_period("M")
            .nunique()
        )

        # ==========================================
        # Producción fotovoltaica
        # ==========================================

        installed_power = (
            self.configuration.installed_power_kwp
        )

        productive_hours = (
            production > 0
        ).sum()

        zero_production_hours = (
            production == 0
        ).sum()

        hourly_average = (
            production.mean()
        )

        daily_average = (
            period_production /
            number_of_days
        )

        monthly_average = (
            period_production /
            number_of_months
        )

        equivalent_hours = (
            period_production /
            installed_power
        )

        specific_yield = (
            period_production /
            installed_power
        )

        capacity_factor = (
            period_production /
            (
                installed_power *
                len(valid_balance)
            )
        ) * 100

        maximum_power = (
            production.max()
        )

        if productive_hours > 0:

            minimum_power = (
                production[
                    production > 0
                ].min()
            )

        else:

            minimum_power = 0.0

        # ==========================================
        # Balance energético
        # ==========================================

        self_consumption = (
            valid_balance["self_consumption_kwh"]
            .sum()
        )

        grid_import = (
            valid_balance["grid_import_kwh"]
            .sum()
        )

        grid_export = (
            valid_balance["grid_export_kwh"]
            .sum()
        )

        self_consumption_ratio = (
            self_consumption /
            period_production
        ) * 100

        self_sufficiency = (
            self_consumption /
            consumption
        ) * 100

        coverage_ratio = (
            period_production /
            consumption
        ) * 100

        surplus_ratio = (
            grid_export /
            period_production
        ) * 100

        import_ratio = (
            grid_import /
            consumption
        ) * 100

        # ==========================================
        # Resultados
        # ==========================================

        self.solar_statistics = {

            "hours": len(valid_balance),

            "productive_hours": productive_hours,

            "zero_production_hours": zero_production_hours,

            "period_production": period_production,

            "annual_production": reference_production,

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

        if self.daily_production is None:

            self.calculate_daily_production()

        self.monthly_production = (
            SolarProductionEngine.monthly(
                self.daily_production
            )
        )

    def calculate_yearly_production(self):

        if self.monthly_production is None:

            self.calculate_monthly_production()

        self.yearly_production = (
            SolarProductionEngine.yearly(
                self.monthly_production
            )
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

    def production_statistics_report(self):

        if not self.solar_statistics:

            raise ValueError(
                "Solar statistics have not been calculated."
            )

        ReportPrinter.title("SOLAR PRODUCTION REPORT")
        ReportPrinter.blank()

        # Configuración FV
        ReportPrinter.text(
            "Tecnología FV",
            self.configuration.pv_technology
        )

        ReportPrinter.energy(
            "Potencia instalada",
            self.configuration.installed_power_kwp
        )

        ReportPrinter.text(
            "Inclinación",
            f"{self.configuration.tilt}°"
        )

        ReportPrinter.text(
            "Orientación",
            f"{self.configuration.azimuth}°"
        )

        ReportPrinter.percent(
            "Pérdidas consideradas",
            self.configuration.losses,
            decimals=1
        )

        ReportPrinter.blank()

        print("-" * 55)
        print("PRODUCCIÓN")
        print("-" * 55)

        ReportPrinter.count(
            "Horas del periodo analizado",
            self.solar_statistics["hours"]
        )

        ReportPrinter.energy(
            "Producción estimada anual (PVGIS)",
            self.solar_statistics["annual_production"]
        )

        ReportPrinter.energy(
            "Producción simulada del periodo",
            self.solar_statistics["period_production"]
        )

        ReportPrinter.energy(
            "Producción media diaria",
            self.solar_statistics["daily_average"]
        )

        ReportPrinter.text(
            "Potencia máxima",
            f"{self.solar_statistics['maximum_power']:.2f} kW"
        )

        ReportPrinter.text(
            "Potencia mínima (>0)",
            f"{self.solar_statistics['minimum_power']:.2f} kW"
        )

        ReportPrinter.text(
            "Horas equivalentes",
            f"{self.solar_statistics['equivalent_hours']:.2f} h"
        )

        ReportPrinter.percent(
            "Factor de capacidad",
            self.solar_statistics["capacity_factor"]
        )
        
    def energy_balance_report(self):

        if self.solar_statistics is None:

            raise RuntimeError(
                "Energy statistics have not been calculated."
            )

        s = self.solar_statistics

        ReportPrinter.title("ENERGY BALANCE")
        ReportPrinter.blank()

        ReportPrinter.energy(
            "Consumo total periodo",
            s["consumption"]
        )

        ReportPrinter.energy(
            "Producción periodo",
            s["period_production"]
        )

        ReportPrinter.blank()

        ReportPrinter.energy(
            "Autoconsumo total",
            s["self_consumption"]
        )

        ReportPrinter.energy(
            "Importación de red",
            s["grid_import"]
        )

        ReportPrinter.energy(
            "Exportación a red",
            s["grid_export"]
        )

        ReportPrinter.blank()

        ReportPrinter.percent(
            "Autosuficiencia",
            s["self_sufficiency"]
        )

        ReportPrinter.percent(
            "Autoconsumo FV",
            s["self_consumption_ratio"]
        )

        ReportPrinter.percent(
            "Cobertura FV",
            s["coverage_ratio"]
        )

        ReportPrinter.percent(
            "Excedentes",
            s["surplus_ratio"]
        )