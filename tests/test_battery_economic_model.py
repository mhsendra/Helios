import math

import pytest

from helios.solar.battery_economic_model import (
    BatteryEconomicConfiguration,
    BatteryEconomicModel, 
    CombinedEconomicConfiguration
)


class TestBatteryEconomicModel:

    def test_calculate_basic_cash_flow(self):
        configuration = BatteryEconomicConfiguration(
            battery_cost_eur=1000.0,
            annual_savings_eur=500.0,
            years=2,
            electricity_price_growth=0.0,
            pv_degradation=0.0,
            battery_degradation=0.0,
            annual_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        result = BatteryEconomicModel().calculate(configuration)

        assert result.cash_flows == pytest.approx(
            [-1000.0, 500.0, 500.0]
        )

        assert result.cumulative_cash_flow == pytest.approx(
            [-1000.0, -500.0, 0.0]
        )

    def test_calculate_npv_without_discount(self):
        configuration = BatteryEconomicConfiguration(
            battery_cost_eur=1000.0,
            annual_savings_eur=500.0,
            years=2,
            electricity_price_growth=0.0,
            pv_degradation=0.0,
            battery_degradation=0.0,
            annual_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        result = BatteryEconomicModel().calculate(configuration)

        assert result.npv_eur == pytest.approx(0.0)

    def test_calculate_payback(self):
        configuration = BatteryEconomicConfiguration(
            battery_cost_eur=1000.0,
            annual_savings_eur=500.0,
            years=2,
            electricity_price_growth=0.0,
            pv_degradation=0.0,
            battery_degradation=0.0,
            annual_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        result = BatteryEconomicModel().calculate(configuration)

        assert result.payback_years == pytest.approx(2.0)

    def test_calculate_irr(self):
        configuration = BatteryEconomicConfiguration(
            battery_cost_eur=1000.0,
            annual_savings_eur=600.0,
            years=2,
            electricity_price_growth=0.0,
            pv_degradation=0.0,
            battery_degradation=0.0,
            annual_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        result = BatteryEconomicModel().calculate(configuration)

        assert result.irr_percent == pytest.approx(
            13.0662,
            rel=1e-4,
        )

    def test_electricity_price_growth_increases_savings(self):
        configuration = BatteryEconomicConfiguration(
            battery_cost_eur=1000.0,
            annual_savings_eur=500.0,
            years=2,
            electricity_price_growth=0.10,
            pv_degradation=0.0,
            battery_degradation=0.0,
            annual_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        result = BatteryEconomicModel().calculate(configuration)

        assert result.cash_flows == pytest.approx(
            [-1000.0, 500.0, 550.0]
        )

    def test_pv_degradation_reduces_savings(self):
        configuration = BatteryEconomicConfiguration(
            battery_cost_eur=1000.0,
            annual_savings_eur=500.0,
            years=2,
            electricity_price_growth=0.0,
            pv_initial_degradation=0.0,
            pv_degradation=0.10,
            battery_degradation=0.0,
            annual_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        result = BatteryEconomicModel().calculate(configuration)

        assert result.cash_flows == pytest.approx(
            [-1000.0, 500.0, 450.0]
        )

    def test_battery_degradation_reduces_savings(self):
        configuration = BatteryEconomicConfiguration(
            battery_cost_eur=1000.0,
            annual_savings_eur=500.0,
            years=2,
            electricity_price_growth=0.0,
            pv_degradation=0.0,
            battery_degradation=0.10,
            annual_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        result = BatteryEconomicModel().calculate(configuration)

        assert result.cash_flows == pytest.approx(
            [-1000.0, 500.0, 450.0]
        )

    def test_maintenance_reduces_cash_flow_and_grows(self):
        configuration = BatteryEconomicConfiguration(
            battery_cost_eur=1000.0,
            annual_savings_eur=500.0,
            years=2,
            electricity_price_growth=0.0,
            pv_degradation=0.0,
            battery_degradation=0.0,
            annual_maintenance_eur=100.0,
            maintenance_growth=0.10,
            discount_rate=0.0,
        )

        result = BatteryEconomicModel().calculate(configuration)

        assert result.cash_flows == pytest.approx(
            [-1000.0, 400.0, 390.0]
        )

    def test_discount_rate_reduces_npv(self):
        configuration = BatteryEconomicConfiguration(
            battery_cost_eur=1000.0,
            annual_savings_eur=500.0,
            years=2,
            electricity_price_growth=0.0,
            pv_degradation=0.0,
            battery_degradation=0.0,
            annual_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.10,
        )

        result = BatteryEconomicModel().calculate(configuration)

        expected_npv = (
            -1000.0
            + 500.0 / 1.10
            + 500.0 / (1.10 ** 2)
        )

        assert result.npv_eur == pytest.approx(
            expected_npv
        )

    def test_payback_is_infinite_when_investment_is_not_recovered(self):
        configuration = BatteryEconomicConfiguration(
            battery_cost_eur=5000.0,
            annual_savings_eur=100.0,
            years=10,
            electricity_price_growth=0.0,
            pv_degradation=0.0,
            battery_degradation=0.0,
            annual_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        result = BatteryEconomicModel().calculate(configuration)

        assert math.isinf(result.payback_years)

    def test_electricity_price_growth_is_compounded(self):
        configuration = BatteryEconomicConfiguration(
            battery_cost_eur=0.0,
            annual_savings_eur=1000.0,
            years=3,
            electricity_price_growth=0.02,
            pv_degradation=0.0,
            battery_degradation=0.0,
            annual_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        result = BatteryEconomicModel().calculate(configuration)

        assert result.cash_flows[1] == pytest.approx(1000.0)
        assert result.cash_flows[2] == pytest.approx(1020.0)
        assert result.cash_flows[3] == pytest.approx(1040.4)

    def test_battery_degradation_is_compounded(self):
        configuration = BatteryEconomicConfiguration(
            battery_cost_eur=0.0,
            annual_savings_eur=1000.0,
            years=3,
            electricity_price_growth=0.0,
            pv_degradation=0.0,
            battery_degradation=0.02,
            annual_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        result = BatteryEconomicModel().calculate(configuration)

        assert result.cash_flows[1] == pytest.approx(1000.0)
        assert result.cash_flows[2] == pytest.approx(980.0)
        assert result.cash_flows[3] == pytest.approx(960.4)

    def test_growth_and_degradation_are_combined(self):
        configuration = BatteryEconomicConfiguration(
            battery_cost_eur=0.0,
            annual_savings_eur=1000.0,
            years=3,
            electricity_price_growth=0.02,
            pv_initial_degradation=0.01,
            pv_degradation=0.0035,
            battery_degradation=0.02,
            annual_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        result = BatteryEconomicModel().calculate(configuration)

        expected_year_1 = (
            1000.0
            * 0.99
        )

        expected_year_2 = (
            1000.0
            * 0.9865
            * 0.98
            * 1.02
        )

        expected_year_3 = (
            1000.0
            * 0.9830
            * 0.98**2
            * 1.02**2
        )

        assert result.cash_flows[1] == pytest.approx(
            expected_year_1
        )
        assert result.cash_flows[2] == pytest.approx(
            expected_year_2
        )
        assert result.cash_flows[3] == pytest.approx(
            expected_year_3
        )

    def test_payback_uses_accumulated_dynamic_savings(self):
        configuration = BatteryEconomicConfiguration(
            battery_cost_eur=1000.0,
            annual_savings_eur=400.0,
            years=25,
            electricity_price_growth=0.02,
            pv_degradation=0.0,
            battery_degradation=0.0,
            annual_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        result = BatteryEconomicModel().calculate(configuration)

        assert result.payback_years > 2.0
        assert result.payback_years < 3.0

    def test_payback_is_infinite_when_not_recovered_within_horizon(self):
        configuration = BatteryEconomicConfiguration(
            battery_cost_eur=10000.0,
            annual_savings_eur=100.0,
            years=25,
            electricity_price_growth=0.0,
            pv_degradation=0.0035,
            battery_degradation=0.02,
            annual_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.05,
        )

        result = BatteryEconomicModel().calculate(configuration)

        assert math.isinf(result.payback_years)

    def test_maintenance_grows_over_time(self):
        configuration = BatteryEconomicConfiguration(
            battery_cost_eur=0.0,
            annual_savings_eur=1000.0,
            years=3,
            electricity_price_growth=0.0,
            pv_degradation=0.0,
            battery_degradation=0.0,
            annual_maintenance_eur=100.0,
            maintenance_growth=0.02,
            discount_rate=0.0,
        )

        result = BatteryEconomicModel().calculate(configuration)

        assert result.cash_flows[1] == pytest.approx(900.0)
        assert result.cash_flows[2] == pytest.approx(898.0)
        assert result.cash_flows[3] == pytest.approx(895.96)

    def test_pv_degradation_applies_initial_and_annual_degradation(self):
        configuration = BatteryEconomicConfiguration(
            battery_cost_eur=0.0,
            annual_savings_eur=1000.0,
            years=3,
            electricity_price_growth=0.0,
            pv_initial_degradation=0.01,
            pv_degradation=0.0035,
            battery_degradation=0.0,
            annual_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        result = BatteryEconomicModel().calculate(configuration)

        assert result.cash_flows[1] == pytest.approx(
            990.0
        )

        assert result.cash_flows[2] == pytest.approx(
            986.5
        )

        assert result.cash_flows[3] == pytest.approx(
            983.0
        )

    def test_calculate_combined_uses_total_investment(
        self,
    ):
        configuration = CombinedEconomicConfiguration(
            installation_cost_eur=10000.0,
            battery_cost_eur=2000.0,
            annual_pv_savings_eur=2000.0,
            annual_battery_additional_savings_eur=500.0,
            years=2,
            electricity_price_growth=0.0,
            pv_initial_degradation=0.0,
            pv_degradation=0.0,
            battery_degradation=0.0,
            annual_pv_maintenance_eur=0.0,
            annual_battery_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        result = BatteryEconomicModel().calculate_combined(
            configuration
        )

        assert result.cash_flows == pytest.approx(
            [
                -12000.0,
                2500.0,
                2500.0,
            ]
        )

        assert result.cumulative_cash_flow == pytest.approx(
            [
                -12000.0,
                -9500.0,
                -7000.0,
            ]
        )

    def test_calculate_combined_applies_battery_degradation_only_to_additional_savings(
        self,
    ):
        configuration = CombinedEconomicConfiguration(
            installation_cost_eur=0.0,
            battery_cost_eur=0.0,
            annual_pv_savings_eur=1000.0,
            annual_battery_additional_savings_eur=500.0,
            years=2,
            electricity_price_growth=0.0,
            pv_initial_degradation=0.0,
            pv_degradation=0.0,
            battery_degradation=0.10,
            annual_pv_maintenance_eur=0.0,
            annual_battery_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        result = BatteryEconomicModel().calculate_combined(
            configuration
        )

        assert result.cash_flows[1] == pytest.approx(
            1500.0
        )

        assert result.cash_flows[2] == pytest.approx(
            1450.0
        )

    def test_calculate_combined_applies_pv_degradation_to_both_components(
        self,
    ):
        configuration = CombinedEconomicConfiguration(
            installation_cost_eur=0.0,
            battery_cost_eur=0.0,
            annual_pv_savings_eur=1000.0,
            annual_battery_additional_savings_eur=500.0,
            years=2,
            electricity_price_growth=0.0,
            pv_initial_degradation=0.0,
            pv_degradation=0.10,
            battery_degradation=0.0,
            annual_pv_maintenance_eur=0.0,
            annual_battery_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        result = BatteryEconomicModel().calculate_combined(
            configuration
        )

        assert result.cash_flows[1] == pytest.approx(
            1500.0
        )

        assert result.cash_flows[2] == pytest.approx(
            1350.0
        )

    def test_calculate_combined_includes_pv_and_battery_maintenance(
        self,
    ):
        configuration = CombinedEconomicConfiguration(
            installation_cost_eur=0.0,
            battery_cost_eur=0.0,
            annual_pv_savings_eur=1000.0,
            annual_battery_additional_savings_eur=0.0,
            years=2,
            electricity_price_growth=0.0,
            pv_initial_degradation=0.0,
            pv_degradation=0.0,
            battery_degradation=0.0,
            annual_pv_maintenance_eur=100.0,
            annual_battery_maintenance_eur=50.0,
            maintenance_growth=0.10,
            discount_rate=0.0,
        )

        result = BatteryEconomicModel().calculate_combined(
            configuration
        )

        assert result.cash_flows == pytest.approx(
            [
                0.0,
                850.0,
                835.0,
            ]
        )

    def test_combined_economics_separates_import_and_export_growth(
        self,
    ):
        configuration = CombinedEconomicConfiguration(
            installation_cost_eur=0.0,
            battery_cost_eur=0.0,
            annual_pv_savings_eur=1200.0,
            annual_battery_additional_savings_eur=0.0,
            years=3,
            electricity_price_growth=0.10,
            export_price_growth=0.02,
            annual_pv_self_consumption_savings_eur=1000.0,
            annual_export_compensation_eur=200.0,
            pv_initial_degradation=0.0,
            pv_degradation=0.0,
            battery_degradation=0.0,
            annual_pv_maintenance_eur=0.0,
            annual_battery_maintenance_eur=0.0,
            maintenance_growth=0.0,
            discount_rate=0.0,
        )

        result = BatteryEconomicModel().calculate_combined(
            configuration
        )

        assert result.cash_flows == pytest.approx(
            [
                0.0,
                1200.0,
                1304.0,
                1418.08,
            ]
        )