import sys

from PySide6.QtWidgets import QApplication

from helios.gui.main_window import MainWindow

from helios.styles.dark import DARK_STYLE

def main():

    app = QApplication(sys.argv)

    app.setStyleSheet(DARK_STYLE)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()