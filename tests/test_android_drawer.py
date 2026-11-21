"""Pruebas de navegación del menú Android de Helios."""

from unittest.mock import patch

import pytest

from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest

from helios.core.economics_configuration import EconomicsConfiguration
from helios.gui.main_window import MainWindow
from helios.gui.navigation_state import NAVIGATION_SECTIONS


@pytest.fixture
def android_window():
    app = QApplication.instance() or QApplication([])

    with patch(
        "helios.gui.main_window.is_android",
        return_value=True,
    ):
        window = MainWindow(
            EconomicsConfiguration(installation_cost=10000)
        )

        window.resize(400, 800)
        window.show()
        app.processEvents()

        try:
            yield window
        finally:
            window.close()
            app.processEvents()


def test_android_drawer_starts_closed(android_window):
    navigation = android_window.android_navigation_container

    assert navigation.isHidden()


def test_android_drawer_opens_and_closes(android_window):
    navigation = android_window.android_navigation_container

    android_window.toggle_android_navigation()
    QApplication.processEvents()

    assert navigation.isVisible()

    android_window.toggle_android_navigation()
    QTest.qWait(350)
    QApplication.processEvents()

    assert navigation.isHidden()


def test_android_drawer_has_all_navigation_buttons(android_window):
    buttons = android_window.android_navigation_buttons

    expected_pages = {
        page_id
        for pages in NAVIGATION_SECTIONS.values()
        for page_id in pages
    }

    assert len(buttons) == 13
    assert set(buttons) == expected_pages


def test_android_drawer_respects_page_availability(android_window):
    buttons = android_window.android_navigation_buttons

    for page_id, button in buttons.items():
        assert button.isEnabled() == (
            android_window.is_page_enabled(page_id)
        )


def test_android_drawer_disabled_style(android_window):
    buttons = android_window.android_navigation_buttons

    for button in buttons.values():
        style = button.styleSheet()

        assert "QPushButton:disabled" in style
        assert "#808080" in style


def test_android_drawer_section_selector(android_window):
    selector = android_window.android_section_selector

    assert selector.count() == 2
    assert selector.itemText(0) == "Entrada de datos"
    assert selector.itemText(1) == "Resultados"



def test_android_drawer_uses_left_panel_in_portrait(android_window):
    """El menú vertical debe ser lateral, no una franja superior."""
    window = android_window
    navigation = window.android_navigation_container
    central = window.centralWidget()

    window.resize(400, 800)
    QApplication.processEvents()

    window.update_android_orientation()

    geometry = navigation.geometry()

    assert geometry.x() == 0
    assert geometry.y() == 0
    assert geometry.height() == central.height()
    assert geometry.width() <= 320


def test_android_drawer_closes_after_navigation(android_window):
    """Seleccionar una página disponible debe cerrar el menú."""
    window = android_window
    navigation = window.android_navigation_container

    window.toggle_android_navigation()
    QApplication.processEvents()

    assert navigation.isVisible()

    window.navigate_to("Configuración solar")
    QApplication.processEvents()

    assert navigation.isHidden()


def test_android_drawer_remains_usable_after_resize(android_window):
    """El menú debe seguir abriéndose tras cambiar el tamaño."""
    window = android_window
    navigation = window.android_navigation_container

    window.resize(900, 500)
    QApplication.processEvents()

    window.update_android_orientation()

    window.toggle_android_navigation()
    QApplication.processEvents()

    assert navigation.isVisible()

    window.toggle_android_navigation()
    QTest.qWait(350)
    QApplication.processEvents()

    assert navigation.isHidden()



