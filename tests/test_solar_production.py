import pandas as pd
import pytest

from helios.solar.production import SolarProductionEngine


class TestSolarProductionEngine:

    def test_daily(self):

        hourly = pd.DataFrame(
            {
                "production_kwh": [
                    1.0,
                    2.0,
                    3.0,
                    4.0,
                    5.0,
                    6.0,
                ]
            },
            index=pd.to_datetime(
                [
                    "2025-01-01 00:00",
                    "2025-01-01 01:00",
                    "2025-01-01 02:00",
                    "2025-01-01 03:00",
                    "2025-01-02 00:00",
                    "2025-01-02 01:00",
                ]
            )
        )

        result = SolarProductionEngine.daily(
            hourly
        )

        assert result.loc[
            pd.Timestamp("2025-01-01")
        ] == pytest.approx(10.0)

        assert result.loc[
            pd.Timestamp("2025-01-02")
        ] == pytest.approx(11.0)

    def test_monthly(self):

        daily = pd.Series(
            [
                10.0,
                20.0,
                30.0,
                40.0,
            ],
            index=pd.to_datetime(
                [
                    "2025-01-01",
                    "2025-01-15",
                    "2025-02-01",
                    "2025-02-15",
                ]
            )
        )

        result = SolarProductionEngine.monthly(
            daily
        )

        assert result.loc[
            pd.Timestamp("2025-01-31")
        ] == pytest.approx(30.0)

        assert result.loc[
            pd.Timestamp("2025-02-28")
        ] == pytest.approx(70.0)

    def test_yearly(self):

        monthly = pd.Series(
            [
                100.0,
                200.0,
                300.0,
                400.0,
            ],
            index=pd.to_datetime(
                [
                    "2025-01-31",
                    "2025-02-28",
                    "2025-03-31",
                    "2026-01-31",
                ]
            )
        )

        result = SolarProductionEngine.yearly(
            monthly
        )

        assert result.loc[
            pd.Timestamp("2025-12-31")
        ] == pytest.approx(600.0)

        assert result.loc[
            pd.Timestamp("2026-12-31")
        ] == pytest.approx(400.0)

    def test_production_is_conserved_across_aggregations(self):

        hourly = pd.DataFrame(
            {
                "production_kwh": [
                    1.0,
                    2.0,
                    3.0,
                    4.0,
                    5.0,
                    6.0,
                ]
            },
            index=pd.to_datetime(
                [
                    "2025-01-31 22:00",
                    "2025-01-31 23:00",
                    "2025-02-01 00:00",
                    "2025-02-01 01:00",
                    "2025-12-31 22:00",
                    "2026-01-01 00:00",
                ]
            ),
        )

        daily = SolarProductionEngine.daily(
            hourly
        )

        monthly = SolarProductionEngine.monthly(
            daily
        )

        yearly = SolarProductionEngine.yearly(
            monthly
        )

        assert hourly["production_kwh"].sum() == pytest.approx(
            daily.sum()
        )

        assert daily.sum() == pytest.approx(
            monthly.sum()
        )

        assert monthly.sum() == pytest.approx(
            yearly.sum()
        )