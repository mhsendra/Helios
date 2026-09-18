import pandas as pd
import pytest

from helios.solar.production_profile import SolarProductionProfile

from helios.solar.production_profile import (
    scale_solar_production_profile,
)

def make_hourly_series(
    year: int = 2025,
    value: float = 1.0,
) -> pd.Series:
    index = pd.date_range(
        start=f"{year}-01-01 00:00:00",
        periods=8760,
        freq="h",
    )

    return pd.Series(
        value,
        index=index,
        name="production_kwh",
    )


def test_valid_profile_is_created():
    series = make_hourly_series(value=1.0)

    profile = SolarProductionProfile(
        hourly_production=series,
        reference_year=2025,
        installed_power_kwp=1.0,
    )

    assert profile.hourly_production.equals(series)
    assert profile.reference_year == 2025
    assert profile.installed_power_kwp == 1.0


def test_annual_production_returns_total():
    series = make_hourly_series(value=1.0)

    profile = SolarProductionProfile(
        hourly_production=series,
        reference_year=2025,
        installed_power_kwp=1.0,
    )

    assert profile.annual_production == 8760.0


def test_rejects_non_series():
    with pytest.raises(TypeError):
        SolarProductionProfile(
            hourly_production=[1.0] * 8760,
            reference_year=2025,
            installed_power_kwp=1.0,
        )


def test_rejects_non_datetime_index():
    series = pd.Series(
        1.0,
        index=range(8760),
    )

    with pytest.raises(TypeError):
        SolarProductionProfile(
            hourly_production=series,
            reference_year=2025,
            installed_power_kwp=1.0,
        )


def test_rejects_wrong_number_of_hours():
    series = make_hourly_series().iloc[:-1]

    with pytest.raises(ValueError):
        SolarProductionProfile(
            hourly_production=series,
            reference_year=2025,
            installed_power_kwp=1.0,
        )


def test_rejects_nan_values():
    series = make_hourly_series()
    series.iloc[100] = float("nan")

    with pytest.raises(ValueError):
        SolarProductionProfile(
            hourly_production=series,
            reference_year=2025,
            installed_power_kwp=1.0,
        )


def test_rejects_negative_production():
    series = make_hourly_series()
    series.iloc[100] = -1.0

    with pytest.raises(ValueError):
        SolarProductionProfile(
            hourly_production=series,
            reference_year=2025,
            installed_power_kwp=1.0,
        )


def test_rejects_incomplete_reference_year():
    series = make_hourly_series().drop(
        pd.Timestamp("2025-01-01 08:00:00")
    )

    with pytest.raises(ValueError):
        SolarProductionProfile(
            hourly_production=series,
            reference_year=2025,
            installed_power_kwp=1.0,
        )


def test_rejects_zero_installed_power():
    series = make_hourly_series()

    with pytest.raises(ValueError):
        SolarProductionProfile(
            hourly_production=series,
            reference_year=2025,
            installed_power_kwp=0.0,
        )


def test_rejects_negative_installed_power():
    series = make_hourly_series()

    with pytest.raises(ValueError):
        SolarProductionProfile(
            hourly_production=series,
            reference_year=2025,
            installed_power_kwp=-1.0,
        )

def test_scale_profile_to_larger_installation():
    series = make_hourly_series(value=1.0)

    profile = SolarProductionProfile(
        hourly_production=series,
        reference_year=2025,
        installed_power_kwp=1.0,
    )

    scaled = scale_solar_production_profile(
        profile,
        installed_power_kwp=8.1,
    )

    assert scaled.installed_power_kwp == 8.1
    assert (scaled.hourly_production == 8.1).all()
    assert scaled.annual_production == pytest.approx(
        8760.0 * 8.1
    )


def test_scale_profile_preserves_temporal_shape():
    series = make_hourly_series()

    series.iloc[100] = 2.0
    series.iloc[200] = 5.0

    profile = SolarProductionProfile(
        hourly_production=series,
        reference_year=2025,
        installed_power_kwp=1.0,
    )

    scaled = scale_solar_production_profile(
        profile,
        installed_power_kwp=8.0,
    )

    assert scaled.hourly_production.iloc[100] == 16.0
    assert scaled.hourly_production.iloc[200] == 40.0


def test_scale_profile_does_not_modify_original():
    series = make_hourly_series(value=1.0)

    original = series.copy()

    profile = SolarProductionProfile(
        hourly_production=series,
        reference_year=2025,
        installed_power_kwp=1.0,
    )

    scale_solar_production_profile(
        profile,
        installed_power_kwp=8.1,
    )

    assert profile.hourly_production.equals(original)
    assert profile.installed_power_kwp == 1.0


def test_scale_profile_from_non_normalized_power():
    series = make_hourly_series(value=4.0)

    profile = SolarProductionProfile(
        hourly_production=series,
        reference_year=2025,
        installed_power_kwp=4.0,
    )

    scaled = scale_solar_production_profile(
        profile,
        installed_power_kwp=8.0,
    )

    assert (scaled.hourly_production == 8.0).all()
    assert scaled.annual_production == 8760.0 * 8.0


def test_scale_profile_rejects_invalid_profile():
    with pytest.raises(TypeError):
        scale_solar_production_profile(
            profile="invalid",
            installed_power_kwp=8.0,
        )


def test_scale_profile_rejects_zero_power():
    profile = SolarProductionProfile(
        hourly_production=make_hourly_series(),
        reference_year=2025,
        installed_power_kwp=1.0,
    )

    with pytest.raises(ValueError):
        scale_solar_production_profile(
            profile,
            installed_power_kwp=0.0,
        )


def test_scale_profile_rejects_negative_power():
    profile = SolarProductionProfile(
        hourly_production=make_hourly_series(),
        reference_year=2025,
        installed_power_kwp=1.0,
    )

    with pytest.raises(ValueError):
        scale_solar_production_profile(
            profile,
            installed_power_kwp=-2.0,
        )

def test_solar_production_profile_accepts_bissextile_reference_year_without_february_29():
    index = pd.date_range(
        "2024-01-01 00:00:00",
        "2024-12-31 23:00:00",
        freq="h",
    )

    index = index[
        ~(
            (index.month == 2)
            & (index.day == 29)
        )
    ]

    series = pd.Series(1.0, index=index)

    profile = SolarProductionProfile(
        hourly_production=series,
        reference_year=2024,
        installed_power_kwp=1.0,
    )

    assert len(profile.hourly_production) == 8760
    assert profile.hourly_production.index[0] == pd.Timestamp(
        "2024-01-01 00:00:00"
    )
    assert profile.hourly_production.index[-1] == pd.Timestamp(
        "2024-12-31 23:00:00"
    )


def test_solar_production_profile_bissextile_reference_year_excludes_february_29():
    index = pd.date_range(
        "2024-01-01 00:00:00",
        "2024-12-31 23:00:00",
        freq="h",
    )

    index = index[
        ~(
            (index.month == 2)
            & (index.day == 29)
        )
    ]

    series = pd.Series(1.0, index=index)

    profile = SolarProductionProfile(
        hourly_production=series,
        reference_year=2024,
        installed_power_kwp=1.0,
    )

    assert len(profile.hourly_production) == 8760
    assert not (
        (profile.hourly_production.index.month == 2)
        & (profile.hourly_production.index.day == 29)
    ).any()
    assert pd.Timestamp("2024-02-28 23:00:00") in profile.hourly_production.index
    assert pd.Timestamp("2024-03-01 00:00:00") in profile.hourly_production.index