@pytest.mark.parametrize(
    "section",
    ["Entrada de datos", "Resultados"],
)
def test_android_drawer_scroll_reaches_last_button(
    android_window, section
):
    """Permite llegar al último botón cuando la lista no cabe."""
    window = android_window

    window.resize(900, 600)
    QApplication.processEvents()

    window.toggle_android_navigation()
    QApplication.processEvents()

    scroll = window.android_navigation_scroll
    scrollbar = scroll.verticalScrollBar()

    window.android_section_selector.setCurrentText(section)
    QApplication.processEvents()

    # Forzar un área pequeña para comprobar el desplazamiento.
    scroll.setFixedHeight(80)
    QApplication.processEvents()

    assert scrollbar.maximum() > 0

    page_ids = NAVIGATION_SECTIONS[section]
    last_button = window.android_navigation_buttons[page_ids[-1]]

    scrollbar.setValue(scrollbar.maximum())
    QApplication.processEvents()

    viewport = scroll.viewport()

    top = last_button.mapTo(
        viewport,
        last_button.rect().topLeft(),
    ).y()

    bottom = last_button.mapTo(
        viewport,
        last_button.rect().bottomRight(),
    ).y()

    assert top >= 0
    assert bottom < viewport.height()

    # El encabezado no forma parte del contenido desplazable.
    assert window.android_header.parent() is (
        window.android_navigation_container
    )



def test_android_drawer_animation_reaches_open_position(
    android_window,
):
    """La animación sitúa el menú en el borde izquierdo."""
    window = android_window
    navigation = window.android_navigation_container

    window.toggle_android_navigation()
    QTest.qWait(350)
    QApplication.processEvents()

    assert navigation.isVisible()
    assert navigation.geometry().x() == 0
    assert navigation.geometry().width() == min(
        280, window.centralWidget().width()
    )

    window.toggle_android_navigation()
    QTest.qWait(350)
    QApplication.processEvents()

    assert navigation.isHidden()



def test_android_drawer_rapid_open_close_open(android_window):
    """Tres pulsaciones rápidas dejan el cajón abierto."""
    from PySide6.QtCore import QAbstractAnimation

    window = android_window
    navigation = window.android_navigation_container
    animation = window.android_drawer_animation

    window.toggle_android_navigation()
    QTest.qWait(50)

    window.toggle_android_navigation()
    QTest.qWait(50)

    window.toggle_android_navigation()
    QTest.qWait(350)

    assert navigation.isVisible()
    assert navigation.x() == 0
    assert animation.state() == QAbstractAnimation.Stopped
    assert not window._android_drawer_closing


def test_android_drawer_reopens_during_closing(android_window):
    """Interrumpir el cierre permite reabrir correctamente."""
    from PySide6.QtCore import QAbstractAnimation

    window = android_window
    navigation = window.android_navigation_container
    animation = window.android_drawer_animation

    window.toggle_android_navigation()
    QTest.qWait(350)

    assert navigation.isVisible()

    window.toggle_android_navigation()
    QTest.qWait(50)

    assert window._android_drawer_closing

    window.toggle_android_navigation()
    QTest.qWait(350)

    assert navigation.isVisible()
    assert navigation.x() == 0
    assert animation.state() == QAbstractAnimation.Stopped
    assert not window._android_drawer_closing


def test_android_drawer_rotation_during_opening(android_window):
    """Cambiar la orientación detiene y cierra el cajón."""
    from PySide6.QtCore import QAbstractAnimation

    window = android_window
    navigation = window.android_navigation_container
    animation = window.android_drawer_animation

    window.resize(900, 600)
    QApplication.processEvents()

    window.toggle_android_navigation()
    QTest.qWait(50)

    window.resize(600, 900)
    QApplication.processEvents()

    window.update_android_orientation()
    QApplication.processEvents()

    assert navigation.isHidden()
    assert navigation.x() == 0
    assert navigation.width() == min(
        280, window.centralWidget().width()
    )
    assert navigation.height() == window.centralWidget().height()
    assert animation.state() == QAbstractAnimation.Stopped



