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
    values,
    year: int = 2025,
) -> ConsumptionScenario:
    index = make_index(year)

    if isinstance(values, (int, float)):
        series = pd.Series(
            float(values),
            index=index,
            dtype=float,
        )
    else:
        series = pd.Series(
            values,
            index=index,
            dtype=float,
        )

    return ConsumptionScenario(
        hourly_consumption=series,
        reference_year=year,
    )


def make_ev(
    values,
    year: int = 2025,
) -> EVScenario:
    index = make_index(year)

    if isinstance(values, (int, float)):
        series = pd.Series(
            float(values),
            index=index,
            dtype=float,
        )
    else:
        series = pd.Series(
            values,
            index=index,
            dtype=float,
        )

    return EVScenario(
        hourly_consumption=series,
        reference_year=year,
    )


def make_production(
    values,
    year: int = 2025,
) -> SolarProductionProfile:
    index = make_index(year)

    if isinstance(values, (int, float)):
        series = pd.Series(
            float(values),
            index=index,
            dtype=float,
        )
    else:
        series = pd.Series(
            values,
            index=index,
            dtype=float,
        )

    return SolarProductionProfile(
        hourly_production=series,
        installed_power_kwp=1.0,
        reference_year=year,
    )


def make_battery(
    capacity_kwh: float = 10.0,
    initial_soc: float = 0.5,
) -> BatteryConfiguration:
    return BatteryConfiguration(
        capacity_kwh=capacity_kwh,
        max_charge_power_kw=10.0,
        max_discharge_power_kw=10.0,
        charge_efficiency=1.0,
        discharge_efficiency=1.0,
        min_soc=0.0,
        max_soc=1.0,
        initial_soc=initial_soc,
    )

