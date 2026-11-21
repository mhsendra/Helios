"""Selector animado de secciones exclusivo de la interfaz Android."""

from PySide6.QtCore import (
    Qt,
    QRect,
    Property,
    Signal,
    QEasingCurve,
    QPropertyAnimation,
)
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout


class AndroidSectionSwitch(QWidget):
    """Selector de dos posiciones con transición horizontal."""

    currentTextChanged = Signal(str)

    SECTIONS = ("Entrada de datos", "Resultados")

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("android_section_switch")
        self.setFixedHeight(48)
        self.setMinimumWidth(240)

        self._current_text = self.SECTIONS[0]
        self._position = 0.0

        self.setStyleSheet(
            """
            AndroidSectionSwitch {
                background-color: #252525;
                border: 1px solid #454545;
                border-radius: 24px;
            }
            """
        )

        self._indicator = QWidget(self)
        self._indicator.setObjectName("android_section_indicator")
        self._indicator.setStyleSheet(
            "background-color: #505050; border-radius: 20px;"
        )
        self._indicator.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )

        self._buttons = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)

        for section in self.SECTIONS:
            button = QPushButton(section, self)
            button.setFlat(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setStyleSheet(
                """
                QPushButton {
                    background: transparent;
                    color: white;
                    border: none;
                    font-weight: 600;
                    font-size: 12px;
                }
                """
            )
            button.clicked.connect(
                lambda checked=False, name=section:
                self.setCurrentText(name)
            )
            layout.addWidget(button, 1)
            self._buttons.append(button)

        self._animation = QPropertyAnimation(self, b"position", self)
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self._update_indicator()

    def count(self):
        """Número de secciones disponibles."""
        return len(self.SECTIONS)

    def itemText(self, index):
        """Texto de una sección por índice, como en QComboBox."""
        if 0 <= index < len(self.SECTIONS):
            return self.SECTIONS[index]
        return ""

    def currentIndex(self):
        """Índice de la sección seleccionada."""
        return self.SECTIONS.index(self._current_text)

    def setCurrentIndex(self, index):
        """Selecciona una sección mediante su índice."""
        if 0 <= index < len(self.SECTIONS):
            self.setCurrentText(self.SECTIONS[index])

    def currentText(self):
        return self._current_text

    def setCurrentText(self, section):
        if section not in self.SECTIONS:
            return

        if section == self._current_text:
            return

        self._current_text = section

        target = float(self.SECTIONS.index(section))

        self._animation.stop()
        self._animation.setStartValue(self._position)
        self._animation.setEndValue(target)
        self._animation.start()

        self.currentTextChanged.emit(section)

    def getPosition(self):
        return self._position

    def setPosition(self, value):
        self._position = float(value)
        self._update_indicator()

    position = Property(float, getPosition, setPosition)

    def _update_indicator(self):
        margin = 4
        available = max(0, self.width() - 2 * margin)
        segment = available / 2

        x = margin + segment * self._position

        self._indicator.setGeometry(
            QRect(
                round(x),
                margin,
                round(segment),
                max(0, self.height() - 2 * margin),
            )
        )

        self._indicator.lower()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_indicator()
