import pandas as pd
import pytest

from unittest.mock import patch

from helios.reports.solar_reports import SolarReports


class TestSolarReports:

    def setup_method(self):

        self.reports = SolarReports()

    def test_production_statistics_prints_configuration(self):

        statistics = {
            "hours": 100,
            "annual_production": 5000.0,
            "period_production": 4800.0,
            "daily_average": 13.15,
            "maximum_power": 5.2,
            "minimum_power": 0.1,
            "equivalent_hours": 960.0,
            "capacity_factor": 11.0,
        }

        class Configuration:
            pv_technology = "crystSi"
            installed_power_kwp = 5.4
            tilt = 30
            azimuth = 0
            losses = 14

        with patch(
            "helios.reports.solar_reports.ReportPrinter"
        ) as printer:

            self.reports.production_statistics(
                statistics,
                Configuration()
            )

            printer.title.assert_called_once_with(
                "SOLAR PRODUCTION REPORT"
            )

            printer.text.assert_called_once_with(
                "Tecnología FV",
                "crystSi"
            )

            printer.value.assert_any_call(
                "Potencia instalada",
                5.4,
                "kWp",
                decimals=2
            )

            printer.value.assert_any_call(
                "Inclinación",
                30,
                "°"
            )

            printer.value.assert_any_call(
                "Orientación",
                0,
                "°"
            )

            printer.percent.assert_any_call(
                "Pérdidas consideradas",
                14,
                decimals=1
            )

    def test_production_statistics_prints_statistics(self):

        statistics = {
            "hours": 100,
            "annual_production": 5000.0,
            "period_production": 4800.0,
            "daily_average": 13.15,
            "maximum_power": 5.2,
            "minimum_power": 0.1,
            "equivalent_hours": 960.0,
            "capacity_factor": 11.0,
        }

        class Configuration:
            pv_technology = "crystSi"
            installed_power_kwp = 5.4
            tilt = 30
            azimuth = 0
            losses = 14

        with patch(
            "helios.reports.solar_reports.ReportPrinter"
        ) as printer:

            self.reports.production_statistics(
                statistics,
                Configuration()
            )

            printer.count.assert_called_once_with(
                "Horas del periodo analizado",
                100
            )

            printer.energy.assert_any_call(
                "Producción estimada anual (PVGIS)",
                5000.0
            )

            printer.energy.assert_any_call(
                "Producción simulada del periodo",
                4800.0
            )

            printer.energy.assert_any_call(
                "Producción media diaria",
                13.15
            )

            printer.value.assert_any_call(
                "Potencia máxima",
                5.2,
                "kW",
                decimals=2
            )

            printer.value.assert_any_call(
                "Potencia mínima (>0)",
                0.1,
                "kW",
                decimals=2
            )

            printer.value.assert_any_call(
                "Horas equivalentes",
                960.0,
                "h",
                decimals=2
            )

            printer.percent.assert_any_call(
                "Factor de capacidad",
                11.0
            )

    def test_production_statistics_requires_statistics(self):

        class Configuration:
            pv_technology = "crystSi"
            installed_power_kwp = 5.4
            tilt = 30
            azimuth = 0
            losses = 14

        with pytest.raises(
            ValueError,
            match="Solar statistics have not been calculated."
        ):

            self.reports.production_statistics(
                {},
                Configuration()
            )

    def test_energy_balance(self):

        statistics = {
            "consumption": 1000.0,
            "period_production": 1200.0,
            "self_consumption": 800.0,
            "grid_import": 200.0,
            "grid_export": 400.0,
            "self_sufficiency": 80.0,
            "self_consumption_ratio": 66.67,
            "coverage_ratio": 120.0,
            "surplus_ratio": 33.33,
        }

        with patch(
            "helios.reports.solar_reports.ReportPrinter"
        ) as printer:

            self.reports.energy_balance(
                statistics
            )

            printer.title.assert_called_once_with(
                "ENERGY BALANCE"
            )

            printer.energy.assert_any_call(
                "Consumo total periodo",
                1000.0
            )

            printer.energy.assert_any_call(
                "Producción periodo",
                1200.0
            )

            printer.energy.assert_any_call(
                "Autoconsumo total",
                800.0
            )

            printer.energy.assert_any_call(
                "Importación de red",
                200.0
            )

            printer.energy.assert_any_call(
                "Exportación a red",
                400.0
            )

            printer.percent.assert_any_call(
                "Autosuficiencia",
                80.0
            )

            printer.percent.assert_any_call(
                "Autoconsumo FV",
                66.67
            )

            printer.percent.assert_any_call(
                "Cobertura FV",
                120.0
            )

            printer.percent.assert_any_call(
                "Excedentes",
                33.33
            )

    def test_monthly_production(self):

        monthly_production = pd.Series(
            [100.0, 200.0, 300.0],
            index=pd.to_datetime(
                [
                    "2025-01-31",
                    "2025-02-28",
                    "2025-03-31",
                ]
            )
        )

        with patch(
            "helios.reports.solar_reports.ReportPrinter"
        ) as printer:

            self.reports.monthly_production(
                monthly_production
            )

            printer.title.assert_called_once_with(
                "MONTHLY PV PRODUCTION"
            )

            assert printer.energy.call_count == 3

            printer.energy.assert_any_call(
                "01-2025",
                100.0
            )

            printer.energy.assert_any_call(
                "02-2025",
                200.0
            )

            printer.energy.assert_any_call(
                "03-2025",
                300.0
            )