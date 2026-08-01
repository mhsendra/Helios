from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QStackedWidget,
    QSplitter,
    QLabel
)
from PySide6.QtCore import Qt
from helios.gui.widgets.home_page import HomePage


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.page_map = {}

    # ==================================================
    # Ventana
    # ==================================================

        self.configure_window()

        self.build_navigation()
    # ==================================================
    # Página temporal
    # ==================================================

        self.build_pages()

        self.connect_signals()

    def configure_window(self):
    
            self.setWindowTitle("HELIOS")
    
            self.resize(1400, 900)
    
            self.statusBar().showMessage("Listo")
    
            self.create_layout()

    def create_layout(self):

    # ==================================================
    # Widget central
    # ==================================================

        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)

    # ==================================================
    # Splitter principal
    # ==================================================

        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

    # ==================================================
    # Árbol de navegación
    # ==================================================

        self.navigation = QTreeWidget()
        self.navigation.setHeaderHidden(True)

        splitter.addWidget(self.navigation)

    # ==================================================
    # Páginas
    # ==================================================

        self.pages = QStackedWidget()

        splitter.addWidget(self.pages)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 5)

    def build_navigation(self):

        inicio = QTreeWidgetItem(["Inicio"])

        self.navigation.addTopLevelItem(inicio)
    # ==================================================
    # Construcción del árbol
    # ==================================================

        proyecto = QTreeWidgetItem(["Proyecto"])
        analisis = QTreeWidgetItem(["Análisis"])
        resultados = QTreeWidgetItem(["Resultados"])

        QTreeWidgetItem(proyecto, ["Cargar datos"])
        QTreeWidgetItem(proyecto, ["Configuración solar"])

        QTreeWidgetItem(analisis, ["Validación"])
        QTreeWidgetItem(analisis, ["Estadísticas"])
        QTreeWidgetItem(analisis, ["Perfiles"])
        QTreeWidgetItem(analisis, ["Comparativas"])
        QTreeWidgetItem(analisis, ["Indicadores"])
        QTreeWidgetItem(analisis, ["Tarifas"])
        QTreeWidgetItem(analisis, ["Solar"])

        QTreeWidgetItem(resultados, ["Informes"])
        QTreeWidgetItem(resultados, ["Gráficas"])

        self.navigation.addTopLevelItem(proyecto)
        self.navigation.addTopLevelItem(analisis)
        self.navigation.addTopLevelItem(resultados)

        self.navigation.expandAll()

    def build_pages(self):

        self.home_page = HomePage()

        self.pages.addWidget(self.home_page)

        self.page_map["Inicio"] = self.home_page

    def connect_signals(self):

        self.navigation.itemClicked.connect(self.change_page)

    def change_page(self, item):

        page = self.page_map.get(item.text(0))

        if page is not None:
            self.pages.setCurrentWidget(page)
    