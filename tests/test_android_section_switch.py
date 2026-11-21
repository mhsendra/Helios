"""Pruebas del selector animado de secciones Android."""

import pytest

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from helios.gui.widgets.android_section_switch import (
    AndroidSectionSwitch,
)


@pytest.fixture(scope="module")
def app():
    instance = QApplication.instance()
    if instance is None:
        instance = QApplication([])
    return instance


@pytest.fixture
def switch(app):
    widget = AndroidSectionSwitch()
    widget.resize(280, 48)
    widget.show()
    app.processEvents()

    yield widget

    widget.close()
    app.processEvents()


def test_initial_section(switch):
    assert switch.currentText() == "Entrada de datos"
    assert switch.getPosition() == 0.0


def test_change_to_results(switch):
    received = []
    switch.currentTextChanged.connect(received.append)

    switch.setCurrentText("Resultados")

    assert switch.currentText() == "Resultados"
    assert received == ["Resultados"]


def test_invalid_section_is_ignored(switch):
    switch.setCurrentText("No existe")

    assert switch.currentText() == "Entrada de datos"


def test_same_section_does_not_emit_signal(switch):
    received = []
    switch.currentTextChanged.connect(received.append)

    switch.setCurrentText("Entrada de datos")

    assert received == []


def test_animation_reaches_results(switch):
    switch.setCurrentText("Resultados")

    QTest.qWait(300)

    assert switch.getPosition() == pytest.approx(1.0)


def test_animation_returns_to_data(switch):
    switch.setCurrentText("Resultados")
    QTest.qWait(300)

    switch.setCurrentText("Entrada de datos")
    QTest.qWait(300)

    assert switch.getPosition() == pytest.approx(0.0)


def test_rapid_changes(switch):
    switch.setCurrentText("Resultados")
    QTest.qWait(40)

    switch.setCurrentText("Entrada de datos")
    QTest.qWait(40)

    switch.setCurrentText("Resultados")
    QTest.qWait(300)

    assert switch.currentText() == "Resultados"
    assert switch.getPosition() == pytest.approx(1.0)


def test_click_results_button(switch):
    results_button = switch._buttons[1]

    QTest.mouseClick(results_button, Qt.MouseButton.LeftButton)

    assert switch.currentText() == "Resultados"


def test_click_data_button(switch):
    switch.setCurrentText("Resultados")

    data_button = switch._buttons[0]
    QTest.mouseClick(data_button, Qt.MouseButton.LeftButton)

    assert switch.currentText() == "Entrada de datos"


def test_indicator_stays_inside_widget(switch):
    switch.setCurrentText("Resultados")
    QTest.qWait(300)

    indicator = switch._indicator.geometry()

    assert indicator.left() >= 0
    assert indicator.right() < switch.width()
    assert indicator.top() >= 0
    assert indicator.bottom() < switch.height()


def test_resize_preserves_selection(switch):
    switch.setCurrentText("Resultados")
    QTest.qWait(300)

    switch.resize(360, 48)
    QApplication.processEvents()

    assert switch.currentText() == "Resultados"
    assert switch.getPosition() == pytest.approx(1.0)
    assert switch._indicator.geometry().right() < switch.width()
