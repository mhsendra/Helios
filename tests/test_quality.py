import pandas as pd
import pytest

from helios.core.quality import DataQualityEngine


def create_engine():

    return DataQualityEngine()


def create_dataset(statuses):

    index = pd.date_range(
        "2025-01-01",
        periods=len(statuses),
        freq="h"
    )

    return pd.DataFrame(
        {
            "data_status": statuses
        },
        index=index
    )


# ==========================================================
# Cálculo básico
# ==========================================================


def test_calculate_excellent():

    engine = create_engine()

    dataset = create_dataset(
        ["original"] * 100
    )

    result = engine.calculate(dataset)

    assert result is engine.quality

    assert result["total_hours"] == 100
    assert result["valid_hours"] == 100
    assert result["missing_hours"] == 0
    assert result["duplicates"] == 0
    assert result["coverage"] == pytest.approx(100.0)
    assert result["rating"] == "EXCELENTE"


def test_calculate_missing_hours():

    engine = create_engine()

    dataset = create_dataset(
        ["original"] * 99
        + ["missing"]
    )

    result = engine.calculate(dataset)

    assert result["total_hours"] == 100
    assert result["valid_hours"] == 99
    assert result["missing_hours"] == 1
    assert result["duplicates"] == 0
    assert result["coverage"] == pytest.approx(99.0)
    assert result["rating"] == "EXCELENTE"


# ==========================================================
# Ratings
# ==========================================================


def test_rating_muy_buena():

    engine = create_engine()

    dataset = create_dataset(
        ["original"] * 98
        + ["missing"] * 2
    )

    result = engine.calculate(dataset)

    assert result["coverage"] == pytest.approx(98.0)
    assert result["rating"] == "MUY BUENA"


def test_rating_buena():

    engine = create_engine()

    dataset = create_dataset(
        ["original"] * 96
        + ["missing"] * 4
    )

    result = engine.calculate(dataset)

    assert result["coverage"] == pytest.approx(96.0)
    assert result["rating"] == "BUENA"


def test_rating_revisar():

    engine = create_engine()

    dataset = create_dataset(
        ["original"] * 94
        + ["missing"] * 6
    )

    result = engine.calculate(dataset)

    assert result["coverage"] == pytest.approx(94.0)
    assert result["rating"] == "REVISAR"


# ==========================================================
# Duplicados
# ==========================================================


def test_calculate_detects_duplicates():

    engine = create_engine()

    index = pd.DatetimeIndex(
        [
            pd.Timestamp("2025-01-01 00:00"),
            pd.Timestamp("2025-01-01 01:00"),
            pd.Timestamp("2025-01-01 01:00"),
            pd.Timestamp("2025-01-01 02:00"),
        ]
    )

    dataset = pd.DataFrame(
        {
            "data_status": [
                "original",
                "original",
                "original",
                "missing",
            ]
        },
        index=index
    )

    result = engine.calculate(dataset)

    assert result["total_hours"] == 4
    assert result["valid_hours"] == 3
    assert result["missing_hours"] == 1
    assert result["duplicates"] == 1
    assert result["coverage"] == pytest.approx(75.0)
    assert result["rating"] == "REVISAR"


# ==========================================================
# Estado
# ==========================================================


def test_quality_is_created_after_calculation():

    engine = create_engine()

    assert not hasattr(
        engine,
        "quality"
    )

    dataset = create_dataset(
        ["original", "original"]
    )

    result = engine.calculate(dataset)

    assert hasattr(
        engine,
        "quality"
    )

    assert result == engine.quality

def test_calculate_empty_dataset():

    engine = create_engine()

    dataset = create_dataset([])

    result = engine.calculate(dataset)

    assert result["total_hours"] == 0
    assert result["valid_hours"] == 0
    assert result["missing_hours"] == 0
    assert result["duplicates"] == 0
    assert result["coverage"] == pytest.approx(0.0)
    assert result["rating"] == "REVISAR"