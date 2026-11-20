from PySide6.QtCore import QLocale
from PySide6.QtWidgets import QDoubleSpinBox


class LocalizedDoubleSpinBox(QDoubleSpinBox):
    """Control experimental para comprobar la entrada decimal Android."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Prueba: punto decimal sin filtros de teclado.
        self.setLocale(QLocale("es_ES"))
        self.setGroupSeparatorShown(False)
