import os
import sys


from PySide6.QtCore import QEvent, QLocale, Qt
from PySide6.QtGui import QInputMethodEvent
from PySide6.QtWidgets import QDoubleSpinBox


def _is_android():
    """Detecta la ejecución bajo Python-for-Android."""
    return (
        sys.platform == "android"
        or "ANDROID_ARGUMENT" in os.environ
        or "ANDROID_PRIVATE" in os.environ
    )


class LocalizedDoubleSpinBox(QDoubleSpinBox):
    """QDoubleSpinBox con coma decimal y soporte del punto numérico."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._android_mode = _is_android()

        self.setLocale(
            QLocale("en_US" if self._android_mode else "es_ES")
        )
        self.setGroupSeparatorShown(False)

        # En Android dejamos que Qt procese directamente el teclado.
        # En Windows conservamos la conversión del teclado numérico.
        if not self._android_mode:
            self.installEventFilter(self)
            self.lineEdit().installEventFilter(self)

    def eventFilter(self, watched, event):
        if self._android_mode:
            return super().eventFilter(watched, event)

        if (
            watched is self.lineEdit()
            and event.type() == QEvent.Type.InputMethod
        ):
            committed_text = event.commitString()

            if "." in committed_text:
                decimal_point = self.locale().decimalPoint()

                normalized_text = committed_text.replace(
                    ".", decimal_point
                )

                normalized_event = QInputMethodEvent(
                    event.preeditString(),
                    event.attributes(),
                )

                normalized_event.setCommitString(
                    normalized_text,
                    event.replacementStart(),
                    event.replacementLength(),
                )

                return self.lineEdit().event(
                    normalized_event
                )
        if event.type() != QEvent.Type.KeyPress:
            return super().eventFilter(watched, event)

        if watched not in (self, self.lineEdit()):
            return super().eventFilter(watched, event)

        key = event.key()
        text = event.text()
        modifiers = event.modifiers()

        is_decimal_key = (
            text in {".", ","}
            or event.nativeVirtualKey() == 0x6E
            or (
                key == Qt.Key.Key_Period
                and bool(
                    modifiers & Qt.KeyboardModifier.KeypadModifier
                )
            )
        )

        if not is_decimal_key:
            return super().eventFilter(watched, event)

        line_edit = self.lineEdit()
        decimal_point = self.locale().decimalPoint()

        current_text = line_edit.text()
        selected_text = line_edit.selectedText()
        remaining_text = current_text

        if selected_text:
            start = line_edit.selectionStart()
            end = start + len(selected_text)
            remaining_text = (
                current_text[:start] + current_text[end:]
            )

        # Evita insertar una segunda coma decimal.
        if decimal_point not in remaining_text:
            line_edit.insert(decimal_point)

        # Evita que Qt procese también el punto original.
        return True
