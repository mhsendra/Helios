from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QStackedWidget,
    QSplitter,
    QPushButton,
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from helios.gui.navigation_state import is_page_available
from helios.gui.widgets.load_data_page import LoadDataPage
from helios.gui.widgets.validation_page import ValidationPage
from helios.gui.widgets.statistics_page import StatisticsPage
from helios.gui.widgets.profiles_page import ProfilesPage
from helios.gui.widgets.comparisons_page import ComparisonsPage
from helios.gui.widgets.indicators_page import IndicatorsPage
from helios.gui.widgets.solar_page import SolarPage
from helios.gui.widgets.economics_page import EconomicsPage
from helios.gui.widgets.tariffs_page import TariffsPage
from helios.gui.widgets.graphics_page import GraphicsPage
from helios.gui.widgets.reports_page import ReportsPage
from helios.gui.widgets.solar_config_page import SolarConfigPage
from helios.gui.widgets.solar_optimization_page import SolarOptimizationPage

from helios.core.project import HeliosProject

class MainWindow(QMainWindow):

    def __init__(self, economics_configuration):

        super().__init__()

        self.project = HeliosProject(
            economics_configuration
        )

        self.page_map = {}

        self.solar_configured = False

        self.project_loaded = False

        self.solar_production_calculated = False

        self.solar_optimized = False

        self.economics_calculated = False

        self.configure_window()

        self.create_layout()

        self.build_pages()

        self.configure_button_keyboard_accessibility()

        self.build_navigation()

        self.connect_signals()

    # ==================================================
    # Configuración de ventana
    # ==================================================

    def configure_window(self):

        self.setWindowTitle("HELIOS")

        self.resize(1400, 900)

        self.statusBar().showMessage("Listo")

    # ==================================================
    # Layout principal
    # ==================================================

    def create_layout(self):

        central = QWidget()

        self.setCentralWidget(central)

        layout = QHBoxLayout(central)

        splitter = QSplitter(Qt.Horizontal)

        layout.addWidget(splitter)

        self.navigation = QTreeWidget()

        self.navigation.setHeaderHidden(True)

        self.navigation.setMinimumWidth(240)

        splitter.addWidget(self.navigation)

        self.pages = QStackedWidget()

        splitter.addWidget(self.pages)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 5)

    # ==================================================
    # Páginas
    # ==================================================

    def build_pages(self):

        self.solar_config_page = SolarConfigPage(self.project, self)

        self.pages.addWidget(self.solar_config_page)

        self.solar_optimization_page = SolarOptimizationPage(self.project, self)

        self.pages.addWidget(self.solar_optimization_page)
        
        self.load_page = LoadDataPage(self.project, self)

        self.pages.addWidget(self.load_page)

        self.validation_page = ValidationPage(self.project)

        self.pages.addWidget(self.validation_page)

        self.statistics_page = StatisticsPage(self.project)
        
        self.pages.addWidget(self.statistics_page)

        self.profiles_page = ProfilesPage(self.project)

        self.pages.addWidget(self.profiles_page)

        self.comparisons_page = ComparisonsPage(self.project)

        self.pages.addWidget(self.comparisons_page)

        self.indicators_page = IndicatorsPage(self.project)

        self.pages.addWidget(self.indicators_page)

        self.tariffs_page = TariffsPage(self.project)

        self.pages.addWidget(self.tariffs_page)

        self.graphics_page = GraphicsPage(self.project)

        self.pages.addWidget(self.graphics_page)

        self.reports_page = ReportsPage(self.project)

        self.pages.addWidget(self.reports_page)

        self.solar_page = SolarPage(self.project, self)

        self.pages.addWidget(self.solar_page)

        self.economics_page = EconomicsPage(
            self.project,
            self,
        )

        self.pages.addWidget(self.economics_page)

    # ==================================================
    # Accesibilidad con el tabulador
    # ==================================================

    def configure_button_keyboard_accessibility(self):
        """Permite recorrer y activar los botones con el teclado."""

        for button in self.findChildren(QPushButton):
            button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    # ==================================================
    # Árbol de navegación
    # ==================================================

    def build_navigation(self):

        self.project_item = QTreeWidgetItem(["Proyecto"])

        self.analysis_item = QTreeWidgetItem(["Análisis"])

        self.results_item = QTreeWidgetItem(["Resultados"])

        self.configuration_item = QTreeWidgetItem(
            self.project_item,
            ["Configuración solar"]
        )
        
        self.load_item = QTreeWidgetItem(
            self.project_item,
            ["Cargar datos"]
        )

        self.solar_optimization_item = QTreeWidgetItem(
            self.project_item,
            ["Optimización solar"]
        )

        self.validation_item = QTreeWidgetItem(
            self.analysis_item,
            ["Validación"]
        )

        self.statistics_item = QTreeWidgetItem(
            self.analysis_item,
            ["Estadísticas"]
        )

        self.profiles_item = QTreeWidgetItem(
            self.analysis_item,
            ["Perfiles"]
        )

        self.comparisons_item = QTreeWidgetItem(
            self.analysis_item,
            ["Comparativas"]
        )

        self.indicators_item = QTreeWidgetItem(
            self.analysis_item,
            ["Indicadores"]
        )

        self.tariffs_item = QTreeWidgetItem(
            self.analysis_item,
            ["Tarifas"]
        )

        self.solar_item = QTreeWidgetItem(
            self.analysis_item,
            ["Solar"]
        )

        self.economics_item = QTreeWidgetItem(
            self.analysis_item,
            ["Economía"]
        )

        self.reports_item = QTreeWidgetItem(
            self.results_item,
            ["Informes"]
        )

        self.charts_item = QTreeWidgetItem(
            self.results_item,
            ["Gráficas"]
        )

        self.navigation.addTopLevelItem(self.project_item)
        self.navigation.addTopLevelItem(self.analysis_item)
        self.navigation.addTopLevelItem(self.results_item)

        # Asociación árbol → páginas

        self.page_map["Cargar datos"] = self.load_page
        self.page_map["Configuración solar"] = self.solar_config_page
        self.page_map["Optimización solar"] = self.solar_optimization_page
        self.page_map["Validación"] = self.validation_page
        self.page_map["Estadísticas"] = self.statistics_page
        self.page_map["Perfiles"] = self.profiles_page
        self.page_map["Comparativas"] = self.comparisons_page
        self.page_map["Indicadores"] = self.indicators_page
        self.page_map["Tarifas"] = self.tariffs_page
        self.page_map["Gráficas"] = self.graphics_page
        self.page_map["Informes"] = self.reports_page
        self.page_map["Solar"] = self.solar_page
        self.page_map["Economía"] = self.economics_page

        self.pages.setCurrentWidget(self.solar_config_page)

        self.set_project_loaded(False)

        self.set_solar_configured(
            self.project.solar_configuration is not None
        )

        self.navigation.expandAll()

    def set_economics_calculated(self, calculated: bool):
        """Controla el acceso a Informes tras el análisis económico."""

        self.economics_calculated = bool(
            calculated
            and self.solar_optimized
            and self.solar_production_calculated
        )

        self.refresh_navigation_state()

        self.reports_page.set_solar_report_available(
            self.economics_calculated
        )

    def set_project_loaded(self, loaded: bool):
        """Actualiza la carga del proyecto e invalida resultados solares."""

        self.project_loaded = bool(loaded)

        # Cargar nuevos datos invalida los cálculos solares anteriores.
        self.set_solar_optimized(False)

    def set_solar_production_calculated(
        self,
        calculated: bool,
    ):
        """Actualiza el estado de la producción fotovoltaica."""

        self.solar_production_calculated = bool(
            calculated and self.solar_optimized
        )

        if not self.solar_production_calculated:
            self.economics_calculated = False

        self.set_economics_calculated(
            self.economics_calculated
        )

    def set_solar_configured(self, configured: bool):
        """Actualiza el estado de la configuración fotovoltaica."""
        self.solar_configured = bool(configured)
        self.refresh_navigation_state()

    def set_solar_optimized(self, optimized: bool):
        """Actualiza el estado tras la optimización fotovoltaica."""

        self.solar_optimized = bool(optimized)

        if not self.solar_optimized:
            self.economics_calculated = False
            self.set_solar_production_calculated(False)

        self.set_economics_calculated(
            self.economics_calculated
        )
        
    # ==================================================
    # Señales
    # ==================================================

    def connect_signals(self):

        self.navigation.itemClicked.connect(
            self.change_page
        )

    # ==================================================
    # Slots
    # ==================================================

    def refresh_navigation_state(self) -> None:
        """Sincroniza el árbol de escritorio con los permisos del modelo."""

        navigation_items = (
            self.configuration_item,
            self.load_item,
            self.solar_optimization_item,
            self.validation_item,
            self.statistics_item,
            self.profiles_item,
            self.comparisons_item,
            self.indicators_item,
            self.tariffs_item,
            self.solar_item,
            self.economics_item,
            self.reports_item,
            self.charts_item,
        )

        enabled_color = QColor("#FFFFFF")
        disabled_color = QColor("#808080")

        for item in navigation_items:
            enabled = self.is_page_enabled(item.text(0))

            item.setDisabled(not enabled)
            item.setForeground(
                0,
                enabled_color if enabled else disabled_color,
            )

    def is_page_enabled(self, page_id: str) -> bool:
        """Consulta los permisos de navegación independientes de la interfaz."""

        return is_page_available(
            page_id,
            solar_configured=self.solar_configured,
            project_loaded=self.project_loaded,
            solar_optimized=self.solar_optimized,
            solar_production_calculated=self.solar_production_calculated,
            economics_calculated=self.economics_calculated,
        )

    def navigate_to(self, page_id: str) -> None:
        """Navega a una página habilitada mediante su identificador."""

        if not self.is_page_enabled(page_id):
            return

        page = self.page_map.get(page_id)

        if page is None:
            return

        if page is self.solar_config_page:
            self.solar_config_page.update_data()

        if page is self.solar_page:
            self.solar_page.load_saved_configuration()

        self.pages.setCurrentWidget(page)

    def change_page(self, item):
        """Adaptador de navegación para el árbol de escritorio."""

        if item.isDisabled():
            return

        self.navigate_to(item.text(0))

    def update_project_pages(self):

        self.validation_page.update_data()
        self.statistics_page.update_data()
        self.profiles_page.update_data()
        self.comparisons_page.update_data()
        self.indicators_page.update_data()
        self.tariffs_page.update()
        self.solar_config_page.update_data()
        self.economics_page.refresh_battery_analysis()

