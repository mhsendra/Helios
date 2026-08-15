from unittest.mock import MagicMock

from PySide6.QtWidgets import QApplication

from helios.gui.widgets.validation_page import ValidationPage


class TestValidationPage:

    @classmethod
    def setup_class(cls):

        cls.app = QApplication.instance()

        if cls.app is None:
            cls.app = QApplication([])

    def setup_method(self):

        self.project = MagicMock()

        self.page = ValidationPage(
            self.project
        )

    # ==================================================
    # Estado inicial
    # ==================================================

    def test_page_stores_project(self):

        assert self.page.project is self.project

    def test_labels_start_with_dash(self):

        labels = [
            self.page.quality_label,
            self.page.coverage_label,
            self.page.records_label,
            self.page.valid_hours_label,
            self.page.missing_hours_label,
            self.page.duplicates_label,
        ]

        assert all(
            label.text() == "-"
            for label in labels
        )

    # ==================================================
    # update_data — datos no disponibles
    # ==================================================

    def test_update_data_returns_when_quality_is_missing(self):

        self.project.quality = None

        self.page.update_data()

        assert self.page.quality_label.text() == "-"
        assert self.page.coverage_label.text() == "-"
        assert self.page.records_label.text() == "-"
        assert self.page.valid_hours_label.text() == "-"
        assert self.page.missing_hours_label.text() == "-"
        assert self.page.duplicates_label.text() == "-"

    # ==================================================
    # update_data — calidad excelente
    # ==================================================

    def test_update_data_sets_quality_data(self):

        self.project.quality = {
            "rating": "EXCELENTE",
            "coverage": 99.43,
            "total_hours": 19920,
            "valid_hours": 19807,
            "missing_hours": 113,
            "duplicates": 0,
        }

        self.page.update_data()

        assert (
            self.page.quality_label.text()
            == "🟢 EXCELENTE"
        )

        assert (
            self.page.coverage_label.text()
            == "99.43 %"
        )

        assert (
            self.page.records_label.text()
            == "19.920"
        )

        assert (
            self.page.valid_hours_label.text()
            == "19.807"
        )

        assert (
            self.page.missing_hours_label.text()
            == "113"
        )

        assert (
            self.page.duplicates_label.text()
            == "0"
        )

    # ==================================================
    # Calidad — iconos
    # ==================================================

    def test_quality_rating_very_good(self):

        self.project.quality = {
            "rating": "MUY BUENA",
            "coverage": 98.50,
            "total_hours": 10000,
            "valid_hours": 9850,
            "missing_hours": 150,
            "duplicates": 0,
        }

        self.page.update_data()

        assert (
            self.page.quality_label.text()
            == "🟡 MUY BUENA"
        )

    def test_quality_rating_good(self):

        self.project.quality = {
            "rating": "BUENA",
            "coverage": 95.00,
            "total_hours": 10000,
            "valid_hours": 9500,
            "missing_hours": 500,
            "duplicates": 0,
        }

        self.page.update_data()

        assert (
            self.page.quality_label.text()
            == "🟠 BUENA"
        )

    def test_quality_rating_review(self):

        self.project.quality = {
            "rating": "REVISAR",
            "coverage": 80.00,
            "total_hours": 10000,
            "valid_hours": 8000,
            "missing_hours": 2000,
            "duplicates": 10,
        }

        self.page.update_data()

        assert (
            self.page.quality_label.text()
            == "🔴 REVISAR"
        )

    # ==================================================
    # Formato de números
    # ==================================================

    def test_update_data_formats_large_numbers(self):

        self.project.quality = {
            "rating": "EXCELENTE",
            "coverage": 99.99,
            "total_hours": 1234567,
            "valid_hours": 1234000,
            "missing_hours": 567,
            "duplicates": 12,
        }

        self.page.update_data()

        assert (
            self.page.records_label.text()
            == "1.234.567"
        )

        assert (
            self.page.valid_hours_label.text()
            == "1.234.000"
        )

        assert (
            self.page.missing_hours_label.text()
            == "567"
        )

        assert (
            self.page.duplicates_label.text()
            == "12"
        )

    # ==================================================
    # Actualización de estado
    # ==================================================

    def test_update_data_replaces_previous_values(self):

        self.project.quality = {
            "rating": "EXCELENTE",
            "coverage": 99.43,
            "total_hours": 19920,
            "valid_hours": 19807,
            "missing_hours": 113,
            "duplicates": 0,
        }

        self.page.update_data()

        assert (
            self.page.quality_label.text()
            == "🟢 EXCELENTE"
        )

        self.project.quality = {
            "rating": "REVISAR",
            "coverage": 80.00,
            "total_hours": 10000,
            "valid_hours": 8000,
            "missing_hours": 2000,
            "duplicates": 5,
        }

        self.page.update_data()

        assert (
            self.page.quality_label.text()
            == "🔴 REVISAR"
        )

        assert (
            self.page.coverage_label.text()
            == "80.00 %"
        )

        assert (
            self.page.records_label.text()
            == "10.000"
        )

        assert (
            self.page.valid_hours_label.text()
            == "8.000"
        )

        assert (
            self.page.missing_hours_label.text()
            == "2000"
        )

        assert (
            self.page.duplicates_label.text()
            == "5"
        )