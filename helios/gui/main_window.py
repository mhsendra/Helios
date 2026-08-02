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

from helios.gui.widgets.home_page import HomePage
from helios.gui.widgets.load_data_page import LoadDataPage
from helios.gui.widgets.validation_page import ValidationPage
from helios.core.analyzer import ConsumptionAnalyzer


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.analyzer = ConsumptionAnalyzer()

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

        splitter.addWidget(self.navigation)

        self.pages = QStackedWidget()

        splitter.addWidget(self.pages)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 5)

    # ==================================================
    # Páginas
    # ==================================================

    def build_pages(self):

        self.home_page = HomePage(self.analyzer)

        self.pages.addWidget(self.home_page)

        self.load_page = LoadDataPage(self.analyzer, self)

        self.pages.addWidget(self.load_page)

        self.validation_page = ValidationPage(self.analyzer)

        self.pages.addWidget(self.validation_page)

    # ==================================================
    # Árbol de navegación
    # ==================================================

    def build_navigation(self):

        self.home_item = QTreeWidgetItem(["Inicio"])

        self.project_item = QTreeWidgetItem(["Proyecto"])

        self.analysis_item = QTreeWidgetItem(["Análisis"])

        self.results_item = QTreeWidgetItem(["self.results_item"])

        QTreeWidgetItem(self.project_item, ["Cargar datos"])
        QTreeWidgetItem(self.project_item, ["Configuración solar"])

        QTreeWidgetItem(self.analysis_item, ["Validación"])
        QTreeWidgetItem(self.analysis_item, ["Estadísticas"])
        QTreeWidgetItem(self.analysis_item, ["Perfiles"])
        QTreeWidgetItem(self.analysis_item, ["Comparativas"])
        QTreeWidgetItem(self.analysis_item, ["Indicadores"])
        QTreeWidgetItem(self.analysis_item, ["Tarifas"])
        QTreeWidgetItem(self.analysis_item, ["Solar"])

        QTreeWidgetItem(self.results_item, ["Informes"])
        QTreeWidgetItem(self.results_item, ["Gráficas"])

        self.navigation.addTopLevelItem(self.home_item)
        self.navigation.addTopLevelItem(self.project_item)
        self.navigation.addTopLevelItem(self.analysis_item)
        self.navigation.addTopLevelItem(self.results_item)

        # Asociación árbol → páginas

        self.page_map["Inicio"] = self.home_page
        self.page_map["Cargar datos"] = self.load_page
        self.page_map["Validación"] = self.validation_page

        self.set_project_loaded(False)

        self.navigation.expandAll()

    def set_project_loaded(self, loaded: bool):

        self.analysis_item.setDisabled(not loaded)

        self.results_item.setDisabled(not loaded)

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

        page = self.page_map.get(item.text(0))

        if page is not None:

            self.pages.setCurrentWidget(page)