class TestSolarBalanceWithEVAndBattery:
    def test_pv_covers_home_and_ev_before_battery(self):
        consumption = make_consumption(2.0)
        ev = make_ev(1.0)
        production = make_production(5.0)
        battery = make_battery(
            capacity_kwh=10.0,
            initial_soc=0.5,
        )

        result = SolarBalanceEngine.calculate(
            consumption,
            production,
            battery_configuration=battery,
            ev_scenario=ev,
        )

        first_hour = result.iloc[0]

        assert first_hour["consumption_kwh"] == pytest.approx(3.0)
        assert first_hour["production_kwh"] == pytest.approx(5.0)
        assert first_hour["direct_self_consumption_kwh"] == pytest.approx(3.0)
        assert first_hour["battery_charge_kwh"] == pytest.approx(2.0)
        assert first_hour["battery_discharge_kwh"] == pytest.approx(0.0)
        assert first_hour["grid_import_kwh"] == pytest.approx(0.0)
        assert first_hour["grid_export_kwh"] == pytest.approx(0.0)
        assert first_hour["battery_soc"] == pytest.approx(0.7)

    def test_battery_covers_combined_home_and_ev_demand(self):
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

        consumption.iloc[0] = 2.0
        ev.iloc[0] = 1.0

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

        assert first_hour["consumption_kwh"] == pytest.approx(3.0)
        assert first_hour["direct_self_consumption_kwh"] == pytest.approx(0.0)
        assert first_hour["battery_discharge_kwh"] == pytest.approx(3.0)
        assert first_hour["grid_import_kwh"] == pytest.approx(0.0)
        assert first_hour["battery_soc"] == pytest.approx(0.2)

    def test_pv_charges_battery_with_combined_demand(self):
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

        consumption.iloc[0] = 1.0
        ev.iloc[0] = 1.0
        production.iloc[0] = 5.0

        battery = make_battery(
            capacity_kwh=10.0,
            initial_soc=0.0,
        )

        result = SolarBalanceEngine.calculate(
            make_consumption(consumption),
            make_production(production),
            battery_configuration=battery,
            ev_scenario=make_ev(ev),
        )

        first_hour = result.iloc[0]

        assert first_hour["consumption_kwh"] == pytest.approx(2.0)
        assert first_hour["direct_self_consumption_kwh"] == pytest.approx(2.0)
        assert first_hour["battery_charge_kwh"] == pytest.approx(3.0)
        assert first_hour["battery_discharge_kwh"] == pytest.approx(0.0)
        assert first_hour["grid_import_kwh"] == pytest.approx(0.0)
        assert first_hour["grid_export_kwh"] == pytest.approx(0.0)
        assert first_hour["battery_soc"] == pytest.approx(0.3)

    def test_excess_pv_is_exported_after_battery_is_full(self):
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

        consumption.iloc[0] = 1.0
        ev.iloc[0] = 1.0
        production.iloc[0] = 15.0

        battery = make_battery(
            capacity_kwh=10.0,
            initial_soc=0.5,
        )

        result = SolarBalanceEngine.calculate(
            make_consumption(consumption),
            make_production(production),
            battery_configuration=battery,
            ev_scenario=make_ev(ev),
        )

        first_hour = result.iloc[0]

        assert first_hour["consumption_kwh"] == pytest.approx(2.0)
        assert first_hour["direct_self_consumption_kwh"] == pytest.approx(2.0)
        assert first_hour["battery_charge_kwh"] == pytest.approx(5.0)
        assert first_hour["grid_export_kwh"] == pytest.approx(8.0)
        assert first_hour["grid_import_kwh"] == pytest.approx(0.0)
        assert first_hour["battery_soc"] == pytest.approx(1.0)

    def test_combined_demand_preserves_hourly_energy_balance(self):
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

        consumption.iloc[0] = 2.0
        ev.iloc[0] = 2.0
        production.iloc[0] = 1.0

        battery = make_battery(
            capacity_kwh=10.0,
            initial_soc=0.5,
        )

        result = SolarBalanceEngine.calculate(
            make_consumption(consumption),
            make_production(production),
            battery_configuration=battery,
            ev_scenario=make_ev(ev),
        )

        first_hour = result.iloc[0]

        assert first_hour["consumption_kwh"] == pytest.approx(4.0)
        assert first_hour["production_kwh"] == pytest.approx(1.0)
        assert first_hour["direct_self_consumption_kwh"] == pytest.approx(1.0)
        assert first_hour["battery_discharge_kwh"] == pytest.approx(3.0)
        assert first_hour["grid_import_kwh"] == pytest.approx(0.0)

        lhs = (
            first_hour["production_kwh"]
            + first_hour["battery_discharge_kwh"]
            + first_hour["grid_import_kwh"]
        )

        rhs = (
            first_hour["consumption_kwh"]
            + first_hour["battery_charge_kwh"]
            + first_hour["grid_export_kwh"]
        )

        assert lhs == pytest.approx(rhs)

    def test_ev_zero_matches_domestic_only_balance(self):
        consumption = make_consumption(2.0)
        ev = make_ev(0.0)
        production = make_production(3.0)
        battery = make_battery(
            capacity_kwh=10.0,
            initial_soc=0.5,
        )

        result_with_ev = SolarBalanceEngine.calculate(
            consumption,
            production,
            battery_configuration=battery,
            ev_scenario=ev,
        )

        result_without_ev = SolarBalanceEngine.calculate(
            consumption,
            production,
            battery_configuration=battery,
        )

        pd.testing.assert_series_equal(
            result_with_ev["consumption_kwh"],
            result_without_ev["consumption_kwh"],
            check_names=False,
        )

        pd.testing.assert_series_equal(
            result_with_ev["production_kwh"],
            result_without_ev["production_kwh"],
            check_names=False,
        )

        pd.testing.assert_series_equal(
            result_with_ev["grid_import_kwh"],
            result_without_ev["grid_import_kwh"],
            check_names=False,
        )

        pd.testing.assert_series_equal(
            result_with_ev["grid_export_kwh"],
            result_without_ev["grid_export_kwh"],
            check_names=False,
        )

        pd.testing.assert_series_equal(
            result_with_ev["battery_soc"],
            result_without_ev["battery_soc"],
            check_names=False,
        )

    def test_ev_is_added_to_annual_consumption(self):
        consumption = make_consumption(2.0)
        ev = make_ev(1.0)
        production = make_production(0.0)
        battery = make_battery(
            capacity_kwh=10.0,
            initial_soc=0.0,
        )

        result = SolarBalanceEngine.calculate(
            consumption,
            production,
            battery_configuration=battery,
            ev_scenario=ev,
        )

        assert result["consumption_kwh"].sum() == pytest.approx(
            3.0 * 8760.0
        )

    def test_ev_does_not_change_production(self):
        consumption = make_consumption(2.0)
        ev = make_ev(1.0)
        production = make_production(4.0)
        battery = make_battery(
            capacity_kwh=10.0,
            initial_soc=0.0,
        )

        result = SolarBalanceEngine.calculate(
            consumption,
            production,
            battery_configuration=battery,
            ev_scenario=ev,
        )

        assert result["production_kwh"].sum() == pytest.approx(
            4.0 * 8760.0
        )

    def test_ev_and_battery_work_together_over_multiple_hours(self):
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

        consumption.iloc[0] = 1.0
        ev.iloc[0] = 1.0
        production.iloc[0] = 5.0

        consumption.iloc[1] = 2.0
        ev.iloc[1] = 1.0
        production.iloc[1] = 0.0

        battery = make_battery(
            capacity_kwh=10.0,
            initial_soc=0.0,
        )

        result = SolarBalanceEngine.calculate(
            make_consumption(consumption),
            make_production(production),
            battery_configuration=battery,
            ev_scenario=make_ev(ev),
        )

        first_hour = result.iloc[0]
        second_hour = result.iloc[1]

        assert first_hour["consumption_kwh"] == pytest.approx(2.0)
        assert first_hour["direct_self_consumption_kwh"] == pytest.approx(
            2.0
        )
        assert first_hour["battery_charge_kwh"] == pytest.approx(3.0)
        assert first_hour["battery_soc"] == pytest.approx(0.3)

        assert second_hour["consumption_kwh"] == pytest.approx(3.0)
        assert second_hour["direct_self_consumption_kwh"] == pytest.approx(
            0.0
        )
        assert second_hour["battery_discharge_kwh"] == pytest.approx(
            3.0
        )
        assert second_hour["grid_import_kwh"] == pytest.approx(0.0)
        assert second_hour["battery_soc"] == pytest.approx(0.0)

    def test_result_index_is_preserved(self):
        consumption = make_consumption(1.0)
        ev = make_ev(1.0)
        production = make_production(2.0)
        battery = make_battery()

        result = SolarBalanceEngine.calculate(
            consumption,
            production,
            battery_configuration=battery,
            ev_scenario=ev,
        )

        assert result.index.equals(make_index())

    def test_inputs_are_not_mutated(self):
        consumption = make_consumption(2.0)
        ev = make_ev(1.0)
        production = make_production(4.0)
        battery = make_battery()

        consumption_before = consumption.hourly_consumption.copy()
        ev_before = ev.hourly_consumption.copy()
        production_before = production.hourly_production.copy()

        SolarBalanceEngine.calculate(
            consumption,
            production,
            battery_configuration=battery,
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

        pd.testing.assert_series_equal(
            production.hourly_production,
            production_before,
        )