def test_android_backdrop_starts_hidden(android_window):
    """El fondo no debe bloquear la página al iniciar."""
    window = android_window
    backdrop = window.android_navigation_backdrop

    assert backdrop.parentWidget() is window.centralWidget()
    assert backdrop.isHidden()


def test_android_backdrop_follows_drawer_visibility(android_window):
    """El fondo acompaña la apertura y el cierre del menú."""
    window = android_window
    backdrop = window.android_navigation_backdrop
    navigation = window.android_navigation_container

    window.toggle_android_navigation()
    QApplication.processEvents()

    assert navigation.isVisible()
    assert backdrop.isVisible()

    window.toggle_android_navigation()
    QTest.qWait(350)
    QApplication.processEvents()

    assert navigation.isHidden()
    assert backdrop.isHidden()


def test_android_backdrop_covers_central_widget(android_window):
    """El fondo cubre toda la página en ambas orientaciones."""
    window = android_window
    backdrop = window.android_navigation_backdrop

    for width, height in [(400, 800), (900, 500)]:
        window.resize(width, height)
        QApplication.processEvents()

        window.update_android_orientation()
        QApplication.processEvents()

        assert backdrop.geometry() == window.centralWidget().rect()

        window.toggle_android_navigation()
        QTest.qWait(350)

        assert backdrop.isVisible()
        assert backdrop.geometry() == window.centralWidget().rect()

        window.toggle_android_navigation()
        QTest.qWait(350)

        assert backdrop.isHidden()


def test_android_backdrop_closes_after_navigation(android_window):
    """Navegar oculta el menú y su fondo."""
    window = android_window
    backdrop = window.android_navigation_backdrop
    navigation = window.android_navigation_container

    window.toggle_android_navigation()
    QApplication.processEvents()

    assert backdrop.isVisible()
    assert navigation.isVisible()

    window.navigate_to("Configuración solar")
    QApplication.processEvents()

    assert navigation.isHidden()
    assert backdrop.isHidden()
    assert not window._android_drawer_closing



def test_android_backdrop_click_closes_drawer(android_window):
    """Un toque exterior inicia el cierre animado."""
    from PySide6.QtCore import Qt

    window = android_window
    backdrop = window.android_navigation_backdrop
    navigation = window.android_navigation_container

    window.toggle_android_navigation()
    QTest.qWait(350)

    assert navigation.isVisible()
    assert backdrop.isVisible()

    QTest.mouseClick(backdrop, Qt.LeftButton)
    QApplication.processEvents()

    assert window._android_drawer_closing

    QTest.qWait(350)

    assert navigation.isHidden()
    assert backdrop.isHidden()


def test_android_backdrop_click_during_closing(android_window):
    """Dos toques exteriores no invierten el cierre."""
    from PySide6.QtCore import Qt

    window = android_window
    backdrop = window.android_navigation_backdrop
    navigation = window.android_navigation_container

    window.toggle_android_navigation()
    QTest.qWait(350)

    QTest.mouseClick(backdrop, Qt.LeftButton)
    QApplication.processEvents()

    assert window._android_drawer_closing

    QTest.mouseClick(backdrop, Qt.LeftButton)
    QApplication.processEvents()

    assert window._android_drawer_closing

    QTest.qWait(350)

    assert navigation.isHidden()
    assert backdrop.isHidden()


def test_android_drawer_click_inside_does_not_close(android_window):
    """Un toque en el interior no debe cerrar el menú."""
    from PySide6.QtCore import Qt

    window = android_window
    navigation = window.android_navigation_container

    window.toggle_android_navigation()
    QTest.qWait(350)

    QTest.mouseClick(navigation, Qt.LeftButton)
    QApplication.processEvents()

    assert navigation.isVisible()
    assert not window._android_drawer_closing


