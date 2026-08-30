import pandas as pd
from unittest.mock import call, patch

from helios.reports.profiles import ProfilesReports


class TestProfilesReports:

    def setup_method(self):

        self.report = ProfilesReports()

    # ==================================================
    # hourly_profile
    # ==================================================

    def test_hourly_profile_none(self, capsys):

        result = self.report.hourly_profile(None)

        assert result is None


    @patch(
        "helios.reports.profiles.ReportPrinter"
    )
    def test_hourly_profile(self, printer):

        hourly = pd.Series(
            [
                1.0,
                2.0,
                5.0,
                3.0,
                4.0,
                0.5
            ],
            index=[0, 1, 2, 3, 4, 5]
        )

        result = self.report.hourly_profile(hourly)

        assert result is None

        printer.title.assert_called_once_with(
            "HOURLY PROFILE REPORT"
        )

        printer.blank.assert_has_calls(
            [
                call(),
                call(),
                call(),
                call(),
            ]
        )

        assert printer.blank.call_count == 4

        printer.count.assert_called_once_with(
            "Horas analizadas",
            len(hourly)
        )

        printer.energy.assert_has_calls(
            [
                call(
                    "Consumo medio horario",
                    hourly.mean(),
                    decimals=3
                ),
                call(
                    "Consumo máximo",
                    hourly.max(),
                    decimals=3
                ),
                call(
                    "Consumo mínimo",
                    hourly.min(),
                    decimals=3
                ),
            ]
        )

        assert printer.energy.call_count == 3

        printer.text.assert_any_call(
            "Hora de mayor consumo",
            "02:00"
        )

        printer.text.assert_any_call(
            "Hora de menor consumo",
            "05:00"
        )

        printer.text.assert_has_calls(
            [
                call(
                    "Hora 02:00",
                    "5.000 kWh"
                ),
                call(
                    "Hora 04:00",
                    "4.000 kWh"
                ),
                call(
                    "Hora 03:00",
                    "3.000 kWh"
                ),
                call(
                    "Hora 01:00",
                    "2.000 kWh"
                ),
                call(
                    "Hora 00:00",
                    "1.000 kWh"
                ),
            ]
        )

        assert printer.text.call_count == 7

    # ==================================================
    # weekday_profile
    # ==================================================

    def test_weekday_profile_none(self, capsys):

        result = self.report.weekday_profile(None)

        assert result is None

    @patch(
        "helios.reports.profiles.ReportPrinter"
    )
    def test_weekday_profile(self, printer):

        weekday = pd.Series(
            [
                10.0,
                11.0,
                12.0,
                13.0,
                14.0,
                20.0,
                22.0
            ],
            index=[
                "Lunes",
                "Martes",
                "Miércoles",
                "Jueves",
                "Viernes",
                "Sábado",
                "Domingo"
            ]
        )

        result = self.report.weekday_profile(weekday)

        assert result is None

        laborables = weekday.iloc[:5].mean()
        fin_semana = weekday.iloc[5:].mean()
        incremento = (
            (fin_semana - laborables)
            / laborables
            * 100
        )

        printer.title.assert_called_once_with(
            "WEEKDAY PROFILE REPORT"
        )

        printer.blank.assert_has_calls(
            [
                call(),
                call(),
                call(),
                call(),
            ]
        )

        assert printer.blank.call_count == 5

        printer.energy.assert_has_calls(
            [
                call(
                    "Consumo medio semanal",
                    weekday.mean(),
                    decimals=3
                ),
                call(
                    "Media laborables",
                    laborables,
                    decimals=3
                ),
                call(
                    "Media fin de semana",
                    fin_semana,
                    decimals=3
                ),
                call(
                    "Consumo máximo",
                    weekday.max(),
                    decimals=3
                ),
                call(
                    "Consumo mínimo",
                    weekday.min(),
                    decimals=3
                ),
            ]
        )

        assert printer.energy.call_count == 5

        printer.percent.assert_called_once_with(
            "Incremento fin de semana",
            incremento,
            decimals=1
        )

        printer.text.assert_has_calls(
            [
                call(
                    "Día de mayor consumo",
                    "Domingo"
                ),
                call(
                    "Día de menor consumo",
                    "Lunes"
                ),
                call("Lunes", "10.000 kWh"),
                call("Martes", "11.000 kWh"),
                call("Miércoles", "12.000 kWh"),
                call("Jueves", "13.000 kWh"),
                call("Viernes", "14.000 kWh"),
                call("Sábado", "20.000 kWh"),
                call("Domingo", "22.000 kWh"),
            ]
        )

        assert printer.text.call_count == 9

    # ==================================================
    # monthly_profile
    # ==================================================

    def test_monthly_profile_none(self, capsys):

        result = self.report.monthly_profile(None)

        assert result is None

    @patch(
        "helios.reports.profiles.ReportPrinter"
    )
    def test_monthly_profile(self, printer):

        monthly = pd.Series(
            [
                100.0,
                150.0,
                200.0,
                120.0
            ],
            index=[
                "Enero",
                "Febrero",
                "Marzo",
                "Abril"
            ]
        )

        result = self.report.monthly_profile(monthly)

        assert result is None

        incremento = (
            (monthly.max() - monthly.min())
            / monthly.min()
            * 100
        )

        printer.title.assert_called_once_with(
            "MONTHLY PROFILE REPORT"
        )

        printer.blank.assert_has_calls(
            [
                call(),
                call(),
                call(),
                call(),
            ]
        )

        assert printer.blank.call_count == 4

        printer.text.assert_has_calls(
            [
                call(
                    "Mes de mayor consumo",
                    "Marzo (promedio multianual)"
                ),
                call(
                    "Mes de menor consumo",
                    "Enero (promedio multianual)"
                ),
                call("Enero", "100.000 kWh"),
                call("Febrero", "150.000 kWh"),
                call("Marzo", "200.000 kWh"),
                call("Abril", "120.000 kWh"),
            ]
        )

        assert printer.text.call_count == 6

        printer.energy.assert_has_calls(
            [
                call(
                    "Consumo máximo",
                    monthly.max(),
                    decimals=3
                ),
                call(
                    "Consumo mínimo",
                    monthly.min(),
                    decimals=3
                ),
            ]
        )

        assert printer.energy.call_count == 2

        printer.percent.assert_called_once_with(
            "Variación estacional",
            incremento,
            decimals=1
        )

    # ==================================================
    # seasonal_profile
    # ==================================================

    def test_seasonal_profile_none(self, capsys):

        result = self.report.seasonal_profile(None)

        assert result is None

    @patch(
        "helios.reports.profiles.ReportPrinter"
    )
    def test_seasonal_profile(self, printer):

        seasonal = pd.Series(
            [
                100.0,
                150.0,
                200.0,
                120.0
            ],
            index=[
                "Invierno",
                "Primavera",
                "Verano",
                "Otoño"
            ]
        )

        result = self.report.seasonal_profile(seasonal)

        assert result is None

        incremento = (
            (seasonal.max() - seasonal.min())
            / seasonal.min()
            * 100
        )

        printer.title.assert_called_once_with(
            "SEASONAL PROFILE REPORT"
        )

        printer.blank.assert_has_calls(
            [
                call(),
                call(),
                call(),
                call(),
            ]
        )

        assert printer.blank.call_count == 4

        printer.text.assert_has_calls(
            [
                call(
                    "Estación de mayor consumo",
                    "Verano (promedio multianual)"
                ),
                call(
                    "Estación de menor consumo",
                    "Invierno (promedio multianual)"
                ),
                call("Invierno", "100.000 kWh"),
                call("Primavera", "150.000 kWh"),
                call("Verano", "200.000 kWh"),
                call("Otoño", "120.000 kWh"),
            ]
        )

        assert printer.text.call_count == 6

        printer.energy.assert_has_calls(
            [
                call(
                    "Consumo máximo",
                    seasonal.max(),
                    decimals=3
                ),
                call(
                    "Consumo mínimo",
                    seasonal.min(),
                    decimals=3
                ),
            ]
        )

        assert printer.energy.call_count == 2

        printer.percent.assert_called_once_with(
            "Variación estacional",
            incremento,
            decimals=1
        )