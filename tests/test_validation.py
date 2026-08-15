import pandas as pd

from helios.core.validation import ValidationEngine


# ==========================================================
# Helpers
# ==========================================================

def create_engine():

    return ValidationEngine()


# ==========================================================
# Estado inicial
# ==========================================================

def test_initial_state():

    engine = create_engine()

    assert engine.gap_summary is None
    assert engine.duplicates is None


# ==========================================================
# Gap summary
# ==========================================================

def test_calculate_gap_summary_without_gaps():

    engine = create_engine()

    index = pd.date_range(
        "2025-01-01",
        periods=3,
        freq="h"
    )

    dataset = pd.DataFrame(
        {
            "gap_id": [None, None, None],
            "gap_size": [None, None, None],
            "gap_type": [None, None, None],
            "data_status": [
                "valid",
                "valid",
                "valid"
            ]
        },
        index=index
    )

    result = engine.calculate_gap_summary(
        dataset
    )

    assert result is None
    assert engine.gap_summary is None


def test_calculate_gap_summary():

    engine = create_engine()

    index = pd.to_datetime(
        [
            "2025-01-01 00:00",
            "2025-01-01 01:00",
            "2025-01-01 02:00",
            "2025-01-01 03:00",
            "2025-01-01 04:00",
            "2025-01-01 05:00",
        ]
    )

    dataset = pd.DataFrame(
        {
            "gap_id": [
                None,
                "G1",
                "G1",
                "G2",
                "G2",
                None
            ],
            "gap_size": [
                None,
                2,
                2,
                3,
                3,
                None
            ],
            "gap_type": [
                None,
                "small",
                "small",
                "large",
                "large",
                None
            ],
            "data_status": [
                "valid",
                "missing",
                "missing",
                "missing",
                "missing",
                "valid"
            ]
        },
        index=index
    )

    result = engine.calculate_gap_summary(
        dataset
    )

    assert result is engine.gap_summary

    assert set(result.keys()) == {
        "gaps",
        "summary",
        "total_missing",
        "total_blocks",
        "largest_gap",
        "small",
        "large",
        "distribution",
    }

    assert len(result["gaps"]) == 4

    assert result["total_missing"] == 4

    assert result["total_blocks"] == 2

    assert result["largest_gap"] == 3

    assert result["small"] == 1

    assert result["large"] == 1

    assert result["distribution"].to_dict() == {
        2: 1,
        3: 1,
    }


def test_calculate_gap_summary_summary_content():

    engine = create_engine()

    index = pd.to_datetime(
        [
            "2025-01-01 00:00",
            "2025-01-01 01:00",
            "2025-01-01 02:00",
            "2025-01-01 03:00",
        ]
    )

    dataset = pd.DataFrame(
        {
            "gap_id": [
                "G1",
                "G1",
                "G2",
                "G2"
            ],
            "gap_size": [
                2,
                2,
                4,
                4
            ],
            "gap_type": [
                "small",
                "small",
                "large",
                "large"
            ],
            "data_status": [
                "missing",
                "missing",
                "missing",
                "missing"
            ]
        },
        index=index
    )

    result = engine.calculate_gap_summary(
        dataset
    )

    summary = result["summary"]

    assert summary.loc["G1", "start"] == index[0]
    assert summary.loc["G1", "end"] == index[1]
    assert summary.loc["G1", "hours"] == 2
    assert summary.loc["G1", "gap_type"] == "small"

    assert summary.loc["G2", "start"] == index[2]
    assert summary.loc["G2", "end"] == index[3]
    assert summary.loc["G2", "hours"] == 4
    assert summary.loc["G2", "gap_type"] == "large"


# ==========================================================
# Duplicate timestamps
# ==========================================================

def test_find_duplicate_timestamps_without_duplicates():

    engine = create_engine()

    index = pd.to_datetime(
        [
            "2025-01-01 00:00",
            "2025-01-01 01:00",
            "2025-01-01 02:00",
        ]
    )

    dataset = pd.DataFrame(
        {
            "AE_kWh": [
                1.0,
                2.0,
                3.0
            ]
        },
        index=index
    )

    result = engine.find_duplicate_timestamps(
        dataset
    )

    assert result is engine.duplicates

    assert result["count"] == 0
    assert result["duplicates"] is None


def test_find_duplicate_timestamps():

    timestamp = pd.Timestamp(
        "2025-01-01 01:00"
    )

    index = pd.DatetimeIndex(
        [
            pd.Timestamp("2025-01-01 00:00"),
            timestamp,
            timestamp,
            pd.Timestamp("2025-01-01 02:00"),
        ]
    )

    dataset = pd.DataFrame(
        {
            "AE_kWh": [
                1.0,
                2.0,
                3.0,
                4.0
            ]
        },
        index=index
    )

    engine = create_engine()

    result = engine.find_duplicate_timestamps(
        dataset
    )

    assert result is engine.duplicates

    assert result["count"] == 2

    duplicates = result["duplicates"]

    assert len(duplicates) == 2

    assert all(
        duplicates.index == timestamp
    )

    assert list(
        duplicates["AE_kWh"]
    ) == [2.0, 3.0]