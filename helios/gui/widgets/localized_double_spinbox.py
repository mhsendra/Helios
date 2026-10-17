
from PySide6.QtCore import QEvent
from PySide6.QtCore import QLocale
from PySide6.QtWidgets import QDoubleSpinBox


class LocalizedDoubleSpinBox(QDoubleSpinBox):
    """QDoubleSpinBox con coma decimal y soporte del punto del teclado numérico."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setLocale(QLocale("es_ES"))
        self.setGroupSeparatorShown(False)

        # El foco de edición está en el QLineEdit interno.
        self.lineEdit().installEventFilter(self)

    def eventFilter(self, watched, event):
        if (
            watched is self.lineEdit()
            and event.type() == QEvent.Type.KeyPress
            and event.text() in {".", ","}
        ):
            line_edit = self.lineEdit()
            decimal_point = self.locale().decimalPoint()
            current_text = line_edit.text()
            selected_text = line_edit.selectedText()

            # Permite reemplazar el contenido seleccionado, incluso
            # cuando ya contenía un separador decimal.
            remaining_text = current_text

            if selected_text:
                start = line_edit.selectionStart()
                end = start + len(selected_text)
                remaining_text = (
                    current_text[:start] + current_text[end:]
                )

            if decimal_point not in remaining_text:
                line_edit.insert(decimal_point)

            return True

        return super().eventFilter(watched, event)
