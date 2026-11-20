import uuid
from pathlib import Path
from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QApplication

from helios.gui.widgets.load_data_page import LoadDataPage


@pytest.fixture
def page(qapp, tmp_path, monkeypatch):
    monkeypatch.setenv("ANDROID_PRIVATE", str(tmp_path))

    with patch(
        "helios.gui.widgets.load_data_page.is_android",
        return_value=True,
    ):
        widget = LoadDataPage(
            project=None,
            main_window=None,
        )
        yield widget
        if getattr(widget, "_excel_timer", None) is not None:
            widget._excel_timer.stop()
        widget.close()


def test_creates_request(page, tmp_path):
    page.browse_file()

    directory = tmp_path / "helios_excel"
    request = directory / "excel_request.txt"

    assert request.is_file()
    assert uuid.UUID(request.read_text().strip())
    assert not page.browse_button.isEnabled()
    assert not page.load_button.isEnabled()


def test_successful_selection(page, tmp_path):
    page.browse_file()

    directory = tmp_path / "helios_excel"
    request_id = page._excel_request_id
    excel = directory / f"{request_id}.xlsx"
    excel.write_bytes(b"test excel")

    (directory / "excel_result.txt").write_text(
        f"{request_id}\nOK\n{excel}",
        encoding="utf-8",
    )

    page._check_android_excel_result()

    assert page._excel_path == str(excel)
    assert page.path_edit.text() == excel.name
    assert page.browse_button.isEnabled()
    assert page.load_button.isEnabled()
    assert page._excel_request_id is None


def test_cancelled_selection(page, tmp_path):
    page.browse_file()

    directory = tmp_path / "helios_excel"
    request_id = page._excel_request_id

    (directory / "excel_result.txt").write_text(
        f"{request_id}\nCANCELLED\n",
        encoding="utf-8",
    )

    page._check_android_excel_result()

    assert page._excel_path is None
    assert page.browse_button.isEnabled()
    assert page.load_button.isEnabled()
    assert "cancelada" in page.info_label.text().lower()


def test_selection_error(page, tmp_path):
    page.browse_file()

    directory = tmp_path / "helios_excel"
    request_id = page._excel_request_id

    (directory / "excel_result.txt").write_text(
        f"{request_id}\nERROR\nNo se puede abrir documento",
        encoding="utf-8",
    )

    page._check_android_excel_result()

    assert page._excel_path is None
    assert page.browse_button.isEnabled()
    assert page.load_button.isEnabled()
    assert "error" in page.info_label.text().lower()


def test_ignores_old_result(page, tmp_path):
    page.browse_file()

    directory = tmp_path / "helios_excel"

    (directory / "excel_result.txt").write_text(
        f"{uuid.uuid4()}\nCANCELLED\n",
        encoding="utf-8",
    )

    page._check_android_excel_result()

    assert page._excel_request_id is not None
    assert not page.browse_button.isEnabled()
    assert page._excel_timer.isActive()


@pytest.mark.parametrize(
    "original_name",
    [
        "Consumos_2025.xlsx",
        "Consumos eléctricos 2025.xlsx",
    ],
)
def test_selection_preserves_original_filename(
    page, tmp_path, original_name
):
    page.browse_file()

    directory = tmp_path / "helios_excel"
    request_id = page._excel_request_id

    excel = directory / f"{request_id}.xlsx"
    excel.write_bytes(b"test excel")

    (directory / "excel_result.txt").write_text(
        f"{request_id}\nOK\n{excel}\n{original_name}",
        encoding="utf-8",
    )

    page._check_android_excel_result()

    assert page._excel_path == str(excel)
    assert page.path_edit.text() == original_name
    assert page.load_button.isEnabled()
    assert page._excel_request_id is None


def test_selection_accepts_legacy_three_line_result(
    page, tmp_path
):
    page.browse_file()

    directory = tmp_path / "helios_excel"
    request_id = page._excel_request_id

    excel = directory / f"{request_id}.xlsx"
    excel.write_bytes(b"test excel")

    (directory / "excel_result.txt").write_text(
        f"{request_id}\nOK\n{excel}",
        encoding="utf-8",
    )

    page._check_android_excel_result()

    assert page._excel_path == str(excel)
    assert page.path_edit.text() == excel.name
    assert page.load_button.isEnabled()
