from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QStackedWidget,
    QSplitter
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from helios.gui.widgets.home_page import HomePage
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

from helios.core.project import HeliosProject

class MainWindow(QMainWindow):

    def __init__(self, economics_configuration):

        super().__init__()

        self.project = HeliosProject(
            economics_configuration
        )

        self.page_map = {}

        self.configure_window()

        self.create_layout()

        self.build_pages()

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

        self.home_page = HomePage(self.project)

        self.pages.addWidget(self.home_page)

        self.load_page = LoadDataPage(self.project, self)

        self.pages.addWidget(self.load_page)

        self.solar_config_page = SolarConfigPage(self.project, self)

        self.pages.addWidget(self.solar_config_page)

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

        self.economics_page = EconomicsPage(self.project)

        self.pages.addWidget(self.economics_page)

    # ==================================================
    # Árbol de navegación
    # ==================================================

    def build_navigation(self):

        self.home_item = QTreeWidgetItem(["Inicio"])

        self.project_item = QTreeWidgetItem(["Proyecto"])

        self.analysis_item = QTreeWidgetItem(["Análisis"])

        self.results_item = QTreeWidgetItem(["Resultados"])

        self.load_item = QTreeWidgetItem(
            self.project_item,
            ["Cargar datos"]
        )

        self.configuration_item = QTreeWidgetItem(
            self.project_item,
            ["Configuración solar"]
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

        self.navigation.addTopLevelItem(self.home_item)
        self.navigation.addTopLevelItem(self.project_item)
        self.navigation.addTopLevelItem(self.analysis_item)
        self.navigation.addTopLevelItem(self.results_item)

        # Asociación árbol → páginas

        self.page_map["Inicio"] = self.home_page
        self.page_map["Cargar datos"] = self.load_page
        self.page_map["Configuración solar"] = self.solar_config_page
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
        

        self.set_project_loaded(False)

        self.navigation.expandAll()

    def set_project_loaded(self, loaded: bool):

        enabled_color = QColor("#FFFFFF")
        disabled_color = QColor("#808080")

        items = [
            self.validation_item,
            self.statistics_item,
            self.profiles_item,
            self.comparisons_item,
            self.indicators_item,
            self.tariffs_item,
            self.solar_item,
            self.reports_item,
            self.charts_item,
        ]

        for item in items:

            item.setDisabled(not loaded)

            item.setForeground(
                0,
                enabled_color if loaded else disabled_color
            )

        # Economía requiere resultados solares válidos
        self.set_solar_calculated(False)

    def set_solar_calculated(self, calculated: bool):

        enabled_color = QColor("#FFFFFF")
        disabled_color = QColor("#808080")

        self.economics_item.setDisabled(
            not calculated
        )

        self.economics_item.setForeground(
            0,
            enabled_color if calculated else disabled_color
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

    def change_page(self, item):

        if item.isDisabled():
            return

        page = self.page_map.get(item.text(0))

        if page is not None:

            if page is self.solar_config_page:
                self.solar_config_page.update_data()

            self.pages.setCurrentWidget(page)

    def update_project_pages(self):

        self.validation_page.update_data()
        self.statistics_page.update_data()
        self.profiles_page.update_data()
        self.comparisons_page.update_data()
        self.indicators_page.update_data()
        self.tariffs_page.update()
        self.solar_config_page.update_data()
        self.economics_page.update()

