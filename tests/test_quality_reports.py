import pytest

from unittest.mock import patch

from helios.reports.quality import QualityReports


class TestQualityReports:

    def setup_method(self):

        self.report = QualityReports()

    @patch(
        "helios.reports.quality.ReportPrinter"
    )
    def test_quality(self, printer):

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


class TestQualityReportsGap:

    def setup_method(self):

        self.report = QualityReports()

    def test_gap_without_gaps(self, capsys):

        result = self.report.gap(None)

        assert result is None

        captured = capsys.readouterr()

        assert (
            captured.out
            == "No se han detectado huecos.\n"
        )


class TestQualityReportsDuplicates:

    def setup_method(self):

        self.report = QualityReports()

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

        assert (
            printer.blank.call_count
            == 1
        )


    @patch(
        "helios.reports.quality.ReportPrinter"
    )
    def test_duplicates_with_duplicates(
        self,
        printer
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

        assert (
            printer.count.call_args
            == (
                ("Duplicados encontrados", 2),
                {}
            )
        )

        assert (
            printer.blank.call_count
            == 2
        )