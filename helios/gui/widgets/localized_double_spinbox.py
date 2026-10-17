
from PySide6.QtCore import QEvent, QLocale, Qt
from PySide6.QtWidgets import QDoubleSpinBox


class LocalizedDoubleSpinBox(QDoubleSpinBox):
    """QDoubleSpinBox con coma decimal y soporte del punto numérico."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setLocale(QLocale("es_ES"))
        self.setGroupSeparatorShown(False)

        # El evento puede llegar tanto al spinbox como al editor interno.
        self.installEventFilter(self)
        self.lineEdit().installEventFilter(self)

    def eventFilter(self, watched, event):
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
