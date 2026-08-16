import pandas as pd

from helios.reports.printer import ReportPrinter


class TestReportPrinter:

    def test_text(self, capsys):

        ReportPrinter.text(
            "Consumo",
            "123.45 kWh"
        )

        output = capsys.readouterr().out

        assert "Consumo" in output
        assert "123.45 kWh" in output

    def test_hours(self, capsys):

        ReportPrinter.hours(
            "Horas",
            123.9
        )

        output = capsys.readouterr().out

        assert "Horas" in output
        assert "123" in output

    def test_percent_default_decimals(self, capsys):

        ReportPrinter.percent(
            "Porcentaje",
            12.3456
        )

        output = capsys.readouterr().out

        assert "12.35 %" in output

    def test_percent_custom_decimals(self, capsys):

        ReportPrinter.percent(
            "Porcentaje",
            12.3456,
            decimals=1
        )

        output = capsys.readouterr().out

        assert "12.3 %" in output

    def test_energy_default_decimals(self, capsys):

        ReportPrinter.energy(
            "Energía",
            12.3456
        )

        output = capsys.readouterr().out

        assert "12.35 kWh" in output

    def test_energy_custom_decimals(self, capsys):

        ReportPrinter.energy(
            "Energía",
            12.3456,
            decimals=3
        )

        output = capsys.readouterr().out

        assert "12.346 kWh" in output

    def test_datetime_with_value(self, capsys):

        timestamp = pd.Timestamp(
            "2025-01-15 18:30"
        )

        ReportPrinter.datetime(
            "Fecha",
            timestamp
        )

        output = capsys.readouterr().out

        assert "15/01/2025 18:30" in output

    def test_datetime_with_none(self, capsys):

        ReportPrinter.datetime(
            "Fecha",
            None
        )

        output = capsys.readouterr().out

        assert "-" in output

    def test_day_with_value(self, capsys):

        ReportPrinter.day(
            "Día",
            pd.Timestamp("2025-01-15")
        )

        output = capsys.readouterr().out

        assert "15/01/2025" in output

    def test_day_with_nan(self, capsys):

        ReportPrinter.day(
            "Día",
            pd.NaT
        )

        output = capsys.readouterr().out

        assert "---" in output

    def test_month_with_value(self, capsys):

        ReportPrinter.month(
            "Mes",
            pd.Timestamp("2025-03-15")
        )

        output = capsys.readouterr().out

        assert "Marzo 2025" in output

    def test_month_with_nan(self, capsys):

        ReportPrinter.month(
            "Mes",
            pd.NaT
        )

        output = capsys.readouterr().out

        assert "---" in output

    def test_year_with_value(self, capsys):

        ReportPrinter.year(
            "Año",
            pd.Timestamp("2025-03-15")
        )

        output = capsys.readouterr().out

        assert "2025" in output

    def test_year_with_nan(self, capsys):

        ReportPrinter.year(
            "Año",
            pd.NaT
        )

        output = capsys.readouterr().out

        assert "---" in output

    def test_count(self, capsys):

        ReportPrinter.count(
            "Registros",
            123.9
        )

        output = capsys.readouterr().out

        assert "123" in output

    def test_quality(self, capsys):

        ReportPrinter.quality(
            "Calidad",
            "excelente"
        )

        output = capsys.readouterr().out

        assert "EXCELENTE" in output

    def test_title(self, capsys):

        ReportPrinter.title(
            "TEST REPORT"
        )

        output = capsys.readouterr().out

        assert "HELIOS - TEST REPORT" in output
        assert "=" * 55 in output

    def test_table_header_default_alignment(self, capsys):

        ReportPrinter.table_header(
            ["Nombre", "Valor"],
            [10, 10]
        )

        output = capsys.readouterr().out
        lines = output.splitlines()

        assert lines[0] == "Nombre    Valor     "
        assert lines[1] == "-" * 20

    def test_table_header_right_alignment(self, capsys):

        ReportPrinter.table_header(
            ["Nombre", "Valor"],
            [10, 10],
            ["left", "right"]
        )

        output = capsys.readouterr().out
        lines = output.splitlines()

        assert lines[0] == "Nombre         Valor"
        assert lines[1] == "-" * 20

    def test_table_row_default_alignment(self, capsys):

        ReportPrinter.table_row(
            ["A", "B"],
            [5, 5]
        )

        output = capsys.readouterr().out

        assert output.strip() == "A    B"

    def test_table_row_right_alignment(self, capsys):

        ReportPrinter.table_row(
            ["A", "B"],
            [5, 5],
            ["left", "right"]
        )

        output = capsys.readouterr().out

        assert output.strip() == "A        B"

    def test_blank(self, capsys):

        ReportPrinter.blank()

        output = capsys.readouterr().out

        assert output == "\n"

    def test_line(self, capsys):

        ReportPrinter.line(
            "Consumo",
            123.45,
            "kWh"
        )

        output = capsys.readouterr().out

        assert "Consumo" in output
        assert "123.45" in output
        assert "kWh" in output

    def test_subtitle(self, capsys):

        ReportPrinter.subtitle(
            "ANNUAL COST"
        )

        output = capsys.readouterr().out

        assert "ANNUAL COST" in output
        assert "-" * 55 in output

    def test_value_float_with_decimals(self, capsys):

        ReportPrinter.value(
            "Coste",
            123.4567,
            "€",
            decimals=2
        )

        output = capsys.readouterr().out

        assert "123.46 €" in output

    def test_value_float_without_decimals(self, capsys):

        ReportPrinter.value(
            "Coste",
            123.4567,
            "€"
        )

        output = capsys.readouterr().out

        assert "123.4567 €" in output

    def test_value_non_float_with_decimals(self, capsys):

        ReportPrinter.value(
            "Cantidad",
            123,
            "unidades",
            decimals=2
        )

        output = capsys.readouterr().out

        assert "123 unidades" in output

    def test_value_without_unit(self, capsys):

        ReportPrinter.value(
            "Cantidad",
            123,
            decimals=2
        )

        output = capsys.readouterr().out

        assert "123" in output