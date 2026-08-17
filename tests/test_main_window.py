from unittest.mock import MagicMock

from PySide6.QtWidgets import QApplication

from helios.gui.main_window import MainWindow
from helios.core.economics_configuration import EconomicsConfiguration


class TestMainWindow:

    @classmethod
    def setup_class(cls):

        cls.app = QApplication.instance()

        if cls.app is None:
            cls.app = QApplication([])

    def setup_method(self):

        self.economics_configuration = EconomicsConfiguration(
            installation_cost=10000
        )

        self.window = MainWindow(
            self.economics_configuration
        )

    # ==================================================
    # Inicialización
    # ==================================================

    def test_main_window_creates_project(self):

        assert self.window.project is not None

    def test_main_window_configuration(self):

        assert self.window.windowTitle() == "HELIOS"

        assert self.window.width() == 1400
        assert self.window.height() == 900

    def test_main_window_creates_navigation(self):

        assert self.window.navigation is not None
        assert self.window.pages is not None

    # ==================================================
    # Páginas
    # ==================================================

    def test_main_window_creates_all_pages(self):

        assert self.window.home_page is not None
        assert self.window.load_page is not None
        assert self.window.validation_page is not None
        assert self.window.statistics_page is not None
        assert self.window.profiles_page is not None
        assert self.window.comparisons_page is not None
        assert self.window.indicators_page is not None
        assert self.window.solar_page is not None

    def test_all_pages_use_same_project(self):

        pages = [
            self.window.home_page,
            self.window.load_page,
            self.window.validation_page,
            self.window.statistics_page,
            self.window.profiles_page,
            self.window.comparisons_page,
            self.window.indicators_page,
            self.window.solar_page,
        ]

        for page in pages:
            assert page.project is self.window.project

    def test_all_pages_are_added_to_stack(self):

        assert self.window.pages.count() == 11

        for page in [
            self.window.home_page,
            self.window.load_page,
            self.window.validation_page,
            self.window.statistics_page,
            self.window.profiles_page,
            self.window.comparisons_page,
            self.window.indicators_page,
            self.window.solar_page,
        ]:
            assert self.window.pages.indexOf(page) != -1

        # ==================================================
    # Navegación
    # ==================================================

    def test_navigation_has_expected_top_level_items(self):

        assert self.window.navigation.topLevelItemCount() == 4

        assert (
            self.window.navigation.topLevelItem(0).text(0)
            == "Inicio"
        )

        assert (
            self.window.navigation.topLevelItem(1).text(0)
            == "Proyecto"
        )

        assert (
            self.window.navigation.topLevelItem(2).text(0)
            == "Análisis"
        )

        assert (
            self.window.navigation.topLevelItem(3).text(0)
            == "Resultados"
        )

    def test_navigation_has_expected_project_items(self):

        project_item = self.window.project_item

        children = [
            project_item.child(i).text(0)
            for i in range(project_item.childCount())
        ]

        assert children == [
            "Cargar datos",
            "Configuración solar",
        ]

    def test_navigation_has_expected_analysis_items(self):

        analysis_item = self.window.analysis_item

        children = [
            analysis_item.child(i).text(0)
            for i in range(analysis_item.childCount())
        ]

        assert children == [
            "Validación",
            "Estadísticas",
            "Perfiles",
            "Comparativas",
            "Indicadores",
            "Tarifas",
            "Solar",
            "Economía"
        ]

        # ==================================================
    # Asociación navegación → páginas
    # ==================================================

    def test_page_map_contains_expected_pages(self):

        assert self.window.page_map == {
            "Inicio": self.window.home_page,
            "Cargar datos": self.window.load_page,
            "Validación": self.window.validation_page,
            "Estadísticas": self.window.statistics_page,
            "Perfiles": self.window.profiles_page,
            "Comparativas": self.window.comparisons_page,
            "Indicadores": self.window.indicators_page,
            "Tarifas": self.window.tariffs_page,
            "Gráficas": self.window.graphics_page,
            "Solar": self.window.solar_page,
            "Economía": self.window.economics_page
        }

    # ==================================================
    # Estado inicial
    # ==================================================

    def test_analysis_items_are_disabled_initially(self):

        items = [
            self.window.validation_item,
            self.window.statistics_item,
            self.window.profiles_item,
            self.window.comparisons_item,
            self.window.indicators_item,
            self.window.tariffs_item,
            self.window.solar_item,
            self.window.reports_item,
            self.window.charts_item,
        ]

        assert all(
            item.isDisabled()
            for item in items
        )

    def test_project_navigation_items_remain_enabled_initially(self):

        assert not self.window.home_item.isDisabled()
        assert not self.window.load_item.isDisabled()

        # ==================================================
    # Estado del proyecto
    # ==================================================

    def test_set_project_loaded_enables_analysis_items(self):

        self.window.set_project_loaded(True)

        items = [
            self.window.validation_item,
            self.window.statistics_item,
            self.window.profiles_item,
            self.window.comparisons_item,
            self.window.indicators_item,
            self.window.tariffs_item,
            self.window.solar_item,
            self.window.reports_item,
            self.window.charts_item,
        ]

        assert all(
            not item.isDisabled()
            for item in items
        )

    def test_set_project_loaded_disables_analysis_items(self):

        self.window.set_project_loaded(True)

        self.window.set_project_loaded(False)

        items = [
            self.window.validation_item,
            self.window.statistics_item,
            self.window.profiles_item,
            self.window.comparisons_item,
            self.window.indicators_item,
            self.window.tariffs_item,
            self.window.solar_item,
            self.window.reports_item,
            self.window.charts_item,
        ]

        assert all(
            item.isDisabled()
            for item in items
        )

        # ==================================================
    # Cambio de página
    # ==================================================

    def test_change_page_changes_current_page(self):

        self.window.set_project_loaded(True)

        self.window.change_page(
            self.window.statistics_item
        )

        assert (
            self.window.pages.currentWidget()
            is self.window.statistics_page
        )

    def test_change_page_ignores_disabled_item(self):

        current_page = self.window.pages.currentWidget()

        self.window.change_page(
            self.window.statistics_item
        )

        assert (
            self.window.pages.currentWidget()
            is current_page
        )

    def test_change_page_ignores_item_without_page(self):

        current_page = self.window.pages.currentWidget()

        self.window.change_page(
            self.window.configuration_item
        )

        assert (
            self.window.pages.currentWidget()
            is current_page
        )

        # ==================================================
    # Actualización de páginas
    # ==================================================

    def test_update_project_pages_updates_all_analysis_pages(self):

        self.window.validation_page.update_data = MagicMock()
        self.window.statistics_page.update_data = MagicMock()
        self.window.profiles_page.update_data = MagicMock()
        self.window.comparisons_page.update_data = MagicMock()
        self.window.indicators_page.update_data = MagicMock()

        self.window.update_project_pages()

        self.window.validation_page.update_data.assert_called_once()
        self.window.statistics_page.update_data.assert_called_once()
        self.window.profiles_page.update_data.assert_called_once()
        self.window.comparisons_page.update_data.assert_called_once()
        self.window.indicators_page.update_data.assert_called_once()