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