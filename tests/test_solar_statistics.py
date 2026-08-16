import pandas as pd
import pytest

from helios.solar.statistics import SolarStatisticsEngine


class Configuration:

    installed_power_kwp = 2.0


class TestSolarStatisticsEngine:

    def setup_method(self):

        self.configuration = Configuration()

    def test_calculate_statistics(self):

        index = pd.to_datetime(
            [
                "2025-01-01 10:00",
                "2025-01-01 11:00",
                "2025-01-02 10:00",
                "2025-02-01 10:00",
            ]
        )

        hourly_production = pd.DataFrame(
            {
                "production_kwh": [
                    1.0,
                    2.0,
                    0.0,
                    3.0,
                ]
            },
            index=index
        )

        energy_balance = pd.DataFrame(
            {
                "consumption_kwh": [
                    2.0,
                    1.0,
                    4.0,
                    4.0,
                ],
                "production_kwh": [
                    1.0,
                    2.0,
                    0.0,
                    3.0,
                ],
                "self_consumption_kwh": [
                    1.0,
                    1.0,
                    0.0,
                    3.0,
                ],
                "grid_import_kwh": [
                    1.0,
                    0.0,
                    4.0,
                    1.0,
                ],
                "grid_export_kwh": [
                    0.0,
                    1.0,
                    0.0,
                    0.0,
                ],
            },
            index=index
        )

        result = SolarStatisticsEngine.calculate(
            hourly_production,
            energy_balance,
            self.configuration
        )

        # ------------------------------------------
        # Period
        # ------------------------------------------

        assert result["hours"] == 4

        assert result["productive_hours"] == 3

        assert result["zero_production_hours"] == 1

        assert result["period_production"] == pytest.approx(
            6.0
        )

        # ------------------------------------------
        # Reference production
        # ------------------------------------------

        assert result["annual_production"] == pytest.approx(
            6.0
        )

        # ------------------------------------------
        # Averages
        # ------------------------------------------

        assert result["daily_average"] == pytest.approx(
            2.0
        )

        assert result["monthly_average"] == pytest.approx(
            3.0
        )

        assert result["hourly_average"] == pytest.approx(
            1.5
        )

        # ------------------------------------------
        # Production
        # ------------------------------------------

        assert result["maximum_power"] == pytest.approx(
            3.0
        )

        assert result["minimum_power"] == pytest.approx(
            1.0
        )

        assert result["equivalent_hours"] == pytest.approx(
            3.0
        )

        assert result["specific_yield"] == pytest.approx(
            3.0
        )

        assert result["capacity_factor"] == pytest.approx(
            75.0
        )

        # ------------------------------------------
        # Consumption
        # ------------------------------------------

        assert result["consumption"] == pytest.approx(
            11.0
        )

        # ------------------------------------------
        # Energy balance
        # ------------------------------------------

        assert result["self_consumption"] == pytest.approx(
            5.0
        )

        assert result["grid_import"] == pytest.approx(
            6.0
        )

        assert result["grid_export"] == pytest.approx(
            1.0
        )

        # ------------------------------------------
        # Ratios
        # ------------------------------------------

        assert result["self_consumption_ratio"] == pytest.approx(
            83.3333333333
        )

        assert result["self_sufficiency"] == pytest.approx(
            45.4545454545
        )

        assert result["coverage_ratio"] == pytest.approx(
            54.5454545455
        )

        assert result["surplus_ratio"] == pytest.approx(
            16.6666666667
        )

        assert result["import_ratio"] == pytest.approx(
            54.5454545455
        )

    def test_calculate_statistics_without_production(self):

        index = pd.to_datetime(
            [
                "2025-01-01 10:00",
                "2025-01-01 11:00",
            ]
        )

        hourly_production = pd.DataFrame(
            {
                "production_kwh": [
                    0.0,
                    0.0,
                ]
            },
            index=index
        )

        energy_balance = pd.DataFrame(
            {
                "consumption_kwh": [
                    2.0,
                    3.0,
                ],
                "production_kwh": [
                    0.0,
                    0.0,
                ],
                "self_consumption_kwh": [
                    0.0,
                    0.0,
                ],
                "grid_import_kwh": [
                    2.0,
                    3.0,
                ],
                "grid_export_kwh": [
                    0.0,
                    0.0,
                ],
            },
            index=index
        )

        result = SolarStatisticsEngine.calculate(
            hourly_production,
            energy_balance,
            self.configuration
        )

        assert result["productive_hours"] == 0

        assert result["zero_production_hours"] == 2

        assert result["minimum_power"] == 0.0

        assert result["self_consumption_ratio"] == 0.0

        assert result["self_sufficiency"] == 0.0

        assert result["coverage_ratio"] == 0.0

        assert result["surplus_ratio"] == 0.0