from helios.config.constants import (
    DATE_COLUMN,
    HOUR_COLUMN,
    ENERGY_COLUMN,
    DATETIME_COLUMN,
    RAW_DATA_PATH,
    PROCESSED_DATA_PATH,
    EXPORT_PATH,
    EXCLUDED_SHEET,
)


def test_project_constants():
    assert DATE_COLUMN == "Fecha"
    assert HOUR_COLUMN == "Hora"
    assert ENERGY_COLUMN == "AE_kWh"
    assert DATETIME_COLUMN == "datetime"

    assert RAW_DATA_PATH == "data/raw"
    assert PROCESSED_DATA_PATH == "data/processed"
    assert EXPORT_PATH == "data/exports"

    assert EXCLUDED_SHEET == "Tabla Dinámica"