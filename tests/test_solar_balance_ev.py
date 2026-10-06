import numpy as np
import pandas as pd
import pytest

from helios.core.consumption_scenario import ConsumptionScenario
from helios.ev.scenario import EVScenario
from helios.solar.balance import SolarBalanceEngine
from helios.solar.battery_configuration import BatteryConfiguration
from helios.solar.production_profile import SolarProductionProfile


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


def make_consumption(
    value: float | pd.Series,
    year: int = 2025,
) -> ConsumptionScenario:
    index = make_index(year)

    if isinstance(value, pd.Series):
        hourly_consumption = value.copy()
        hourly_consumption.index = index
    else:
        hourly_consumption = pd.Series(
            value,
            index=index,
            dtype=float,
        )

    return ConsumptionScenario(
        hourly_consumption=hourly_consumption,
        reference_year=year,
    )


def make_ev(
    value: float | pd.Series,
    year: int = 2025,
) -> EVScenario:
    index = make_index(year)

    if isinstance(value, pd.Series):
        hourly_consumption = value.copy()
        hourly_consumption.index = index
    else:
        hourly_consumption = pd.Series(
            value,
            index=index,
            dtype=float,
        )

    return EVScenario(
        hourly_consumption=hourly_consumption,
        reference_year=year,
    )


def make_production(
    value: float | pd.Series,
    year: int = 2025,
) -> SolarProductionProfile:
    index = make_index(year)

    if isinstance(value, pd.Series):
        hourly_production = value.copy()
        hourly_production.index = index
    else:
        hourly_production = pd.Series(
            value,
            index=index,
            dtype=float,
        )

    return SolarProductionProfile(
        hourly_production=hourly_production,
        reference_year=year,
        installed_power_kwp=1.0,
    )


def make_battery(
    *,
    capacity_kwh: float = 10.0,
    max_charge_power_kw: float = 10.0,
    max_discharge_power_kw: float = 10.0,
    charge_efficiency: float = 1.0,
    discharge_efficiency: float = 1.0,
    min_soc: float = 0.0,
    max_soc: float = 1.0,
    initial_soc: float = 0.0,
) -> BatteryConfiguration:
    return BatteryConfiguration(
        capacity_kwh=capacity_kwh,
        max_charge_power_kw=max_charge_power_kw,
        max_discharge_power_kw=max_discharge_power_kw,
        charge_efficiency=charge_efficiency,
        discharge_efficiency=discharge_efficiency,
        min_soc=min_soc,
        max_soc=max_soc,
        initial_soc=initial_soc,
    )


