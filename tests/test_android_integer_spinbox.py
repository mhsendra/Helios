"""Pruebas del teclado numérico entero Android."""

import pytest

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QSpinBox

import helios.gui.widgets.android_integer_spinbox as module


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance()
    return application or QApplication([])


def test_android_integer_keyboard(app, monkeypatch):
    monkeypatch.setattr(module, "_is_android", lambda: True)

    widget = module.AndroidIntegerSpinBox()

    try:
        hint = Qt.InputMethodHint.ImhDigitsOnly

        assert widget.inputMethodHints() & hint
        assert widget.lineEdit().inputMethodHints() & hint
    finally:
        widget.close()


def test_desktop_integer_keyboard_unchanged(app, monkeypatch):
    monkeypatch.setattr(module, "_is_android", lambda: False)

    widget = module.AndroidIntegerSpinBox()
    standard = QSpinBox()

    try:
        assert (
            widget.inputMethodHints()
            == standard.inputMethodHints()
        )

        assert (
            widget.lineEdit().inputMethodHints()
            == standard.lineEdit().inputMethodHints()
        )
    finally:
        widget.close()
        standard.close()


def test_integer_spinbox_value_and_range(app, monkeypatch):
    monkeypatch.setattr(module, "_is_android", lambda: True)

    widget = module.AndroidIntegerSpinBox()

    try:
        widget.setRange(-180, 180)
        widget.setValue(-35)

        assert widget.minimum() == -180
        assert widget.maximum() == 180
        assert widget.value() == -35
    finally:
        widget.close()


def test_android_negative_range_uses_signed_keyboard(app, monkeypatch):
    monkeypatch.setattr(module, "_is_android", lambda: True)

    widget = module.AndroidIntegerSpinBox()

    try:
        widget.setRange(-180, 180)

        hint = Qt.InputMethodHint.ImhFormattedNumbersOnly

        assert widget.inputMethodHints() & hint
        assert widget.lineEdit().inputMethodHints() & hint
    finally:
        widget.close()


def test_android_positive_range_uses_digits_keyboard(app, monkeypatch):
    monkeypatch.setattr(module, "_is_android", lambda: True)

    widget = module.AndroidIntegerSpinBox()

    try:
        widget.setRange(0, 100)

        hint = Qt.InputMethodHint.ImhDigitsOnly

        assert widget.inputMethodHints() & hint
        assert widget.lineEdit().inputMethodHints() & hint
    finally:
        widget.close()


def test_android_keyboard_updates_when_minimum_changes(app, monkeypatch):
    monkeypatch.setattr(module, "_is_android", lambda: True)

    widget = module.AndroidIntegerSpinBox()

    try:
        widget.setMinimum(-90)

        signed = Qt.InputMethodHint.ImhFormattedNumbersOnly
        digits = Qt.InputMethodHint.ImhDigitsOnly

        assert widget.lineEdit().inputMethodHints() & signed

        widget.setMinimum(0)

        assert widget.lineEdit().inputMethodHints() & digits
    finally:
        widget.close()