def test_android_backdrop_click_does_not_reach_page(android_window):
    """El fondo consume el toque sin pulsar controles inferiores."""
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QPushButton

    window = android_window
    central = window.centralWidget()
    backdrop = window.android_navigation_backdrop

    # Botón de prueba situado en la zona exterior del menú.
    underlying_button = QPushButton("Control inferior", central)
    underlying_button.setGeometry(
        max(300, central.width() - 90),
        100,
        80,
        40,
    )

    clicks = []
    underlying_button.clicked.connect(
        lambda: clicks.append("clicked")
    )

    underlying_button.show()
    QApplication.processEvents()

    window.toggle_android_navigation()
    QTest.qWait(350)

    assert backdrop.isVisible()

    # Comprobar que el fondo está por encima del botón.
    point = underlying_button.mapTo(
        central,
        underlying_button.rect().center(),
    )

    assert central.childAt(point) is backdrop

    QTest.mouseClick(
        backdrop,
        Qt.LeftButton,
        pos=backdrop.mapFrom(central, point),
    )

    QApplication.processEvents()

    assert clicks == []

    QTest.qWait(350)

    assert backdrop.isHidden()
    assert clicks == []



def test_android_drawer_reversal_has_no_position_jump(android_window):
    """Reabrir durante el cierre no debe provocar un salto."""
    window = android_window
    navigation = window.android_navigation_container

    window.toggle_android_navigation()
    QTest.qWait(350)

    window.toggle_android_navigation()
    QTest.qWait(50)

    QApplication.processEvents()
    position_before = navigation.x()

    assert position_before < 0

    window.toggle_android_navigation()
    QApplication.processEvents()

    position_after = navigation.x()

    # El inicio de la nueva animación debe conservar la
    # posición de la animación anterior.
    assert abs(position_after - position_before) <= 3

    QTest.qWait(350)

    assert navigation.isVisible()
    assert navigation.x() == 0
    assert not window._android_drawer_closing


def test_android_drawer_rotation_resets_closing_state(android_window):
    """Rotar durante el cierre elimina el estado pendiente."""
    from PySide6.QtCore import QAbstractAnimation

    window = android_window
    navigation = window.android_navigation_container
    backdrop = window.android_navigation_backdrop
    animation = window.android_drawer_animation

    window.resize(400, 800)
    QApplication.processEvents()

    window.toggle_android_navigation()
    QTest.qWait(350)

    window.toggle_android_navigation()
    QTest.qWait(50)

    assert window._android_drawer_closing

    window.resize(900, 500)
    QApplication.processEvents()
    window.update_android_orientation()

    assert navigation.isHidden()
    assert backdrop.isHidden()
    assert not window._android_drawer_closing
    assert animation.state() == QAbstractAnimation.Stopped

    # Después de rotar debe poder abrirse normalmente.
    window.toggle_android_navigation()
    QTest.qWait(350)

    assert navigation.isVisible()
    assert backdrop.isVisible()
    assert navigation.x() == 0



def test_android_history_records_navigation(android_window):
    window = android_window

    assert window.android_page_history == []

    window.set_solar_configured(True)
    window.navigate_to("Cargar datos")

    assert window.android_page_history == ["Configuración solar"]


def test_android_history_ignores_same_page(android_window):
    window = android_window

    window.navigate_to("Configuración solar")

    assert window.android_page_history == []


def test_android_history_back_to_previous_page(android_window):
    window = android_window

    window.set_solar_configured(True)
    window.navigate_to("Cargar datos")

    assert window.android_navigate_back()

    assert window.pages.currentWidget() is window.solar_config_page
    assert window.android_page_history == []


def test_android_history_skips_disabled_pages(android_window):
    window = android_window

    window.set_solar_configured(True)
    window.navigate_to("Cargar datos")
    window.navigate_to("Configuración solar")

    # La última página del historial queda bloqueada.
    window.set_solar_configured(False)

    assert not window.android_navigate_back()
    assert window.pages.currentWidget() is window.solar_config_page
    assert window.android_page_history == []



