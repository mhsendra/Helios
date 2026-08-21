import pandas as pd

import pytest

from helios.reports.printer import ReportPrinter


class TestReportPrinter:

    # ==================================================
    # _print_line
    # ==================================================

    def test_print_line_basic(self, capsys):

        ReportPrinter._print_line(
            "Consumo",
            "123.45 kWh"
        )

        output = capsys.readouterr().out

        assert output == (
            "Consumo..................................... "
            "123.45 kWh\n"
        )

    def test_print_line_converts_value_to_string(
        self,
        capsys
    ):

        ReportPrinter._print_line(
            "Valor",
            str(123)
        )

        output = capsys.readouterr().out

        assert output.endswith(
            " 123\n"
        )

    def test_print_line_total_width(
        self,
        capsys
    ):

        ReportPrinter._print_line(
            "Test",
            "123"
        )

        output = capsys.readouterr().out.rstrip("\n")

        assert len(output) == ReportPrinter.TOTAL_WIDTH

    def test_print_line_preserves_label_and_value(
        self,
        capsys
    ):

        ReportPrinter._print_line(
            "Etiqueta",
            "Valor"
        )

        output = capsys.readouterr().out

        assert output.startswith("Etiqueta")
        assert output.endswith("Valor\n")
        assert "." in output

    # ==================================================
    # text
    # ==================================================

    def test_text(self, capsys):

        ReportPrinter.text(
            "Consumo",
            "123.45 kWh"
        )

        output = capsys.readouterr().out

        assert "Consumo" in output
        assert "123.45 kWh" in output

    def test_text_converts_non_string_value(
        self,
        capsys
    ):

        ReportPrinter.text(
            "Valor",
            123
        )

        output = capsys.readouterr().out

        assert "Valor" in output
        assert "123" in output

    # ==================================================
    # hours
    # ==================================================

    def test_hours(self, capsys):

        ReportPrinter.hours(
            "Horas",
            123.9
        )

        output = capsys.readouterr().out

        assert "Horas" in output
        assert "123" in output
        assert "123.9" not in output

    def test_hours_integer(
        self,
        capsys
    ):

        ReportPrinter.hours(
            "Horas",
            100
        )

        output = capsys.readouterr().out

        assert "100" in output

    # ==================================================
    # percent
    # ==================================================

    def test_percent_default_decimals(
        self,
        capsys
    ):

        ReportPrinter.percent(
            "Porcentaje",
            12.3456
        )

        output = capsys.readouterr().out

        assert "12.35 %" in output

    def test_percent_custom_decimals(
        self,
        capsys
    ):

        ReportPrinter.percent(
            "Porcentaje",
            12.3456,
            decimals=1
        )

        output = capsys.readouterr().out

        assert "12.3 %" in output

    def test_percent_zero_decimals(
        self,
        capsys
    ):

        ReportPrinter.percent(
            "Porcentaje",
            12.6,
            decimals=0
        )

        output = capsys.readouterr().out

        assert "13 %" in output

    def test_percent_negative_value(
        self,
        capsys
    ):

        ReportPrinter.percent(
            "Variación",
            -5.4321
        )

        output = capsys.readouterr().out

        assert "-5.43 %" in output

    # ==================================================
    # energy
    # ==================================================

    def test_energy_default_decimals(
        self,
        capsys
    ):

        ReportPrinter.energy(
            "Energía",
            12.3456
        )

        output = capsys.readouterr().out

        assert "12.35 kWh" in output

    def test_energy_custom_decimals(
        self,
        capsys
    ):

        ReportPrinter.energy(
            "Energía",
            12.3456,
            decimals=3
        )

        output = capsys.readouterr().out

        assert "12.346 kWh" in output

    def test_energy_zero(
        self,
        capsys
    ):

        ReportPrinter.energy(
            "Energía",
            0
        )

        output = capsys.readouterr().out

        assert "0.00 kWh" in output

    def test_energy_negative(
        self,
        capsys
    ):

        ReportPrinter.energy(
            "Energía",
            -12.345
        )

        output = capsys.readouterr().out

        assert "-12.35 kWh" in output

    # ==================================================
    # datetime
    # ==================================================

    def test_datetime_with_value(
        self,
        capsys
    ):

        timestamp = pd.Timestamp(
            "2025-01-15 18:30"
        )

        ReportPrinter.datetime(
            "Fecha",
            timestamp
        )

        output = capsys.readouterr().out

        assert "15/01/2025 18:30" in output

    def test_datetime_with_none(
        self,
        capsys
    ):

        ReportPrinter.datetime(
            "Fecha",
            None
        )

        output = capsys.readouterr().out

        assert output.endswith(
            " -\n"
        )

    # ==================================================
    # day
    # ==================================================

    def test_day_with_value(
        self,
        capsys
    ):

        ReportPrinter.day(
            "Día",
            pd.Timestamp("2025-01-15")
        )

        output = capsys.readouterr().out

        assert "15/01/2025" in output

    def test_day_with_nan(
        self,
        capsys
    ):

        ReportPrinter.day(
            "Día",
            pd.NaT
        )

        output = capsys.readouterr().out

        assert "---" in output

    def test_day_with_string_date(
        self,
        capsys
    ):

        ReportPrinter.day(
            "Día",
            "2025-01-15"
        )

        output = capsys.readouterr().out

        assert "15/01/2025" in output

    # ==================================================
    # month
    # ==================================================

    def test_month_with_value(
        self,
        capsys
    ):

        ReportPrinter.month(
            "Mes",
            pd.Timestamp("2025-03-15")
        )

        output = capsys.readouterr().out

        assert "Marzo 2025" in output

    def test_month_with_nan(
        self,
        capsys
    ):

        ReportPrinter.month(
            "Mes",
            pd.NaT
        )

        output = capsys.readouterr().out

        assert "---" in output

    @pytest.mark.parametrize(
        "month, expected",
        [
            (1, "Enero 2025"),
            (2, "Febrero 2025"),
            (3, "Marzo 2025"),
            (4, "Abril 2025"),
            (5, "Mayo 2025"),
            (6, "Junio 2025"),
            (7, "Julio 2025"),
            (8, "Agosto 2025"),
            (9, "Septiembre 2025"),
            (10, "Octubre 2025"),
            (11, "Noviembre 2025"),
            (12, "Diciembre 2025"),
        ]
    )
    def test_month_all_months(
        self,
        month,
        expected,
        capsys
    ):

        ReportPrinter.month(
            "Mes",
            pd.Timestamp(
                year=2025,
                month=month,
                day=1
            )
        )

        output = capsys.readouterr().out

        assert expected in output

    # ==================================================
    # year
    # ==================================================

    def test_year_with_value(
        self,
        capsys
    ):

        ReportPrinter.year(
            "Año",
            pd.Timestamp("2025-03-15")
        )

        output = capsys.readouterr().out

        assert "2025" in output

    def test_year_with_nan(
        self,
        capsys
    ):

        ReportPrinter.year(
            "Año",
            pd.NaT
        )

        output = capsys.readouterr().out

        assert "---" in output

    # ==================================================
    # count
    # ==================================================

    def test_count(self, capsys):

        ReportPrinter.count(
            "Registros",
            123.9
        )

        output = capsys.readouterr().out

        assert "123" in output
        assert "123.9" not in output

    def test_count_integer(
        self,
        capsys
    ):

        ReportPrinter.count(
            "Registros",
            19919
        )

        output = capsys.readouterr().out

        assert "19919" in output

    # ==================================================
    # quality
    # ==================================================

    def test_quality(
        self,
        capsys
    ):

        ReportPrinter.quality(
            "Calidad",
            "excelente"
        )

        output = capsys.readouterr().out

        assert "EXCELENTE" in output

    def test_quality_uppercase(
        self,
        capsys
    ):

        ReportPrinter.quality(
            "Calidad",
            "BUENA"
        )

        output = capsys.readouterr().out

        assert "BUENA" in output

    def test_quality_mixed_case(
        self,
        capsys
    ):

        ReportPrinter.quality(
            "Calidad",
            "BuEnA"
        )

        output = capsys.readouterr().out

        assert "BUENA" in output

    # ==================================================
    # title
    # ==================================================

    def test_title(
        self,
        capsys
    ):

        ReportPrinter.title(
            "TEST REPORT"
        )

        output = capsys.readouterr().out

        assert "HELIOS - TEST REPORT" in output
        assert "=" * 55 in output

    def test_title_structure(
        self,
        capsys
    ):

        ReportPrinter.title(
            "TEST"
        )

        output = capsys.readouterr().out
        lines = output.splitlines()

        assert lines[0] == ""
        assert lines[1] == "=" * 55
        assert lines[2] == "HELIOS - TEST"
        assert lines[3] == "=" * 55

    # ==================================================
    # table_header
    # ==================================================

    def test_table_header_default_alignment(
        self,
        capsys
    ):

        ReportPrinter.table_header(
            ["Nombre", "Valor"],
            [10, 10]
        )

        output = capsys.readouterr().out
        lines = output.splitlines()

        assert lines[0] == "Nombre    Valor     "
        assert lines[1] == "-" * 20

    def test_table_header_right_alignment(
        self,
        capsys
    ):

        ReportPrinter.table_header(
            ["Nombre", "Valor"],
            [10, 10],
            ["left", "right"]
        )

        output = capsys.readouterr().out
        lines = output.splitlines()

        assert lines[0] == "Nombre         Valor"
        assert lines[1] == "-" * 20

    def test_table_header_mixed_alignment(
        self,
        capsys
    ):

        ReportPrinter.table_header(
            ["A", "B", "C"],
            [5, 5, 5],
            ["right", "left", "right"]
        )

        output = capsys.readouterr().out
        lines = output.splitlines()

        assert lines[0] == "    AB        C"
        assert lines[1] == "-" * 15

    def test_table_header_custom_widths(
        self,
        capsys
    ):

        ReportPrinter.table_header(
            ["A", "B"],
            [3, 7]
        )

        output = capsys.readouterr().out
        lines = output.splitlines()

        assert lines[0] == "A  B      "
        assert lines[1] == "-" * 10

    def test_table_header_alignment_length(
        self,
        capsys
    ):

        ReportPrinter.table_header(
            ["A", "B", "C"],
            [5, 5, 5],
            ["left", "right", "left"]
        )

        output = capsys.readouterr().out

        assert output.endswith(
            "-" * 15 + "\n"
        )

    # ==================================================
    # table_row
    # ==================================================

    def test_table_row_default_alignment(
        self,
        capsys
    ):

        ReportPrinter.table_row(
            ["A", "B"],
            [5, 5]
        )

        output = capsys.readouterr().out

        assert output == "A    B    \n"

    def test_table_row_right_alignment(
        self,
        capsys
    ):

        ReportPrinter.table_row(
            ["A", "B"],
            [5, 5],
            ["left", "right"]
        )

        output = capsys.readouterr().out

        assert output == "A        B\n"

    def test_table_row_mixed_alignment(
        self,
        capsys
    ):

        ReportPrinter.table_row(
            ["A", "B", "C"],
            [5, 5, 5],
            ["right", "left", "right"]
        )

        output = capsys.readouterr().out

        assert output == "    AB        C\n"

    def test_table_row_custom_widths(
        self,
        capsys
    ):

        ReportPrinter.table_row(
            ["A", "B"],
            [3, 7]
        )

        output = capsys.readouterr().out

        assert output == "A  B      \n"

    # ==================================================
    # blank
    # ==================================================

    def test_blank(
        self,
        capsys
    ):

        ReportPrinter.blank()

        output = capsys.readouterr().out

        assert output == "\n"

    # ==================================================
    # line
    # ==================================================

    def test_line(
        self,
        capsys
    ):

        ReportPrinter.line(
            "Consumo",
            123.45,
            "kWh"
        )

        output = capsys.readouterr().out

        assert "Consumo" in output
        assert "123.45" in output
        assert "kWh" in output

    def test_line_default_unit(
        self,
        capsys
    ):

        ReportPrinter.line(
            "Consumo",
            123.45
        )

        output = capsys.readouterr().out

        assert "Consumo" in output
        assert "123.45" in output
        assert output.endswith(" \n")

    def test_line_label_width(
        self,
        capsys
    ):

        ReportPrinter.line(
            "A",
            1,
            "kWh"
        )

        output = capsys.readouterr().out

        assert output.startswith(
            "A" + "." * 27
        )

    # ==================================================
    # subtitle
    # ==================================================

    def test_subtitle(
        self,
        capsys
    ):

        ReportPrinter.subtitle(
            "ANNUAL COST"
        )

        output = capsys.readouterr().out

        assert "ANNUAL COST" in output
        assert "-" * 55 in output

    def test_subtitle_structure(
        self,
        capsys
    ):

        ReportPrinter.subtitle(
            "SAVINGS"
        )

        output = capsys.readouterr().out
        lines = output.splitlines()

        assert lines[0] == ""
        assert lines[1] == "SAVINGS"
        assert lines[2] == "-" * 55

    # ==================================================
    # value
    # ==================================================

    def test_value_float_with_decimals(
        self,
        capsys
    ):

        ReportPrinter.value(
            "Coste",
            123.4567,
            "€",
            decimals=2
        )

        output = capsys.readouterr().out

        assert "123.46 €" in output

    def test_value_float_without_decimals(
        self,
        capsys
    ):

        ReportPrinter.value(
            "Coste",
            123.4567,
            "€"
        )

        output = capsys.readouterr().out

        assert "123.4567 €" in output

    def test_value_non_float_with_decimals(
        self,
        capsys
    ):

        ReportPrinter.value(
            "Cantidad",
            123,
            "unidades",
            decimals=2
        )

        output = capsys.readouterr().out

        assert "123 unidades" in output
        assert "123.00" not in output

    def test_value_without_unit(
        self,
        capsys
    ):

        ReportPrinter.value(
            "Cantidad",
            123,
            decimals=2
        )

        output = capsys.readouterr().out

        assert "123" in output

    def test_value_float_zero(
        self,
        capsys
    ):

        ReportPrinter.value(
            "Valor",
            0.0,
            "€",
            decimals=2
        )

        output = capsys.readouterr().out

        assert "0.00 €" in output

    def test_value_float_negative(
        self,
        capsys
    ):

        ReportPrinter.value(
            "Valor",
            -123.456,
            "€",
            decimals=2
        )

        output = capsys.readouterr().out

        assert "-123.46 €" in output

    def test_value_integer_without_decimals(
        self,
        capsys
    ):

        ReportPrinter.value(
            "Valor",
            123,
            "kWh"
        )

        output = capsys.readouterr().out

        assert "123 kWh" in output

    # ==================================================
    # constants
    # ==================================================

    def test_constants(self):

        assert ReportPrinter.TOTAL_WIDTH == 55
        assert ReportPrinter.LABEL_WIDTH == 28
        assert ReportPrinter.VALUE_WIDTH == 12