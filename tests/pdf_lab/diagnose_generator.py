import sys
import time
import traceback
import resource
from pathlib import Path
from unittest.mock import patch

from reportlab.platypus.doctemplate import BaseDocTemplate

from helios.reports.solar_report_generator import (
    SolarReportGenerator,
    NumberedCanvas,
)

from tests.test_solar_report_generator import TestSolarReportGenerator


OUTPUT = Path("tests/pdf_lab/output/solar_diagnostic.pdf")

start = time.perf_counter()


def log(message):
    elapsed = time.perf_counter() - start
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    print(
        f"[{elapsed:8.3f}s] "
        f"[RAM MAX {rss:8.1f} MiB] "
        f"{message}",
        flush=True,
    )


original_multibuild = BaseDocTemplate.multiBuild
original_show_page = NumberedCanvas.showPage
original_save = NumberedCanvas.save

page_count = 0


def traced_multibuild(self, story, *args, **kwargs):
    log(f"INICIO multiBuild - {len(story)} elementos")
    try:
        result = original_multibuild(self, story, *args, **kwargs)
        log("FIN multiBuild")
        return result
    except BaseException:
        log("ERROR en multiBuild")
        raise


def traced_show_page(self, *args, **kwargs):
    global page_count
    page_count += 1

    if page_count <= 5 or page_count % 10 == 0:
        log(f"showPage llamada {page_count}")

    return original_show_page(self, *args, **kwargs)


def traced_save(self, *args, **kwargs):
    log(
        "INICIO NumberedCanvas.save - "
        f"{len(self._saved_page_states)} paginas almacenadas"
    )

    result = original_save(self, *args, **kwargs)

    log("FIN NumberedCanvas.save")
    return result


try:
    log("Preparando datos de prueba")

    data = TestSolarReportGenerator._report_data()

    log("Datos preparados")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with (
        patch.object(
            BaseDocTemplate,
            "multiBuild",
            traced_multibuild,
        ),
        patch.object(
            NumberedCanvas,
            "showPage",
            traced_show_page,
        ),
        patch.object(
            NumberedCanvas,
            "save",
            traced_save,
        ),
    ):
        log("INICIO SolarReportGenerator.generate")

        SolarReportGenerator().generate(data, OUTPUT)

        log("FIN SolarReportGenerator.generate")

    size = OUTPUT.stat().st_size
    header = OUTPUT.read_bytes()[:8]

    log(f"PDF generado: {size} bytes")
    log(f"Cabecera: {header!r}")

    assert size > 100
    assert header.startswith(b"%PDF-")

    log("RESULTADO: OK")

except BaseException:
    log("RESULTADO: ERROR")
    traceback.print_exc()
    sys.exit(1)