def test_android_history_multiple_back_steps(android_window):
    """Retroceder varias veces consume el historial en orden."""
    window = android_window

    window.set_solar_configured(True)
    window.set_project_loaded(True)

    window.navigate_to("Cargar datos")
    window.navigate_to("Optimización solar")

    assert window.android_page_history == [
        "Configuración solar",
        "Cargar datos",
    ]

    assert window.android_navigate_back()
    assert window.pages.currentWidget() is window.load_page
    assert window.android_page_history == ["Configuración solar"]

    assert window.android_navigate_back()
    assert window.pages.currentWidget() is window.solar_config_page
    assert window.android_page_history == []

    assert not window.android_navigate_back()
    assert window.pages.currentWidget() is window.solar_config_page


def test_android_history_repeated_visits(android_window):
    """Visitar la misma página no crea duplicados consecutivos."""
    window = android_window

    window.set_solar_configured(True)

    window.navigate_to("Cargar datos")
    window.navigate_to("Cargar datos")
    window.navigate_to("Cargar datos")

    assert window.android_page_history == ["Configuración solar"]

    assert window.android_navigate_back()
    assert window.pages.currentWidget() is window.solar_config_page
    assert window.android_page_history == []


def test_android_history_skips_disabled_intermediate_page(android_window):
    """El retroceso omite páginas que ya no están disponibles."""
    window = android_window

    window.set_solar_configured(True)
    window.set_project_loaded(True)

    window.navigate_to("Cargar datos")
    window.navigate_to("Optimización solar")

    assert window.android_page_history == [
        "Configuración solar",
        "Cargar datos",
    ]

    # Bloqueamos Cargar datos y Optimización solar.
    window.set_solar_configured(False)

    assert window.android_navigate_back()

    assert window.pages.currentWidget() is window.solar_config_page
    assert window.android_page_history == []


def test_android_history_ignores_blocked_navigation(android_window):
    """Una navegación rechazada no modifica el historial."""
    window = android_window

    initial_page = window.pages.currentWidget()
    initial_history = list(window.android_page_history)

    assert not window.is_page_enabled("Optimización solar")

    window.navigate_to("Optimización solar")

    assert window.pages.currentWidget() is initial_page
    assert window.android_page_history == initial_history



def test_android_back_shortcut_closes_drawer(android_window):
    """Atrás cierra primero el menú, sin cambiar de página."""
    from PySide6.QtCore import Qt

    window = android_window
    initial_page = window.pages.currentWidget()

    window.toggle_android_navigation()
    QTest.qWait(350)

    assert window.android_navigation_container.isVisible()

    window.activateWindow()
    window.setFocus()
    QApplication.processEvents()

    QTest.keyClick(window, Qt.Key.Key_Back)
    QApplication.processEvents()

    assert window._android_drawer_closing
    assert window.pages.currentWidget() is initial_page

    QTest.qWait(350)

    assert window.android_navigation_container.isHidden()
    assert window.android_navigation_backdrop.isHidden()


def test_android_back_shortcut_navigates_previous_page(android_window):
    """Atrás vuelve a la página anterior mediante el atajo."""
    from PySide6.QtCore import Qt

    window = android_window
    window.set_solar_configured(True)
    window.navigate_to("Cargar datos")

    assert window.pages.currentWidget() is window.load_page

    window.activateWindow()
    window.setFocus()
    QApplication.processEvents()

    QTest.keyClick(window, Qt.Key.Key_Back)
    QApplication.processEvents()

    assert window.pages.currentWidget() is window.solar_config_page
    assert window.android_page_history == []


def test_android_back_shortcut_at_root_does_not_close(
    android_window,
):
    """Atrás en la pantalla inicial solicita confirmación."""
    from unittest.mock import patch
    from PySide6.QtCore import Qt

    window = android_window

    assert window.android_page_history == []

    window.activateWindow()
    window.setFocus()
    QApplication.processEvents()

    with patch.object(
        window,
        "confirm_android_exit",
    ) as confirm:
        QTest.keyClick(window, Qt.Key.Key_Back)
        QApplication.processEvents()
        confirm.assert_called_once_with()

    assert window.isVisible()
    assert window.pages.currentWidget() is window.solar_config_page



