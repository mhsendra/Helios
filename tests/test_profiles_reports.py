import pandas as pd
from unittest.mock import patch

from helios.reports.profiles import ProfilesReports


class TestProfilesReports:

    def setup_method(self):

        self.report = ProfilesReports()

    # ==================================================
    # hourly_profile
    # ==================================================

    def test_hourly_profile_none(self, capsys):

        result = self.report.hourly_profile(
            None
        )

        assert result is None

        captured = capsys.readouterr()

        assert (
            captured.out
            == "No hay perfil horario calculado.\n"
        )

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

        result = self.report.hourly_profile(
            hourly
        )

        assert result is None

        printer.title.assert_called_once_with(
            "HOURLY PROFILE REPORT"
        )

        printer.count.assert_called_once_with(
            "Horas analizadas",
            6
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

        assert printer.text.call_count == 7

    # ==================================================
    # weekday_profile
    # ==================================================

    def test_weekday_profile_none(self, capsys):

        result = self.report.weekday_profile(
            None
        )

        assert result is None

        captured = capsys.readouterr()

        assert (
            captured.out
            == "No hay perfil semanal calculado.\n"
        )

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

        result = self.report.weekday_profile(
            weekday
        )

        assert result is None

        printer.title.assert_called_once_with(
            "WEEKDAY PROFILE REPORT"
        )

        assert printer.energy.call_count == 5

        printer.percent.assert_called_once()

        printer.text.assert_any_call(
            "Día de mayor consumo",
            "Domingo"
        )

        printer.text.assert_any_call(
            "Día de menor consumo",
            "Lunes"
        )

        assert printer.text.call_count == 9

    # ==================================================
    # monthly_profile
    # ==================================================

    def test_monthly_profile_none(self, capsys):

        result = self.report.monthly_profile(
            None
        )

        assert result is None

        captured = capsys.readouterr()

        assert (
            captured.out
            == "No hay perfil mensual calculado.\n"
        )

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

        result = self.report.monthly_profile(
            monthly
        )

        assert result is None

        printer.title.assert_called_once_with(
            "MONTHLY PROFILE REPORT"
        )

        printer.text.assert_any_call(
            "Mes de mayor consumo",
            "Marzo (promedio multianual)"
        )

        printer.text.assert_any_call(
            "Mes de menor consumo",
            "Enero (promedio multianual)"
        )

        assert printer.energy.call_count == 2

        printer.percent.assert_called_once_with(
            "Variación estacional",
            100.0,
            decimals=1
        )

        assert printer.text.call_count == 6

    # ==================================================
    # seasonal_profile
    # ==================================================

    def test_seasonal_profile_none(self, capsys):

        result = self.report.seasonal_profile(
            None
        )

        assert result is None

        captured = capsys.readouterr()

        assert (
            captured.out
            == "No hay perfil estacional calculado.\n"
        )

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

        result = self.report.seasonal_profile(
            seasonal
        )

        assert result is None

        printer.title.assert_called_once_with(
            "SEASONAL PROFILE REPORT"
        )

        printer.text.assert_any_call(
            "Estación de mayor consumo",
            "Verano (promedio multianual)"
        )

        printer.text.assert_any_call(
            "Estación de menor consumo",
            "Invierno (promedio multianual)"
        )

        assert printer.energy.call_count == 2

        printer.percent.assert_called_once_with(
            "Variación estacional",
            100.0,
            decimals=1
        )

        assert printer.text.call_count == 6