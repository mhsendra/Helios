"""Integración de los controles enteros en los formularios."""

from unittest.mock import MagicMock

import pytest

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

import helios.gui.widgets.android_integer_spinbox as integer_module
import helios.gui.widgets.solar_config_page as config_module
import helios.gui.widgets.solar_optimization_page as optimization_module
import helios.gui.widgets.solar_page as solar_module

from helios.gui.widgets.android_integer_spinbox import (
    AndroidIntegerSpinBox,
)


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance()
    return application or QApplication([])


@pytest.fixture
def android_environment(monkeypatch):
    """Simula Android antes de construir los controles."""
    monkeypatch.setattr(
        integer_module,
        "_is_android",
        lambda: True,
    )

    for module in (
        config_module,
        optimization_module,
        solar_module,
    ):
        monkeypatch.setattr(
            module,
            "is_android",
            lambda: True,
        )


@pytest.mark.parametrize(
    "module, class_name, fields",
    [
        (
            config_module,
            "SolarConfigPage",
            (
                ("tilt_spinbox", 0, 90),
                ("azimuth_spinbox", -180, 180),
                ("reference_year_spinbox", 2000, 2100),
            ),
        ),
        (
            optimization_module,
            "SolarOptimizationPage",
            (
                ("min_panels_spinbox", 1, 1000),
                ("max_panels_spinbox", 1, 1000),
            ),
        ),
        (
            solar_module,
            "SolarPage",
            (
                ("tilt_spinbox", 0, 90),
                ("azimuth_spinbox", -180, 180),
            ),
        ),
    ],
)
def test_android_integer_controls_in_real_pages(
    app,
    android_environment,
    module,
    class_name,
    fields,
):
    project = MagicMock()
    project.solar_configuration = None
    project.dataset = None

    page_class = getattr(module, class_name)

    page = page_class(project)

    try:
        for name, minimum, maximum in fields:
            widget = getattr(page, name)

            assert isinstance(
                widget,
                AndroidIntegerSpinBox,
            ), name

            assert widget.minimum() == minimum, name
            assert widget.maximum() == maximum, name

            if minimum < 0:
                hint = (
                    Qt.InputMethodHint.ImhFormattedNumbersOnly
                )

                widget.setValue(-35)
                assert widget.value() == -35

            else:
                hint = Qt.InputMethodHint.ImhDigitsOnly

            assert widget.inputMethodHints() & hint, name
            assert (
                widget.lineEdit().inputMethodHints() & hint
            ), name

    finally:
        page.close()
