import pandas as pd
import pytest
import numpy as np

from helios.solar.balance import SolarBalanceEngine
from helios.core.consumption_scenario import ConsumptionScenario
from helios.solar.production_profile import SolarProductionProfile

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

    def test_energy_balance_invariants(self):

        consumption = pd.Series(
            [5.0, 3.0],
            index=pd.to_datetime(
                [
                    "2025-01-15 12:00",
                    "2025-01-15 13:00",
                ]
            ),
        )

        hourly_production = pd.DataFrame(
            {
                "production_kwh": [3.0, 5.0],
            },
            index=pd.to_datetime(
                [
                    "2025-01-15 12:00",
                    "2025-01-15 13:00",
                ]
            ),
        )

        result = SolarBalanceEngine.calculate(
            consumption,
            hourly_production,
        )

        assert np.allclose(
            result["consumption_kwh"],
            result["self_consumption_kwh"]
            + result["grid_import_kwh"],
        )

        assert np.allclose(
            result["production_kwh"],
            result["self_consumption_kwh"]
            + result["grid_export_kwh"],
        )

    def test_calculate_with_zero_consumption(self):

        consumption = pd.Series(
            [0.0],
            index=pd.to_datetime(
                ["2025-01-15 12:00"]
            ),
        )

        hourly_production = pd.DataFrame(
            {
                "production_kwh": [5.0]
            },
            index=pd.to_datetime(
                ["2025-01-15 12:00"]
            ),
        )

        result = SolarBalanceEngine.calculate(
            consumption,
            hourly_production,
        )

        assert result.loc[
            pd.Timestamp("2025-01-15 12:00"),
            "self_consumption_kwh",
        ] == pytest.approx(0.0)

        assert result.loc[
            pd.Timestamp("2025-01-15 12:00"),
            "grid_import_kwh",
        ] == pytest.approx(0.0)

        assert result.loc[
            pd.Timestamp("2025-01-15 12:00"),
            "grid_export_kwh",
        ] == pytest.approx(5.0)

    def test_calculate_multiple_hours(self):

        consumption = pd.Series(
            [5.0, 2.0, 6.0],
            index=pd.to_datetime(
                [
                    "2025-01-15 12:00",
                    "2025-01-15 13:00",
                    "2025-01-15 14:00",
                ]
            ),
        )

        hourly_production = pd.DataFrame(
            {
                "production_kwh": [3.0, 4.0, 1.0],
            },
            index=pd.to_datetime(
                [
                    "2025-01-15 12:00",
                    "2025-01-15 13:00",
                    "2025-01-15 14:00",
                ]
            ),
        )

        result = SolarBalanceEngine.calculate(
            consumption,
            hourly_production,
        )

        assert result["production_kwh"].tolist() == pytest.approx(
            [3.0, 4.0, 1.0]
        )

        assert result["self_consumption_kwh"].tolist() == pytest.approx(
            [3.0, 2.0, 1.0]
        )

        assert result["grid_import_kwh"].tolist() == pytest.approx(
            [2.0, 0.0, 5.0]
        )

        assert result["grid_export_kwh"].tolist() == pytest.approx(
            [0.0, 2.0, 0.0]
        )

    def test_calculate_accepts_representative_consumption_scenario_data(self):
        """El balance puede trabajar con el perfil horario del escenario representativo."""

        index = pd.date_range(
            start="2025-01-01 00:00:00",
            periods=8760,
            freq="h",
        )

        scenario = ConsumptionScenario(
            hourly_consumption=pd.Series(
                5.0,
                index=index,
            ),
            reference_year=2025,
        )

        production_profile = SolarProductionProfile(
            hourly_production=pd.Series(
                1.0,
                index=index,
            ),
            reference_year=2025,
            installed_power_kwp=1.0,
        )

        hourly_production = pd.DataFrame(
            {
                "production_kwh": production_profile.hourly_production,
            },
            index=production_profile.hourly_production.index,
        )

        result = SolarBalanceEngine.calculate(
            scenario.hourly_consumption,
            hourly_production,
        )

        assert len(result) == 8760

        assert result["consumption_kwh"].sum() == pytest.approx(
            8760.0 * 5.0
        )

        assert result["production_kwh"].sum() == pytest.approx(
            8760.0
        )

        assert result["self_consumption_kwh"].sum() == pytest.approx(
            8760.0
        )

        assert result["grid_import_kwh"].sum() == pytest.approx(
            8760.0 * 4.0
        )

        assert result["grid_export_kwh"].sum() == pytest.approx(
            0.0
        )


    def test_calculate_preserves_hourly_solar_surplus(self):
        """La producción solar sobrante se exporta y no se pierde."""

        index = pd.date_range(
            start="2025-01-01 00:00:00",
            periods=8760,
            freq="h",
        )

        scenario = ConsumptionScenario(
            hourly_consumption=pd.Series(
                2.0,
                index=index,
            ),
            reference_year=2025,
        )

        production_profile = SolarProductionProfile(
            hourly_production=pd.Series(
                5.0,
                index=index,
            ),
            reference_year=2025,
            installed_power_kwp=1.0,
        )

        hourly_production = pd.DataFrame(
            {
                "production_kwh": production_profile.hourly_production,
            },
            index=production_profile.hourly_production.index,
        )

        result = SolarBalanceEngine.calculate(
            scenario.hourly_consumption,
            hourly_production,
        )

        assert result["self_consumption_kwh"].sum() == pytest.approx(
            8760.0 * 2.0
        )

        assert result["grid_import_kwh"].sum() == pytest.approx(
            0.0
        )

        assert result["grid_export_kwh"].sum() == pytest.approx(
            8760.0 * 3.0
        )


    def test_calculate_preserves_hourly_energy_balance_with_variable_profiles(self):
        """El balance conserva producción y consumo con perfiles horarios variables."""

        index = pd.date_range(
            start="2025-01-01 00:00:00",
            periods=8760,
            freq="h",
        )

        consumption_values = pd.Series(
            2.0,
            index=index,
        )

        production_values = pd.Series(
            0.0,
            index=index,
        )

        # Horas de baja producción
        production_values.iloc[12:14] = 1.0

        # Horas de producción superior al consumo
        production_values.iloc[14:16] = 5.0

        scenario = ConsumptionScenario(
            hourly_consumption=consumption_values,
            reference_year=2025,
        )

        production_profile = SolarProductionProfile(
            hourly_production=production_values,
            reference_year=2025,
            installed_power_kwp=1.0,
        )

        hourly_production = pd.DataFrame(
            {
                "production_kwh": production_profile.hourly_production,
            },
            index=production_profile.hourly_production.index,
        )

        result = SolarBalanceEngine.calculate(
            scenario.hourly_consumption,
            hourly_production,
        )

        assert np.allclose(
            result["consumption_kwh"],
            result["self_consumption_kwh"]
            + result["grid_import_kwh"],
        )

        assert np.allclose(
            result["production_kwh"],
            result["self_consumption_kwh"]
            + result["grid_export_kwh"],
        )

        assert result.loc[
            index[12],
            "grid_import_kwh",
        ] == pytest.approx(1.0)

        assert result.loc[
            index[14],
            "grid_import_kwh",
        ] == pytest.approx(0.0)

        assert result.loc[
            index[14],
            "grid_export_kwh",
        ] == pytest.approx(3.0)