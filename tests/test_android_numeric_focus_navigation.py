"""Navegación por teclado entre controles numéricos."""

from unittest.mock import MagicMock

import pytest

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from helios.gui.widgets.solar_config_page import (
    SolarConfigPage,
)


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def page(app):
    project = MagicMock()
    project.solar_configuration = None

    widget = SolarConfigPage(project)
    widget.resize(420, 700)
    widget.show()
    app.processEvents()

    yield widget

    widget.close()
    app.processEvents()


def focused_control(app, controls):
    """Devuelve el control que contiene el foco actual."""
    focused = app.focusWidget()

    for control in controls:
        if focused is control:
            return control

        if focused is control.lineEdit():
            return control

        if control.isAncestorOf(focused):
            return control

    return None


def test_tab_moves_through_solar_configuration(app, page):
    controls = (
        page.latitude_spinbox,
        page.longitude_spinbox,
        page.tilt_spinbox,
        page.azimuth_spinbox,
        page.reference_year_spinbox,
        page.system_losses_spinbox,
    )

    controls[0].setFocus()
    app.processEvents()

    assert focused_control(app, controls) is controls[0]

    for expected in controls[1:]:
        current = app.focusWidget()

        QTest.keyClick(current, Qt.Key.Key_Tab)
        app.processEvents()

        assert focused_control(app, controls) is expected


def test_shift_tab_moves_backwards(app, page):
    controls = (
        page.latitude_spinbox,
        page.longitude_spinbox,
        page.tilt_spinbox,
        page.azimuth_spinbox,
        page.reference_year_spinbox,
        page.system_losses_spinbox,
    )

    controls[-1].setFocus()
    app.processEvents()

    assert focused_control(app, controls) is controls[-1]

    for expected in reversed(controls[:-1]):
        current = app.focusWidget()

        QTest.keyClick(current, Qt.Key.Key_Backtab)
        app.processEvents()

        assert focused_control(app, controls) is expected


def test_tab_skips_disabled_numeric_control(app, page):
    controls = (
        page.latitude_spinbox,
        page.longitude_spinbox,
        page.tilt_spinbox,
        page.azimuth_spinbox,
    )

    page.tilt_spinbox.setEnabled(False)

    try:
        page.longitude_spinbox.setFocus()
        app.processEvents()

        QTest.keyClick(
            app.focusWidget(),
            Qt.Key.Key_Tab,
        )
        app.processEvents()

        assert focused_control(app, controls) is (
            page.azimuth_spinbox
        )

    finally:
        page.tilt_spinbox.setEnabled(True)


def test_optimization_tab_between_roof_fields(app):
    """Avanza por superficie, anchura y altura de cubierta."""
    from helios.gui.widgets.solar_optimization_page import (
        SolarOptimizationPage,
    )

    project = MagicMock()
    project.dataset = None
    project.solar_configuration = None

    page = SolarOptimizationPage(project)

    try:
        page.resize(420, 700)
        page.show()
        app.processEvents()

        controls = (
            page.available_area_spinbox,
            page.roof_width_spinbox,
            page.roof_height_spinbox,
        )

        controls[0].setFocus()
        app.processEvents()

        assert focused_control(app, controls) is controls[0]

        for expected in controls[1:]:
            QTest.keyClick(
                app.focusWidget(),
                Qt.Key.Key_Tab,
            )
            app.processEvents()

            assert focused_control(app, controls) is expected

    finally:
        page.close()
        app.processEvents()


def test_optimization_skips_disabled_max_panels(app):
    """El campo de máximo de paneles no recibe foco deshabilitado."""
    from helios.gui.widgets.solar_optimization_page import (
        SolarOptimizationPage,
    )

    project = MagicMock()
    project.dataset = None
    project.solar_configuration = None

    page = SolarOptimizationPage(project)

    try:
        page.resize(420, 700)
        page.show()
        app.processEvents()

        minimum = page.min_panels_spinbox
        maximum = page.max_panels_spinbox

        assert not maximum.isEnabled()

        minimum.setFocus()
        app.processEvents()

        assert focused_control(app, (minimum,)) is minimum

        QTest.keyClick(
            app.focusWidget(),
            Qt.Key.Key_Tab,
        )
        app.processEvents()

        assert focused_control(app, (maximum,)) is None

    finally:
        page.close()
        app.processEvents()


def test_solar_tab_and_backtab_between_angles(app):
    """Permite avanzar y retroceder entre inclinación y orientación."""
    from helios.gui.widgets.solar_page import SolarPage

    project = MagicMock()
    project.solar_configuration = None

    page = SolarPage(project)

    try:
        page.resize(420, 700)
        page.show()
        app.processEvents()

        tilt = page.tilt_spinbox
        azimuth = page.azimuth_spinbox

        tilt.setFocus()
        app.processEvents()

        assert focused_control(app, (tilt, azimuth)) is tilt

        QTest.keyClick(
            app.focusWidget(),
            Qt.Key.Key_Tab,
        )
        app.processEvents()

        assert focused_control(app, (tilt, azimuth)) is azimuth

        QTest.keyClick(
            app.focusWidget(),
            Qt.Key.Key_Backtab,
        )
        app.processEvents()

        assert focused_control(app, (tilt, azimuth)) is tilt

    finally:
        page.close()
        app.processEvents()