def test_android_back_during_drawer_closing_does_not_navigate(
    android_window,
):
    """Atrás durante el cierre no consume el historial."""
    window = android_window
    window.set_solar_configured(True)
    window.navigate_to("Cargar datos")

    history_before = list(window.android_page_history)

    window.toggle_android_navigation()
    QTest.qWait(350)

    window.close_android_navigation()
    QTest.qWait(50)

    assert window._android_drawer_closing
    assert window.handle_android_back()

    assert window.pages.currentWidget() is window.load_page
    assert window.android_page_history == history_before

    QTest.qWait(350)

    assert window.android_navigation_container.isHidden()



def test_android_back_keyboard_has_priority(android_window):
    """Atrás oculta el teclado sin cambiar de página."""
    from unittest.mock import patch

    window = android_window
    window.set_solar_configured(True)
    window.navigate_to("Cargar datos")

    history_before = list(window.android_page_history)

    with patch(
        "PySide6.QtGui.QInputMethod.isVisible",
        return_value=True,
    ), patch(
        "PySide6.QtGui.QInputMethod.hide",
    ) as hide_keyboard:
        assert window.handle_android_back()
        hide_keyboard.assert_called_once()

    assert window.pages.currentWidget() is window.load_page
    assert window.android_page_history == history_before


def test_android_back_modal_has_priority(android_window):
    """Un diálogo modal no debe provocar navegación."""
    from unittest.mock import patch
    from PySide6.QtWidgets import QWidget

    window = android_window
    window.set_solar_configured(True)
    window.navigate_to("Cargar datos")

    history_before = list(window.android_page_history)
    modal = QWidget()

    try:
        with patch.object(
            QApplication,
            "activeModalWidget",
            return_value=modal,
        ):
            assert window.handle_android_back()

        assert window.pages.currentWidget() is window.load_page
        assert window.android_page_history == history_before
    finally:
        modal.close()


def test_android_back_popup_has_priority(android_window):
    """Una ventana emergente no debe provocar navegación."""
    from unittest.mock import patch
    from PySide6.QtWidgets import QWidget

    window = android_window
    window.set_solar_configured(True)
    window.navigate_to("Cargar datos")

    history_before = list(window.android_page_history)
    popup = QWidget()

    try:
        with patch.object(
            QApplication,
            "activePopupWidget",
            return_value=popup,
        ):
            assert window.handle_android_back()

        assert window.pages.currentWidget() is window.load_page
        assert window.android_page_history == history_before
    finally:
        popup.close()



def test_android_exit_cancel_keeps_window_open(android_window):
    """Cancelar oculta el panel y conserva la ventana."""
    from unittest.mock import patch

    window = android_window

    with patch.object(window, "close") as close:
        window.confirm_android_exit()

        assert window.android_exit_overlay.isVisible()
        assert window.android_exit_panel.isVisible()

        window.android_exit_cancel_button.click()

        assert not window.android_exit_overlay.isVisible()
        assert window.isVisible()
        close.assert_not_called()


def test_android_exit_accept_closes_window(android_window):
    """Aceptar solicita cerrar la ventana principal."""
    from unittest.mock import patch

    window = android_window

    with patch.object(window, "close") as close:
        window.confirm_android_exit()

        assert window.android_exit_overlay.isVisible()

        window.android_exit_confirm_button.click()

        close.assert_called_once_with()
        assert not window.android_exit_overlay.isVisible()


def test_android_exit_dialog_is_not_duplicated(android_window):
    """Pulsaciones repetidas reutilizan el mismo panel."""
    window = android_window

    window.confirm_android_exit()
    first_panel = window.android_exit_panel

    window.confirm_android_exit()
    window.confirm_android_exit()

    assert window.android_exit_panel is first_panel
    assert window.android_exit_overlay.isVisible()

    window.android_exit_cancel_button.click()

    assert not window.android_exit_overlay.isVisible()


