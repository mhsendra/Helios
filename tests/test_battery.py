import pandas as pd
import pytest

from helios.core.consumption_scenario import ConsumptionScenario
from helios.solar.battery import BatteryEngine
from helios.solar.battery_configuration import BatteryConfiguration
from helios.solar.production_profile import SolarProductionProfile


REFERENCE_YEAR = 2025


def make_index():
    return pd.date_range(
        start=f"{REFERENCE_YEAR}-01-01 00:00:00",
        periods=8760,
        freq="h",
    )


def make_consumption(values):
    return ConsumptionScenario(
        hourly_consumption=pd.Series(
            values,
            index=make_index(),
            dtype=float,
        ),
        reference_year=REFERENCE_YEAR,
    )


def make_production(values):
    return SolarProductionProfile(
        hourly_production=pd.Series(
            values,
            index=make_index(),
            dtype=float,
        ),
        reference_year=REFERENCE_YEAR,
        installed_power_kwp=10.0,
    )


def make_configuration(**overrides):
    values = {
        "capacity_kwh": 10.0,
        "max_charge_power_kw": 10.0,
        "max_discharge_power_kw": 10.0,
        "charge_efficiency": 1.0,
        "discharge_efficiency": 1.0,
        "min_soc": 0.0,
        "max_soc": 1.0,
        "initial_soc": 0.5,
    }
    values.update(overrides)
    return BatteryConfiguration(**values)


