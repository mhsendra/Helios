from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QStackedWidget,
    QSplitter,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QScrollArea,
    QApplication,
    QMessageBox,
)

from PySide6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QColor, QKeySequence, QShortcut, QPixmap


class AndroidNavigationBackdrop(QWidget):
    """Fondo que intercepta toques fuera del menú Android."""

    def __init__(self, on_pressed, parent=None):
        super().__init__(parent)
        self._on_pressed = on_pressed

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._on_pressed()
            event.accept()
            return

        super().mousePressEvent(event)

from helios.gui.widgets.android_section_switch import AndroidSectionSwitch
from helios.utils.platform import is_android
from helios.gui.navigation_state import (is_page_available, NAVIGATION_SECTIONS)
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



def _helios_window_log(message):
    import sys
    print(
        f"[HELIOS-BOOT] MainWindow: {message}",
        file=sys.stderr,
        flush=True,
    )


class MainWindow(QMainWindow):

    def __init__(self, economics_configuration):

        super().__init__()

        _helios_window_log("Creando HeliosProject")
        self.project = HeliosProject(
            economics_configuration
        )

        _helios_window_log("Preparando navegación")
        self.page_map = {}

        # Historial exclusivo de navegación Android.
        self.android_page_history = []
        self._android_navigating_back = False

        # Navegación guiada Android: temporizador reutilizable.
        self.android_guided_navigation_timer = QTimer(self)
        self.android_guided_navigation_timer.setSingleShot(True)
        self.android_guided_navigation_timer.setInterval(3000)

        self._android_guided_target = None
        self._android_guided_source = None

        self.solar_configured = False

        self.project_loaded = False

        self.solar_production_calculated = False

        self.solar_optimized = False

        self.economics_calculated = False

        _helios_window_log("Configurando ventana")
        self.configure_window()

        _helios_window_log("Creando diseño")
        self.create_layout()

        _helios_window_log("Construyendo páginas")
        self.build_pages()

        _helios_window_log("Configurando accesibilidad")
        self.configure_button_keyboard_accessibility()

        _helios_window_log("Construyendo navegación")
        self.build_navigation()

        _helios_window_log("Conectando señales")
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
        """Construye la interfaz según la plataforma."""
        if is_android():
            self.create_android_layout()
        else:
            self.create_desktop_layout()

    def create_desktop_layout(self):
        """Construye la interfaz de escritorio existente."""
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

    def create_android_layout(self):
        """Construye el contenedor principal de Android."""
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        self.android_main_layout = layout

        # Fondo oscurecido entre las páginas y el menú lateral.
        # No ocupa espacio en el layout principal.
        self.android_navigation_backdrop = AndroidNavigationBackdrop(
            self.close_android_navigation,
            central,
        )
        self.android_navigation_backdrop.setObjectName(
            "android_navigation_backdrop"
        )
        self.android_navigation_backdrop.setStyleSheet(
            "background-color: rgba(0, 0, 0, 150);"
        )
        self.android_navigation_backdrop.hide()

        # Confirmación integrada en el widget central de Android.
        self.android_exit_overlay = QWidget(central)
        self.android_exit_overlay.setObjectName("android_exit_overlay")
        self.android_exit_overlay.setStyleSheet(
            "QWidget#android_exit_overlay {"
            "background-color: rgba(0, 0, 0, 170);"
            "}"
        )
        self.android_exit_overlay.hide()

        # Aviso de navegación guiada: flotante, sin ocupar
        # espacio permanente en el diseño principal.
        self.create_android_guided_navigation()

        self.android_exit_panel = QWidget(self.android_exit_overlay)
        self.android_exit_panel.setObjectName("android_exit_panel")
        self.android_exit_panel.setStyleSheet(
            "QWidget#android_exit_panel {"
            "background-color: #292929;"
            "border: 1px solid #555555;"
            "border-radius: 12px;"
            "}"
            "QLabel { color: white; border: none; }"
            "QPushButton {"
            "background-color: #404040;"
            "color: white;"
            "border: 1px solid #666666;"
            "border-radius: 6px;"
            "padding: 10px;"
            "}"
        )

        exit_layout = QVBoxLayout(self.android_exit_panel)
        exit_layout.setSpacing(16)
        exit_layout.setContentsMargins(20, 20, 20, 20)

        self.android_exit_title = QLabel("Salir de Helios")
        self.android_exit_title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: white;"
        )
        exit_layout.addWidget(self.android_exit_title)

        self.android_exit_message = QLabel(
            "¿Quieres cerrar la aplicación?"
        )
        self.android_exit_message.setWordWrap(True)
        exit_layout.addWidget(self.android_exit_message)

        exit_buttons = QHBoxLayout()

        self.android_exit_cancel_button = QPushButton("Cancelar")
        self.android_exit_confirm_button = QPushButton(
            "Salir de Helios"
        )

        exit_buttons.addWidget(self.android_exit_cancel_button)
        exit_buttons.addWidget(self.android_exit_confirm_button)
        exit_layout.addLayout(exit_buttons)

        self.android_exit_cancel_button.clicked.connect(
            self.cancel_android_exit
        )
        self.android_exit_confirm_button.clicked.connect(
            self.accept_android_exit
        )

        # Contenedor reservado para la navegación Android.
        self.android_navigation_container = QWidget()
        self.android_navigation_layout = QVBoxLayout(
            self.android_navigation_container
        )

        # Cabecera principal de Android.
        self.android_header = QWidget()
        header_layout = QVBoxLayout(self.android_header)

        # Logotipo blanco exclusivo del menú Android.
        self.android_title = QLabel()
        self.android_title.setObjectName("android_menu_logo")
        self.android_title.setAlignment(Qt.AlignCenter)
        self.android_title.setStyleSheet(
            "background: transparent; border: none;"
        )

        # Ruta relativa al paquete: válida en desarrollo y en Android.
        logo_path = (
            Path(__file__).resolve().parents[1]
            / "resources"
            / "images"
            / "Logo_Helios_White.png"
        )
        logo_pixmap = QPixmap(str(logo_path))

        if logo_pixmap.isNull():
            raise FileNotFoundError(
                f"No se pudo cargar el logotipo Android: {logo_path}"
            )

        self.android_title.setPixmap(
            logo_pixmap.scaled(
                200,
                70,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )
        self.android_title.setFixedHeight(75)

        header_layout.addWidget(self.android_title)

        self.android_section_selector = AndroidSectionSwitch()

        header_layout.addWidget(self.android_section_selector)

        self.android_navigation_layout.addWidget(self.android_header)

        self.android_section_selector.currentTextChanged.connect(
            self.change_android_section
        )

        # El encabezado permanece fijo. Solo la lista de páginas
        # se desplaza cuando no cabe en la pantalla.
        self.android_navigation_scroll = QScrollArea()
        self.android_navigation_scroll.setWidgetResizable(True)
        self.android_navigation_scroll.setFrameShape(
            QScrollArea.NoFrame
        )
        self.android_navigation_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )
        self.android_navigation_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        self.android_navigation_content = QWidget()
        self.android_navigation_buttons_layout = QVBoxLayout(
            self.android_navigation_content
        )
        self.android_navigation_buttons_layout.setAlignment(
            Qt.AlignTop
        )

        self.android_navigation_scroll.setWidget(
            self.android_navigation_content
        )
        self.android_navigation_layout.addWidget(
            self.android_navigation_scroll, 1
        )

        # Botones de navegación Android.
        self.android_navigation_buttons = {}

        for section, page_ids in NAVIGATION_SECTIONS.items():
            for page_id in page_ids:
                button = QPushButton(page_id)

                # Estilo exclusivo del menú Android.
                # Las páginas bloqueadas permanecen visibles en gris.
                button.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #2D2D2D;
                        color: #FFFFFF;
                        border: 1px solid #444444;
                        border-radius: 6px;
                        padding: 6px 14px;
                    }
                    QPushButton:disabled {
                        background-color: #242424;
                        color: #808080;
                        border: 1px solid #303030;
                    }
                    """
                )

                button.clicked.connect(
                    lambda checked=False, page=page_id: self.navigate_to(page)
                )

                self.android_navigation_buttons[page_id] = button
                self.android_navigation_buttons_layout.addWidget(button)

                # Inicialmente solo mostramos Entrada de datos.
                button.setVisible(section == "Entrada de datos")

        # La navegación pertenece al widget central, pero no ocupa
        # espacio permanente dentro del layout principal.
        self.android_navigation_container.setParent(central)
        self.android_navigation_container.hide()

        # Animación exclusiva del cajón lateral Android.
        self.android_drawer_animation = QPropertyAnimation(
            self.android_navigation_container, b"geometry"
        )
        self.android_drawer_animation.setDuration(220)
        self.android_drawer_animation.setEasingCurve(
            QEasingCurve.OutCubic
        )
        self.android_drawer_animation.finished.connect(
            self.finish_android_drawer_animation
        )
        self._android_drawer_closing = False

        # El atajo pertenece solo a la ventana principal Android.
        # Las ventanas de gráficos conservan su propio atajo Back.
        self.android_back_shortcut = QShortcut(
            QKeySequence("Back"),
            self,
        )
        self.android_back_shortcut.setContext(
            Qt.ShortcutContext.WindowShortcut
        )
        self.android_back_shortcut.activated.connect(
            self.handle_android_back
        )

        # Botón para abrir la navegación en orientación horizontal.
        self.android_menu_button = QPushButton("☰")
        self.android_menu_button.clicked.connect(
            self.toggle_android_navigation
        )
        self.android_menu_button.setAccessibleName("Abrir menú de navegación")
        self.android_menu_button.setFixedSize(48, 48)
        self.android_menu_button.hide()

        layout.addWidget(self.android_menu_button)

        # Las páginas existentes se siguen reutilizando.
        self.pages = QStackedWidget()
        layout.addWidget(self.pages, 1)

        # Adaptador temporal para build_navigation().
        self.navigation = QTreeWidget()
        self.navigation.setHeaderHidden(True)
        self.navigation.hide()

    def change_android_section(self, section: str):
        """Muestra los botones de la sección Android seleccionada."""

        if section not in NAVIGATION_SECTIONS:
            return

        visible_pages = NAVIGATION_SECTIONS[section]

        for page_id, button in self.android_navigation_buttons.items():
            button.setVisible(page_id in visible_pages)

        # Recalcular la lista desplazable al cambiar de sección.
        self.android_navigation_buttons_layout.invalidate()
        self.android_navigation_buttons_layout.activate()
        self.android_navigation_layout.invalidate()
        self.android_navigation_layout.activate()

        self.update_android_orientation()

    def is_android_landscape(self) -> bool:
        """Indica si la ventana Android está en orientación horizontal."""
        return (
            is_android()
            and self.width() > self.height()
        )

    def sync_android_section(self, page_id: str):
        """Sincroniza el selector Android con la página activa."""

        if not hasattr(self, "android_section_selector"):
            return

        for section, page_ids in NAVIGATION_SECTIONS.items():
            if page_id in page_ids:
                self.android_section_selector.setCurrentText(section)
                return

    def resizeEvent(self, event):
        """Actualiza la disposición Android al cambiar el tamaño."""
        super().resizeEvent(event)

        if not is_android():
            return

        if not hasattr(self, "android_navigation_container"):
            return

        self.update_android_orientation()

    def update_android_orientation(self):
        """Actualiza la navegación según la orientación Android."""
        landscape = self.is_android_landscape()

        central = self.centralWidget()
        navigation = self.android_navigation_container

        # La navegación nunca reserva espacio en el layout.
        self.android_main_layout.setContentsMargins(0, 0, 0, 0)

        # En ambas orientaciones el menú es lateral izquierdo.
        # No reserva espacio en el layout principal.
        panel_width = min(280, central.width())

        # Evitar que una animación activa interfiera con el
        # cambio de orientación o tamaño de pantalla.
        self.android_drawer_animation.stop()

        navigation.setGeometry(
            0,
            0,
            panel_width,
            central.height(),
        )

        self.android_navigation_backdrop.setGeometry(
            central.rect()
        )

        self.android_exit_overlay.setGeometry(central.rect())

        # Aviso inferior, adaptable a ambas orientaciones.
        guided = self.android_guided_navigation
        guided_width = min(460, max(1, central.width() - 24))

        guided.setFixedWidth(guided_width)
        guided.adjustSize()

        guided.move(
            max(0, (central.width() - guided_width) // 2),
            max(0, central.height() - guided.height() - 16),
        )

        exit_width = min(420, max(1, central.width() - 32))
        self.android_exit_panel.setFixedWidth(exit_width)
        self.android_exit_panel.adjustSize()
        self.android_exit_panel.move(
            max(0, (central.width() - exit_width) // 2),
            max(
                0,
                (central.height() - self.android_exit_panel.height()) // 2,
            ),
        )

        # Cerrar el menú únicamente cuando cambia la orientación.
        if getattr(self, "_android_was_landscape", None) != landscape:
            navigation.hide()
            self.android_navigation_backdrop.hide()
            self._android_drawer_closing = False

        self.android_menu_button.show()
        self.android_menu_button.raise_()

        self._android_was_landscape = landscape

        self.android_main_layout.invalidate()
        self.android_main_layout.activate()

    def toggle_android_navigation(self):
        """Abre o cierra el cajón lateral con animación."""
        navigation = self.android_navigation_container
        animation = self.android_drawer_animation

        # Una segunda pulsación invierte el estado solicitado.
        currently_open = (
            navigation.isVisible() and not self._android_drawer_closing
        )
        animation.stop()

        width = min(280, self.centralWidget().width())
        height = self.centralWidget().height()

        if currently_open:
            self._android_drawer_closing = True
            animation.setStartValue(navigation.geometry())
            animation.setEndValue(
                QRect(-width, 0, width, height)
            )
            animation.start()
        else:
            # Si interrumpimos un cierre, continuar desde la
            # posición actual, sin saltar al borde izquierdo.
            was_visible = navigation.isVisible()
            current_x = navigation.x() if was_visible else -width

            self._android_drawer_closing = False
            navigation.setGeometry(current_x, 0, width, height)
            self.android_navigation_backdrop.show()
            self.android_navigation_backdrop.raise_()
            navigation.show()
            navigation.raise_()
            self.android_menu_button.raise_()

            animation.setStartValue(navigation.geometry())
            animation.setEndValue(
                QRect(0, 0, width, height)
            )
            animation.start()

    def close_android_navigation(self):
        """Inicia el cierre si el menú está abierto."""
        navigation = self.android_navigation_container

        if navigation.isVisible() and not self._android_drawer_closing:
            self.toggle_android_navigation()

    def finish_android_drawer_animation(self):
        """Oculta el cajón al finalizar la animación de cierre."""
        if self._android_drawer_closing:
            self.android_navigation_container.hide()
            self.android_navigation_backdrop.hide()
            self._android_drawer_closing = False

    # ==================================================
    # Páginas
    # ==================================================

    def build_pages(self):

        _helios_window_log("Creando página: SolarConfigPage")
        self.solar_config_page = SolarConfigPage(self.project, self)

        self.pages.addWidget(self.solar_config_page)

        _helios_window_log("Creando página: SolarOptimizationPage")
        self.solar_optimization_page = SolarOptimizationPage(self.project, self)

        self.pages.addWidget(self.solar_optimization_page)
        
        _helios_window_log("Creando página: LoadDataPage")
        self.load_page = LoadDataPage(self.project, self)

        self.pages.addWidget(self.load_page)

        _helios_window_log("Creando página: ValidationPage")
        self.validation_page = ValidationPage(self.project)

        self.pages.addWidget(self.validation_page)

        _helios_window_log("Creando página: StatisticsPage")
        self.statistics_page = StatisticsPage(self.project)
        
        self.pages.addWidget(self.statistics_page)

        _helios_window_log("Creando página: ProfilesPage")
        self.profiles_page = ProfilesPage(self.project)

        self.pages.addWidget(self.profiles_page)

        _helios_window_log("Creando página: ComparisonsPage")
        self.comparisons_page = ComparisonsPage(self.project)

        self.pages.addWidget(self.comparisons_page)

        _helios_window_log("Creando página: IndicatorsPage")
        self.indicators_page = IndicatorsPage(self.project)

        self.pages.addWidget(self.indicators_page)

        _helios_window_log("Creando página: TariffsPage")
        self.tariffs_page = TariffsPage(self.project)

        self.pages.addWidget(self.tariffs_page)

        _helios_window_log("Creando página: GraphicsPage")
        self.graphics_page = GraphicsPage(self.project)

        self.pages.addWidget(self.graphics_page)

        _helios_window_log("Creando página: ReportsPage")
        self.reports_page = ReportsPage(self.project)

        self.pages.addWidget(self.reports_page)

        _helios_window_log("Creando página: SolarPage")
        self.solar_page = SolarPage(self.project, self)

        self.pages.addWidget(self.solar_page)

        _helios_window_log("Creando página: EconomicsPage")
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

        if is_android():
            self.economics_page._update_android_economics_button()

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

        if is_android():
            self.solar_page._update_android_production_button()

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

        # Sincroniza también los botones de navegación Android.
        for page_id, button in getattr(
            self, "android_navigation_buttons", {}
        ).items():
            button.setEnabled(self.is_page_enabled(page_id))

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

        previous_page = self.pages.currentWidget()

        # Android: cancelar cualquier avance automático pendiente
        # cuando se cambia de página manualmente o con Atrás.
        if is_android() and previous_page is not page:
            self.cancel_android_guided_navigation()

        if (
            is_android()
            and previous_page is not page
            and not self._android_navigating_back
        ):
            previous_id = next(
                (
                    name
                    for name, widget in self.page_map.items()
                    if widget is previous_page
                ),
                None,
            )

            if previous_id is not None:
                self.android_page_history.append(previous_id)

        self.pages.setCurrentWidget(page)

        self.sync_android_section(page_id)

        # Al seleccionar una página, cerrar el menú Android.
        if is_android() and hasattr(
            self, "android_navigation_container"
        ):
            self.android_drawer_animation.stop()
            self.android_navigation_container.hide()
            self.android_navigation_backdrop.hide()
            self._android_drawer_closing = False

    def create_android_guided_navigation(self):
        """Crea la notificación de avance dentro de la ventana."""

        if not is_android():
            return

        central = self.centralWidget()

        self.android_guided_navigation = QWidget(central)
        self.android_guided_navigation.setObjectName(
            "androidGuidedNavigation"
        )
        self.android_guided_navigation.setStyleSheet(
            "QWidget#androidGuidedNavigation {"
            "background-color: #263238;"
            "border: 1px solid #607D8B;"
            "border-radius: 12px;"
            "}"
        )

        layout = QVBoxLayout(self.android_guided_navigation)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        self.android_guided_title = QLabel()
        self.android_guided_title.setWordWrap(True)
        layout.addWidget(self.android_guided_title)

        self.android_guided_message = QLabel()
        self.android_guided_message.setWordWrap(True)
        layout.addWidget(self.android_guided_message)

        actions = QHBoxLayout()
        actions.addStretch()

        self.android_guided_stay_button = QPushButton(
            "Permanecer aquí"
        )
        self.android_guided_now_button = QPushButton(
            "Ir ahora"
        )

        actions.addWidget(self.android_guided_stay_button)
        actions.addWidget(self.android_guided_now_button)
        layout.addLayout(actions)

        self.android_guided_navigation.hide()

        self.android_guided_stay_button.clicked.connect(
            self.cancel_android_guided_navigation
        )
        self.android_guided_now_button.clicked.connect(
            self.accept_android_guided_navigation
        )
        self.android_guided_navigation_timer.timeout.connect(
            self.finish_android_guided_navigation
        )

    def show_android_guided_navigation(
        self,
        title: str,
        destination: str,
    ) -> None:
        """Ofrece avanzar tras una operación completada."""

        if not is_android():
            return

        self.cancel_android_guided_navigation()

        if not self.is_page_enabled(destination):
            return

        source = self.pages.currentWidget()
        target = self.page_map.get(destination)

        if source is None or target is None or source is target:
            return

        self._android_guided_source = source
        self._android_guided_target = destination

        self.android_guided_title.setText(title)
        self.android_guided_message.setText(
            f"Continuando a {destination} en 3 segundos..."
        )

        self.update_android_orientation()
        self.android_guided_navigation.show()
        self.android_guided_navigation.raise_()

        self.android_guided_navigation_timer.start()

    def cancel_android_guided_navigation(self) -> None:
        """Cancela un avance pendiente."""

        if not is_android():
            return

        self.android_guided_navigation_timer.stop()
        self._android_guided_target = None
        self._android_guided_source = None

        self.android_guided_navigation.hide()

    def accept_android_guided_navigation(self) -> None:
        """Avanza únicamente si el contexto sigue siendo válido."""

        if not is_android():
            return

        destination = self._android_guided_target
        source = self._android_guided_source

        self.cancel_android_guided_navigation()

        if destination is None or source is None:
            return

        if self.pages.currentWidget() is not source:
            return

        if not self.is_page_enabled(destination):
            return

        self.navigate_to(destination)

    def finish_android_guided_navigation(self) -> None:
        """Ejecuta el avance al terminar la cuenta atrás."""

        self.accept_android_guided_navigation()

    def handle_android_back(self) -> bool:
        """Gestiona Atrás en la ventana principal Android."""
        if not is_android():
            return False

        app = QApplication.instance()

        if app is not None:
            input_method = app.inputMethod()

            # El teclado virtual tiene prioridad sobre la navegación.
            if input_method.isVisible():
                input_method.hide()
                return True

            # No navegar mientras exista un diálogo modal
            # o una ventana emergente activa.
            modal = app.activeModalWidget()
            popup = app.activePopupWidget()

            if (
                (modal is not None and modal is not self)
                or (popup is not None and popup is not self)
            ):
                return True

        if self.android_exit_overlay.isVisible():
            self.cancel_android_exit()
            return True

        navigation = self.android_navigation_container

        # El menú tiene prioridad sobre el historial.
        if navigation.isVisible():
            if not self._android_drawer_closing:
                self.close_android_navigation()
            return True

        # Retroceder si existe una página anterior.
        if self.android_navigate_back():
            return True

        # En la pantalla inicial, solicitar confirmación.
        self.confirm_android_exit()
        return True

    def confirm_android_exit(self) -> None:
        """Muestra la confirmación dentro de la ventana Android."""
        if not is_android():
            return

        if self.android_exit_overlay.isVisible():
            return

        self.update_android_orientation()
        self.android_exit_overlay.show()
        self.android_exit_overlay.raise_()
        self.android_exit_cancel_button.setFocus()

    def cancel_android_exit(self) -> None:
        """Cancela la salida y vuelve a la página actual."""
        if not is_android():
            return

        self.android_exit_overlay.hide()

    def accept_android_exit(self) -> None:
        """Solicita el cierre tras la confirmación."""
        if not is_android():
            return

        self.android_exit_overlay.hide()
        self.close()

    def android_navigate_back(self) -> bool:
        """Retrocede a la última página Android todavía habilitada."""
        if not is_android():
            return False

        current_page = self.pages.currentWidget()

        while self.android_page_history:
            previous_id = self.android_page_history.pop()

            if not self.is_page_enabled(previous_id):
                continue

            previous_page = self.page_map.get(previous_id)

            if previous_page is None or previous_page is current_page:
                continue

            # El retroceso no debe registrar la página abandonada.
            self._android_navigating_back = True
            try:
                self.navigate_to(previous_id)
            finally:
                self._android_navigating_back = False

            if self.pages.currentWidget() is previous_page:
                return True

        return False

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

        if is_android():
            self.solar_optimization_page.update_data()

        self.economics_page.refresh_battery_analysis()

