import pandas as pd
import pytest

from unittest.mock import patch, call

from helios.reports.solar_reports import SolarReports


class TestSolarReports:

    def setup_method(self):

        self.reports = SolarReports()

        class Configuration:
            pv_technology = "crystSi"
            installed_power_kwp = 5.4
            tilt = 30
            azimuth = 0
            losses = 14

        self.configuration = Configuration()

    # ==================================================
    # production_statistics
    # ==================================================

    def test_production_statistics_requires_statistics(self):

        with pytest.raises(
            ValueError,
            match="Solar statistics have not been calculated."
        ):

            self.reports.production_statistics(
                None,
                self.configuration
            )

        with pytest.raises(
            ValueError,
            match="Solar statistics have not been calculated."
        ):

            self.reports.production_statistics(
                {},
                self.configuration
            )

    @patch(
        "helios.reports.solar_reports.ReportPrinter"
    )
    def test_production_statistics(self, printer):

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

        result = self.reports.production_statistics(
            statistics,
            self.configuration
        )

        assert result is None

        # --------------------------------------------------
        # Estructura
        # --------------------------------------------------

        printer.title.assert_called_once_with(
            "SOLAR PRODUCTION REPORT"
        )

        assert printer.blank.call_count == 3

        printer.subtitle.assert_called_once_with(
            "PRODUCCIÓN"
        )

        # --------------------------------------------------
        # Configuración FV
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Estadísticas de producción
        # --------------------------------------------------

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

        # 4 energy calls:
        # annual production
        # period production
        # daily average
        # (the remaining values use value)
        assert printer.energy.call_count == 3

        # 4 percent/value calls for configuration/statistics
        assert printer.percent.call_count == 2
        assert printer.value.call_count == 6

    # ==================================================
    # energy_balance
    # ==================================================

    def test_energy_balance_requires_statistics(self):

        with pytest.raises(
            RuntimeError,
            match="Energy statistics have not been calculated."
        ):

            self.reports.energy_balance(None)

    @patch(
        "helios.reports.solar_reports.ReportPrinter"
    )
    def test_energy_balance(self, printer):

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

        result = self.reports.energy_balance(
            statistics
        )

        assert result is None

        # --------------------------------------------------
        # Estructura
        # --------------------------------------------------

        printer.title.assert_called_once_with(
            "ENERGY BALANCE"
        )

        assert printer.blank.call_count == 3

        # --------------------------------------------------
        # Energía
        # --------------------------------------------------

        assert printer.energy.call_count == 5

        expected_energy_calls = [
            call(
                "Consumo total periodo",
                1000.0
            ),
            call(
                "Producción periodo",
                1200.0
            ),
            call(
                "Autoconsumo total",
                800.0
            ),
            call(
                "Importación de red",
                200.0
            ),
            call(
                "Exportación a red",
                400.0
            ),
        ]

        assert (
            printer.energy.call_args_list
            == expected_energy_calls
        )

        # --------------------------------------------------
        # Ratios
        # --------------------------------------------------

        assert printer.percent.call_count == 4

        expected_percent_calls = [
            call(
                "Autosuficiencia",
                80.0
            ),
            call(
                "Autoconsumo FV",
                66.67
            ),
            call(
                "Cobertura FV",
                120.0
            ),
            call(
                "Excedentes",
                33.33
            ),
        ]

        assert (
            printer.percent.call_args_list
            == expected_percent_calls
        )

    # ==================================================
    # monthly_production
    # ==================================================

    @patch(
        "helios.reports.solar_reports.ReportPrinter"
    )
    def test_monthly_production(self, printer):

        monthly_production = pd.Series(
            [
                100.0,
                200.0,
                300.0,
            ],
            index=pd.to_datetime(
                [
                    "2025-01-31",
                    "2025-02-28",
                    "2025-03-31",
                ]
            )
        )

        result = self.reports.monthly_production(
            monthly_production
        )

        assert result is None

        printer.title.assert_called_once_with(
            "MONTHLY PV PRODUCTION"
        )

        assert printer.blank.call_count == 1

        assert printer.energy.call_count == 3

        expected_calls = [
            call(
                "01-2025",
                100.0
            ),
            call(
                "02-2025",
                200.0
            ),
            call(
                "03-2025",
                300.0
            ),
        ]

        assert (
            printer.energy.call_args_list
            == expected_calls
        )