def test_android_back_cancels_exit_confirmation(android_window):
    """Atrás con el panel visible cancela la salida."""
    from unittest.mock import patch

    window = android_window
    window.confirm_android_exit()

    with patch.object(window, "close") as close:
        assert window.handle_android_back() is True

        assert not window.android_exit_overlay.isVisible()
        assert window.isVisible()
        close.assert_not_called()


def test_android_exit_does_not_create_modal_window(android_window):
    """La confirmación permanece dentro del widget central."""
    from PySide6.QtWidgets import QApplication

    window = android_window
    window.confirm_android_exit()

    assert window.android_exit_overlay.parentWidget() is window.centralWidget()
    assert window.android_exit_panel.parentWidget() is window.android_exit_overlay
    assert QApplication.activeModalWidget() is None

    window.android_exit_cancel_button.click()




def test_android_guided_navigation_lifecycle(monkeypatch, qapp):
    """Comprueba aviso, cancelación, avance y protección de origen."""
    from unittest.mock import MagicMock
    import helios.gui.main_window as module

    monkeypatch.setattr(module, "is_android", lambda: True)

    window = MagicMock()
    source = object()
    target = object()

    window.pages.currentWidget.return_value = source
    window.page_map = {"Cargar datos": target}
    window.is_page_enabled.return_value = True

    window._android_guided_target = None
    window._android_guided_source = None

    window.android_guided_navigation_timer = MagicMock()
    window.android_guided_navigation = MagicMock()
    window.android_guided_title = MagicMock()
    window.android_guided_message = MagicMock()

    window.cancel_android_guided_navigation = (
        lambda: module.MainWindow.cancel_android_guided_navigation(window)
    )
    window.accept_android_guided_navigation = (
        lambda: module.MainWindow.accept_android_guided_navigation(window)
    )

    window.update_android_orientation = MagicMock()
    window.navigate_to = MagicMock()

    show = module.MainWindow.show_android_guided_navigation
    accept = module.MainWindow.accept_android_guided_navigation
    cancel = module.MainWindow.cancel_android_guided_navigation
    finish = module.MainWindow.finish_android_guided_navigation

    # 1. Mostrar un destino habilitado.
    show(window, "Configuración guardada", "Cargar datos")

    assert window._android_guided_target == "Cargar datos"
    assert window._android_guided_source is source
    window.android_guided_navigation.show.assert_called()
    window.android_guided_navigation_timer.start.assert_called()

    # 2. Cancelar.
    cancel(window)

    assert window._android_guided_target is None
    assert window._android_guided_source is None
    window.android_guided_navigation_timer.stop.assert_called()
    window.android_guided_navigation.hide.assert_called()

    # 3. No mostrar destinos bloqueados.
    window.is_page_enabled.return_value = False
    show(window, "Configuración guardada", "Cargar datos")

    assert window._android_guided_target is None

    # 4. Avance inmediato.
    window.is_page_enabled.return_value = True
    show(window, "Configuración guardada", "Cargar datos")
    accept(window)

    window.navigate_to.assert_called_once_with("Cargar datos")

    # 5. Avance por temporizador.
    window.navigate_to.reset_mock()
    show(window, "Configuración guardada", "Cargar datos")
    finish(window)

    window.navigate_to.assert_called_once_with("Cargar datos")

    # 6. No avanzar si la página de origen ha cambiado.
    window.navigate_to.reset_mock()
    window.pages.currentWidget.return_value = source
    show(window, "Configuración guardada", "Cargar datos")

    window.pages.currentWidget.return_value = object()
    accept(window)

    window.navigate_to.assert_not_called()



