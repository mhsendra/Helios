import pytest
import pandas as pd

from helios.solar.parser import PVGISParser


class TestPVGISParser:

    def test_parse_datetime_and_index(self):

        response = {
            "outputs": {
                "hourly": [
                    {
                        "time": "20250101:1000",
                        "P": 1500,
                        "G(i)": 500,
                        "T2m": 20,
                        "WS10m": 2,
                        "Int": 0,
                    }
                ]
            }
        }

        result = PVGISParser.parse(response)

        assert isinstance(result.index, pd.DatetimeIndex)

        assert result.index[0] == pd.Timestamp(
            "2025-01-01 10:00"
        )

    def test_parse_production_conversion(self):

        response = {
            "outputs": {
                "hourly": [
                    {
                        "time": "20250101:1000",
                        "P": 1500,
                        "G(i)": 500,
                        "T2m": 20,
                        "WS10m": 2,
                        "Int": 0,
                    }
                ]
            }
        }

        result = PVGISParser.parse(response)

        assert result["production_kwh"].iloc[0] == pytest.approx(
            1.5
        )

        assert "production_w" not in result.columns

    def test_parse_columns(self):

        response = {
            "outputs": {
                "hourly": [
                    {
                        "time": "20250101:1000",
                        "P": 1500,
                        "G(i)": 500,
                        "T2m": 20,
                        "WS10m": 2,
                        "Int": 0,
                    }
                ]
            }
        }

        result = PVGISParser.parse(response)

        assert list(result.columns) == [
            "production_kwh",
            "irradiance",
            "temperature",
            "wind_speed",
            "interpolated",
        ]

    def test_parse_multiple_hourly_records(self):

        response = {
            "outputs": {
                "hourly": [
                    {
                        "time": "20250101:1000",
                        "P": 1000,
                        "G(i)": 400,
                        "T2m": 18,
                        "WS10m": 2,
                        "Int": 0,
                    },
                    {
                        "time": "20250101:1100",
                        "P": 2500,
                        "G(i)": 700,
                        "T2m": 20,
                        "WS10m": 3,
                        "Int": 1,
                    },
                ]
            }
        }

        result = PVGISParser.parse(response)

        assert len(result) == 2

        assert result.index.tolist() == [
            pd.Timestamp("2025-01-01 10:00"),
            pd.Timestamp("2025-01-01 11:00"),
        ]

        assert result["production_kwh"].tolist() == pytest.approx(
            [1.0, 2.5]
        )

        assert result["irradiance"].tolist() == pytest.approx(
            [400, 700]
        )

        assert result["temperature"].tolist() == pytest.approx(
            [18, 20]
        )

    def test_parse_normalizes_timestamp_to_hour(self):

        response = {
            "outputs": {
                "hourly": [
                    {
                        "time": "20250101:1037",
                        "P": 1500,
                        "G(i)": 500,
                        "T2m": 20,
                        "WS10m": 2,
                        "Int": 0,
                    }
                ]
            }
        }

        result = PVGISParser.parse(response)

        assert result.index[0] == pd.Timestamp(
            "2025-01-01 10:00"
        )