from unittest.mock import MagicMock

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
)

from helios.gui.widgets.home_page import HomePage


class TestHomePage:

    @classmethod
    def setup_class(cls):

        cls.app = QApplication.instance()

        if cls.app is None:
            cls.app = QApplication([])

    def setup_method(self):

        self.project = MagicMock()

        self.page = HomePage(
            self.project
        )

    # ==================================================
    # Estado inicial
    # ==================================================

    def test_page_stores_project(self):

        assert self.page.project is self.project

    # ==================================================
    # Contenido
    # ==================================================

    def test_page_contains_title(self):

        labels = self.page.findChildren(QLabel)

        assert any(
            label.text() == "Página principal"
            for label in labels
        )