class TestSolarBalanceWithEV:

    def test_without_ev_preserves_existing_behavior(self):
        consumption = make_consumption(5.0)
        production = make_production(3.0)

        result_without_ev = SolarBalanceEngine.calculate(
            consumption,
            production,
        )

        result_with_no_ev = SolarBalanceEngine.calculate(
            consumption,
            production,
            ev_scenario=None,
        )

        pd.testing.assert_frame_equal(
            result_without_ev,
            result_with_no_ev,
        )

    def test_ev_is_added_to_total_consumption(self):
        consumption = make_consumption(2.0)
        ev = make_ev(1.0)
        production = make_production(0.0)

        result = SolarBalanceEngine.calculate(
            consumption,
            production,
            ev_scenario=ev,
        )

        assert len(result) == 8760

        assert (
            result["consumption_kwh"].sum()
            == pytest.approx(8760.0 * 3.0)
        )

    def test_solar_is_used_against_combined_demand(self):
        consumption = make_consumption(2.0)
        ev = make_ev(1.0)
        production = make_production(2.5)

        result = SolarBalanceEngine.calculate(
            consumption,
            production,
            ev_scenario=ev,
        )

        timestamp = pd.Timestamp("2025-01-15 12:00")

        assert result.loc[
            timestamp,
            "consumption_kwh",
        ] == pytest.approx(3.0)

        assert result.loc[
            timestamp,
            "production_kwh",
        ] == pytest.approx(2.5)

        assert result.loc[
            timestamp,
            "self_consumption_kwh",
        ] == pytest.approx(2.5)

        assert result.loc[
            timestamp,
            "grid_import_kwh",
        ] == pytest.approx(0.5)

        assert result.loc[
            timestamp,
            "grid_export_kwh",
        ] == pytest.approx(0.0)

    def test_ev_can_use_solar_surplus(self):
        consumption = make_consumption(1.0)
        ev = make_ev(2.0)
        production = make_production(5.0)

        result = SolarBalanceEngine.calculate(
            consumption,
            production,
            ev_scenario=ev,
        )

        timestamp = pd.Timestamp("2025-01-15 12:00")

        assert result.loc[
            timestamp,
            "consumption_kwh",
        ] == pytest.approx(3.0)

        assert result.loc[
            timestamp,
            "self_consumption_kwh",
        ] == pytest.approx(3.0)

        assert result.loc[
            timestamp,
            "grid_import_kwh",
        ] == pytest.approx(0.0)

        assert result.loc[
            timestamp,
            "grid_export_kwh",
        ] == pytest.approx(2.0)

    def test_ev_participates_in_battery_discharge(self):
        consumption = pd.Series(
            0.0,
            index=make_index(),
            dtype=float,
        )

        ev = pd.Series(
            0.0,
            index=make_index(),
            dtype=float,
        )

        production = make_production(0.0)

        consumption.iloc[0] = 1.0
        ev.iloc[0] = 2.0

        battery = make_battery(
            capacity_kwh=10.0,
            initial_soc=0.5,
        )

        result = SolarBalanceEngine.calculate(
            make_consumption(consumption),
            production,
            battery_configuration=battery,
            ev_scenario=make_ev(ev),
        )

        first_hour = result.iloc[0]

        assert first_hour[
            "consumption_kwh"
        ] == pytest.approx(3.0)

        assert first_hour[
            "battery_discharge_kwh"
        ] == pytest.approx(3.0)

        assert first_hour[
            "grid_import_kwh"
        ] == pytest.approx(0.0)

        assert first_hour[
            "battery_soc"
        ] == pytest.approx(0.2)

    def test_ev_participates_in_battery_charging_and_later_discharge(self):
        consumption = pd.Series(
            0.0,
            index=make_index(),
            dtype=float,
        )

        ev = pd.Series(
            0.0,
            index=make_index(),
            dtype=float,
        )

        production = pd.Series(
            0.0,
            index=make_index(),
            dtype=float,
        )

        production.iloc[0] = 5.0
        ev.iloc[1] = 3.0

        result = SolarBalanceEngine.calculate(
            make_consumption(consumption),
            make_production(production),
            battery_configuration=make_battery(
                capacity_kwh=10.0,
                initial_soc=0.0,
            ),
            ev_scenario=make_ev(ev),
        )

        first_hour = result.iloc[0]
        second_hour = result.iloc[1]

        assert first_hour[
            "battery_charge_kwh"
        ] == pytest.approx(5.0)

        assert first_hour[
            "battery_soc"
        ] == pytest.approx(0.5)

        assert second_hour[
            "consumption_kwh"
        ] == pytest.approx(3.0)

        assert second_hour[
            "battery_discharge_kwh"
        ] == pytest.approx(3.0)

        assert second_hour[
            "grid_import_kwh"
        ] == pytest.approx(0.0)

        assert second_hour[
            "battery_soc"
        ] == pytest.approx(0.2)

    def test_combined_demand_energy_is_conserved_without_battery(self):
        consumption = pd.Series(
            0.0,
            index=make_index(),
            dtype=float,
        )

        ev = pd.Series(
            0.0,
            index=make_index(),
            dtype=float,
        )

        production = pd.Series(
            0.0,
            index=make_index(),
            dtype=float,
        )

        consumption.iloc[0:3] = [2.0, 4.0, 1.0]
        ev.iloc[0:3] = [1.0, 2.0, 3.0]
        production.iloc[0:3] = [1.0, 10.0, 2.0]

        result = SolarBalanceEngine.calculate(
            make_consumption(consumption),
            make_production(production),
            ev_scenario=make_ev(ev),
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

        assert result[
            "consumption_kwh"
        ].sum() == pytest.approx(
            consumption.sum() + ev.sum()
        )

    def test_ev_reference_year_must_match_consumption(self):
        consumption = make_consumption(
            2.0,
            year=2025,
        )

        ev = make_ev(
            1.0,
            year=2024,
        )

        production = make_production(
            3.0,
            year=2025,
        )

        with pytest.raises(
            ValueError,
            match="same reference year",
        ):
            SolarBalanceEngine.calculate(
                consumption,
                production,
                ev_scenario=ev,
            )

    def test_invalid_ev_input_is_rejected(self):
        consumption = make_consumption(2.0)
        production = make_production(3.0)

        with pytest.raises(
            TypeError,
            match="ev_scenario must be an EVScenario",
        ):
            SolarBalanceEngine.calculate(
                consumption,
                production,
                ev_scenario=pd.Series(
                    1.0,
                    index=make_index(),
                ),
            )

    def test_ev_and_consumption_inputs_are_not_mutated(self):
        consumption = make_consumption(2.0)
        ev = make_ev(1.0)
        production = make_production(3.0)

        consumption_before = (
            consumption.hourly_consumption.copy()
        )

        ev_before = ev.hourly_consumption.copy()

        SolarBalanceEngine.calculate(
            consumption,
            production,
            ev_scenario=ev,
        )

        pd.testing.assert_series_equal(
            consumption.hourly_consumption,
            consumption_before,
        )

        pd.testing.assert_series_equal(
            ev.hourly_consumption,
            ev_before,
        )

    def test_battery_result_contains_combined_consumption(self):
        consumption = make_consumption(2.0)
        ev = make_ev(1.0)
        production = make_production(0.0)

        result = SolarBalanceEngine.calculate(
            consumption,
            production,
            battery_configuration=make_battery(
                capacity_kwh=10.0,
                initial_soc=0.0,
            ),
            ev_scenario=ev,
        )

        assert len(result) == 8760

        assert result[
            "consumption_kwh"
        ].sum() == pytest.approx(
            8760.0 * 3.0
        )

        assert result[
            "grid_import_kwh"
        ].sum() == pytest.approx(
            8760.0 * 3.0
        )

        assert result[
            "grid_export_kwh"
        ].sum() == pytest.approx(0.0)