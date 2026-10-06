import pytest

from helios.ev.configuration import EVConfiguration


def test_ev_configuration_accepts_valid_values():
    configuration = EVConfiguration(
        annual_consumption_kwh=3000.0,
        reference_year=2025,
    )

    assert configuration.annual_consumption_kwh == 3000.0
    assert configuration.reference_year == 2025


def test_ev_configuration_uses_default_reference_year():
    configuration = EVConfiguration(
        annual_consumption_kwh=3000.0,
    )

    assert configuration.reference_year == 2025


def test_ev_configuration_accepts_zero_consumption():
    configuration = EVConfiguration(
        annual_consumption_kwh=0.0,
    )

    assert configuration.annual_consumption_kwh == 0.0


def test_ev_configuration_rejects_negative_consumption():
    with pytest.raises(ValueError, match="negative"):
        EVConfiguration(
            annual_consumption_kwh=-1.0,
        )


def test_ev_configuration_rejects_invalid_reference_year():
    with pytest.raises(ValueError, match="positive"):
        EVConfiguration(
            annual_consumption_kwh=3000.0,
            reference_year=0,
        )


def test_ev_configuration_calculates_average_daily_consumption():
    configuration = EVConfiguration(
        annual_consumption_kwh=3650.0,
    )

    assert configuration.average_daily_consumption_kwh == pytest.approx(
        10.0
    )


def test_ev_configuration_is_immutable():
    configuration = EVConfiguration(
        annual_consumption_kwh=3000.0,
    )

    with pytest.raises(AttributeError):
        configuration.annual_consumption_kwh = 4000.0