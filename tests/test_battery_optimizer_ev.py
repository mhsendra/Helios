import pandas as pd
import pytest

from helios.core.consumption_scenario import ConsumptionScenario
from helios.ev.scenario import EVScenario
from helios.solar.battery_optimizer import BatteryOptimizer
from helios.solar.production_profile import SolarProductionProfile


REFERENCE_YEAR = 2025


def make_index():
    return pd.date_range(
        f"{REFERENCE_YEAR}-01-01 00:00:00",
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


def make_ev(values):
    return EVScenario(
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
        installed_power_kwp=1.0,
    )


def test_optimizer_accepts_ev_scenario():
    consumption = make_consumption([1.0] * 8760)
    ev = make_ev([0.5] * 8760)
    production = make_production([0.0] * 8760)

    recommendations = BatteryOptimizer().evaluate(
        consumption,
        production,
        [5.0],
        max_charge_power_kw=5.0,
        max_discharge_power_kw=5.0,
        ev_scenario=ev,
    )

    assert len(recommendations) == 1
    assert recommendations[0].annual_consumption_kwh == pytest.approx(
        13140.0
    )


def test_optimizer_without_ev_preserves_consumption():
    consumption = make_consumption([1.0] * 8760)
    production = make_production([0.0] * 8760)

    recommendations = BatteryOptimizer().evaluate(
        consumption,
        production,
        [5.0],
        max_charge_power_kw=5.0,
        max_discharge_power_kw=5.0,
    )

    assert recommendations[0].annual_consumption_kwh == pytest.approx(
        8760.0
    )


def test_optimizer_rejects_invalid_ev_scenario():
    consumption = make_consumption([1.0] * 8760)
    production = make_production([0.0] * 8760)

    with pytest.raises(
        TypeError,
        match="ev_scenario must be an EVScenario",
    ):
        BatteryOptimizer().evaluate(
            consumption,
            production,
            [5.0],
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            ev_scenario="invalid",
        )


def test_optimizer_ev_participates_in_battery_balance():
    consumption_values = [0.0] * 8760
    ev_values = [0.0] * 8760

    consumption_values[0] = 1.0
    ev_values[0] = 2.0

    consumption = make_consumption(consumption_values)
    ev = make_ev(ev_values)
    production = make_production([0.0] * 8760)

    recommendations = BatteryOptimizer().evaluate(
        consumption,
        production,
        [10.0],
        max_charge_power_kw=10.0,
        max_discharge_power_kw=10.0,
        charge_efficiency=1.0,
        discharge_efficiency=1.0,
        min_soc=0.0,
        max_soc=1.0,
        initial_soc=0.5,
        ev_scenario=ev,
    )

    recommendation = recommendations[0]

    assert recommendation.annual_grid_import_kwh == pytest.approx(
    0.0
    )
    assert recommendation.annual_battery_discharge_kwh == pytest.approx(
        3.0
    )
    assert recommendation.annual_consumption_kwh == pytest.approx(
        3.0
    )