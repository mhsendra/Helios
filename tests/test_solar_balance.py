import numpy as np
import pandas as pd
import pytest

from helios.core.consumption_scenario import ConsumptionScenario
from helios.core.statistics import ConsumptionStatistics
from helios.solar.balance import SolarBalanceEngine
from helios.solar.installation_configuration import (
    InstallationConfiguration,
)
from helios.solar.installation_coordinator import (
    InstallationCoordinator,
)
from helios.solar.installation_evaluation import (
    InstallationEvaluator,
)
from helios.solar.installation_optimizer import (
    InstallationOptimizer,
)
from helios.solar.installation_recommendation import (
    InstallationRecommender,
)
from helios.solar.production_calculator import (
    SolarProductionCalculator,
)
from helios.solar.production_profile import (
    SolarProductionProfile,
)


def make_index(year: int = 2025) -> pd.DatetimeIndex:
    index = pd.date_range(
        start=f"{year}-01-01 00:00:00",
        end=f"{year}-12-31 23:00:00",
        freq="h",
    )

    if pd.Timestamp(f"{year}-12-31").is_leap_year:
        index = index[
            ~(
                (index.month == 2)
                & (index.day == 29)
            )
        ]

    return index


def make_scenario(
    values: float | pd.Series,
    year: int = 2025,
) -> ConsumptionScenario:
    index = make_index(year)

    if isinstance(values, pd.Series):
        hourly_consumption = values.copy()
        hourly_consumption.index = index
    else:
        hourly_consumption = pd.Series(
            values,
            index=index,
            dtype=float,
        )

    return ConsumptionScenario(
        hourly_consumption=hourly_consumption,
        reference_year=year,
    )


def make_profile(
    values: float | pd.Series,
    year: int = 2025,
) -> SolarProductionProfile:
    index = make_index(year)

    if isinstance(values, pd.Series):
        hourly_production = values.copy()
        hourly_production.index = index
    else:
        hourly_production = pd.Series(
            values,
            index=index,
            dtype=float,
        )

    return SolarProductionProfile(
        hourly_production=hourly_production,
        reference_year=year,
        installed_power_kwp=1.0,
    )


