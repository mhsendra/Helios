
import pytest

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from helios.gui.widgets.localized_double_spinbox import (
    LocalizedDoubleSpinBox,
)


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance()

    if application is None:
        application = QApplication([])

    return application


def test_displays_decimal_comma(app):
    spinbox = LocalizedDoubleSpinBox()
    spinbox.setDecimals(2)
    spinbox.setValue(12.5)

    assert spinbox.lineEdit().text().startswith("12,50")


def test_accepts_numeric_keypad_decimal_point(app):
    spinbox = LocalizedDoubleSpinBox()
    spinbox.setRange(0.0, 100.0)
    spinbox.setDecimals(2)
    spinbox.show()

    spinbox.lineEdit().setText("12")
    spinbox.lineEdit().setCursorPosition(2)

    QTest.keyClick(
        spinbox.lineEdit(),
        Qt.Key.Key_Period,
        Qt.KeyboardModifier.KeypadModifier,
    )
    QTest.keyClick(
        spinbox.lineEdit(),
        Qt.Key.Key_5,
    )

    spinbox.interpretText()

    assert spinbox.value() == pytest.approx(12.5)

    spinbox.close()


def test_accepts_decimal_comma(app):
    spinbox = LocalizedDoubleSpinBox()
    spinbox.setRange(0.0, 100.0)
    spinbox.setDecimals(2)
    spinbox.show()

    spinbox.lineEdit().setText("12")
    spinbox.lineEdit().setCursorPosition(2)

    QTest.keyClick(
        spinbox.lineEdit(),
        Qt.Key.Key_Comma,
    )
    QTest.keyClick(
        spinbox.lineEdit(),
        Qt.Key.Key_5,
    )

    spinbox.interpretText()

    assert spinbox.value() == pytest.approx(12.5)

    spinbox.close()