def test_android_guided_navigation_cancelled_on_manual_navigation(
    android_window,
):
    """Cambiar de página cancela el avance automático pendiente."""
    window = android_window

    window.set_solar_configured(True)

    assert window.is_page_enabled("Cargar datos")

    window.navigate_to("Configuración solar")
    window.show_android_guided_navigation(
        "Configuración guardada",
        "Cargar datos",
    )

    assert window.android_guided_navigation_timer.isActive()
    assert window.android_guided_navigation.isVisible()

    window.navigate_to("Cargar datos")

    assert window.pages.currentWidget() is window.page_map["Cargar datos"]
    assert not window.android_guided_navigation_timer.isActive()
    assert not window.android_guided_navigation.isVisible()
    assert window._android_guided_target is None
    assert window._android_guided_source is None


def test_android_guided_navigation_cancelled_on_back(
    android_window,
):
    """Retroceder cancela el avance automático pendiente."""
    window = android_window

    window.set_solar_configured(True)

    assert window.is_page_enabled("Cargar datos")

    window.navigate_to("Cargar datos")

    window.show_android_guided_navigation(
        "Volver a configuración",
        "Configuración solar",
    )

    assert window.android_guided_navigation_timer.isActive()
    assert window.android_guided_navigation.isVisible()

    assert window.android_navigate_back()

    assert (
        window.pages.currentWidget()
        is window.page_map["Configuración solar"]
    )
    assert not window.android_guided_navigation_timer.isActive()
    assert not window.android_guided_navigation.isVisible()
    assert window._android_guided_target is None
    assert window._android_guided_source is None



def test_android_back_keyboard_then_previous_page(android_window):
    """Primero oculta el teclado y después retrocede."""
    from unittest.mock import patch

    window = android_window

    window.set_solar_configured(True)
    window.navigate_to("Cargar datos")

    assert window.pages.currentWidget() is window.load_page

    history_before = list(window.android_page_history)

    # Primera pulsación: teclado visible.
    with patch(
        "PySide6.QtGui.QInputMethod.isVisible",
        return_value=True,
    ), patch(
        "PySide6.QtGui.QInputMethod.hide",
    ) as hide_keyboard:

        assert window.handle_android_back()
        hide_keyboard.assert_called_once()

    assert window.pages.currentWidget() is window.load_page
    assert window.android_page_history == history_before

    # Segunda pulsación: teclado ya oculto.
    with patch(
        "PySide6.QtGui.QInputMethod.isVisible",
        return_value=False,
    ):
        assert window.handle_android_back()

    assert (
        window.pages.currentWidget()
        is window.solar_config_page
    )
    assert window.android_page_history == []


def test_android_optimization_to_solar_opens_production_tab(
    monkeypatch, qapp
):
    """Desde Optimización, Solar debe abrir la pestaña Producción."""
    from unittest.mock import MagicMock
    import helios.gui.main_window as module

    monkeypatch.setattr(module, "is_android", lambda: True)

    window = module.MainWindow.__new__(module.MainWindow)

    optimization_page = object()
    solar_page = MagicMock()

    window.solar_optimization_page = optimization_page
    window.solar_page = solar_page
    window.solar_config_page = MagicMock()

    window.pages = MagicMock()
    window.pages.currentWidget.return_value = optimization_page

    window.page_map = {"Solar": solar_page}
    window.is_page_enabled = lambda page_id: page_id == "Solar"

    window.cancel_android_guided_navigation = MagicMock()
    window.android_page_history = []
    window._android_navigating_back = False
    window.sync_android_section = MagicMock()
    window.android_navigation_container = MagicMock()
    window.android_drawer_animation = MagicMock()
    window.android_navigation_backdrop = MagicMock()

    window.navigate_to("Solar")

    solar_page.tabs.setCurrentWidget.assert_called_once_with(
        solar_page.production_tab
    )
    window.pages.setCurrentWidget.assert_called_once_with(
        solar_page
    )
