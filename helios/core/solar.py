from dataclasses import dataclass
from pathlib import Path
import json
import requests

import pandas as pd
from helios.reports.printer import ReportPrinter
from helios.solar.configuration import SolarConfiguration
from helios.solar.production import SolarProductionEngine
from helios.solar.balance import SolarBalanceEngine
from helios.solar.statistics import SolarStatisticsEngine
from helios.solar.pvgis import PVGISClient

class SolarEngine:

    def __init__(self):

        self.hourly_production = None
        self.solar_statistics = None
        self.hourly_profile = None
        self.energy_balance: pd.DataFrame | None = None
        self.daily_production: pd.Series | None = None
        self.monthly_production: pd.Series | None = None
        self.yearly_production: pd.Series | None = None
        self.client = PVGISClient()
        self.production_engine = SolarProductionEngine()

    def calculate_hourly_production(
        self,
        configuration: SolarConfiguration
    ) -> pd.DataFrame:

        self.configuration = configuration

        response = self.client.fetch(
            configuration
        )

        self.hourly_production = (
            self._parse_pvgis_response(
                response
            )
        )

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

        return self.daily_production

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

        self.solar_statistics = (
            SolarStatisticsEngine.calculate(
                self.hourly_production,
                self.energy_balance,
                self.configuration
            )
        )

        return self.solar_statistics

    def calculate_monthly_production(self):

        if self.daily_production is None:

            self.calculate_daily_production()

        self.monthly_production = (
            SolarProductionEngine.monthly(
                self.daily_production
            )
        )

        return self.monthly_production

    def calculate_yearly_production(self):

        if self.monthly_production is None:

            self.calculate_monthly_production()

        self.yearly_production = (
            SolarProductionEngine.yearly(
                self.monthly_production
            )
        )

        return self.yearly_production

    def calculate_energy_balance(
        self,
        consumption: pd.Series
    ):

        if self.hourly_production is None:

            raise RuntimeError(
                "Hourly production has not been calculated."
            )

        self.energy_balance = (
            SolarBalanceEngine.calculate(
                consumption,
                self.hourly_production
            )
        )

        return self.energy_balance

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