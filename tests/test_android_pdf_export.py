import os
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from helios.gui.widgets.reports_page import ReportsPage


@pytest.fixture
def pdf_page(qtbot, tmp_path):
    project = MagicMock()
    page = ReportsPage(project)
    qtbot.addWidget(page)

    page.set_solar_report_available(True)

    with patch.dict(
        os.environ,
        {"ANDROID_PRIVATE": str(tmp_path)},
    ), patch(
        "helios.gui.widgets.reports_page.is_android",
        return_value=True,
    ), patch.object(
        page,
        "_generate_solar_pdf_to_path",
        side_effect=lambda path: (
            Path(path).write_bytes(b"%PDF-1.4\n") or True
        ),
    ):
        page.generate_solar_pdf_report()

    assert page._pdf_request_id is not None

    yield page

    if getattr(page, "_pdf_timer", None):
        page._pdf_timer.stop()


def write_result(page, status, detail=""):
    result = page._pdf_directory / "pdf_result.txt"

    result.write_text(
        f"{page._pdf_request_id}\n{status}\n{detail}",
        encoding="utf-8",
    )

    return result


def test_android_pdf_request_created(pdf_page):
    request = pdf_page._pdf_directory / "pdf_request.txt"

    assert request.is_file()
    assert request.read_text(encoding="utf-8") == pdf_page._pdf_request_id

    uuid.UUID(pdf_page._pdf_request_id)

    assert pdf_page._pdf_output_path.is_file()
    assert not pdf_page.generate_solar_pdf_button.isEnabled()


@pytest.mark.parametrize("status", ["OK", "CANCELLED", "ERROR"])
def test_android_pdf_result_finishes_request(pdf_page, status):
    output = pdf_page._pdf_output_path

    write_result(pdf_page, status, "Prueba")

    with patch(
        "helios.gui.widgets.reports_page.QMessageBox"
    ):
        pdf_page._check_android_pdf_result()

    assert pdf_page._pdf_request_id is None
    assert not output.exists()
    assert pdf_page.generate_solar_pdf_button.isEnabled()
    assert not pdf_page._pdf_timer.isActive()


def test_android_pdf_ignores_other_request_id(pdf_page):
    result = pdf_page._pdf_directory / "pdf_result.txt"

    result.write_text(
        f"{uuid.uuid4()}\nOK\n",
        encoding="utf-8",
    )

    with patch(
        "helios.gui.widgets.reports_page.QMessageBox"
    ):
        pdf_page._check_android_pdf_result()

    assert pdf_page._pdf_request_id is not None
    assert pdf_page._pdf_timer.isActive()
    assert pdf_page._pdf_output_path.is_file()


def test_android_pdf_incomplete_result_does_not_finish(pdf_page):
    result = pdf_page._pdf_directory / "pdf_result.txt"

    result.write_text(
        f"{pdf_page._pdf_request_id}\nOK",
        encoding="utf-8",
    )

    with patch(
        "helios.gui.widgets.reports_page.QMessageBox"
    ):
        pdf_page._check_android_pdf_result()

    assert pdf_page._pdf_request_id is not None
    assert pdf_page._pdf_timer.isActive()
    assert pdf_page._pdf_output_path.is_file()


def test_android_pdf_prevents_duplicate_requests(pdf_page):
    original_id = pdf_page._pdf_request_id
    original_path = pdf_page._pdf_output_path

    with patch(
        "helios.gui.widgets.reports_page.is_android",
        return_value=True,
    ), patch.object(
        pdf_page,
        "_generate_solar_pdf_to_path",
    ) as generate:
        pdf_page.generate_solar_pdf_report()

    generate.assert_not_called()
    assert pdf_page._pdf_request_id == original_id
    assert pdf_page._pdf_output_path == original_path


def test_android_pdf_incomplete_result_is_not_consumed(pdf_page):
    result = pdf_page._pdf_directory / "pdf_result.txt"

    result.write_text(
        pdf_page._pdf_request_id + chr(10) + "OK",
        encoding="utf-8",
    )

    with patch(
        "helios.gui.widgets.reports_page.QMessageBox"
    ) as message:
        pdf_page._check_android_pdf_result()

    message.critical.assert_not_called()
    message.information.assert_not_called()

    assert result.exists()
    assert pdf_page._pdf_request_id is not None
    assert pdf_page._pdf_timer.isActive()


def test_android_pdf_preserves_disabled_button(qtbot, tmp_path):
    project = MagicMock()
    page = ReportsPage(project)
    qtbot.addWidget(page)

    page.generate_solar_pdf_button.setEnabled(False)

    with patch.dict(
        os.environ,
        {"ANDROID_PRIVATE": str(tmp_path)},
    ), patch(
        "helios.gui.widgets.reports_page.is_android",
        return_value=True,
    ), patch.object(
        page,
        "_generate_solar_pdf_to_path",
        side_effect=lambda path: (
            Path(path).write_bytes(b"%PDF-1.4" + bytes([10])) or True
        ),
    ), patch(
        "helios.gui.widgets.reports_page.QMessageBox"
    ):
        page.generate_solar_pdf_report()

    assert page._pdf_request_id is not None
    assert not page.generate_solar_pdf_button.isEnabled()

    result = page._pdf_directory / "pdf_result.txt"
    result.write_text(
        page._pdf_request_id + chr(10) + "CANCELLED" + chr(10),
        encoding="utf-8",
    )

    with patch(
        "helios.gui.widgets.reports_page.QMessageBox"
    ):
        page._check_android_pdf_result()

    assert page._pdf_request_id is None
    assert not page.generate_solar_pdf_button.isEnabled()


