import pandas as pd

from helios.core.cleaning import ConsumptionCleaner


def create_engine():

    return ConsumptionCleaner()


def create_dataset():

    index = pd.date_range(
        "2025-01-01",
        periods=10,
        freq="h"
    )

    return pd.DataFrame(
        {
            "AE_kWh": [
                1.0,
                2.0,
                None,
                None,
                5.0,
                6.0,
                None,
                8.0,
                None,
                None,
            ]
        },
        index=index
    )


# ==========================================================
# mark_missing_data
# ==========================================================


def test_mark_missing_data():

    engine = create_engine()

    df = create_dataset()

    result = engine.mark_missing_data(df)

    assert "data_status" in result.columns

    assert result["data_status"].tolist() == [
        "original",
        "original",
        "missing",
        "missing",
        "original",
        "original",
        "missing",
        "original",
        "missing",
        "missing",
    ]


def test_mark_missing_data_does_not_modify_original():

    engine = create_engine()

    df = create_dataset()

    original_columns = df.columns.tolist()

    result = engine.mark_missing_data(df)

    assert "data_status" not in df.columns

    assert df.columns.tolist() == original_columns

    assert result is not df


def test_mark_missing_data_without_missing_values():

    engine = create_engine()

    df = pd.DataFrame(
        {
            "AE_kWh": [
                1.0,
                2.0,
                3.0,
            ]
        }
    )

    result = engine.mark_missing_data(df)

    assert result["data_status"].tolist() == [
        "original",
        "original",
        "original",
    ]


# ==========================================================
# classify_gaps
# ==========================================================


def test_classify_gaps_without_missing_values():

    engine = create_engine()

    df = pd.DataFrame(
        {
            "AE_kWh": [
                1.0,
                2.0,
                3.0,
                4.0,
            ]
        }
    )

    result = engine.classify_gaps(df)

    assert result["gap_size"].tolist() == [
        0,
        0,
        0,
        0,
    ]

    assert result["gap_id"].isna().all()

    assert result["gap_type"].isna().all()


def test_classify_small_gap():

    engine = create_engine()

    df = pd.DataFrame(
        {
            "AE_kWh": [
                1.0,
                None,
                None,
                4.0,
            ]
        }
    )

    result = engine.classify_gaps(df)

    assert result["gap_size"].tolist() == [
        0,
        2,
        2,
        0,
    ]

    assert result["gap_id"].tolist()[1:3] == [
        1,
        1,
    ]

    assert result.loc[1, "gap_type"] == "small"
    assert result.loc[2, "gap_type"] == "small"

    assert pd.isna(result.loc[0, "gap_type"])
    assert pd.isna(result.loc[3, "gap_type"])


def test_classify_large_gap():

    engine = create_engine()

    df = pd.DataFrame(
        {
            "AE_kWh": [
                1.0,
                None,
                None,
                None,
                None,
                6.0,
            ]
        }
    )

    result = engine.classify_gaps(df)

    assert result["gap_size"].tolist() == [
        0,
        4,
        4,
        4,
        4,
        0,
    ]

    assert result["gap_id"].tolist()[1:5] == [
        1,
        1,
        1,
        1,
    ]

    assert all(
        result.loc[index, "gap_type"] == "large"
        for index in range(1, 5)
    )


def test_classify_multiple_gaps():

    engine = create_engine()

    df = pd.DataFrame(
        {
            "AE_kWh": [
                None,
                None,
                3.0,
                None,
                None,
                None,
                None,
                8.0,
            ]
        }
    )

    result = engine.classify_gaps(df)

    assert result["gap_size"].tolist() == [
        2,
        2,
        0,
        4,
        4,
        4,
        4,
        0,
    ]

    assert result.loc[0, "gap_id"] == 1
    assert result.loc[1, "gap_id"] == 1

    assert result.loc[3, "gap_id"] == 2
    assert result.loc[4, "gap_id"] == 2
    assert result.loc[5, "gap_id"] == 2
    assert result.loc[6, "gap_id"] == 2

    assert result.loc[0, "gap_type"] == "small"
    assert result.loc[1, "gap_type"] == "small"

    assert all(
        result.loc[index, "gap_type"] == "large"
        for index in range(3, 7)
    )


def test_classify_gap_of_three_hours_is_small():

    engine = create_engine()

    df = pd.DataFrame(
        {
            "AE_kWh": [
                None,
                None,
                None,
                4.0,
            ]
        }
    )

    result = engine.classify_gaps(df)

    assert result.loc[0, "gap_size"] == 3
    assert result.loc[1, "gap_size"] == 3
    assert result.loc[2, "gap_size"] == 3

    assert result.loc[0, "gap_type"] == "small"


def test_classify_gap_of_four_hours_is_large():

    engine = create_engine()

    df = pd.DataFrame(
        {
            "AE_kWh": [
                None,
                None,
                None,
                None,
                5.0,
            ]
        }
    )

    result = engine.classify_gaps(df)

    assert result.loc[0, "gap_size"] == 4
    assert result.loc[0, "gap_type"] == "large"


def test_classify_gaps_does_not_modify_original():

    engine = create_engine()

    df = create_dataset()

    original_columns = df.columns.tolist()

    result = engine.classify_gaps(df)

    assert "gap_size" not in df.columns
    assert "gap_id" not in df.columns
    assert "gap_type" not in df.columns

    assert df.columns.tolist() == original_columns

    assert result is not df