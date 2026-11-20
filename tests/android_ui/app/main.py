import sys
from PySide6.QtGui import QColor, QPalette, QDoubleValidator

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QGroupBox,
    QLineEdit,
)

from localized_double_spinbox import LocalizedDoubleSpinBox


class TestWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Helios UI Test")
        self.setAutoFillBackground(True)

        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                color: #111111;
                font-size: 16px;
            }
            QDoubleSpinBox, QLineEdit {
                background-color: #303030;
                color: #FFFFFF;
                border: 2px solid #888888;
                border-radius: 5px;
                padding: 8px;
                min-height: 38px;
                selection-background-color: #1769AA;
                selection-color: #FFFFFF;
            }
            QPushButton {
                background-color: #1769AA;
                color: #FFFFFF;
                padding: 12px;
                border-radius: 6px;
            }
            QGroupBox {
                border: 1px solid #888888;
                margin-top: 12px;
                padding-top: 12px;
            }
        """)

        layout = QVBoxLayout(self)

        title = QLabel("PRUEBA DE DECIMALES")
        layout.addWidget(title)

        instructions = QLabel(
            "Escribe 8,10 o 8.10 sin salir del campo. "
            "Después prueba las coordenadas."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        content = QVBoxLayout(container)

        group = QGroupBox("Configuración solar")
        form = QFormLayout(group)
        form.setRowWrapPolicy(QFormLayout.WrapAllRows)

        self.power = LocalizedDoubleSpinBox()
        self.power.setRange(0.01, 1000.0)
        self.power.setDecimals(2)
        self.power.setSuffix(" kWp")
        self.power.setValue(1.0)

        self.losses = LocalizedDoubleSpinBox()
        self.losses.setRange(0.0, 100.0)
        self.losses.setDecimals(1)
        self.losses.setSuffix(" %")

        self.latitude = LocalizedDoubleSpinBox()
        self.latitude.setRange(-90.0, 90.0)
        self.latitude.setDecimals(6)

        self.longitude = LocalizedDoubleSpinBox()
        self.longitude.setRange(-180.0, 180.0)
        self.longitude.setDecimals(6)

        form.addRow("Potencia instalada", self.power)
        form.addRow("Pérdidas del sistema", self.losses)
        form.addRow("Latitud", self.latitude)
        form.addRow("Longitud", self.longitude)

        content.addWidget(group)

        diagnostic_group = QGroupBox("Diagnóstico del teclado Android")
        diagnostic_form = QFormLayout(diagnostic_group)
        diagnostic_form.setRowWrapPolicy(QFormLayout.WrapAllRows)

        self.plain_input = QLineEdit()
        self.plain_input.setPlaceholderText("Escribe 8.10")
        self.plain_input.setText("")
        diagnostic_form.addRow(
            "Texto libre (sin validador)",
            self.plain_input,
        )

        self.validated_input = QLineEdit()
        self.validated_input.setPlaceholderText("Escribe 8.10")

        validator = QDoubleValidator(
            0.0,
            1000.0,
            2,
            self.validated_input,
        )
        validator.setLocale(self.power.locale())
        self.validated_input.setValidator(validator)

        diagnostic_form.addRow(
            "Texto con validador decimal",
            self.validated_input,
        )

        content.addWidget(diagnostic_group)
        content.addStretch()

        scroll.setWidget(container)
        layout.addWidget(scroll)

        button = QPushButton("Comprobar valores")
        button.clicked.connect(self.show_values)
        layout.addWidget(button)

        self.result = QLabel("Esperando prueba...")
        self.result.setWordWrap(True)
        layout.addWidget(self.result)

    def show_values(self):
        values = [
            ("Potencia", self.power),
            ("Pérdidas", self.losses),
            ("Latitud", self.latitude),
            ("Longitud", self.longitude),
        ]

        results = [
            f"{name}: valor={widget.value()!r} | texto={widget.text()!r}"
            for name, widget in values
        ]

        results.append(
            f"Texto libre: {self.plain_input.text()!r}"
        )
        results.append(
            f"Texto validado: {self.validated_input.text()!r}"
        )

        self.result.setText("\n".join(results))


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#000000"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#000000"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#E8E8E8"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#000000"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#1769AA"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(palette)

    window = TestWindow()
    window.resize(400, 700)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