class TestSolarBalanceEngine:

    def test_calculate_with_self_consumption(self):
        scenario = make_scenario(5.0)
        production = make_profile(3.0)

        result = SolarBalanceEngine.calculate(
            scenario,
            production,
        )

        timestamp = pd.Timestamp("2025-01-15 12:00")

        assert result.loc[
            timestamp, "consumption_kwh"
        ] == pytest.approx(5.0)

        assert result.loc[
            timestamp, "production_kwh"
        ] == pytest.approx(3.0)

        assert result.loc[
            timestamp, "self_consumption_kwh"
        ] == pytest.approx(3.0)

        assert result.loc[
            timestamp, "grid_import_kwh"
        ] == pytest.approx(2.0)

        assert result.loc[
            timestamp, "grid_export_kwh"
        ] == pytest.approx(0.0)

    def test_calculate_with_surplus_production(self):
        scenario = make_scenario(3.0)
        production = make_profile(5.0)

        result = SolarBalanceEngine.calculate(
            scenario,
            production,
        )

        timestamp = pd.Timestamp("2025-01-15 12:00")

        assert result.loc[
            timestamp, "self_consumption_kwh"
        ] == pytest.approx(3.0)

        assert result.loc[
            timestamp, "grid_import_kwh"
        ] == pytest.approx(0.0)

        assert result.loc[
            timestamp, "grid_export_kwh"
        ] == pytest.approx(2.0)

    def test_calculate_without_production(self):
        scenario = make_scenario(4.0)
        production = make_profile(0.0)

        result = SolarBalanceEngine.calculate(
            scenario,
            production,
        )

        timestamp = pd.Timestamp("2025-01-15 12:00")

        assert result.loc[
            timestamp, "self_consumption_kwh"
        ] == pytest.approx(0.0)

        assert result.loc[
            timestamp, "grid_import_kwh"
        ] == pytest.approx(4.0)

        assert result.loc[
            timestamp, "grid_export_kwh"
        ] == pytest.approx(0.0)

    def test_calculate_aligns_synthetic_years_by_month_day_and_hour(self):
        consumption = make_scenario(
            4.0,
            year=2025,
        )

        production = make_profile(
            3.0,
            year=2024,
        )

        result = SolarBalanceEngine.calculate(
            consumption,
            production,
        )

        timestamp = pd.Timestamp("2025-01-15 12:00")

        assert result.loc[
            timestamp, "production_kwh"
        ] == pytest.approx(3.0)

        assert result.loc[
            timestamp, "self_consumption_kwh"
        ] == pytest.approx(3.0)

        assert result.loc[
            timestamp, "grid_import_kwh"
        ] == pytest.approx(1.0)

        assert result.loc[
            timestamp, "grid_export_kwh"
        ] == pytest.approx(0.0)

    def test_energy_balance_invariants(self):
        consumption = pd.Series(
            2.0,
            index=make_index(),
            dtype=float,
        )

        production = pd.Series(
            0.0,
            index=make_index(),
            dtype=float,
        )

        production.iloc[12] = 1.0
        production.iloc[13] = 3.0

        scenario = make_scenario(consumption)
        profile = make_profile(production)

        result = SolarBalanceEngine.calculate(
            scenario,
            profile,
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
        scenario = make_scenario(0.0)
        production = make_profile(5.0)

        result = SolarBalanceEngine.calculate(
            scenario,
            production,
        )

        timestamp = pd.Timestamp("2025-01-15 12:00")

        assert result.loc[
            timestamp, "self_consumption_kwh"
        ] == pytest.approx(0.0)

        assert result.loc[
            timestamp, "grid_import_kwh"
        ] == pytest.approx(0.0)

        assert result.loc[
            timestamp, "grid_export_kwh"
        ] == pytest.approx(5.0)

    def test_calculate_multiple_hours(self):
        consumption = pd.Series(
            0.0,
            index=make_index(),
            dtype=float,
        )

        production = pd.Series(
            0.0,
            index=make_index(),
            dtype=float,
        )

        consumption.iloc[12:15] = [5.0, 2.0, 6.0]
        production.iloc[12:15] = [3.0, 4.0, 1.0]

        scenario = make_scenario(consumption)
        profile = make_profile(production)

        result = SolarBalanceEngine.calculate(
            scenario,
            profile,
        )

        timestamps = make_index()[12:15]

        assert result.loc[
            timestamps, "production_kwh"
        ].tolist() == pytest.approx(
            [3.0, 4.0, 1.0]
        )

        assert result.loc[
            timestamps, "self_consumption_kwh"
        ].tolist() == pytest.approx(
            [3.0, 2.0, 1.0]
        )

        assert result.loc[
            timestamps, "grid_import_kwh"
        ].tolist() == pytest.approx(
            [2.0, 0.0, 5.0]
        )

        assert result.loc[
            timestamps, "grid_export_kwh"
        ].tolist() == pytest.approx(
            [0.0, 2.0, 0.0]
        )

    def test_calculate_returns_exactly_the_consumption_index(self):
        scenario = make_scenario(5.0)
        production = make_profile(1.0)

        result = SolarBalanceEngine.calculate(
            scenario,
            production,
        )

        assert len(result) == 8760
        assert result.index.equals(
            scenario.hourly_consumption.index
        )

    def test_calculate_does_not_mutate_input_indexes(self):
        scenario = make_scenario(
            5.0,
            year=2025,
        )

        production = make_profile(
            1.0,
            year=2024,
        )

        consumption_index_before = (
            scenario.hourly_consumption.index.copy()
        )

        production_index_before = (
            production.hourly_production.index.copy()
        )

        SolarBalanceEngine.calculate(
            scenario,
            production,
        )

        assert scenario.hourly_consumption.index.equals(
            consumption_index_before
        )

        assert production.hourly_production.index.equals(
            production_index_before
        )

    def test_calculate_rejects_invalid_consumption_input(self):
        production = make_profile(1.0)

        with pytest.raises(TypeError):
            SolarBalanceEngine.calculate(
                pd.Series(
                    1.0,
                    index=make_index(),
                ),
                production,
            )

    def test_calculate_rejects_invalid_production_input(self):
        scenario = make_scenario(1.0)

        with pytest.raises(TypeError):
            SolarBalanceEngine.calculate(
                scenario,
                pd.DataFrame(
                    {
                        "production_kwh": 1.0,
                    },
                    index=make_index(),
                ),
            )

    def test_calculate_accepts_representative_consumption_scenario_data(self):
        scenario = make_scenario(5.0)
        production = make_profile(1.0)

        result = SolarBalanceEngine.calculate(
            scenario,
            production,
        )

        assert len(result) == 8760

        assert result[
            "consumption_kwh"
        ].sum() == pytest.approx(
            8760.0 * 5.0
        )

        assert result[
            "production_kwh"
        ].sum() == pytest.approx(
            8760.0
        )

        assert result[
            "self_consumption_kwh"
        ].sum() == pytest.approx(
            8760.0
        )

        assert result[
            "grid_import_kwh"
        ].sum() == pytest.approx(
            8760.0 * 4.0
        )

        assert result[
            "grid_export_kwh"
        ].sum() == pytest.approx(0.0)

    def test_calculate_preserves_hourly_solar_surplus(self):
        scenario = make_scenario(2.0)
        production = make_profile(5.0)

        result = SolarBalanceEngine.calculate(
            scenario,
            production,
        )

        assert result[
            "self_consumption_kwh"
        ].sum() == pytest.approx(
            8760.0 * 2.0
        )

        assert result[
            "grid_import_kwh"
        ].sum() == pytest.approx(0.0)

        assert result[
            "grid_export_kwh"
        ].sum() == pytest.approx(
            8760.0 * 3.0
        )

    def test_calculate_preserves_hourly_energy_balance_with_variable_profiles(
        self,
    ):
        consumption = pd.Series(
            2.0,
            index=make_index(),
            dtype=float,
        )

        production = pd.Series(
            0.0,
            index=make_index(),
            dtype=float,
        )

        production.iloc[12:14] = 1.0
        production.iloc[14:16] = 5.0

        scenario = make_scenario(consumption)
        profile = make_profile(production)

        result = SolarBalanceEngine.calculate(
            scenario,
            profile,
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

        index = make_index()

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

    def test_calculate_integrates_representative_consumption_with_recommended_installation(
        self,
    ):
        index = make_index()

        consumption_data = pd.DataFrame(
            {
                "AE_kWh": 5.0,
            },
            index=index,
        )

        statistics = ConsumptionStatistics()

        statistics.calculate_representative_year_consumption(
            consumption_data,
            reference_year=2025,
        )

        scenario = (
            statistics.representative_consumption_scenario
        )

        assert isinstance(
            scenario,
            ConsumptionScenario,
        )

        base_profile = make_profile(1.0)

        calculator = SolarProductionCalculator(
            base_profile=base_profile,
        )

        installation_configuration = InstallationConfiguration(
            available_area_m2=42.25,
            panel_width_m=1.134,
            panel_height_m=1.762,
            panel_power_wp=540,
            min_panels=5,
            max_panels=15,
            maintenance_passage_required=False,
            maintenance_passage_width_m=0.45,
            maintenance_passage_orientation="auto",
        )

        constraints = (
            installation_configuration.to_constraints()
        )

        coordinator = InstallationCoordinator(
            optimizer=InstallationOptimizer(
                constraints
            ),
            evaluator=InstallationEvaluator(
                constraints
            ),
            recommender=InstallationRecommender(),
            production_calculator=calculator.calculate,
        )

        recommendation = coordinator.recommend(
            configuration=installation_configuration,
            annual_consumption_kwh=scenario.annual_consumption,
        )

        assert recommendation.panel_count == 10

        assert recommendation.installed_power_kwp == pytest.approx(
            5.4
        )

        production_profile = calculator.calculate(
            recommendation.evaluation.candidate
        )

        assert isinstance(
            production_profile,
            SolarProductionProfile,
        )

        assert production_profile.installed_power_kwp == pytest.approx(
            5.4
        )

        result = SolarBalanceEngine.calculate(
            scenario,
            production_profile,
        )

        assert len(result) == 8760

        assert result[
            "consumption_kwh"
        ].sum() == pytest.approx(
            scenario.annual_consumption
        )

        assert result[
            "production_kwh"
        ].sum() == pytest.approx(
            production_profile.annual_production
        )

        assert result[
            "self_consumption_kwh"
        ].sum() == pytest.approx(
            scenario.annual_consumption
        )

        assert result[
            "grid_import_kwh"
        ].sum() == pytest.approx(0.0)

        assert result[
            "grid_export_kwh"
        ].sum() == pytest.approx(
            production_profile.annual_production
            - scenario.annual_consumption
        )