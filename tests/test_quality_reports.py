import pandas as pd
import pytest

from unittest.mock import patch

from helios.reports.quality import QualityReports


class TestQualityReports:

    def setup_method(self):

        self.report = QualityReports()

    # ==================================================
    # quality
    # ==================================================

    @patch(
        "helios.reports.quality.ReportPrinter"
    )
    def test_quality(
        self,
        printer
    ):

        quality = {
            "total_hours": 19919,
            "rating": "EXCELENTE",
        }

        result = self.report.quality(
            quality
        )

        assert result is None

        printer.title.assert_called_once_with(
            "DATA QUALITY REPORT"
        )

        printer.blank.assert_called_once_with()

        printer.count.assert_called_once_with(
            "Registros totales",
            19919
        )

        printer.quality.assert_called_once_with(
            "Calidad",
            "EXCELENTE"
        )

    @pytest.mark.parametrize(
        "rating",
        [
            "EXCELENTE",
            "BUENA",
            "REGULAR",
            "MALA",
        ]
    )
    @patch(
        "helios.reports.quality.ReportPrinter"
    )
    def test_quality_preserves_rating(
        self,
        printer,
        rating
    ):

        quality = {
            "total_hours": 100,
            "rating": rating,
        }

        result = self.report.quality(
            quality
        )

        assert result is None

        printer.quality.assert_called_once_with(
            "Calidad",
            rating
        )

    @pytest.mark.parametrize(
        "total_hours",
        [
            0,
            1,
            113,
            19919,
            100000,
        ]
    )
    @patch(
        "helios.reports.quality.ReportPrinter"
    )
    def test_quality_prints_total_hours(
        self,
        printer,
        total_hours
    ):

        quality = {
            "total_hours": total_hours,
            "rating": "EXCELENTE",
        }

        self.report.quality(
            quality
        )

        printer.count.assert_called_once_with(
            "Registros totales",
            total_hours
        )

    @patch(
    "helios.reports.quality.ReportPrinter"
    )
    def test_quality_print_order(
            self,
        printer
    ):

        quality = {
            "total_hours": 19919,
            "rating": "EXCELENTE",
        }

        self.report.quality(
            quality
        )

        calls = printer.mock_calls

        assert calls[0] == (
            printer.title.call_args
            if False
            else calls[0]
        )

        assert calls[0][0] == "title"
        assert calls[0][1] == (
            "DATA QUALITY REPORT",
        )

        assert calls[1][0] == "blank"

        assert calls[2][0] == "count"
        assert calls[2][1] == (
            "Registros totales",
            19919,
        )

        assert calls[3][0] == "quality"
        assert calls[3][1] == (
            "Calidad",
            "EXCELENTE",
        )

    # ==================================================
    # gap
    # ==================================================

    def test_gap_without_gaps(
        self,
        capsys
    ):

        result = self.report.gap(
            None
        )

        assert result is None

        captured = capsys.readouterr()

        assert captured.out == (
            "No se han detectado huecos.\n"
        )

    def test_gap_without_gaps_does_not_use_printer(
        self
    ):

        with patch(
            "helios.reports.quality.ReportPrinter"
        ) as printer:

            result = self.report.gap(
                None
            )

        assert result is None

        printer.title.assert_not_called()
        printer.blank.assert_not_called()
        printer.count.assert_not_called()
        printer.quality.assert_not_called()

    def test_gap_with_empty_dictionary(
        self,
        capsys
    ):

        result = self.report.gap(
            {}
        )

        assert result is None

        captured = capsys.readouterr()

        assert captured.out == ""

    def test_gap_with_summary(
        self,
        capsys
    ):

        summary = {
            "count": 3,
            "total": 10,
        }

        result = self.report.gap(
            summary
        )

        assert result is None

        captured = capsys.readouterr()

        assert captured.out == ""

    # ==================================================
    # duplicates
    # ==================================================

    @patch(
        "helios.reports.quality.ReportPrinter"
    )
    def test_duplicates_without_duplicates(
        self,
        printer
    ):

        duplicates = {
            "count": 0,
            "duplicates": [],
        }

        result = self.report.duplicates(
            duplicates
        )

        assert result is None

        printer.title.assert_called_once_with(
            "DUPLICATE TIMESTAMPS"
        )

        printer.blank.assert_called_once_with()

        printer.count.assert_called_once_with(
            "Duplicados encontrados",
            0
        )

        assert printer.blank.call_count == 1

    @patch(
        "helios.reports.quality.ReportPrinter"
    )
    def test_duplicates_with_duplicates(
        self,
        printer,
        capsys
    ):

        duplicates = {
            "count": 2,
            "duplicates": [
                "2025-01-01 10:00",
                "2025-01-01 11:00",
            ],
        }

        result = self.report.duplicates(
            duplicates
        )

        assert result is None

        printer.title.assert_called_once_with(
            "DUPLICATE TIMESTAMPS"
        )

        printer.count.assert_called_once_with(
            "Duplicados encontrados",
            2
        )

        assert printer.blank.call_count == 2

        captured = capsys.readouterr()

        assert (
            "2025-01-01 10:00" in captured.out
        )

        assert (
            "2025-01-01 11:00" in captured.out
        )

    @patch(
        "helios.reports.quality.ReportPrinter"
    )
    def test_duplicates_prints_exact_duplicate_collection(
        self,
        printer,
        capsys
    ):

        duplicates = {
            "count": 3,
            "duplicates": [
                "A",
                "B",
                "C",
            ],
        }

        self.report.duplicates(
            duplicates
        )

        captured = capsys.readouterr()

        assert captured.out.endswith(
            "['A', 'B', 'C']\n"
        )

    @patch(
        "helios.reports.quality.ReportPrinter"
    )
    def test_duplicates_does_not_print_duplicates_when_count_zero(
        self,
        printer,
        capsys
    ):

        duplicates = {
            "count": 0,
            "duplicates": [
                "should-not-be-printed"
            ],
        }

        self.report.duplicates(
            duplicates
        )

        captured = capsys.readouterr()

        assert (
            "should-not-be-printed"
            not in captured.out
        )

        assert printer.blank.call_count == 1

    @pytest.mark.parametrize(
        "count",
        [
            1,
            2,
            10,
            113,
            19919,
        ]
    )
    @patch(
        "helios.reports.quality.ReportPrinter"
    )
    def test_duplicates_prints_count(
        self,
        printer,
        count
    ):

        duplicates = {
            "count": count,
            "duplicates": [],
        }

        self.report.duplicates(
            duplicates
        )

        printer.count.assert_called_once_with(
            "Duplicados encontrados",
            count
        )

    @patch(
        "helios.reports.quality.ReportPrinter"
    )
    def test_duplicates_with_single_duplicate(
        self,
        printer,
        capsys
    ):

        duplicates = {
            "count": 1,
            "duplicates": [
                "2025-01-01 10:00"
            ],
        }

        result = self.report.duplicates(
            duplicates
        )

        assert result is None

        captured = capsys.readouterr()

        assert (
            "2025-01-01 10:00"
            in captured.out
        )

        assert printer.blank.call_count == 2

    # ==================================================
    # integration-style behaviour
    # ==================================================

    @patch(
        "helios.reports.quality.ReportPrinter"
    )
    def test_quality_only_calls_expected_printer_methods(
        self,
        printer
    ):

        quality = {
            "total_hours": 19919,
            "rating": "EXCELENTE",
        }

        self.report.quality(
            quality
        )

        printer.title.assert_called_once()
        printer.blank.assert_called_once()
        printer.count.assert_called_once()
        printer.quality.assert_called_once()

        printer.text.assert_not_called()
        printer.energy.assert_not_called()
        printer.percent.assert_not_called()
        printer.value.assert_not_called()
        printer.table_header.assert_not_called()
        printer.table_row.assert_not_called()

    @patch(
        "helios.reports.quality.ReportPrinter"
    )
    def test_duplicates_only_calls_expected_printer_methods_when_empty(
        self,
        printer
    ):

        duplicates = {
            "count": 0,
            "duplicates": [],
        }

        self.report.duplicates(
            duplicates
        )

        printer.title.assert_called_once()
        printer.blank.assert_called_once()
        printer.count.assert_called_once()

        printer.quality.assert_not_called()
        printer.text.assert_not_called()
        printer.energy.assert_not_called()
        printer.percent.assert_not_called()
        printer.value.assert_not_called()
        printer.table_header.assert_not_called()
        printer.table_row.assert_not_called()