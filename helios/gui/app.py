import sys

from PySide6.QtWidgets import QApplication

from helios.gui.main_window import MainWindow
from helios.styles.dark import DARK_STYLE

from helios.core.economics_configuration import EconomicsConfiguration

import traceback


def excepthook(exc_type, exc_value, exc_traceback):
    print("\n" + "=" * 80)
    print("EXCEPCIÓN NO CONTROLADA EN HELIOS")
    print("=" * 80)
    traceback.print_exception(
        exc_type,
        exc_value,
        exc_traceback,
    )
    print("=" * 80 + "\n")


sys.excepthook = excepthook


def main():

    def boot_log(message):
        print(
            f"[HELIOS-BOOT] {message}",
            file=sys.stderr,
            flush=True,
        )

    boot_log("05 - Creando QApplication")
    app = QApplication(sys.argv)
    boot_log("06 - QApplication creada")

    boot_log("07 - Aplicando estilo")
    app.setStyleSheet(DARK_STYLE)
    boot_log("08 - Estilo aplicado")

    boot_log("09 - Creando EconomicsConfiguration")
    economics_configuration = EconomicsConfiguration()
    boot_log("10 - EconomicsConfiguration creada")

    boot_log("11 - Construyendo MainWindow")
    window = MainWindow(
        economics_configuration
    )
    boot_log("12 - MainWindow construida")

    boot_log("13 - Mostrando ventana")
    window.show()
    boot_log("14 - Ventana mostrada")

    boot_log("15 - Iniciando bucle de eventos Qt")
    exit_code = app.exec()
    boot_log(
        f"16 - Bucle de eventos finalizado: {exit_code}"
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()