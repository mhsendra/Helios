from unittest.mock import MagicMock

from PySide6.QtWidgets import QApplication, QTreeWidgetItem

from helios.gui.main_window import MainWindow
from helios.gui.navigation_state import NAVIGATION_SECTIONS
from helios.core.economics_configuration import EconomicsConfiguration
from helios.gui.main_window import MainWindow


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

    def test_results_items_are_mapped_to_correct_pages(self):

        assert (
            self.window.page_map["Gráficas"]
            is self.window.graphics_page
        )

        assert (
            self.window.page_map["Informes"]
            is self.window.reports_page
        )

    # ==================================================
    # Páginas
    # ==================================================

    def test_main_window_creates_all_pages(self):

        assert self.window.load_page is not None
        assert self.window.solar_config_page is not None
        assert self.window.validation_page is not None
        assert self.window.statistics_page is not None
        assert self.window.profiles_page is not None
        assert self.window.comparisons_page is not None
        assert self.window.indicators_page is not None
        assert self.window.tariffs_page is not None
        assert self.window.graphics_page is not None
        assert self.window.reports_page is not None
        assert self.window.solar_page is not None
        assert self.window.economics_page is not None


    def test_all_pages_use_same_project(self):

        pages = [
            self.window.load_page,
            self.window.solar_config_page,
            self.window.validation_page,
            self.window.statistics_page,
            self.window.profiles_page,
            self.window.comparisons_page,
            self.window.indicators_page,
            self.window.tariffs_page,
            self.window.graphics_page,
            self.window.reports_page,
            self.window.solar_page,
            self.window.economics_page,
        ]

        for page in pages:
            assert page.project is self.window.project

    def test_all_pages_are_added_to_stack(self):

        assert self.window.pages.count() == 13

        pages = [
            self.window.load_page,
            self.window.solar_config_page,
            self.window.validation_page,
            self.window.statistics_page,
            self.window.profiles_page,
            self.window.comparisons_page,
            self.window.indicators_page,
            self.window.tariffs_page,
            self.window.graphics_page,
            self.window.reports_page,
            self.window.solar_page,
            self.window.economics_page,
        ]

        for page in pages:
            assert self.window.pages.indexOf(page) != -1

    # ==================================================
    # Navegación
    # ==================================================

    def test_navigation_has_expected_top_level_items(self):

        assert self.window.navigation.topLevelItemCount() == 3

        assert (
            self.window.navigation.topLevelItem(0).text(0)
            == "Proyecto"
        )

        assert (
            self.window.navigation.topLevelItem(1).text(0)
            == "Análisis"
        )

        assert (
            self.window.navigation.topLevelItem(2).text(0)
            == "Resultados"
        )

    def test_navigation_has_expected_project_items(self):

        project_item = self.window.project_item

        children = [
            project_item.child(i).text(0)
            for i in range(project_item.childCount())
        ]

        assert children == [
            "Configuración solar",
            "Cargar datos",
            "Optimización solar",
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

    def test_navigation_has_expected_results_items(self):

        results_item = self.window.results_item

        children = [
            results_item.child(i).text(0)
            for i in range(results_item.childCount())
        ]

        assert children == [
            "Informes",
            "Gráficas"
        ]

    # ==================================================
    # Asociación navegación → páginas
    # ==================================================

    def test_page_map_contains_expected_pages(self):

        assert self.window.page_map == {
            "Cargar datos": self.window.load_page,
            "Configuración solar": self.window.solar_config_page,
            "Optimización solar": self.window.solar_optimization_page,
            "Validación": self.window.validation_page,
            "Estadísticas": self.window.statistics_page,
            "Perfiles": self.window.profiles_page,
            "Comparativas": self.window.comparisons_page,
            "Indicadores": self.window.indicators_page,
            "Tarifas": self.window.tariffs_page,
            "Informes": self.window.reports_page,
            "Gráficas": self.window.graphics_page,
            "Solar": self.window.solar_page,
            "Economía": self.window.economics_page,
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

        assert self.window.load_item.isDisabled()

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
            self.window.charts_item,
        ]

        assert all(
            not item.isDisabled()
            for item in items
        )

        assert not self.window.solar_optimization_item.isDisabled()
        assert self.window.solar_item.isDisabled()
        assert self.window.reports_item.isDisabled()
        assert self.window.economics_item.isDisabled()

    def test_set_project_loaded_disables_analysis_items(self):

        self.window.set_solar_configured(True)

        assert not self.window.load_item.isDisabled()

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

        assert not self.window.load_item.isDisabled()

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

    def test_change_page_changes_to_solar_configuration_page_when_project_is_not_loaded(
        self,
    ):

        self.window.change_page(
            self.window.configuration_item
        )

        assert (
            self.window.pages.currentWidget()
            is self.window.solar_config_page
        )
        
    def test_change_page_does_not_change_to_economics_page_after_solar_optimization(
        self,
    ):

        self.window.set_project_loaded(True)

        self.window.set_solar_optimized(True)

        self.window.change_page(
            self.window.economics_item
        )

        assert (
            self.window.pages.currentWidget()
            is self.window.solar_config_page
        )

    def test_solar_configuration_page_is_enabled_when_project_is_not_loaded(
        self,
    ):

        assert not self.window.configuration_item.isDisabled()

    def test_navigate_to_enabled_page(self):
        """Permite navegar directamente a una página habilitada."""

        self.window.navigate_to("Configuración solar")

        assert (
            self.window.pages.currentWidget()
            is self.window.solar_config_page
        )


    def test_navigate_to_disabled_page(self):
        """Impide navegar directamente a una página bloqueada."""

        initial_page = self.window.pages.currentWidget()

        self.window.navigate_to("Economía")

        assert self.window.pages.currentWidget() is initial_page


    def test_navigate_to_unknown_page(self):
        """Ignora identificadores de página desconocidos."""

        initial_page = self.window.pages.currentWidget()

        self.window.navigate_to("Página inexistente")

        assert self.window.pages.currentWidget() is initial_page
    
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

    def test_economics_is_disabled_when_project_is_loaded_without_solar(self):

        self.window.set_project_loaded(True)

        assert self.window.economics_item.isDisabled()

    def test_economics_remains_disabled_after_solar_optimization(self):

        self.window.set_project_loaded(True)

        self.window.set_solar_optimized(True)

        assert self.window.economics_item.isDisabled()


    def test_economics_remains_disabled_when_solar_optimization_is_reset(self):

        self.window.set_project_loaded(True)

        self.window.set_solar_optimized(True)

        assert self.window.economics_item.isDisabled()

        self.window.set_solar_optimized(False)

        assert self.window.economics_item.isDisabled()

    def test_solar_pages_are_separate(self):

        assert (
            self.window.solar_config_page
            is not self.window.solar_page
        )

    def test_solar_pages_use_same_project(self):

        assert (
            self.window.solar_config_page.project
            is self.window.project
        )

        assert (
            self.window.solar_page.project
            is self.window.project
        )

    def test_change_page_changes_to_solar_configuration_page_when_project_is_loaded(
        self,
    ):

        self.window.set_project_loaded(True)

        self.window.change_page(
            self.window.configuration_item
        )

        assert (
            self.window.pages.currentWidget()
            is self.window.solar_config_page
        )

    def test_change_page_ignores_item_without_mapped_page(
        self,
    ):

        item = QTreeWidgetItem(
            ["Página inexistente"]
        )

        self.window.change_page(item)

        assert (
            self.window.pages.currentWidget()
            is self.window.solar_config_page
        )

    def test_set_solar_configured_enables_load_data(self):
        self.window.set_solar_configured(True)

        assert not self.window.load_item.isDisabled()


    def test_set_solar_configured_disables_load_data(self):
        self.window.set_solar_configured(False)

        assert self.window.load_item.isDisabled()

    def test_solar_report_is_enabled_after_economic_calculation(self):

        self.window.set_project_loaded(True)
        self.window.set_solar_optimized(True)

        # La optimización por sí sola no habilita Informes.
        assert not (
            self.window.reports_page
            .generate_solar_pdf_button
            .isEnabled()
        )

        self.window.set_solar_production_calculated(True)

        # La producción tampoco es suficiente.
        assert not (
            self.window.reports_page
            .generate_solar_pdf_button
            .isEnabled()
        )

        self.window.set_economics_calculated(True)

        assert self.window.economics_calculated is True
        assert (
            self.window.reports_page
            .generate_solar_pdf_button
            .isEnabled()
        )


    def test_solar_report_is_disabled_when_solar_results_are_reset(self):

        self.window.set_project_loaded(True)
        self.window.set_solar_optimized(True)
        self.window.set_solar_production_calculated(True)
        self.window.set_economics_calculated(True)

        assert (
            self.window.reports_page
            .generate_solar_pdf_button
            .isEnabled()
        )

        self.window.set_solar_optimized(False)

        assert self.window.solar_optimized is False
        assert self.window.solar_production_calculated is False
        assert self.window.economics_calculated is False
        assert not (
            self.window.reports_page
            .generate_solar_pdf_button
            .isEnabled()
        )


    def test_solar_page_reset_invalidates_main_window_solar_state(self):

        self.window.set_project_loaded(True)
        self.window.set_solar_optimized(True)
        self.window.set_solar_production_calculated(True)
        self.window.set_economics_calculated(True)

        assert self.window.solar_optimized is True
        assert self.window.solar_production_calculated is True
        assert self.window.economics_calculated is True
        assert not self.window.economics_item.isDisabled()
        assert self.window.reports_page.generate_solar_pdf_button.isEnabled()

        self.window.solar_page.reset_results()

        assert self.window.solar_optimized is False
        assert self.window.solar_production_calculated is False
        assert self.window.economics_calculated is False
        assert self.window.economics_item.isDisabled()
        assert not self.window.reports_page.generate_solar_pdf_button.isEnabled()

    def test_initial_navigation_state_allows_only_solar_configuration(self):

        assert not self.window.configuration_item.isDisabled()
        assert self.window.load_item.isDisabled()
        assert self.window.solar_optimization_item.isDisabled()

    def test_solar_configuration_enables_load_data_but_not_optimization(
        self,
    ):

        self.window.set_solar_configured(True)

        assert not self.window.configuration_item.isDisabled()
        assert not self.window.load_item.isDisabled()
        assert self.window.solar_optimization_item.isDisabled()

    def test_project_loaded_enables_solar_optimization(self):

        self.window.set_solar_configured(True)
        self.window.set_project_loaded(True)

        assert not self.window.configuration_item.isDisabled()
        assert not self.window.load_item.isDisabled()
        assert not self.window.solar_optimization_item.isDisabled()

    def test_project_unloaded_disables_solar_optimization(self):

        self.window.set_solar_configured(True)
        self.window.set_project_loaded(True)

        assert not self.window.solar_optimization_item.isDisabled()

        self.window.set_project_loaded(False)

        assert not self.window.load_item.isDisabled()
        assert self.window.solar_optimization_item.isDisabled()

    def test_navigation_tree_matches_permissions_after_state_changes(self):
        items = (
            self.window.configuration_item,
            self.window.load_item,
            self.window.solar_optimization_item,
            self.window.validation_item,
            self.window.statistics_item,
            self.window.profiles_item,
            self.window.comparisons_item,
            self.window.indicators_item,
            self.window.tariffs_item,
            self.window.solar_item,
            self.window.economics_item,
            self.window.reports_item,
            self.window.charts_item,
        )

        def assert_navigation_synced():
            for item in items:
                page_id = item.text(0)
                expected_enabled = self.window.is_page_enabled(page_id)

                assert item.isDisabled() is (not expected_enabled), page_id

        assert_navigation_synced()

        self.window.set_solar_configured(True)
        assert_navigation_synced()

        self.window.set_project_loaded(True)
        assert_navigation_synced()

        self.window.set_solar_optimized(True)
        assert_navigation_synced()

        self.window.set_solar_production_calculated(True)
        assert_navigation_synced()

        self.window.set_economics_calculated(True)
        assert_navigation_synced()

        self.window.set_solar_optimized(False)
        assert_navigation_synced()

        self.window.set_project_loaded(False)
        assert_navigation_synced()

    def test_android_layout_initialization(self, monkeypatch):
        """Comprueba la estructura inicial de la interfaz Android."""

        monkeypatch.setattr(
            "helios.gui.main_window.is_android",
            lambda: True,
        )

        window = MainWindow(self.economics_configuration)

        try:
            assert window.centralWidget() is not None
            assert window.android_navigation_container is not None
            assert window.android_navigation_layout is not None

            assert window.pages.count() == 13
            assert window.navigation.isHidden()
            assert window.pages.currentWidget() is window.solar_config_page

            # Cabecera Android.
            assert window.android_header is not None
            assert window.android_title.objectName() == "android_menu_logo"
            assert window.android_title.text() == ""

            logo = window.android_title.pixmap()
            assert logo is not None
            assert not logo.isNull()
            assert logo.width() > 0
            assert logo.height() > 0

            # Selector de secciones.
            selector = window.android_section_selector

            assert selector.count() == 2
            assert selector.itemText(0) == "Entrada de datos"
            assert selector.itemText(1) == "Resultados"
            assert selector.currentIndex() == 0

            # El encabezado permanece fuera del área desplazable.
            assert window.android_header.parent() is (
                window.android_navigation_container
            )

            # La lista de páginas pertenece al área desplazable.
            assert window.android_navigation_scroll.widget() is (
                window.android_navigation_content
            )

            # Todos los botones de navegación Android.

            expected_pages = tuple(
                page_id
                for section_pages in NAVIGATION_SECTIONS.values()
                for page_id in section_pages
            )

            assert len(expected_pages) == 13
            assert tuple(window.android_navigation_buttons) == expected_pages

            for page_id in expected_pages:
                button = window.android_navigation_buttons[page_id]

                assert button.text() == page_id
                assert button.parent() is window.android_navigation_content

                # Inicialmente solo se muestra Entrada de datos.
                if page_id in NAVIGATION_SECTIONS["Entrada de datos"]:
                    assert not button.isHidden()
                else:
                    assert button.isHidden()

        finally:
            window.close()

    def test_android_navigation_buttons(self, monkeypatch):
        """Comprueba la navegación Android y sus permisos."""

        monkeypatch.setattr(
            "helios.gui.main_window.is_android",
            lambda: True,
        )

        window = MainWindow(self.economics_configuration)

        try:
            buttons = window.android_navigation_buttons

            # 1. Estado inicial.
            assert window.pages.currentWidget() is window.solar_config_page

            assert buttons["Configuración solar"].isEnabled()
            assert not buttons["Cargar datos"].isEnabled()
            assert not buttons["Optimización solar"].isEnabled()

            # Una página deshabilitada no permite navegar.
            buttons["Cargar datos"].click()

            assert window.pages.currentWidget() is window.solar_config_page

            # 2. Configuración solar completada.
            window.set_solar_configured(True)

            assert buttons["Cargar datos"].isEnabled()
            assert not buttons["Optimización solar"].isEnabled()

            buttons["Cargar datos"].click()

            assert window.pages.currentWidget() is window.load_page

            # 3. Proyecto cargado.
            window.set_project_loaded(True)

            assert buttons["Optimización solar"].isEnabled()

            buttons["Optimización solar"].click()

            assert window.pages.currentWidget() is window.solar_optimization_page

            # 4. Regreso a la configuración solar.
            buttons["Configuración solar"].click()

            assert window.pages.currentWidget() is window.solar_config_page

        finally:
            window.close()

    def test_android_section_selector(self, monkeypatch):
        """Comprueba el cambio entre secciones Android."""

        monkeypatch.setattr(
            "helios.gui.main_window.is_android",
            lambda: True,
        )

        window = MainWindow(self.economics_configuration)

        try:
            selector = window.android_section_selector
            buttons = window.android_navigation_buttons

            input_pages = (
                "Configuración solar",
                "Cargar datos",
                "Optimización solar",
            )

            result_pages = (
                "Validación",
                "Estadísticas",
                "Perfiles",
                "Comparativas",
                "Indicadores",
                "Tarifas",
                "Solar",
                "Economía",
                "Informes",
                "Gráficas",
            )

            initial_page = window.pages.currentWidget()

            # Cambiamos a Resultados.
            selector.setCurrentText("Resultados")

            for page_id in input_pages:
                assert buttons[page_id].isHidden()

            for page_id in result_pages:
                assert not buttons[page_id].isHidden()

            # El cambio de sección no modifica la página.
            assert window.pages.currentWidget() is initial_page

            # Regresamos a Entrada de datos.
            selector.setCurrentText("Entrada de datos")

            for page_id in input_pages:
                assert not buttons[page_id].isHidden()

            for page_id in result_pages:
                assert buttons[page_id].isHidden()

            assert window.pages.currentWidget() is initial_page

        finally:
            window.close()

    def test_android_section_sync_with_navigation(self, monkeypatch):
        """Sincroniza la sección Android con la página seleccionada."""

        monkeypatch.setattr(
            "helios.gui.main_window.is_android",
            lambda: True,
        )

        window = MainWindow(self.economics_configuration)

        try:
            selector = window.android_section_selector

            # Estado inicial.
            assert selector.currentText() == "Entrada de datos"
            assert window.pages.currentWidget() is window.solar_config_page

            # Habilitamos el acceso a las páginas de resultados.
            window.set_solar_configured(True)
            window.set_project_loaded(True)

            # Navegar a Resultados actualiza el selector.
            window.navigate_to("Estadísticas")

            assert window.pages.currentWidget() is window.statistics_page
            assert selector.currentText() == "Resultados"

            # Regresar a Entrada de datos actualiza el selector.
            window.navigate_to("Configuración solar")

            assert window.pages.currentWidget() is window.solar_config_page
            assert selector.currentText() == "Entrada de datos"

            # Una página bloqueada no debe cambiar la sección.
            window.set_project_loaded(False)
            window.navigate_to("Estadísticas")

            assert window.pages.currentWidget() is window.solar_config_page
            assert selector.currentText() == "Entrada de datos"

        finally:
            window.close()

    def test_android_orientation_detection(self, monkeypatch):
        """Comprueba la detección de orientación Android."""

        monkeypatch.setattr(
            "helios.gui.main_window.is_android",
            lambda: True,
        )

        window = MainWindow(self.economics_configuration)

        try:
            # Orientación vertical.
            window.resize(400, 800)

            assert not window.is_android_landscape()

            # Orientación horizontal.
            window.resize(800, 400)

            assert window.is_android_landscape()

            # Dimensiones iguales: no se considera horizontal.
            window.resize(600, 600)

            assert not window.is_android_landscape()

            # Fuera de Android, no debe detectar modo Android horizontal.
            monkeypatch.setattr(
                "helios.gui.main_window.is_android",
                lambda: False,
            )

            window.resize(800, 400)

            assert not window.is_android_landscape()

        finally:
            window.close()

    def test_android_orientation_updates_navigation(self, monkeypatch):
        """Comprueba la navegación al cambiar de orientación."""

        monkeypatch.setattr(
            "helios.gui.main_window.is_android",
            lambda: True,
        )

        window = MainWindow(self.economics_configuration)

        try:
            # Orientación vertical.
            window.resize(400, 800)
            window.update_android_orientation()

            assert not window.is_android_landscape()
            assert window.android_navigation_container.isHidden()
            assert not window.android_menu_button.isHidden()

            # Orientación horizontal.
            window.resize(800, 400)
            window.update_android_orientation()

            assert window.is_android_landscape()
            assert window.android_navigation_container.isHidden()

            # Volver a orientación vertical.
            window.resize(400, 800)
            window.update_android_orientation()

            assert not window.is_android_landscape()
            assert window.android_navigation_container.isHidden()
            assert not window.android_menu_button.isHidden()

            # La página activa debe conservarse.
            assert window.pages.currentIndex() == 0

        finally:
            window.close()

    def test_android_orientation_updates_automatically(self, monkeypatch):
        """Comprueba que resizeEvent actualiza la navegación Android."""
        monkeypatch.setattr(
            "helios.gui.main_window.is_android",
            lambda: True,
        )

        window = MainWindow(self.economics_configuration)

        try:
            window.resize(400, 800)
            window.show()

            assert window.android_navigation_container.isHidden()
            assert not window.android_menu_button.isHidden()

            window.resize(800, 400)

            assert window.android_navigation_container.isHidden()

            window.resize(400, 800)

            assert window.android_navigation_container.isHidden()
            assert not window.android_menu_button.isHidden()
            assert window.pages.currentIndex() == 0

        finally:
            window.close()

    def test_android_menu_button_visibility(self, monkeypatch):
        """Comprueba la visibilidad del botón de menú según la orientación."""
        monkeypatch.setattr(
            "helios.gui.main_window.is_android",
            lambda: True,
        )

        window = MainWindow(self.economics_configuration)

        try:
            window.resize(400, 800)
            window.show()

            # Vertical: navegación cerrada, botón visible.
            assert window.android_navigation_container.isHidden()
            assert not window.android_menu_button.isHidden()

            # Horizontal: navegación oculta, botón visible.
            window.resize(800, 400)

            assert window.android_navigation_container.isHidden()
            assert not window.android_menu_button.isHidden()

            # Volver a vertical.
            window.resize(400, 800)

            assert window.android_navigation_container.isHidden()
            assert not window.android_menu_button.isHidden()

            # La página activa se conserva.
            assert window.pages.currentIndex() == 0

        finally:
            window.close()

    def test_android_menu_button_toggle(self, monkeypatch):
        """Comprueba la apertura y el cierre del menú Android."""
        monkeypatch.setattr(
            "helios.gui.main_window.is_android",
            lambda: True,
        )

        window = MainWindow(self.economics_configuration)

        try:
            window.resize(800, 400)
            window.show()

            # Inicialmente, el menú está cerrado.
            assert window.android_navigation_container.isHidden()
            assert not window.android_menu_button.isHidden()

            # Primer clic: abrir el menú.
            print(
                "ANTES:",
                window.width(),
                window.height(),
                window.is_android_landscape(),
            )

            window.android_menu_button.click()

            print(
                "DESPUÉS:",
                window.width(),
                window.height(),
                window.is_android_landscape(),
                window.android_navigation_container.isHidden(),
            )

            assert not window.android_navigation_container.isHidden()

            # Segundo clic: iniciar el cierre animado.
            window.android_menu_button.click()

            from PySide6.QtTest import QTest
            QTest.qWait(350)

            assert window.android_navigation_container.isHidden()

            # La página activa no debe cambiar.
            assert window.pages.currentIndex() == 0

        finally:
            window.close()

    def test_android_landscape_navigation_overlay(self, monkeypatch):
        """Comprueba que el menú lateral no desplaza las páginas."""
        monkeypatch.setattr(
            "helios.gui.main_window.is_android",
            lambda: True,
        )

        window = MainWindow(self.economics_configuration)

        try:
            window.resize(1000, 600)
            window.show()

            central = window.centralWidget()
            navigation = window.android_navigation_container

            # El menú comienza cerrado.
            assert window.is_android_landscape()
            assert navigation.isHidden()

            # El panel debe ser hijo del widget central.
            assert navigation.parentWidget() is central

            # Comprobar la geometría prevista.
            assert navigation.x() == 0
            assert navigation.y() == 0
            assert navigation.width() == 280
            assert navigation.height() == central.height()

            # Guardar la geometría de las páginas.
            pages_geometry = window.pages.geometry()

            # Abrir el menú.
            window.android_menu_button.click()

            assert not navigation.isHidden()

            # El menú no debe desplazar ni redimensionar las páginas.
            assert window.pages.geometry() == pages_geometry

            # Cerrar el menú y esperar a la animación.
            window.android_menu_button.click()

            from PySide6.QtTest import QTest
            QTest.qWait(350)

            assert navigation.isHidden()
            assert window.pages.geometry() == pages_geometry

        finally:
            window.close()

    def test_android_portrait_navigation_does_not_overlap_pages(
        self, monkeypatch
    ):
        """Comprueba que la navegación vertical no tapa las páginas."""
        monkeypatch.setattr(
            "helios.gui.main_window.is_android",
            lambda: True,
        )

        window = MainWindow(self.economics_configuration)

        try:
            window.resize(400, 800)
            window.show()

            central = window.centralWidget()
            navigation = window.android_navigation_container
            pages = window.pages

            assert not window.is_android_landscape()
            assert navigation.isHidden()
            assert not window.android_menu_button.isHidden()

            # El menú es lateral izquierdo en ambas orientaciones.
            assert navigation.x() == 0
            assert navigation.y() == 0
            assert navigation.width() == min(280, central.width())
            assert navigation.height() == central.height()

            # La navegación oculta no debe reservar espacio.
            assert window.android_main_layout.contentsMargins().top() == 0

            # Las páginas deben comenzar debajo del botón del menú.
            assert pages.geometry().top() >= window.android_menu_button.geometry().bottom()

            # La página activa debe conservarse.
            assert pages.currentIndex() == 0

        finally:
            window.close()

    def test_android_rotation_with_open_navigation(self, monkeypatch):
        """Comprueba la rotación con el menú lateral abierto."""
        monkeypatch.setattr(
            "helios.gui.main_window.is_android",
            lambda: True,
        )

        window = MainWindow(self.economics_configuration)

        try:
            window.resize(1000, 600)
            window.show()

            navigation = window.android_navigation_container
            pages = window.pages

            # Horizontal: abrir el menú lateral.
            assert window.is_android_landscape()
            window.android_menu_button.click()

            assert not navigation.isHidden()
            assert pages.currentIndex() == 0

            # Girar a vertical.
            window.resize(400, 800)

            assert not window.is_android_landscape()
            assert navigation.isHidden()
            assert not window.android_menu_button.isHidden()

            # La navegación oculta no debe reservar espacio.
            assert window.android_main_layout.contentsMargins().top() == 0

            # Las páginas deben comenzar debajo del botón del menú.
            assert (
                pages.geometry().top()
                >= window.android_menu_button.geometry().bottom()
            )


            # Volver a horizontal.
            window.resize(1000, 600)

            assert window.is_android_landscape()

            # El menú debe comenzar cerrado tras la rotación.
            assert navigation.isHidden()
            assert not window.android_menu_button.isHidden()

            # Se conserva la página activa.
            assert pages.currentIndex() == 0

        finally:
            window.close()

    def test_android_portrait_results_navigation_height(self, monkeypatch):
        """Comprueba el espacio y desplazamiento de Informes en Android."""
        monkeypatch.setattr(
            "helios.gui.main_window.is_android",
            lambda: True,
        )
        monkeypatch.setattr(
            "helios.gui.widgets.reports_page.is_android",
            lambda: True,
        )

        window = MainWindow(self.economics_configuration)

        try:
            window.resize(400, 800)
            window.show()

            reports_page = window.pages.widget(10)
            window.pages.setCurrentWidget(reports_page)

            window.android_section_selector.setCurrentText("Resultados")
            window.update_android_orientation()

            QApplication.processEvents()

            navigation = window.android_navigation_container
            pages = window.pages
            scroll_area = reports_page.scroll_area

            # La ventana mantiene las dimensiones solicitadas.
            assert window.width() == 400
            assert window.height() == 800

            # Informes está visible y dispone de espacio suficiente.
            assert pages.currentWidget() is reports_page
            assert reports_page.isVisible()
            assert pages.height() > 600

            # El contenido de Informes permite desplazamiento vertical.
            assert scroll_area.verticalScrollBar().maximum() > 0

            # El menú está cerrado y no reserva espacio.
            assert navigation.isHidden()
            assert not window.android_menu_button.isHidden()
            assert window.android_main_layout.contentsMargins().top() == 0

            # Las páginas comienzan debajo del botón de menú.
            assert (
                pages.geometry().top()
                >= window.android_menu_button.geometry().bottom()
            )

        finally:
            window.close()


    def test_android_navigation_resizes_when_section_changes(
        self, monkeypatch
    ):
        """Comprueba que el menú lateral mantiene su tamaño al cambiar de sección."""
        monkeypatch.setattr(
            "helios.gui.main_window.is_android",
            lambda: True,
        )

        window = MainWindow(self.economics_configuration)

        try:
            window.resize(400, 800)
            window.show()

            navigation = window.android_navigation_container

            # Abrir el menú en orientación vertical.
            window.android_menu_button.click()
            QApplication.processEvents()

            assert not navigation.isHidden()

            # Medir la altura de Entrada de datos.
            window.android_section_selector.setCurrentText("Entrada de datos")
            QApplication.processEvents()
            input_height = navigation.height()

            # Cambiar a Resultados sin cerrar el menú.
            window.android_section_selector.setCurrentText("Resultados")
            QApplication.processEvents()
            results_height = navigation.height()

            assert not navigation.isHidden()

            # El panel lateral conserva toda la altura disponible.
            assert results_height == window.centralWidget().height()
            assert results_height == input_height
            assert navigation.width() == min(
                280,
                window.centralWidget().width(),
            )

            # Volver a Entrada de datos.
            window.android_section_selector.setCurrentText("Entrada de datos")
            QApplication.processEvents()

            assert not navigation.isHidden()
            assert navigation.height() == input_height

        finally:
            window.close()
