import pandas as pd
import pytest

from helios.solar.candidate_production import (
    calculate_candidate_solar_production,
)
from helios.solar.installation_candidate import InstallationCandidate
from helios.solar.production_profile import SolarProductionProfile


def make_base_profile(value: float = 1.0) -> SolarProductionProfile:
    index = pd.date_range(
        start="2025-01-01 00:00:00",
        periods=8760,
        freq="h",
    )

    series = pd.Series(
        value,
        index=index,
        name="production_kwh",
    )

    return SolarProductionProfile(
        hourly_production=series,
        reference_year=2025,
        installed_power_kwp=1.0,
    )


def make_candidate(
    panel_count: int = 15,
    panel_power_wp: float = 540.0,
) -> InstallationCandidate:
    return InstallationCandidate(
        panel_count=panel_count,
        panel_power_wp=panel_power_wp,
        panel_area_m2=2.6,
    )


def test_calculate_candidate_production_uses_installed_power():
    candidate = make_candidate(
        panel_count=15,
        panel_power_wp=540.0,
    )

    base_profile = make_base_profile()

    result = calculate_candidate_solar_production(
        candidate,
        base_profile,
    )

    assert result.installed_power_kwp == pytest.approx(8.1)


def test_calculate_candidate_production_scales_hourly_values():
    candidate = make_candidate(
        panel_count=15,
        panel_power_wp=540.0,
    )

    base_profile = make_base_profile(value=1.0)

    result = calculate_candidate_solar_production(
        candidate,
        base_profile,
    )

    assert result.hourly_production.apply(
        lambda value: value == pytest.approx(8.1)
    ).all()


def test_calculate_candidate_production_scales_annual_production():
    candidate = make_candidate(
        panel_count=15,
        panel_power_wp=540.0,
    )

    base_profile = make_base_profile(value=1.0)

    result = calculate_candidate_solar_production(
        candidate,
        base_profile,
    )

    assert result.annual_production == pytest.approx(
        8760.0 * 8.1
    )


def test_calculate_candidate_production_preserves_temporal_index():
    candidate = make_candidate()

    base_profile = make_base_profile()

    result = calculate_candidate_solar_production(
        candidate,
        base_profile,
    )

    assert result.hourly_production.index.equals(
        base_profile.hourly_production.index
    )


def test_calculate_candidate_production_preserves_temporal_shape():
    candidate = make_candidate()

    index = pd.date_range(
        start="2025-01-01 00:00:00",
        periods=8760,
        freq="h",
    )

    series = pd.Series(
        1.0,
        index=index,
        name="production_kwh",
    )

    series.iloc[100] = 2.0
    series.iloc[200] = 5.0

    base_profile = SolarProductionProfile(
        hourly_production=series,
        reference_year=2025,
        installed_power_kwp=1.0,
    )

    result = calculate_candidate_solar_production(
        candidate,
        base_profile,
    )

    assert result.hourly_production.iloc[100] == pytest.approx(16.2)
    assert result.hourly_production.iloc[200] == pytest.approx(40.5)


def test_calculate_candidate_production_does_not_modify_base_profile():
    candidate = make_candidate()

    base_profile = make_base_profile(value=1.0)

    original_values = base_profile.hourly_production.copy()

    calculate_candidate_solar_production(
        candidate,
        base_profile,
    )

    assert base_profile.installed_power_kwp == 1.0
    assert base_profile.hourly_production.equals(
        original_values
    )


def test_calculate_candidate_production_supports_different_candidates():
    candidate = make_candidate(
        panel_count=10,
        panel_power_wp=400.0,
    )

    base_profile = make_base_profile(value=1.0)

    result = calculate_candidate_solar_production(
        candidate,
        base_profile,
    )

    assert result.installed_power_kwp == pytest.approx(4.0)
    assert result.annual_production == pytest.approx(
        8760.0 * 4.0
    )


def test_calculate_candidate_production_rejects_invalid_candidate():
    base_profile = make_base_profile()

    with pytest.raises(TypeError):
        calculate_candidate_solar_production(
            candidate="invalid",
            base_profile=base_profile,
        )


def test_calculate_candidate_production_rejects_invalid_base_profile():
    candidate = make_candidate()

    with pytest.raises(TypeError):
        calculate_candidate_solar_production(
            candidate=candidate,
            base_profile="invalid",
        )