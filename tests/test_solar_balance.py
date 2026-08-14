import pandas as pd
import pytest

from helios.solar.balance import SolarBalanceEngine


class TestSolarBalanceEngine:

    def test_calculate_with_self_consumption(self):

        consumption = pd.Series(
            [5.0],
            index=pd.to_datetime(
                ["2025-01-15 12:00"]
            )
        )

        hourly_production = pd.DataFrame(
            {
                "production_kwh": [3.0]
            },
            index=pd.to_datetime(
                ["2025-01-15 12:00"]
            )
        )

        result = SolarBalanceEngine.calculate(
            consumption,
            hourly_production
        )

        assert result.loc[
            pd.Timestamp("2025-01-15 12:00"),
            "consumption_kwh"
        ] == pytest.approx(5.0)

        assert result.loc[
            pd.Timestamp("2025-01-15 12:00"),
            "production_kwh"
        ] == pytest.approx(3.0)

        assert result.loc[
            pd.Timestamp("2025-01-15 12:00"),
            "self_consumption_kwh"
        ] == pytest.approx(3.0)

        assert result.loc[
            pd.Timestamp("2025-01-15 12:00"),
            "grid_import_kwh"
        ] == pytest.approx(2.0)

        assert result.loc[
            pd.Timestamp("2025-01-15 12:00"),
            "grid_export_kwh"
        ] == pytest.approx(0.0)

    def test_calculate_with_surplus_production(self):

        consumption = pd.Series(
            [3.0],
            index=pd.to_datetime(
                ["2025-01-15 12:00"]
            )
        )

        hourly_production = pd.DataFrame(
            {
                "production_kwh": [5.0]
            },
            index=pd.to_datetime(
                ["2025-01-15 12:00"]
            )
        )

        result = SolarBalanceEngine.calculate(
            consumption,
            hourly_production
        )

        assert result.loc[
            pd.Timestamp("2025-01-15 12:00"),
            "self_consumption_kwh"
        ] == pytest.approx(3.0)

        assert result.loc[
            pd.Timestamp("2025-01-15 12:00"),
            "grid_import_kwh"
        ] == pytest.approx(0.0)

        assert result.loc[
            pd.Timestamp("2025-01-15 12:00"),
            "grid_export_kwh"
        ] == pytest.approx(2.0)

    def test_calculate_without_production(self):

        consumption = pd.Series(
            [4.0],
            index=pd.to_datetime(
                ["2025-01-15 12:00"]
            )
        )

        hourly_production = pd.DataFrame(
            {
                "production_kwh": [0.0]
            },
            index=pd.to_datetime(
                ["2025-01-15 12:00"]
            )
        )

        result = SolarBalanceEngine.calculate(
            consumption,
            hourly_production
        )

        assert result.loc[
            pd.Timestamp("2025-01-15 12:00"),
            "self_consumption_kwh"
        ] == pytest.approx(0.0)

        assert result.loc[
            pd.Timestamp("2025-01-15 12:00"),
            "grid_import_kwh"
        ] == pytest.approx(4.0)

        assert result.loc[
            pd.Timestamp("2025-01-15 12:00"),
            "grid_export_kwh"
        ] == pytest.approx(0.0)

    def test_calculate_without_matching_production(self):

        consumption = pd.Series(
            [4.0],
            index=pd.to_datetime(
                ["2025-01-15 12:00"]
            )
        )

        hourly_production = pd.DataFrame(
            {
                "production_kwh": [3.0]
            },
            index=pd.to_datetime(
                ["2025-01-16 12:00"]
            )
        )

        result = SolarBalanceEngine.calculate(
            consumption,
            hourly_production
        )

        assert result.loc[
            pd.Timestamp("2025-01-15 12:00"),
            "production_kwh"
        ] == pytest.approx(0.0)

        assert result.loc[
            pd.Timestamp("2025-01-15 12:00"),
            "grid_import_kwh"
        ] == pytest.approx(4.0)

        assert result.loc[
            pd.Timestamp("2025-01-15 12:00"),
            "grid_export_kwh"
        ] == pytest.approx(0.0)