import sys

from PySide6.QtWidgets import QApplication

from helios.gui.main_window import MainWindow
from helios.styles.dark import DARK_STYLE

from helios.core.economics_configuration import EconomicsConfiguration


def main():

    app = QApplication(sys.argv)

    app.setStyleSheet(DARK_STYLE)

    economics_configuration = EconomicsConfiguration(
        installation_cost=12490.0
    )

    window = MainWindow(
        economics_configuration
    )

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()