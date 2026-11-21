"""Control entero con teclado numérico Android."""

import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSpinBox


def _is_android():
    return (
        sys.platform == "android"
        or "ANDROID_ARGUMENT" in os.environ
        or "ANDROID_PRIVATE" in os.environ
    )


class AndroidIntegerSpinBox(QSpinBox):
    """QSpinBox que solicita teclado entero en Android."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._android_mode = _is_android()

        if self._android_mode:
            self._configure_numeric_keyboard()

    def _configure_numeric_keyboard(self):
        """Selecciona teclado entero con soporte de signo si procede."""
        if self.minimum() < 0:
            hint = Qt.InputMethodHint.ImhFormattedNumbersOnly
        else:
            hint = Qt.InputMethodHint.ImhDigitsOnly

        self.setInputMethodHints(hint)
        self.lineEdit().setInputMethodHints(hint)

    def setRange(self, minimum, maximum):
        super().setRange(minimum, maximum)

        if getattr(self, "_android_mode", False):
            self._configure_numeric_keyboard()

    def setMinimum(self, minimum):
        super().setMinimum(minimum)

        if getattr(self, "_android_mode", False):
            self._configure_numeric_keyboard()
