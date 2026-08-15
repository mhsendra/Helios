from unittest.mock import MagicMock

import pandas as pd

from helios.core.controllers.validation_controller import (
    ValidationController
)


def create_controller():

    analyzer = MagicMock()

    analyzer.validation_engine = MagicMock()

    return ValidationController(analyzer), analyzer


# ==========================================================
# Validación temporal
# ==========================================================


def test_validate_timeseries(capsys):

    controller, analyzer = create_controller()

    index = pd.DatetimeIndex([
        "2025-01-01 00:00:00",
        "2025-01-01 01:00:00",
    ])

    analyzer.dataset.index = index

    controller.validate_timeseries()

    output = capsys.readouterr().out

    assert "=== VALIDACIÓN TEMPORAL ===" in output
    assert "Primer registro" in output
    assert "Último registro" in output


# ==========================================================
# Horas esperadas
# ==========================================================


def test_expected_hours_normal_day():

    controller, _ = create_controller()

    result = controller._expected_hours_for_day(
        pd.Timestamp("2025-02-15")
    )

    assert result == set(range(1, 25))


def test_expected_hours_summer_time_change():

    controller, _ = create_controller()

    result = controller._expected_hours_for_day(
        pd.Timestamp("2025-03-30")
    )

    assert result == set(range(1, 24))


def test_expected_hours_winter_time_change():

    controller, _ = create_controller()

    result = controller._expected_hours_for_day(
        pd.Timestamp("2025-10-26")
    )

    assert result == set(range(1, 26))


# ==========================================================
# Horas ausentes
# ==========================================================


def test_find_missing_hours_valid_dataset(capsys):

    controller, analyzer = create_controller()

    index = pd.date_range(
        "2025-01-01 00:00:00",
        periods=24,
        freq="h"
    )

    analyzer.dataset = pd.DataFrame(
        {
            "Hora": range(1, 25)
        },
        index=index
    )

    result = controller.find_missing_hours()

    assert result == {
        "valid": True,
        "errors": 0
    }

    output = capsys.readouterr().out

    assert "Todos los días tienen la secuencia horaria correcta." in output


def test_find_missing_hours_detects_missing_hour(capsys):

    controller, analyzer = create_controller()

    index = pd.date_range(
        "2025-01-01 00:00:00",
        periods=23,
        freq="h"
    )

    analyzer.dataset = pd.DataFrame(
        {
            "Hora": list(range(1, 24))
        },
        index=index
    )

    result = controller.find_missing_hours()

    assert result == {
        "valid": False,
        "errors": 1
    }

    output = capsys.readouterr().out

    assert "2025-01-01" in output
    assert "Horas ausentes" in output


# ==========================================================
# Duplicados
# ==========================================================


def test_find_duplicate_timestamps():

    controller, analyzer = create_controller()

    duplicates = ["duplicate_1", "duplicate_2"]

    analyzer.validation_engine.find_duplicate_timestamps.return_value = (
        duplicates
    )

    controller.find_duplicate_timestamps()

    analyzer.validation_engine.find_duplicate_timestamps.assert_called_once_with(
        analyzer.dataset
    )

    assert analyzer.duplicates == duplicates


# ==========================================================
# Gaps
# ==========================================================


def test_calculate_gap_summary():

    controller, analyzer = create_controller()

    summary = {
        "total_gaps": 3,
        "total_missing": 5
    }

    analyzer.validation_engine.calculate_gap_summary.return_value = summary

    controller.calculate_gap_summary()

    analyzer.validation_engine.calculate_gap_summary.assert_called_once_with(
        analyzer.dataset
    )

    assert analyzer.gap_summary == summary


# ==========================================================
# Inspect gap
# ==========================================================


def test_inspect_gap_nonexistent(capsys):

    controller, analyzer = create_controller()

    analyzer.dataset = pd.DataFrame(
        {
            "gap_id": [1, 1],
            "Fecha": ["2025-01-01", "2025-01-01"],
            "Hora": [1, 2],
            "AE_kWh": [1.0, 2.0],
            "gap_size": [2, 2],
        },
        index=pd.date_range(
            "2025-01-01",
            periods=2,
            freq="h"
        )
    )

    controller.inspect_gap(99)

    output = capsys.readouterr().out

    assert "No existe el bloque de huecos 99." in output


