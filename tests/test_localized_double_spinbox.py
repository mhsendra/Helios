
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

def test_accepts_decimal_from_input_method(app):
    """Simula texto enviado por un teclado virtual Android."""
    from PySide6.QtCore import QCoreApplication
    from PySide6.QtGui import QInputMethodEvent

    spinbox = LocalizedDoubleSpinBox()
    spinbox.setRange(0.0, 100.0)
    spinbox.setDecimals(2)
    spinbox.show()

    editor = spinbox.lineEdit()
    editor.setText("12")
    editor.setCursorPosition(2)

    event = QInputMethodEvent()
    event.setCommitString(".5")

    QCoreApplication.sendEvent(editor, event)

    print("Texto después del evento:", repr(editor.text()))
    print("Valor antes de interpretar:", spinbox.value())

    spinbox.interpretText()

    assert spinbox.value() == pytest.approx(12.5)

    spinbox.close()

@pytest.mark.parametrize(
    "input_text,expected",
    [
        (".5", 12.5),
        (",5", 12.5),
    ],
)
def test_input_method_decimal_separators(app, input_text, expected):
    from PySide6.QtCore import QCoreApplication
    from PySide6.QtGui import QInputMethodEvent

    spinbox = LocalizedDoubleSpinBox()
    spinbox.setRange(0.0, 100.0)
    spinbox.setDecimals(2)
    spinbox.show()

    editor = spinbox.lineEdit()
    editor.setText("12")
    editor.setCursorPosition(2)

    event = QInputMethodEvent()
    event.setCommitString(input_text)
    QCoreApplication.sendEvent(editor, event)

    spinbox.interpretText()

    assert spinbox.value() == pytest.approx(expected)
    spinbox.close()

def test_input_method_does_not_duplicate_decimal(app):
    from PySide6.QtCore import QCoreApplication
    from PySide6.QtGui import QInputMethodEvent

    spinbox = LocalizedDoubleSpinBox()
    spinbox.setRange(0.0, 100.0)
    spinbox.setDecimals(2)
    spinbox.show()

    editor = spinbox.lineEdit()
    editor.setText("12,5")
    editor.setCursorPosition(4)

    event = QInputMethodEvent()
    event.setCommitString(".")
    QCoreApplication.sendEvent(editor, event)

    assert editor.text().count(",") == 1

    spinbox.close()

@pytest.mark.parametrize(
    "android_mode,expected_locale,expected_text",
    [
        (False, "es_ES", "8,10"),
        (True, "en_US", "8.10"),
    ],
)
def test_platform_specific_decimal_locale(
    app, monkeypatch, android_mode, expected_locale, expected_text
):
    import helios.gui.widgets.localized_double_spinbox as module

    monkeypatch.setattr(
        module,
        "_is_android",
        lambda: android_mode,
    )

    spinbox = module.LocalizedDoubleSpinBox()
    spinbox.setDecimals(2)
    spinbox.setValue(8.1)

    assert spinbox._android_mode is android_mode
    assert spinbox.locale().name() == expected_locale
    assert spinbox.text() == expected_text

    spinbox.close()


def test_android_accepts_decimal_point_without_event_filters(
    app, monkeypatch
):
    import helios.gui.widgets.localized_double_spinbox as module

    monkeypatch.setattr(module, "_is_android", lambda: True)

    spinbox = module.LocalizedDoubleSpinBox()
    spinbox.setRange(0.0, 100.0)
    spinbox.setDecimals(2)
    spinbox.show()

    editor = spinbox.lineEdit()
    editor.selectAll()

    QTest.keyClicks(editor, "8.10")
    spinbox.interpretText()

    assert spinbox.value() == pytest.approx(8.1)

    spinbox.close()
