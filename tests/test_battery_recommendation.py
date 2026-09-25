import pytest

from helios.solar.battery_recommendation import BatteryRecommendation


def make_recommendation(**overrides):
    values = {
        "capacity_kwh": 16.6,
        "max_charge_power_kw": 8.0,
        "max_discharge_power_kw": 8.0,
        "annual_consumption_kwh": 10000.0,
        "annual_production_kwh": 12000.0,
        "annual_surplus_kwh": 7000.0,
        "annual_export_kwh": 5000.0,
        "annual_grid_import_kwh": 3000.0,
        "annual_battery_charge_kwh": 2000.0,
        "annual_battery_discharge_kwh": 1800.0,
        "self_consumption_kwh": 9000.0,
        "self_sufficiency_percent": 70.0,
        "equivalent_cycles": 108.43,
    }
    values.update(overrides)
    return BatteryRecommendation(**values)


class TestBatteryRecommendation:

    def test_recommendation_stores_configuration_values(self):
        recommendation = make_recommendation()

        assert recommendation.capacity_kwh == pytest.approx(16.6)
        assert recommendation.max_charge_power_kw == pytest.approx(8.0)
        assert recommendation.max_discharge_power_kw == pytest.approx(8.0)

    def test_recommendation_stores_annual_metrics(self):
        recommendation = make_recommendation()

        assert recommendation.annual_consumption_kwh == pytest.approx(10000.0)
        assert recommendation.annual_production_kwh == pytest.approx(12000.0)
        assert recommendation.annual_surplus_kwh == pytest.approx(7000.0)
        assert recommendation.annual_export_kwh == pytest.approx(5000.0)
        assert recommendation.annual_grid_import_kwh == pytest.approx(3000.0)

    def test_recommendation_stores_battery_metrics(self):
        recommendation = make_recommendation()

        assert recommendation.annual_battery_charge_kwh == pytest.approx(2000.0)
        assert recommendation.annual_battery_discharge_kwh == pytest.approx(1800.0)
        assert recommendation.equivalent_cycles == pytest.approx(108.43)

    def test_recommendation_stores_self_consumption_metrics(self):
        recommendation = make_recommendation()

        assert recommendation.self_consumption_kwh == pytest.approx(9000.0)
        assert recommendation.self_sufficiency_percent == pytest.approx(70.0)

    def test_battery_energy_stored_property(self):
        recommendation = make_recommendation(
            annual_battery_charge_kwh=2500.0,
        )

        assert recommendation.battery_energy_stored_kwh == pytest.approx(2500.0)

    def test_battery_energy_recovered_property(self):
        recommendation = make_recommendation(
            annual_battery_discharge_kwh=2200.0,
        )

        assert recommendation.battery_energy_recovered_kwh == pytest.approx(2200.0)

    def test_solar_energy_used_property(self):
        recommendation = make_recommendation(
            annual_production_kwh=12000.0,
            annual_export_kwh=5000.0,
        )

        assert recommendation.solar_energy_used_kwh == pytest.approx(7000.0)

    def test_recommendation_is_immutable(self):
        recommendation = make_recommendation()

        with pytest.raises(AttributeError):
            recommendation.capacity_kwh = 20.0

    def test_battery_recommendation_marginal_recovered_energy_defaults_to_zero(self):
        recommendation = BatteryRecommendation(
            capacity_kwh=10.0,
            max_charge_power_kw=8.0,
            max_discharge_power_kw=8.0,
            annual_consumption_kwh=10000.0,
            annual_production_kwh=12000.0,
            annual_surplus_kwh=8000.0,
            annual_export_kwh=5000.0,
            annual_grid_import_kwh=3000.0,
            annual_battery_charge_kwh=3000.0,
            annual_battery_discharge_kwh=2850.0,
            self_consumption_kwh=7000.0,
            self_sufficiency_percent=70.0,
            equivalent_cycles=285.0,
        )

        assert (
            recommendation.marginal_recovered_kwh_per_kwh
            == pytest.approx(0.0)
        )
