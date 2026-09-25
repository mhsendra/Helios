import pytest

from helios.solar.battery_configuration import BatteryConfiguration


class TestBatteryConfiguration:

    def test_required_parameters(self):

        configuration = BatteryConfiguration(
            capacity_kwh=16.6,
            max_charge_power_kw=8.0,
            max_discharge_power_kw=8.0,
        )

        assert configuration.capacity_kwh == pytest.approx(16.6)
        assert configuration.max_charge_power_kw == pytest.approx(8.0)
        assert configuration.max_discharge_power_kw == pytest.approx(8.0)

    def test_default_values(self):

        configuration = BatteryConfiguration(
            capacity_kwh=16.6,
            max_charge_power_kw=8.0,
            max_discharge_power_kw=8.0,
        )

        assert configuration.charge_efficiency == pytest.approx(0.95)
        assert configuration.discharge_efficiency == pytest.approx(0.95)

        assert configuration.min_soc == pytest.approx(0.10)
        assert configuration.max_soc == pytest.approx(0.90)
        assert configuration.initial_soc == pytest.approx(0.50)

    def test_custom_values(self):

        configuration = BatteryConfiguration(
            capacity_kwh=20.0,
            max_charge_power_kw=10.0,
            max_discharge_power_kw=12.0,
            charge_efficiency=0.96,
            discharge_efficiency=0.94,
            min_soc=0.15,
            max_soc=0.95,
            initial_soc=0.60,
        )

        assert configuration.capacity_kwh == pytest.approx(20.0)
        assert configuration.max_charge_power_kw == pytest.approx(10.0)
        assert configuration.max_discharge_power_kw == pytest.approx(12.0)

        assert configuration.charge_efficiency == pytest.approx(0.96)
        assert configuration.discharge_efficiency == pytest.approx(0.94)

        assert configuration.min_soc == pytest.approx(0.15)
        assert configuration.max_soc == pytest.approx(0.95)
        assert configuration.initial_soc == pytest.approx(0.60)