class TestBatteryEngine:

    def test_no_solar_production_imports_all_consumption(self):

        consumption = [0.0] * 8760
        production = [0.0] * 8760

        consumption[0] = 5.0

        result = BatteryEngine().calculate(
            make_consumption(consumption),
            make_production(production),
            make_configuration(),
        )

        row = result.hourly_data.iloc[0]

        assert row["consumption_kwh"] == pytest.approx(5.0)
        assert row["production_kwh"] == pytest.approx(0.0)
        assert row["direct_self_consumption_kwh"] == pytest.approx(0.0)
        assert row["battery_discharge_kwh"] == pytest.approx(5.0)
        assert row["grid_import_kwh"] == pytest.approx(0.0)
        assert row["grid_export_kwh"] == pytest.approx(0.0)

    def test_solar_production_equal_to_consumption(self):

        consumption = [0.0] * 8760
        production = [0.0] * 8760

        consumption[0] = 5.0
        production[0] = 5.0

        result = BatteryEngine().calculate(
            make_consumption(consumption),
            make_production(production),
            make_configuration(),
        )

        row = result.hourly_data.iloc[0]

        assert row["direct_self_consumption_kwh"] == pytest.approx(5.0)
        assert row["battery_charge_kwh"] == pytest.approx(0.0)
        assert row["battery_discharge_kwh"] == pytest.approx(0.0)
        assert row["grid_import_kwh"] == pytest.approx(0.0)
        assert row["grid_export_kwh"] == pytest.approx(0.0)

    def test_solar_surplus_charges_battery(self):

        consumption = [0.0] * 8760
        production = [0.0] * 8760

        consumption[0] = 2.0
        production[0] = 6.0

        result = BatteryEngine().calculate(
            make_consumption(consumption),
            make_production(production),
            make_configuration(),
        )

        row = result.hourly_data.iloc[0]

        assert row["direct_self_consumption_kwh"] == pytest.approx(2.0)
        assert row["battery_charge_kwh"] == pytest.approx(4.0)
        assert row["battery_discharge_kwh"] == pytest.approx(0.0)
        assert row["grid_export_kwh"] == pytest.approx(0.0)
        assert row["battery_soc"] == pytest.approx(0.9)

    def test_solar_deficit_discharges_battery(self):

        consumption = [0.0] * 8760
        production = [0.0] * 8760

        consumption[0] = 6.0
        production[0] = 2.0

        result = BatteryEngine().calculate(
            make_consumption(consumption),
            make_production(production),
            make_configuration(),
        )

        row = result.hourly_data.iloc[0]

        assert row["direct_self_consumption_kwh"] == pytest.approx(2.0)
        assert row["battery_charge_kwh"] == pytest.approx(0.0)
        assert row["battery_discharge_kwh"] == pytest.approx(4.0)
        assert row["grid_import_kwh"] == pytest.approx(0.0)
        assert row["grid_export_kwh"] == pytest.approx(0.0)
        assert row["battery_soc"] == pytest.approx(0.1)

    def test_full_battery_exports_remaining_surplus(self):

        consumption = [0.0] * 8760
        production = [0.0] * 8760

        production[0] = 5.0

        result = BatteryEngine().calculate(
            make_consumption(consumption),
            make_production(production),
            make_configuration(initial_soc=1.0),
        )

        row = result.hourly_data.iloc[0]

        assert row["direct_self_consumption_kwh"] == pytest.approx(0.0)
        assert row["battery_charge_kwh"] == pytest.approx(0.0)
        assert row["battery_discharge_kwh"] == pytest.approx(0.0)
        assert row["grid_import_kwh"] == pytest.approx(0.0)
        assert row["grid_export_kwh"] == pytest.approx(5.0)
        assert row["battery_soc"] == pytest.approx(1.0)

    def test_charge_efficiency_reduces_stored_energy_and_creates_losses(self):

        consumption = [0.0] * 8760
        production = [0.0] * 8760

        production[0] = 5.0

        result = BatteryEngine().calculate(
            make_consumption(consumption),
            make_production(production),
            make_configuration(charge_efficiency=0.8),
        )

        row = result.hourly_data.iloc[0]

        assert row["battery_charge_kwh"] == pytest.approx(5.0)
        assert row["battery_losses_kwh"] == pytest.approx(1.0)
        assert row["battery_soc"] == pytest.approx(0.9)


    def test_discharge_efficiency_requires_more_battery_energy(self):

        consumption = [0.0] * 8760
        production = [0.0] * 8760

        consumption[0] = 4.0

        result = BatteryEngine().calculate(
            make_consumption(consumption),
            make_production(production),
            make_configuration(discharge_efficiency=0.8),
        )

        row = result.hourly_data.iloc[0]

        assert row["battery_discharge_kwh"] == pytest.approx(5.0)
        assert row["battery_losses_kwh"] == pytest.approx(1.0)
        assert row["grid_import_kwh"] == pytest.approx(0.0)
        assert row["battery_soc"] == pytest.approx(0.0)


    def test_charge_power_limit_sends_remaining_surplus_to_grid(self):

        consumption = [0.0] * 8760
        production = [0.0] * 8760

        production[0] = 8.0

        result = BatteryEngine().calculate(
            make_consumption(consumption),
            make_production(production),
            make_configuration(max_charge_power_kw=2.0),
        )

        row = result.hourly_data.iloc[0]

        assert row["battery_charge_kwh"] == pytest.approx(2.0)
        assert row["grid_export_kwh"] == pytest.approx(6.0)
        assert row["battery_soc"] == pytest.approx(0.7)


    def test_discharge_power_limit_imports_remaining_deficit_from_grid(self):

        consumption = [0.0] * 8760
        production = [0.0] * 8760

        consumption[0] = 8.0

        result = BatteryEngine().calculate(
            make_consumption(consumption),
            make_production(production),
            make_configuration(max_discharge_power_kw=2.0),
        )

        row = result.hourly_data.iloc[0]

        assert row["battery_discharge_kwh"] == pytest.approx(2.0)
        assert row["grid_import_kwh"] == pytest.approx(6.0)
        assert row["battery_soc"] == pytest.approx(0.3)

    def test_battery_cannot_charge_above_max_soc(self):

        consumption = [0.0] * 8760
        production = [0.0] * 8760

        production[0] = 10.0

        result = BatteryEngine().calculate(
            make_consumption(consumption),
            make_production(production),
            make_configuration(
                initial_soc=0.8,
                max_soc=0.9,
            ),
        )

        row = result.hourly_data.iloc[0]

        assert row["battery_charge_kwh"] == pytest.approx(1.0)
        assert row["grid_export_kwh"] == pytest.approx(9.0)
        assert row["battery_soc"] == pytest.approx(0.9)


    def test_battery_cannot_discharge_below_min_soc(self):

        consumption = [0.0] * 8760
        production = [0.0] * 8760

        consumption[0] = 10.0

        result = BatteryEngine().calculate(
            make_consumption(consumption),
            make_production(production),
            make_configuration(
                initial_soc=0.2,
                min_soc=0.1,
            ),
        )

        row = result.hourly_data.iloc[0]

        assert row["battery_discharge_kwh"] == pytest.approx(1.0)
        assert row["grid_import_kwh"] == pytest.approx(9.0)
        assert row["battery_soc"] == pytest.approx(0.1)


    def test_battery_state_persists_between_hours(self):

        consumption = [0.0] * 8760
        production = [0.0] * 8760

        production[0] = 4.0
        consumption[1] = 3.0

        result = BatteryEngine().calculate(
            make_consumption(consumption),
            make_production(production),
            make_configuration(
                initial_soc=0.5,
            ),
        )

        first_hour = result.hourly_data.iloc[0]
        second_hour = result.hourly_data.iloc[1]

        assert first_hour["battery_charge_kwh"] == pytest.approx(4.0)
        assert first_hour["battery_soc"] == pytest.approx(0.9)

        assert second_hour["battery_discharge_kwh"] == pytest.approx(3.0)
        assert second_hour["grid_import_kwh"] == pytest.approx(0.0)
        assert second_hour["battery_soc"] == pytest.approx(0.6)


    def test_battery_can_charge_and_discharge_across_multiple_hours(self):

        consumption = [0.0] * 8760
        production = [0.0] * 8760

        production[0] = 5.0
        consumption[1] = 2.0
        consumption[2] = 4.0

        result = BatteryEngine().calculate(
            make_consumption(consumption),
            make_production(production),
            make_configuration(
                initial_soc=0.5,
            ),
        )

        hourly = result.hourly_data

        assert hourly.iloc[0]["battery_soc"] == pytest.approx(1.0)
        assert hourly.iloc[1]["battery_soc"] == pytest.approx(0.8)
        assert hourly.iloc[2]["battery_soc"] == pytest.approx(0.4)

        assert hourly.iloc[1]["grid_import_kwh"] == pytest.approx(0.0)
        assert hourly.iloc[2]["grid_import_kwh"] == pytest.approx(0.0)

    def test_result_contains_8760_hours_with_aligned_index(self):

        consumption = make_consumption([0.0] * 8760)
        production = make_production([0.0] * 8760)

        result = BatteryEngine().calculate(
            consumption,
            production,
            make_configuration(),
        )

        assert len(result.hourly_data) == 8760
        assert result.hourly_data.index.equals(
            consumption.hourly_consumption.index
        )
        assert result.hourly_data.index.equals(
            production.hourly_production.index
        )


    def test_result_contains_expected_columns(self):

        consumption = make_consumption([0.0] * 8760)
        production = make_production([0.0] * 8760)

        result = BatteryEngine().calculate(
            consumption,
            production,
            make_configuration(),
        )

        expected_columns = {
            "consumption_kwh",
            "production_kwh",
            "direct_self_consumption_kwh",
            "battery_charge_kwh",
            "battery_discharge_kwh",
            "grid_import_kwh",
            "grid_export_kwh",
            "battery_soc",
            "battery_losses_kwh",
        }

        assert set(result.hourly_data.columns) == expected_columns


    def test_zero_load_and_zero_production_keep_battery_state_unchanged(self):

        consumption = make_consumption([0.0] * 8760)
        production = make_production([0.0] * 8760)

        result = BatteryEngine().calculate(
            consumption,
            production,
            make_configuration(initial_soc=0.5),
        )

        hourly = result.hourly_data

        assert (hourly["consumption_kwh"] == 0.0).all()
        assert (hourly["production_kwh"] == 0.0).all()
        assert (hourly["battery_charge_kwh"] == 0.0).all()
        assert (hourly["battery_discharge_kwh"] == 0.0).all()
        assert (hourly["grid_import_kwh"] == 0.0).all()
        assert (hourly["grid_export_kwh"] == 0.0).all()
        assert (hourly["battery_losses_kwh"] == 0.0).all()
        assert hourly["battery_soc"].to_numpy() == pytest.approx(0.5)