def test_android_pdf_generation_failure_does_not_publish_request(
    qtbot, tmp_path
):
    project = MagicMock()
    page = ReportsPage(project)
    qtbot.addWidget(page)

    page.set_solar_report_available(True)

    with patch.dict(
        os.environ,
        {"ANDROID_PRIVATE": str(tmp_path)},
    ), patch(
        "helios.gui.widgets.reports_page.is_android",
        return_value=True,
    ), patch.object(
        page,
        "_generate_solar_pdf_to_path",
        return_value=False,
    ), patch(
        "helios.gui.widgets.reports_page.QMessageBox"
    ):
        page.generate_solar_pdf_report()

    directory = tmp_path / "helios_pdf"

    assert not (directory / "pdf_request.txt").exists()
    assert getattr(page, "_pdf_request_id", None) is None
    assert page.generate_solar_pdf_button.isEnabled()


def test_android_pdf_allows_second_export(pdf_page):
    first_id = pdf_page._pdf_request_id

    write_result(pdf_page, "CANCELLED")

    with patch(
        "helios.gui.widgets.reports_page.QMessageBox"
    ):
        pdf_page._check_android_pdf_result()

    with patch.dict(
        os.environ,
        {"ANDROID_PRIVATE": str(pdf_page._pdf_directory.parent)},
    ), patch(
        "helios.gui.widgets.reports_page.is_android",
        return_value=True,
    ), patch(
        "helios.gui.widgets.reports_page.QMessageBox"
    ), patch.object(
        pdf_page,
        "_generate_solar_pdf_to_path",
        side_effect=lambda path: (
            Path(path).write_bytes(b"%PDF-1.4" + bytes([10])) or True
        ),
    ):
        pdf_page.generate_solar_pdf_report()

    assert pdf_page._pdf_request_id is not None
    assert pdf_page._pdf_request_id != first_id
    assert pdf_page._pdf_timer.isActive()


@pytest.mark.parametrize("initial_enabled", [True, False])
def test_android_pdf_publication_failure_restores_state(
    qtbot, tmp_path, initial_enabled
):
    project = MagicMock()
    page = ReportsPage(project)
    qtbot.addWidget(page)

    page.set_solar_report_available(True)
    page.generate_solar_pdf_button.setEnabled(initial_enabled)

    pdf_directory = tmp_path / "helios_pdf"

    original_replace = Path.replace

    def fail_request_publication(self, target):
        if self.name == "pdf_request.tmp":
            raise OSError("Fallo simulado al publicar solicitud")
        return original_replace(self, target)

    def create_test_pdf(path):
        Path(path).write_bytes(
            b"%PDF-1.4" + bytes([10])
        )
        return True

    with patch.dict(
        os.environ,
        {"ANDROID_PRIVATE": str(tmp_path)},
    ), patch(
        "helios.gui.widgets.reports_page.is_android",
        return_value=True,
    ), patch.object(
        page,
        "_generate_solar_pdf_to_path",
        side_effect=create_test_pdf,
    ), patch.object(
        Path,
        "replace",
        autospec=True,
        side_effect=fail_request_publication,
    ), patch(
        "helios.gui.widgets.reports_page.QMessageBox"
    ) as message:

        page.generate_solar_pdf_report()

        message.critical.assert_called_once()

    assert page._pdf_request_id is None
    assert page._pdf_output_path is None

    assert (
        page.generate_solar_pdf_button.isEnabled()
        == initial_enabled
    )

    assert not (pdf_directory / "pdf_request.tmp").exists()
    assert not (pdf_directory / "pdf_request.txt").exists()

    assert not list(pdf_directory.glob("*.pdf"))

    timer = getattr(page, "_pdf_timer", None)
    if timer is not None:
        assert not timer.isActive()


def test_android_pdf_unknown_status_finishes_request(
    pdf_page,
):
    request_id = pdf_page._pdf_request_id
    directory = pdf_page._pdf_directory
    output_path = pdf_page._pdf_output_path

    result = directory / "pdf_result.txt"

    result.write_text(
        request_id + chr(10) + "INVALID" + chr(10)
        + "Estado simulado",
        encoding="utf-8",
    )

    with patch(
        "helios.gui.widgets.reports_page.QMessageBox"
    ) as message:
        pdf_page._check_android_pdf_result()

        assert message.critical.call_count == 1

    assert pdf_page._pdf_request_id is None
    assert pdf_page._pdf_output_path is None
    assert not pdf_page._pdf_timer.isActive()
    assert not result.exists()
    assert not output_path.exists()

    # Una segunda consulta no debe volver a mostrar el error.
    with patch(
        "helios.gui.widgets.reports_page.QMessageBox"
    ) as message:
        pdf_page._check_android_pdf_result()
        message.critical.assert_not_called()
