import sys
import traceback


def _helios_boot_log(message):
    print(
        f"[HELIOS-BOOT] {message}",
        file=sys.stderr,
        flush=True,
    )


def _helios_boot_excepthook(exc_type, exc_value, exc_traceback):
    _helios_boot_log("EXCEPCION NO CONTROLADA")
    traceback.print_exception(
        exc_type,
        exc_value,
        exc_traceback,
        file=sys.stderr,
    )
    sys.stderr.flush()


sys.excepthook = _helios_boot_excepthook

_helios_boot_log("01 - main.py iniciado")
_helios_boot_log("02 - Importando helios.gui.app")

try:
    from helios.gui.app import main
except BaseException:
    _helios_boot_log("ERROR importando helios.gui.app")
    traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()
    raise

_helios_boot_log("03 - helios.gui.app importado correctamente")


if __name__ == "__main__":
    _helios_boot_log("04 - Invocando main()")

    try:
        main()
    except BaseException:
        _helios_boot_log("ERROR durante main()")
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        raise
