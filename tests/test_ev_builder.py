import pandas as pd
import pytest

from helios.ev.builder import EVScenarioBuilder
from helios.ev.configuration import EVConfiguration
from helios.ev.scenario import EVScenario


def test_ev_builder_returns_ev_scenario():

    configuration = EVConfiguration(
        annual_consumption_kwh=3000.0,
        reference_year=2025,
    )

    scenario = EVScenarioBuilder.build(
        configuration
    )

    assert isinstance(
        scenario,
        EVScenario,
    )


def test_ev_builder_creates_8760_hours():

    configuration = EVConfiguration(
        annual_consumption_kwh=3000.0,
        reference_year=2025,
    )

    scenario = EVScenarioBuilder.build(
        configuration
    )

    assert len(
        scenario.hourly_consumption
    ) == 8760


def test_ev_builder_preserves_reference_year():

    configuration = EVConfiguration(
        annual_consumption_kwh=3000.0,
        reference_year=2025,
    )

    scenario = EVScenarioBuilder.build(
        configuration
    )

    assert scenario.reference_year == 2025

    assert scenario.hourly_consumption.index[0] == pd.Timestamp(
        "2025-01-01 00:00:00"
    )

    assert scenario.hourly_consumption.index[-1] == pd.Timestamp(
        "2025-12-31 23:00:00"
    )


def test_ev_builder_preserves_annual_consumption():

    configuration = EVConfiguration(
        annual_consumption_kwh=3000.0,
        reference_year=2025,
    )

    scenario = EVScenarioBuilder.build(
        configuration
    )

    assert scenario.annual_consumption == pytest.approx(
        3000.0
    )


def test_ev_builder_creates_uniform_base_profile():

    configuration = EVConfiguration(
        annual_consumption_kwh=8760.0,
        reference_year=2025,
    )

    scenario = EVScenarioBuilder.build(
        configuration
    )

    assert (
        scenario.hourly_consumption == 1.0
    ).all()


def test_ev_builder_accepts_zero_consumption():

    configuration = EVConfiguration(
        annual_consumption_kwh=0.0,
        reference_year=2025,
    )

    scenario = EVScenarioBuilder.build(
        configuration
    )

    assert scenario.annual_consumption == pytest.approx(
        0.0
    )

    assert (
        scenario.hourly_consumption == 0.0
    ).all()


def test_ev_builder_rejects_invalid_configuration():

    with pytest.raises(
        TypeError,
        match="configuration must be an EVConfiguration.",
    ):
        EVScenarioBuilder.build(
            "invalid"
        )


def test_ev_builder_excludes_february_29_in_leap_year():

    configuration = EVConfiguration(
        annual_consumption_kwh=3660.0,
        reference_year=2024,
    )

    scenario = EVScenarioBuilder.build(
        configuration
    )

    assert len(
        scenario.hourly_consumption
    ) == 8760

    assert not (
        (
            scenario.hourly_consumption.index.month == 2
        )
        & (
            scenario.hourly_consumption.index.day == 29
        )
    ).any()


def test_ev_builder_preserves_annual_consumption_in_leap_year():

    configuration = EVConfiguration(
        annual_consumption_kwh=3660.0,
        reference_year=2024,
    )

    scenario = EVScenarioBuilder.build(
        configuration
    )

    assert scenario.annual_consumption == pytest.approx(
        3660.0
    )