def test_inspect_gap_existing(capsys):

    controller, analyzer = create_controller()

    analyzer.dataset = pd.DataFrame(
        {
            "gap_id": [1, 1],
            "Fecha": ["2025-01-01", "2025-01-01"],
            "Hora": [1, 2],
            "AE_kWh": [1.0, 2.0],
            "gap_size": [2, 2],
        },
        index=pd.date_range(
            "2025-01-01",
            periods=2,
            freq="h"
        )
    )

    controller.inspect_gap(1)

    output = capsys.readouterr().out

    assert "HELIOS - GAP #1" in output
    assert "Duración........ 2 horas" in output
    assert "Registros:" in output


# ==========================================================
# Inspect data
# ==========================================================


def test_inspect_data(capsys):

    controller, analyzer = create_controller()

    analyzer.dataset = pd.DataFrame(
        {
            "Fecha": ["2025-01-01", "2025-01-01"],
            "Hora": [1, 2],
            "AE_kWh": [1.0, None],
        }
    )

    controller.inspect_data()

    output = capsys.readouterr().out

    assert "=== Calidad de los datos ===" in output
    assert "Registros totales: 2" in output
    assert "Duplicados:" in output


# ==========================================================
# Calculate completo
# ==========================================================


def test_calculate():

    controller, analyzer = create_controller()

    controller.validate_timeseries = MagicMock()
    controller.find_missing_hours = MagicMock()
    controller.find_duplicate_timestamps = MagicMock()
    controller.calculate_quality = MagicMock()
    controller.calculate_gap_summary = MagicMock()

    analyzer.quality = {
        "missing_pct": 1.5,
        "corrected_pct": 2.5,
        "zero_days": 3,
        "anomaly_days": 4
    }

    controller.calculate()

    controller.validate_timeseries.assert_called_once_with()
    controller.find_missing_hours.assert_called_once_with()
    controller.find_duplicate_timestamps.assert_called_once_with()
    controller.calculate_quality.assert_called_once_with()
    controller.calculate_gap_summary.assert_called_once_with()

    assert analyzer.validation_stats == {
        "missing_pct": 1.5,
        "corrected_pct": 2.5,
        "zero_days": 3,
        "anomaly_days": 4
    }


# ==========================================================
# Reports
# ==========================================================


def test_reports():

    controller, analyzer = create_controller()

    controller.quality_report = MagicMock()
    controller.duplicate_report = MagicMock()
    controller.gap_report = MagicMock()

    controller.reports()

    controller.quality_report.assert_called_once_with()
    controller.gap_report.assert_called_once_with()
    controller.duplicate_report.assert_called_once_with()

# ==========================================================
# Quality
# ==========================================================


def test_calculate_quality():

    controller, analyzer = create_controller()

    quality = {
        "missing_pct": 1.5,
        "corrected_pct": 2.5,
        "zero_days": 3,
        "anomaly_days": 4
    }

    analyzer.quality_engine.calculate.return_value = quality

    controller.calculate_quality()

    analyzer.quality_engine.calculate.assert_called_once_with(
        analyzer.dataset
    )

    assert analyzer.quality == quality


# ==========================================================
# Reports individuales
# ==========================================================


def test_quality_report():

    controller, analyzer = create_controller()

    analyzer.quality = {
        "missing_pct": 1.5
    }

    controller.quality_report()

    analyzer.quality_reporter.quality.assert_called_once_with(
        analyzer.quality
    )


def test_duplicate_report():

    controller, analyzer = create_controller()

    analyzer.duplicates = ["duplicate_1"]

    controller.duplicate_report()

    analyzer.quality_reporter.duplicates.assert_called_once_with(
        analyzer.duplicates
    )


def test_gap_report():

    controller, analyzer = create_controller()

    analyzer.gap_summary = {
        "total_gaps": 3,
        "total_missing": 5
    }

    controller.gap_report()

    analyzer.quality_reporter.gap.assert_called_once_with(
        analyzer.gap_summary
    )