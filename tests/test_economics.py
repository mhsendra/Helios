import numpy as np
import numpy_financial as npf
import pandas as pd
import pytest

from helios.core.economic_scenarios import (
    EconomicScenario,
    EconomicScenarioResult,
    default_economic_scenarios,
)
from helios.core.economics import EconomicsEngine
from helios.core.consumption_scenario import ConsumptionScenario


# ==========================================================
# Factores económicos
# ==========================================================


class TestEconomicsFactors:

    def setup_method(self):
        self.engine = EconomicsEngine()

    def test_degradation_year_1(self):

        class Configuration:
            first_year_degradation = 0.01
            annual_degradation = 0.0035

        result = self.engine.calculate_degradation_factor(
            1,
            Configuration(),
        )

        assert result == pytest.approx(0.99)

    def test_degradation_year_2(self):

        class Configuration:
            first_year_degradation = 0.01
            annual_degradation = 0.0035

        result = self.engine.calculate_degradation_factor(
            2,
            Configuration(),
        )

        assert result == pytest.approx(0.9865)

    def test_degradation_year_25(self):

        class Configuration:
            first_year_degradation = 0.01
            annual_degradation = 0.0035

        expected = (
            1
            - 0.01
            - (0.0035 * 24)
        )

        result = self.engine.calculate_degradation_factor(
            25,
            Configuration(),
        )

        assert result == pytest.approx(expected)

    def test_degradation_year_zero(self):

        class Configuration:
            first_year_degradation = 0.01
            annual_degradation = 0.0035

        result = self.engine.calculate_degradation_factor(
            0,
            Configuration(),
        )

        assert result == pytest.approx(1.0)

    def test_electricity_price_factor(self):

        class Configuration:
            annual_electricity_price_growth = 0.02

        assert (
            self.engine.calculate_electricity_price_factor(
                1,
                Configuration(),
            )
            == pytest.approx(1.0)
        )

        assert (
            self.engine.calculate_electricity_price_factor(
                2,
                Configuration(),
            )
            == pytest.approx(1.02)
        )

    def test_electricity_price_factor_year_zero(self):

        class Configuration:
            annual_electricity_price_growth = 0.02

        result = self.engine.calculate_electricity_price_factor(
            0,
            Configuration(),
        )

        assert result == pytest.approx(1.0)

    def test_export_price_factor_year_zero(self):

        class Configuration:
            annual_export_price_growth = 0.01

        result = self.engine.calculate_export_price_factor(
            0,
            Configuration(),
        )

        assert result == pytest.approx(1.0)

    def test_maintenance_cost(self):

        class Configuration:
            annual_maintenance_cost = 150.0
            annual_maintenance_growth = 0.02

        assert (
            self.engine.calculate_maintenance_cost(
                1,
                Configuration(),
            )
            == pytest.approx(150.0)
        )

        assert (
            self.engine.calculate_maintenance_cost(
                2,
                Configuration(),
            )
            == pytest.approx(153.0)
        )

        assert (
            self.engine.calculate_maintenance_cost(
                3,
                Configuration(),
            )
            == pytest.approx(156.06)
        )

    def test_maintenance_cost_year_zero(self):

        class Configuration:
            annual_maintenance_cost = 150.0
            annual_maintenance_growth = 0.02

        result = self.engine.calculate_maintenance_cost(
            0,
            Configuration(),
        )

        assert result == pytest.approx(0.0)


# ==========================================================
# Cash Flow
# ==========================================================


class TestEconomicsCashFlow:

    def setup_method(self):
        self.engine = EconomicsEngine()

    def _configuration(self):

        class Configuration:
            first_year_degradation = 0.01
            annual_degradation = 0.0035

            annual_electricity_price_growth = 0.02
            annual_export_price_growth = 0.0

            annual_maintenance_cost = 150.0
            annual_maintenance_growth = 0.02

        return Configuration()

    def _prepare_engine(self):

        self.engine.net_investment = 12490.0

        self.engine.self_consumption_savings = (
            1257.4169699999998
        )

        self.engine.export_income = (
            1226.8389605999998
        )

        self.engine.annual_savings = (
            self.engine.self_consumption_savings
            + self.engine.export_income
        )

    def test_cash_flow_year_0(self):

        self._prepare_engine()

        result = self.engine.calculate_cash_flow(
            self._configuration(),
            years=25,
        )

        row = result.iloc[0]

        assert row["year"] == 0

        assert row["cash_flow"] == pytest.approx(
            -12490.0
        )

        assert row["cumulative_cash_flow"] == pytest.approx(
            -12490.0
        )

    def test_cash_flow_year_1(self):

        self._prepare_engine()

        result = self.engine.calculate_cash_flow(
            self._configuration(),
            years=25,
        )

        row = result.iloc[1]

        expected_degradation = 0.99

        expected_self_consumption = (
            1257.4169699999998
            * expected_degradation
        )

        expected_export = (
            1226.8389605999998
            * expected_degradation
        )

        expected_maintenance = 150.0

        expected_cash_flow = (
            expected_self_consumption
            + expected_export
            - expected_maintenance
        )

        assert row["self_consumption_savings"] == pytest.approx(
            expected_self_consumption
        )

        assert row["export_income"] == pytest.approx(
            expected_export
        )

        assert row["maintenance_cost"] == pytest.approx(
            expected_maintenance
        )

        assert row["cash_flow"] == pytest.approx(
            expected_cash_flow
        )

    def test_cash_flow_year_2(self):

        self._prepare_engine()

        result = self.engine.calculate_cash_flow(
            self._configuration(),
            years=25,
        )

        row = result.iloc[2]

        expected_degradation = (
            1
            - 0.01
            - 0.0035
        )

        expected_electricity_price = 1.02

        expected_self_consumption = (
            1257.4169699999998
            * expected_degradation
            * expected_electricity_price
        )

        expected_export = (
            1226.8389605999998
            * expected_degradation
        )

        expected_maintenance = 150.0 * 1.02

        expected_cash_flow = (
            expected_self_consumption
            + expected_export
            - expected_maintenance
        )

        assert row["self_consumption_savings"] == pytest.approx(
            expected_self_consumption
        )

        assert row["export_income"] == pytest.approx(
            expected_export
        )

        assert row["maintenance_cost"] == pytest.approx(
            expected_maintenance
        )

        assert row["cash_flow"] == pytest.approx(
            expected_cash_flow
        )

    def test_cash_flow_has_26_rows(self):

        self._prepare_engine()

        result = self.engine.calculate_cash_flow(
            self._configuration(),
            years=25,
        )

        assert len(result) == 26

        assert result.iloc[0]["year"] == 0
        assert result.iloc[-1]["year"] == 25

    def test_cash_flow_requires_net_investment(self):

        self.engine.annual_savings = 1000.0

        with pytest.raises(
            RuntimeError,
            match="Net investment has not been calculated.",
        ):
            self.engine.calculate_cash_flow(
                self._configuration()
            )

    def test_cash_flow_requires_annual_savings(self):

        self.engine.net_investment = 10000.0

        with pytest.raises(
            RuntimeError,
            match="Annual savings have not been calculated.",
        ):
            self.engine.calculate_cash_flow(
                self._configuration()
            )

    def test_cash_flow_requires_positive_years(self):

        self.engine.net_investment = 10000.0
        self.engine.annual_savings = 2000.0

        with pytest.raises(
            ValueError,
            match="Years must be greater than zero.",
        ):
            self.engine.calculate_cash_flow(
                self._configuration(),
                years=0,
            )

    def test_economic_summary_requires_cash_flow(self):

        with pytest.raises(
            RuntimeError,
            match="Cash flow has not been calculated.",
        ):
            self.engine.economic_summary()

    def test_economic_summary_returns_copy(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
            }
        )

        result = self.engine.economic_summary()

        assert result.equals(
            self.engine.cash_flow
        )

        assert result is not self.engine.cash_flow

    def test_calculate_payback_requires_cash_flow(self):

        self.engine.cash_flow = None

        with pytest.raises(
            RuntimeError,
            match="Cash flow has not been calculated.",
        ):
            self.engine.calculate_payback()

    def test_calculate_payback_first_year(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1],
                "cash_flow": [-1000.0, 1200.0],
                "cumulative_cash_flow": [
                    -1000.0,
                    200.0,
                ],
            }
        )

        result = self.engine.calculate_payback()

        assert result == pytest.approx(
            0.8333333333
        )

    def test_calculate_payback_fractional_year(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -1000.0,
                    400.0,
                    800.0,
                ],
                "cumulative_cash_flow": [
                    -1000.0,
                    -600.0,
                    200.0,
                ],
            }
        )

        result = self.engine.calculate_payback()

        assert result == pytest.approx(
            1.75
        )

    def test_calculate_payback_never_recovered(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -1000.0,
                    300.0,
                    300.0,
                ],
                "cumulative_cash_flow": [
                    -1000.0,
                    -700.0,
                    -400.0,
                ],
            }
        )

        result = self.engine.calculate_payback()

        assert result is None
        assert self.engine.payback_years is None

    def test_calculate_payback_exact_recovery(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -1000.0,
                    500.0,
                    500.0,
                ],
                "cumulative_cash_flow": [
                    -1000.0,
                    -500.0,
                    0.0,
                ],
            }
        )

        result = self.engine.calculate_payback()

        assert result == pytest.approx(
            2.0
        )


# ==========================================================
# Payback
# ==========================================================


class TestEconomicsPayback:

    def setup_method(self):
        self.engine = EconomicsEngine()

    def test_payback(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2, 3, 4, 5, 6],
                "cash_flow": [
                    -12490.00,
                    2309.41,
                    2322.53,
                    2335.90,
                    2349.53,
                    2363.43,
                    2377.60,
                ],
                "cumulative_cash_flow": [
                    -12490.00,
                    -10180.59,
                    -7858.06,
                    -5522.16,
                    -3172.63,
                    -809.19,
                    1568.41,
                ],
            }
        )

        result = self.engine.calculate_payback()

        expected = (
            5
            + 809.19 / 2377.60
        )

        assert result == pytest.approx(
            expected,
            abs=0.001,
        )

    def test_payback_not_reached(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    1000.0,
                    1000.0,
                ],
                "cumulative_cash_flow": [
                    -10000.0,
                    -9000.0,
                    -8000.0,
                ],
            }
        )

        result = self.engine.calculate_payback()

        assert result is None

    def test_payback_exact_year(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    5000.0,
                    5000.0,
                ],
                "cumulative_cash_flow": [
                    -10000.0,
                    -5000.0,
                    0.0,
                ],
            }
        )

        result = self.engine.calculate_payback()

        assert result == pytest.approx(2.0)

    def test_payback_requires_cash_flow(self):

        with pytest.raises(
            RuntimeError,
            match="Cash flow has not been calculated.",
        ):
            self.engine.calculate_payback()


# ==========================================================
# NPV
# ==========================================================


class TestEconomicsNPV:

    def setup_method(self):
        self.engine = EconomicsEngine()

    def test_npv(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
            }
        )

        result = self.engine.calculate_npv(
            discount_rate=0.05
        )

        expected = (
            -10000.0
            + 6000.0 / 1.05
            + 6000.0 / (1.05 ** 2)
        )

        assert result == pytest.approx(expected)

    def test_npv_zero_discount_rate(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
            }
        )

        result = self.engine.calculate_npv(
            discount_rate=0.0
        )

        assert result == pytest.approx(2000.0)

    def test_npv_negative_discount_rate(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1],
                "cash_flow": [
                    -10000.0,
                    12000.0,
                ],
            }
        )

        with pytest.raises(ValueError):
            self.engine.calculate_npv(
                discount_rate=-0.01
            )

    def test_npv_requires_cash_flow(self):

        with pytest.raises(
            RuntimeError,
            match="Cash flow has not been calculated.",
        ):
            self.engine.calculate_npv(
                discount_rate=0.05
            )

    def test_npv_updates_engine_state(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
            }
        )

        result = self.engine.calculate_npv(
            discount_rate=0.05
        )

        assert self.engine.npv == pytest.approx(
            result
        )


    def test_npv_with_only_initial_investment(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0],
                "cash_flow": [
                    -10000.0,
                ],
            }
        )

        result = self.engine.calculate_npv(
            discount_rate=0.05
        )

        assert result == pytest.approx(
            -10000.0
        )

        assert self.engine.npv == pytest.approx(
            -10000.0
        )


    def test_npv_with_zero_cash_flows(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    0.0,
                    0.0,
                    0.0,
                ],
            }
        )

        result = self.engine.calculate_npv(
            discount_rate=0.05
        )

        assert result == pytest.approx(
            0.0
        )


    def test_npv_with_positive_discount_rate(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1],
                "cash_flow": [
                    -10000.0,
                    11000.0,
                ],
            }
        )

        result = self.engine.calculate_npv(
            discount_rate=0.10
        )

        assert result == pytest.approx(
            0.0
        )


    def test_npv_does_not_modify_cash_flow(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
            }
        )

        original = self.engine.cash_flow.copy()

        self.engine.calculate_npv(
            discount_rate=0.05
        )

        pd.testing.assert_frame_equal(
            self.engine.cash_flow,
            original,
        )


# ==========================================================
# IRR
# ==========================================================


class TestEconomicsIRR:

    def setup_method(self):
        self.engine = EconomicsEngine()

    def test_irr(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
            }
        )

        result = self.engine.calculate_irr()

        expected = npf.irr(
            [
                -10000.0,
                6000.0,
                6000.0,
            ]
        )

        assert result == pytest.approx(expected)

    def test_irr_requires_positive_and_negative_cash_flow(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    1000.0,
                    2000.0,
                    3000.0,
                ],
            }
        )

        with pytest.raises(RuntimeError):
            self.engine.calculate_irr()

    def test_irr_requires_cash_flow(self):

        with pytest.raises(RuntimeError):
            self.engine.calculate_irr()

    def test_irr_handles_calculation_exception(
        self,
        monkeypatch,
    ):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1],
                "cash_flow": [
                    -1000.0,
                    1500.0,
                ],
            }
        )

        def failing_irr(cash_flows):
            raise ValueError("IRR calculation failed")

        monkeypatch.setattr(
            npf,
            "irr",
            failing_irr,
        )

        with pytest.raises(
            RuntimeError,
            match="Unable to calculate IRR.",
        ):
            self.engine.calculate_irr()

    def test_irr_returns_none(self, monkeypatch):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1],
                "cash_flow": [
                    -1000.0,
                    1500.0,
                ],
            }
        )

        monkeypatch.setattr(
            npf,
            "irr",
            lambda cash_flows: None,
        )

        with pytest.raises(
            RuntimeError,
            match="IRR could not be calculated.",
        ):
            self.engine.calculate_irr()

    def test_irr_updates_engine_state(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
            }
        )

        result = self.engine.calculate_irr()

        assert self.engine.irr == pytest.approx(
            result
        )


    def test_irr_with_zero_cash_flows(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    0.0,
                    0.0,
                    0.0,
                ],
            }
        )

        with pytest.raises(RuntimeError):
            self.engine.calculate_irr()


    def test_irr_does_not_modify_cash_flow(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
            }
        )

        original = self.engine.cash_flow.copy()

        self.engine.calculate_irr()

        pd.testing.assert_frame_equal(
            self.engine.cash_flow,
            original,
        )


# ==========================================================
# Indicadores económicos
# ==========================================================


class TestEconomicIndicators:

    def setup_method(self):
        self.engine = EconomicsEngine()

    def test_economic_indicators(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
                "cumulative_cash_flow": [
                    -10000.0,
                    -4000.0,
                    2000.0,
                ],
            }
        )

        result = self.engine.calculate_economic_indicators(
            discount_rate=0.05
        )

        expected_payback = (
            1
            + 4000.0 / 6000.0
        )

        expected_npv = (
            -10000.0
            + 6000.0 / 1.05
            + 6000.0 / (1.05 ** 2)
        )

        expected_irr = npf.irr(
            [
                -10000.0,
                6000.0,
                6000.0,
            ]
        )

        assert result["payback_years"] == pytest.approx(
            expected_payback
        )

        assert result["npv"] == pytest.approx(
            expected_npv
        )

        assert result["irr"] == pytest.approx(
            expected_irr
        )

        assert self.engine.payback_years == pytest.approx(
            expected_payback
        )

        assert self.engine.npv == pytest.approx(
            expected_npv
        )

        assert self.engine.irr == pytest.approx(
            expected_irr
        )

    def test_economic_indicators_requires_cash_flow(self):

        with pytest.raises(
            RuntimeError,
            match="Cash flow has not been calculated.",
        ):
            self.engine.calculate_economic_indicators(
                discount_rate=0.05
            )

    def test_economic_indicators_updates_engine_state(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
                "cumulative_cash_flow": [
                    -10000.0,
                    -4000.0,
                    2000.0,
                ],
            }
        )

        result = self.engine.calculate_economic_indicators(
            discount_rate=0.05
        )

        assert self.engine.payback_years == pytest.approx(
            result["payback_years"]
        )

        assert self.engine.npv == pytest.approx(
            result["npv"]
        )

        assert self.engine.irr == pytest.approx(
            result["irr"]
        )


    def test_economic_indicators_returns_all_indicators(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
                "cumulative_cash_flow": [
                    -10000.0,
                    -4000.0,
                    2000.0,
                ],
            }
        )

        result = self.engine.calculate_economic_indicators(
            discount_rate=0.05
        )

        assert set(result.keys()) == {
            "payback_years",
            "npv",
            "irr",
        }


    def test_economic_indicators_uses_discount_rate(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
                "cumulative_cash_flow": [
                    -10000.0,
                    -4000.0,
                    2000.0,
                ],
            }
        )

        result_low_rate = (
            self.engine.calculate_economic_indicators(
                discount_rate=0.03
            )
        )

        result_high_rate = (
            self.engine.calculate_economic_indicators(
                discount_rate=0.08
            )
        )

        assert result_low_rate["npv"] > result_high_rate["npv"]


# ==========================================================
# Costes, ingresos y ahorro
# ==========================================================


class TestEconomicsCosts:

    def setup_method(self):
        self.engine = EconomicsEngine()

    def test_calculate_cost_without_pv(self):

        dataset = pd.DataFrame(
            {
                "AE_kWh": [10.0, 20.0, 30.0],
                "buy_price_eur_kwh": [
                    0.25,
                    0.18,
                    0.12,
                ],
            }
        )

        result = self.engine.calculate_cost_without_pv(
            dataset
        )

        expected = (
            10.0 * 0.25
            + 20.0 * 0.18
            + 30.0 * 0.12
        )

        assert result == pytest.approx(expected)

        assert self.engine.cost_without_pv == pytest.approx(
            expected
        )

    def test_calculate_export_income(self):

        index = pd.date_range(
            "2025-01-01",
            periods=3,
            freq="h",
        )

        energy_balance = pd.DataFrame(
            {
                "grid_export_kwh": [
                    10.0,
                    20.0,
                    30.0,
                ],
            },
            index=index,
        )

        tariff_data = pd.DataFrame(
            {
                "sell_price_eur_kwh": [
                    0.06,
                    0.06,
                    0.06,
                ],
            },
            index=index,
        )

        result = self.engine.calculate_export_income(
            energy_balance,
            tariff_data,
        )

        expected = (
            10.0 * 0.06
            + 20.0 * 0.06
            + 30.0 * 0.06
        )

        assert result == pytest.approx(expected)

        assert self.engine.export_income == pytest.approx(
            expected
        )

    def test_calculate_cost_with_pv(self):

        index = pd.date_range(
            "2025-01-01",
            periods=3,
            freq="h",
        )

        energy_balance = pd.DataFrame(
            {
                "grid_import_kwh": [
                    10.0,
                    20.0,
                    30.0,
                ],
            },
            index=index,
        )

        tariff_data = pd.DataFrame(
            {
                "buy_price_eur_kwh": [
                    0.25,
                    0.18,
                    0.12,
                ],
            },
            index=index,
        )

        self.engine.export_income = 2.0

        result = self.engine.calculate_cost_with_pv(
            energy_balance,
            tariff_data,
        )

        expected_grid_import_cost = (
            10.0 * 0.25
            + 20.0 * 0.18
            + 30.0 * 0.12
        )

        expected_cost_with_pv = (
            expected_grid_import_cost
            - 2.0
        )

        assert self.engine.grid_import_cost == pytest.approx(
            expected_grid_import_cost
        )

        assert result == pytest.approx(
            expected_cost_with_pv
        )

        assert self.engine.cost_with_pv == pytest.approx(
            expected_cost_with_pv
        )

    def test_calculate_annual_savings(self):

        self.engine.cost_without_pv = 1000.0
        self.engine.cost_with_pv = 400.0
        self.engine.export_income = 100.0

        result = self.engine.calculate_annual_savings()

        expected_self_consumption = (
            1000.0
            - (
                400.0
                + 100.0
            )
        )

        expected_annual_savings = (
            expected_self_consumption
            + 100.0
        )

        assert (
            self.engine.self_consumption_savings
            == pytest.approx(
                expected_self_consumption
            )
        )

        assert result == pytest.approx(
            expected_annual_savings
        )

        assert self.engine.annual_savings == pytest.approx(
            expected_annual_savings
        )

    def test_calculate_annual_savings_without_cost_without_pv(self):

        self.engine.cost_with_pv = 400.0
        self.engine.export_income = 100.0

        with pytest.raises(
            RuntimeError,
            match="Cost without PV has not been calculated.",
        ):
            self.engine.calculate_annual_savings()

    def test_calculate_annual_savings_without_cost_with_pv(self):

        self.engine.cost_without_pv = 1000.0
        self.engine.export_income = 100.0

        with pytest.raises(
            RuntimeError,
            match="Cost with PV has not been calculated.",
        ):
            self.engine.calculate_annual_savings()

    def test_calculate_annual_savings_without_export_income(self):

        self.engine.cost_without_pv = 1000.0
        self.engine.cost_with_pv = 400.0

        with pytest.raises(
            RuntimeError,
            match="Export income has not been calculated.",
        ):
            self.engine.calculate_annual_savings()


# ==========================================================
# Inversión
# ==========================================================


class TestNetInvestment:

    def setup_method(self):
        self.engine = EconomicsEngine()

    def test_calculate_net_investment(self):

        class Configuration:
            installation_cost = 15000.0
            subsidies = 2000.0
            tax_deductions = 1000.0

        result = self.engine.calculate_net_investment(
            Configuration()
        )

        assert result == pytest.approx(
            12000.0
        )

        assert self.engine.net_investment == pytest.approx(
            12000.0
        )

    def test_calculate_net_investment_zero_subsidies_and_deductions(self):

        class Configuration:
            installation_cost = 10000.0
            subsidies = 0.0
            tax_deductions = 0.0

        result = self.engine.calculate_net_investment(
            Configuration()
        )

        assert result == pytest.approx(
            10000.0
        )

        assert self.engine.net_investment == pytest.approx(
            10000.0
        )


# ==========================================================
# Escenarios
# ==========================================================


class TestCalculateScenario:

    def setup_method(self):
        self.engine = EconomicsEngine()

        self.engine.net_investment = 10000.0
        self.engine.self_consumption_savings = 2000.0
        self.engine.export_income = 500.0
        self.engine.cost_without_pv = 3000.0

    def _configuration(self):

        class Configuration:
            first_year_degradation = 0.01
            annual_degradation = 0.0035

            annual_electricity_price_growth = 0.02
            annual_export_price_growth = 0.01

            annual_maintenance_cost = 100.0
            annual_maintenance_growth = 0.02

            discount_rate = 0.05

        return Configuration()

    def _scenario(self):

        class Scenario:
            name = "Base"

            annual_degradation = None
            discount_rate = None

            buy_price_factor = 1.0
            sell_price_factor = 1.0

            annual_maintenance = None

        return Scenario()

    def _calculate_base_result(self, years=5):
        return self.engine.calculate_scenario(
            scenario=self._scenario(),
            configuration=self._configuration(),
            years=years,
        )

    def test_calculate_scenario_returns_result(self):

        result = self._calculate_base_result()

        assert result.name == "Base"

        assert isinstance(
            result,
            EconomicScenarioResult,
        )

    def test_calculate_scenario_annual_savings(self):

        result = self._calculate_base_result()

        expected = (
            self.engine.self_consumption_savings
            + self.engine.export_income
        ) * 0.99

        assert result.annual_savings == pytest.approx(
            expected
        )

    def test_calculate_scenario_payback_matches_cash_flow_payback(self):

        configuration = self._configuration()

        # Ruta 1: cash flow + calculate_payback()
        self.engine.annual_savings = (
            self.engine.self_consumption_savings
            + self.engine.export_income
        )

        self.engine.calculate_cash_flow(
            configuration,
            years=5,
        )

        cash_flow_payback = self.engine.calculate_payback()

        # Ruta 2: calculate_scenario()
        scenario_result = self.engine.calculate_scenario(
            scenario=self._scenario(),
            configuration=configuration,
            years=5,
        )

        assert scenario_result.payback_years == pytest.approx(
            cash_flow_payback
        )

# ==========================================================
# Factores económicos
# ==========================================================


class TestEconomicsFactors:

    def setup_method(self):
        self.engine = EconomicsEngine()

    def test_degradation_year_1(self):

        class Configuration:
            first_year_degradation = 0.01
            annual_degradation = 0.0035

        result = self.engine.calculate_degradation_factor(
            1,
            Configuration(),
        )

        assert result == pytest.approx(0.99)

    def test_degradation_year_2(self):

        class Configuration:
            first_year_degradation = 0.01
            annual_degradation = 0.0035

        result = self.engine.calculate_degradation_factor(
            2,
            Configuration(),
        )

        assert result == pytest.approx(0.9865)

    def test_degradation_year_25(self):

        class Configuration:
            first_year_degradation = 0.01
            annual_degradation = 0.0035

        expected = (
            1
            - 0.01
            - (0.0035 * 24)
        )

        result = self.engine.calculate_degradation_factor(
            25,
            Configuration(),
        )

        assert result == pytest.approx(expected)

    def test_degradation_year_zero(self):

        class Configuration:
            first_year_degradation = 0.01
            annual_degradation = 0.0035

        result = self.engine.calculate_degradation_factor(
            0,
            Configuration(),
        )

        assert result == pytest.approx(1.0)

    def test_electricity_price_factor(self):

        class Configuration:
            annual_electricity_price_growth = 0.02

        assert (
            self.engine.calculate_electricity_price_factor(
                1,
                Configuration(),
            )
            == pytest.approx(1.0)
        )

        assert (
            self.engine.calculate_electricity_price_factor(
                2,
                Configuration(),
            )
            == pytest.approx(1.02)
        )

    def test_electricity_price_factor_year_zero(self):

        class Configuration:
            annual_electricity_price_growth = 0.02

        result = self.engine.calculate_electricity_price_factor(
            0,
            Configuration(),
        )

        assert result == pytest.approx(1.0)

    def test_export_price_factor_year_zero(self):

        class Configuration:
            annual_export_price_growth = 0.01

        result = self.engine.calculate_export_price_factor(
            0,
            Configuration(),
        )

        assert result == pytest.approx(1.0)

    def test_maintenance_cost(self):

        class Configuration:
            annual_maintenance_cost = 150.0
            annual_maintenance_growth = 0.02

        assert (
            self.engine.calculate_maintenance_cost(
                1,
                Configuration(),
            )
            == pytest.approx(150.0)
        )

        assert (
            self.engine.calculate_maintenance_cost(
                2,
                Configuration(),
            )
            == pytest.approx(153.0)
        )

        assert (
            self.engine.calculate_maintenance_cost(
                3,
                Configuration(),
            )
            == pytest.approx(156.06)
        )

    def test_maintenance_cost_year_zero(self):

        class Configuration:
            annual_maintenance_cost = 150.0
            annual_maintenance_growth = 0.02

        result = self.engine.calculate_maintenance_cost(
            0,
            Configuration(),
        )

        assert result == pytest.approx(0.0)


# ==========================================================
# Cash Flow
# ==========================================================


class TestEconomicsCashFlow:

    def setup_method(self):
        self.engine = EconomicsEngine()

    def _configuration(self):

        class Configuration:
            first_year_degradation = 0.01
            annual_degradation = 0.0035

            annual_electricity_price_growth = 0.02
            annual_export_price_growth = 0.0

            annual_maintenance_cost = 150.0
            annual_maintenance_growth = 0.02

        return Configuration()

    def _prepare_engine(self):

        self.engine.net_investment = 12490.0

        self.engine.self_consumption_savings = (
            1257.4169699999998
        )

        self.engine.export_income = (
            1226.8389605999998
        )

        self.engine.annual_savings = (
            self.engine.self_consumption_savings
            + self.engine.export_income
        )

    def test_cash_flow_year_0(self):

        self._prepare_engine()

        result = self.engine.calculate_cash_flow(
            self._configuration(),
            years=25,
        )

        row = result.iloc[0]

        assert row["year"] == 0

        assert row["cash_flow"] == pytest.approx(
            -12490.0
        )

        assert row["cumulative_cash_flow"] == pytest.approx(
            -12490.0
        )

    def test_cash_flow_year_1(self):

        self._prepare_engine()

        result = self.engine.calculate_cash_flow(
            self._configuration(),
            years=25,
        )

        row = result.iloc[1]

        expected_degradation = 0.99

        expected_self_consumption = (
            1257.4169699999998
            * expected_degradation
        )

        expected_export = (
            1226.8389605999998
            * expected_degradation
        )

        expected_maintenance = 150.0

        expected_cash_flow = (
            expected_self_consumption
            + expected_export
            - expected_maintenance
        )

        assert row["self_consumption_savings"] == pytest.approx(
            expected_self_consumption
        )

        assert row["export_income"] == pytest.approx(
            expected_export
        )

        assert row["maintenance_cost"] == pytest.approx(
            expected_maintenance
        )

        assert row["cash_flow"] == pytest.approx(
            expected_cash_flow
        )

    def test_cash_flow_year_2(self):

        self._prepare_engine()

        result = self.engine.calculate_cash_flow(
            self._configuration(),
            years=25,
        )

        row = result.iloc[2]

        expected_degradation = (
            1
            - 0.01
            - 0.0035
        )

        expected_electricity_price = 1.02

        expected_self_consumption = (
            1257.4169699999998
            * expected_degradation
            * expected_electricity_price
        )

        expected_export = (
            1226.8389605999998
            * expected_degradation
        )

        expected_maintenance = 150.0 * 1.02

        expected_cash_flow = (
            expected_self_consumption
            + expected_export
            - expected_maintenance
        )

        assert row["self_consumption_savings"] == pytest.approx(
            expected_self_consumption
        )

        assert row["export_income"] == pytest.approx(
            expected_export
        )

        assert row["maintenance_cost"] == pytest.approx(
            expected_maintenance
        )

        assert row["cash_flow"] == pytest.approx(
            expected_cash_flow
        )

    def test_cash_flow_has_26_rows(self):

        self._prepare_engine()

        result = self.engine.calculate_cash_flow(
            self._configuration(),
            years=25,
        )

        assert len(result) == 26

        assert result.iloc[0]["year"] == 0
        assert result.iloc[-1]["year"] == 25

    def test_cash_flow_requires_net_investment(self):

        self.engine.annual_savings = 1000.0

        with pytest.raises(
            RuntimeError,
            match="Net investment has not been calculated.",
        ):
            self.engine.calculate_cash_flow(
                self._configuration()
            )

    def test_cash_flow_requires_annual_savings(self):

        self.engine.net_investment = 10000.0

        with pytest.raises(
            RuntimeError,
            match="Annual savings have not been calculated.",
        ):
            self.engine.calculate_cash_flow(
                self._configuration()
            )

    def test_cash_flow_requires_positive_years(self):

        self.engine.net_investment = 10000.0
        self.engine.annual_savings = 2000.0

        with pytest.raises(
            ValueError,
            match="Years must be greater than zero.",
        ):
            self.engine.calculate_cash_flow(
                self._configuration(),
                years=0,
            )

    def test_cash_flow_payback_not_reached_sets_none(self):

        self.engine.net_investment = 10000.0
        self.engine.self_consumption_savings = 100.0
        self.engine.export_income = 0.0
        self.engine.annual_savings = 100.0

        result = self.engine.calculate_cash_flow(
            self._configuration(),
            years=2,
        )

        assert result.iloc[-1]["cumulative_cash_flow"] < 0
        assert self.engine.payback_years is None

    def test_economic_summary_requires_cash_flow(self):

        with pytest.raises(
            RuntimeError,
            match="Cash flow has not been calculated.",
        ):
            self.engine.economic_summary()

    def test_economic_summary_returns_copy(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
            }
        )

        result = self.engine.economic_summary()

        assert result.equals(
            self.engine.cash_flow
        )

        assert result is not self.engine.cash_flow

    def test_calculate_payback_requires_cash_flow(self):

        self.engine.cash_flow = None

        with pytest.raises(
            RuntimeError,
            match="Cash flow has not been calculated.",
        ):
            self.engine.calculate_payback()

    def test_calculate_payback_first_year(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1],
                "cash_flow": [-1000.0, 1200.0],
                "cumulative_cash_flow": [
                    -1000.0,
                    200.0,
                ],
            }
        )

        result = self.engine.calculate_payback()

        assert result == pytest.approx(
            0.8333333333
        )

    def test_calculate_payback_fractional_year(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -1000.0,
                    400.0,
                    800.0,
                ],
                "cumulative_cash_flow": [
                    -1000.0,
                    -600.0,
                    200.0,
                ],
            }
        )

        result = self.engine.calculate_payback()

        assert result == pytest.approx(
            1.75
        )

    def test_calculate_payback_never_recovered(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -1000.0,
                    300.0,
                    300.0,
                ],
                "cumulative_cash_flow": [
                    -1000.0,
                    -700.0,
                    -400.0,
                ],
            }
        )

        result = self.engine.calculate_payback()

        assert result is None
        assert self.engine.payback_years is None

    def test_calculate_payback_exact_recovery(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -1000.0,
                    500.0,
                    500.0,
                ],
                "cumulative_cash_flow": [
                    -1000.0,
                    -500.0,
                    0.0,
                ],
            }
        )

        result = self.engine.calculate_payback()

        assert result == pytest.approx(
            2.0
        )

    def test_calculate_cash_flow_zero_net_investment_returns_zero_payback(self):

        self.engine.net_investment = 0.0
        self.engine.self_consumption_savings = 1000.0
        self.engine.export_income = 0.0
        self.engine.annual_savings = 1000.0

        result = self.engine.calculate_cash_flow(
            self._configuration(),
            years=2,
        )

        assert len(result) == 3
        assert self.engine.payback_years == 0.0

    def test_calculate_cash_flow_negative_net_investment_has_no_payback(self):

        self.engine.net_investment = -1000.0
        self.engine.self_consumption_savings = 1000.0
        self.engine.export_income = 0.0
        self.engine.annual_savings = 1000.0

        result = self.engine.calculate_cash_flow(
            self._configuration(),
            years=2,
        )

        assert len(result) == 3
        assert self.engine.payback_years is None


# ==========================================================
# Payback
# ==========================================================


class TestEconomicsPayback:

    def setup_method(self):
        self.engine = EconomicsEngine()

    def test_payback(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2, 3, 4, 5, 6],
                "cash_flow": [
                    -12490.00,
                    2309.41,
                    2322.53,
                    2335.90,
                    2349.53,
                    2363.43,
                    2377.60,
                ],
                "cumulative_cash_flow": [
                    -12490.00,
                    -10180.59,
                    -7858.06,
                    -5522.16,
                    -3172.63,
                    -809.19,
                    1568.41,
                ],
            }
        )

        result = self.engine.calculate_payback()

        expected = (
            5
            + 809.19 / 2377.60
        )

        assert result == pytest.approx(
            expected,
            abs=0.001,
        )

    def test_payback_not_reached(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    1000.0,
                    1000.0,
                ],
                "cumulative_cash_flow": [
                    -10000.0,
                    -9000.0,
                    -8000.0,
                ],
            }
        )

        result = self.engine.calculate_payback()

        assert result is None

    def test_payback_exact_year(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    5000.0,
                    5000.0,
                ],
                "cumulative_cash_flow": [
                    -10000.0,
                    -5000.0,
                    0.0,
                ],
            }
        )

        result = self.engine.calculate_payback()

        assert result == pytest.approx(2.0)

    def test_payback_requires_cash_flow(self):

        with pytest.raises(
            RuntimeError,
            match="Cash flow has not been calculated.",
        ):
            self.engine.calculate_payback()

    def test_payback_zero_net_investment_returns_zero(self):

        self.engine.cash_flow = pd.DataFrame(
            [
                {
                    "year": 0,
                    "cash_flow": 0.0,
                    "cumulative_cash_flow": 0.0,
                },
                {
                    "year": 1,
                    "cash_flow": 1000.0,
                    "cumulative_cash_flow": 1000.0,
                },
            ]
        )

        result = self.engine.calculate_payback()

        assert result == 0.0
        assert self.engine.payback_years == 0.0

    def test_calculate_payback_when_recovery_is_exactly_zero(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -1000.0,
                    500.0,
                    500.0,
                ],
                "cumulative_cash_flow": [
                    -1000.0,
                    -500.0,
                    0.0,
                ],
            }
        )

        result = self.engine.calculate_payback()

        assert result == pytest.approx(2.0)
        assert self.engine.payback_years == pytest.approx(2.0)


# ==========================================================
# NPV
# ==========================================================


class TestEconomicsNPV:

    def setup_method(self):
        self.engine = EconomicsEngine()

    def test_npv(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
            }
        )

        result = self.engine.calculate_npv(
            discount_rate=0.05
        )

        expected = (
            -10000.0
            + 6000.0 / 1.05
            + 6000.0 / (1.05 ** 2)
        )

        assert result == pytest.approx(expected)

    def test_npv_zero_discount_rate(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
            }
        )

        result = self.engine.calculate_npv(
            discount_rate=0.0
        )

        assert result == pytest.approx(2000.0)

    def test_npv_negative_discount_rate(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1],
                "cash_flow": [
                    -10000.0,
                    12000.0,
                ],
            }
        )

        with pytest.raises(ValueError):
            self.engine.calculate_npv(
                discount_rate=-0.01
            )

    def test_npv_requires_cash_flow(self):

        with pytest.raises(
            RuntimeError,
            match="Cash flow has not been calculated.",
        ):
            self.engine.calculate_npv(
                discount_rate=0.05
            )

    def test_npv_updates_engine_state(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
            }
        )

        result = self.engine.calculate_npv(
            discount_rate=0.05
        )

        assert self.engine.npv == pytest.approx(
            result
        )


    def test_npv_with_only_initial_investment(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0],
                "cash_flow": [
                    -10000.0,
                ],
            }
        )

        result = self.engine.calculate_npv(
            discount_rate=0.05
        )

        assert result == pytest.approx(
            -10000.0
        )

        assert self.engine.npv == pytest.approx(
            -10000.0
        )


    def test_npv_with_zero_cash_flows(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    0.0,
                    0.0,
                    0.0,
                ],
            }
        )

        result = self.engine.calculate_npv(
            discount_rate=0.05
        )

        assert result == pytest.approx(
            0.0
        )


    def test_npv_with_positive_discount_rate(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1],
                "cash_flow": [
                    -10000.0,
                    11000.0,
                ],
            }
        )

        result = self.engine.calculate_npv(
            discount_rate=0.10
        )

        assert result == pytest.approx(
            0.0
        )


    def test_npv_does_not_modify_cash_flow(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
            }
        )

        original = self.engine.cash_flow.copy()

        self.engine.calculate_npv(
            discount_rate=0.05
        )

        pd.testing.assert_frame_equal(
            self.engine.cash_flow,
            original,
        )


# ==========================================================
# IRR
# ==========================================================


class TestEconomicsIRR:

    def setup_method(self):
        self.engine = EconomicsEngine()

    def test_irr(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
            }
        )

        result = self.engine.calculate_irr()

        expected = npf.irr(
            [
                -10000.0,
                6000.0,
                6000.0,
            ]
        )

        assert result == pytest.approx(expected)

    def test_irr_requires_positive_and_negative_cash_flow(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    1000.0,
                    2000.0,
                    3000.0,
                ],
            }
        )

        with pytest.raises(RuntimeError):
            self.engine.calculate_irr()

    def test_irr_requires_cash_flow(self):

        with pytest.raises(RuntimeError):
            self.engine.calculate_irr()

    def test_irr_handles_calculation_exception(
        self,
        monkeypatch,
    ):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1],
                "cash_flow": [
                    -1000.0,
                    1500.0,
                ],
            }
        )

        def failing_irr(cash_flows):
            raise ValueError("IRR calculation failed")

        monkeypatch.setattr(
            npf,
            "irr",
            failing_irr,
        )

        with pytest.raises(
            RuntimeError,
            match="Unable to calculate IRR.",
        ):
            self.engine.calculate_irr()

    def test_irr_returns_none(self, monkeypatch):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1],
                "cash_flow": [
                    -1000.0,
                    1500.0,
                ],
            }
        )

        monkeypatch.setattr(
            npf,
            "irr",
            lambda cash_flows: None,
        )

        with pytest.raises(
            RuntimeError,
            match="IRR could not be calculated.",
        ):
            self.engine.calculate_irr()

    def test_irr_updates_engine_state(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
            }
        )

        result = self.engine.calculate_irr()

        assert self.engine.irr == pytest.approx(
            result
        )


    def test_irr_with_zero_cash_flows(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    0.0,
                    0.0,
                    0.0,
                ],
            }
        )

        with pytest.raises(RuntimeError):
            self.engine.calculate_irr()


    def test_irr_does_not_modify_cash_flow(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
            }
        )

        original = self.engine.cash_flow.copy()

        self.engine.calculate_irr()

        pd.testing.assert_frame_equal(
            self.engine.cash_flow,
            original,
        )


# ==========================================================
# Indicadores económicos
# ==========================================================


class TestEconomicIndicators:

    def setup_method(self):
        self.engine = EconomicsEngine()

    def test_economic_indicators(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
                "cumulative_cash_flow": [
                    -10000.0,
                    -4000.0,
                    2000.0,
                ],
            }
        )

        result = self.engine.calculate_economic_indicators(
            discount_rate=0.05
        )

        expected_payback = (
            1
            + 4000.0 / 6000.0
        )

        expected_npv = (
            -10000.0
            + 6000.0 / 1.05
            + 6000.0 / (1.05 ** 2)
        )

        expected_irr = npf.irr(
            [
                -10000.0,
                6000.0,
                6000.0,
            ]
        )

        assert result["payback_years"] == pytest.approx(
            expected_payback
        )

        assert result["npv"] == pytest.approx(
            expected_npv
        )

        assert result["irr"] == pytest.approx(
            expected_irr
        )

        assert self.engine.payback_years == pytest.approx(
            expected_payback
        )

        assert self.engine.npv == pytest.approx(
            expected_npv
        )

        assert self.engine.irr == pytest.approx(
            expected_irr
        )

    def test_economic_indicators_requires_cash_flow(self):

        with pytest.raises(
            RuntimeError,
            match="Cash flow has not been calculated.",
        ):
            self.engine.calculate_economic_indicators(
                discount_rate=0.05
            )

    def test_economic_indicators_updates_engine_state(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
                "cumulative_cash_flow": [
                    -10000.0,
                    -4000.0,
                    2000.0,
                ],
            }
        )

        result = self.engine.calculate_economic_indicators(
            discount_rate=0.05
        )

        assert self.engine.payback_years == pytest.approx(
            result["payback_years"]
        )

        assert self.engine.npv == pytest.approx(
            result["npv"]
        )

        assert self.engine.irr == pytest.approx(
            result["irr"]
        )


    def test_economic_indicators_returns_all_indicators(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
                "cumulative_cash_flow": [
                    -10000.0,
                    -4000.0,
                    2000.0,
                ],
            }
        )

        result = self.engine.calculate_economic_indicators(
            discount_rate=0.05
        )

        assert set(result.keys()) == {
            "payback_years",
            "npv",
            "irr",
        }


    def test_economic_indicators_uses_discount_rate(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [0, 1, 2],
                "cash_flow": [
                    -10000.0,
                    6000.0,
                    6000.0,
                ],
                "cumulative_cash_flow": [
                    -10000.0,
                    -4000.0,
                    2000.0,
                ],
            }
        )

        result_low_rate = (
            self.engine.calculate_economic_indicators(
                discount_rate=0.03
            )
        )

        result_high_rate = (
            self.engine.calculate_economic_indicators(
                discount_rate=0.08
            )
        )

        assert result_low_rate["npv"] > result_high_rate["npv"]


# ==========================================================
# Costes, ingresos y ahorro
# ==========================================================


class TestEconomicsCosts:

    def setup_method(self):
        self.engine = EconomicsEngine()

    def test_calculate_cost_without_pv(self):

        index = pd.date_range(
            "2025-01-01",
            periods=8760,
            freq="h",
        )

        consumption = pd.Series(
            0.0,
            index=index,
            name="AE_kWh",
        )

        consumption.iloc[0] = 10.0
        consumption.iloc[1] = 20.0
        consumption.iloc[2] = 30.0

        consumption_scenario = ConsumptionScenario(
            hourly_consumption=consumption,
            reference_year=2025,
        )

        buy_prices = pd.Series(
            0.0,
            index=index,
            name="buy_price_eur_kwh",
        )

        buy_prices.iloc[0] = 0.25
        buy_prices.iloc[1] = 0.18
        buy_prices.iloc[2] = 0.12

        tariff_data = pd.DataFrame(
            {
                "buy_price_eur_kwh": buy_prices,
            },
            index=index,
        )

        result = self.engine.calculate_cost_without_pv(
            consumption_scenario,
            tariff_data,
        )

        expected = (
            10.0 * 0.25
            + 20.0 * 0.18
            + 30.0 * 0.12
        )

        assert result == pytest.approx(expected)
        assert self.engine.cost_without_pv == pytest.approx(
            expected
        )

    def test_calculate_export_income(self):

        index = pd.date_range(
            "2025-01-01",
            periods=3,
            freq="h",
        )

        energy_balance = pd.DataFrame(
            {
                "grid_export_kwh": [
                    10.0,
                    20.0,
                    30.0,
                ],
            },
            index=index,
        )

        tariff_data = pd.DataFrame(
            {
                "sell_price_eur_kwh": [
                    0.06,
                    0.06,
                    0.06,
                ],
            },
            index=index,
        )

        result = self.engine.calculate_export_income(
            energy_balance,
            tariff_data,
        )

        expected = (
            10.0 * 0.06
            + 20.0 * 0.06
            + 30.0 * 0.06
        )

        assert result == pytest.approx(expected)

        assert self.engine.export_income == pytest.approx(
            expected
        )

    def test_calculate_cost_with_pv(self):

        index = pd.date_range(
            "2025-01-01",
            periods=3,
            freq="h",
        )

        energy_balance = pd.DataFrame(
            {
                "grid_import_kwh": [
                    10.0,
                    20.0,
                    30.0,
                ],
            },
            index=index,
        )

        tariff_data = pd.DataFrame(
            {
                "buy_price_eur_kwh": [
                    0.25,
                    0.18,
                    0.12,
                ],
            },
            index=index,
        )

        self.engine.export_income = 2.0

        result = self.engine.calculate_cost_with_pv(
            energy_balance,
            tariff_data,
        )

        expected_grid_import_cost = (
            10.0 * 0.25
            + 20.0 * 0.18
            + 30.0 * 0.12
        )

        expected_cost_with_pv = (
            expected_grid_import_cost
            - 2.0
        )

        assert self.engine.grid_import_cost == pytest.approx(
            expected_grid_import_cost
        )

        assert result == pytest.approx(
            expected_cost_with_pv
        )

        assert self.engine.cost_with_pv == pytest.approx(
            expected_cost_with_pv
        )

    def test_calculate_annual_savings(self):

        self.engine.cost_without_pv = 1000.0
        self.engine.cost_with_pv = 400.0
        self.engine.export_income = 100.0

        result = self.engine.calculate_annual_savings()

        expected_self_consumption = (
            1000.0
            - (
                400.0
                + 100.0
            )
        )

        expected_annual_savings = (
            expected_self_consumption
            + 100.0
        )

        assert (
            self.engine.self_consumption_savings
            == pytest.approx(
                expected_self_consumption
            )
        )

        assert result == pytest.approx(
            expected_annual_savings
        )

        assert self.engine.annual_savings == pytest.approx(
            expected_annual_savings
        )

    def test_calculate_annual_savings_without_cost_without_pv(self):

        self.engine.cost_with_pv = 400.0
        self.engine.export_income = 100.0

        with pytest.raises(
            RuntimeError,
            match="Cost without PV has not been calculated.",
        ):
            self.engine.calculate_annual_savings()

    def test_calculate_annual_savings_without_cost_with_pv(self):

        self.engine.cost_without_pv = 1000.0
        self.engine.export_income = 100.0

        with pytest.raises(
            RuntimeError,
            match="Cost with PV has not been calculated.",
        ):
            self.engine.calculate_annual_savings()

    def test_calculate_annual_savings_without_export_income(self):

        self.engine.cost_without_pv = 1000.0
        self.engine.cost_with_pv = 400.0

        with pytest.raises(
            RuntimeError,
            match="Export income has not been calculated.",
        ):
            self.engine.calculate_annual_savings()


# ==========================================================
# Inversión
# ==========================================================


class TestNetInvestment:

    def setup_method(self):
        self.engine = EconomicsEngine()

    def test_calculate_net_investment(self):

        class Configuration:
            installation_cost = 15000.0
            subsidies = 2000.0
            tax_deductions = 1000.0

        result = self.engine.calculate_net_investment(
            Configuration()
        )

        assert result == pytest.approx(
            12000.0
        )

        assert self.engine.net_investment == pytest.approx(
            12000.0
        )

    def test_calculate_net_investment_zero_subsidies_and_deductions(self):

        class Configuration:
            installation_cost = 10000.0
            subsidies = 0.0
            tax_deductions = 0.0

        result = self.engine.calculate_net_investment(
            Configuration()
        )

        assert result == pytest.approx(
            10000.0
        )

        assert self.engine.net_investment == pytest.approx(
            10000.0
        )


# ==========================================================
# Escenarios
# ==========================================================


class TestCalculateScenario:

    def setup_method(self):
        self.engine = EconomicsEngine()

        self.engine.net_investment = 10000.0
        self.engine.self_consumption_savings = 2000.0
        self.engine.export_income = 500.0
        self.engine.cost_without_pv = 3000.0

    def _configuration(self):

        class Configuration:
            first_year_degradation = 0.01
            annual_degradation = 0.0035

            annual_electricity_price_growth = 0.02
            annual_export_price_growth = 0.01

            annual_maintenance_cost = 100.0
            annual_maintenance_growth = 0.02

            discount_rate = 0.05

        return Configuration()

    def _scenario(self):

        class Scenario:
            name = "Base"

            annual_degradation = None
            discount_rate = None

            buy_price_factor = 1.0
            sell_price_factor = 1.0

            annual_maintenance = None

        return Scenario()

    def _calculate_base_result(self, years=5):

        return self.engine.calculate_scenario(
            scenario=self._scenario(),
            configuration=self._configuration(),
            years=years,
        )

    def test_calculate_scenario_returns_result(self):

        result = self._calculate_base_result()

        assert result.name == "Base"

        assert isinstance(
            result,
            EconomicScenarioResult,
        )

    def test_calculate_scenario_annual_savings(self):

        result = self._calculate_base_result()

        expected = (
            self.engine.self_consumption_savings
            + self.engine.export_income
        ) * 0.99

        assert result.annual_savings == pytest.approx(
            expected
        )

    def test_scenario_annual_savings_applies_buy_price_factor(self):

        class Scenario:

            name = "Buy price factor"

            annual_degradation = None
            discount_rate = None

            buy_price_factor = 0.90
            sell_price_factor = 1.0

            annual_maintenance = None

        result = self.engine.calculate_scenario(
            scenario=Scenario(),
            configuration=self._configuration(),
            years=5,
        )

        expected = (
            self.engine.self_consumption_savings
            * 0.99
            * 0.90
        ) + (
            self.engine.export_income
            * 0.99
        )

        assert result.annual_savings == pytest.approx(
            expected
        )

    def test_scenario_annual_savings_applies_sell_price_factor(self):

        class Scenario:

            name = "Sell price factor"

            annual_degradation = None
            discount_rate = None

            buy_price_factor = 1.0
            sell_price_factor = 0.90

            annual_maintenance = None

        result = self.engine.calculate_scenario(
            scenario=Scenario(),
            configuration=self._configuration(),
            years=5,
        )

        expected = (
            self.engine.self_consumption_savings
            * 0.99
        ) + (
            self.engine.export_income
            * 0.99
            * 0.90
        )

        assert result.annual_savings == pytest.approx(
            expected
        )

    def test_scenario_annual_savings_excludes_maintenance(self):

        class Scenario:

            name = "Maintenance"

            annual_degradation = None
            discount_rate = None

            buy_price_factor = 1.0
            sell_price_factor = 1.0

            annual_maintenance = 500.0

        result = self.engine.calculate_scenario(
            scenario=Scenario(),
            configuration=self._configuration(),
            years=5,
        )

        expected_gross_savings = (
            self.engine.self_consumption_savings
            + self.engine.export_income
        ) * 0.99

        assert result.annual_savings == pytest.approx(
            expected_gross_savings
        )

    def test_scenario_annual_savings_applies_first_year_degradation(
        self,
    ):

        scenario = EconomicScenario(
            name="Base",
        )

        configuration = self._configuration()

        result = self.engine.calculate_scenario(
            scenario=scenario,
            configuration=configuration,
            years=25,
        )

        expected = (
            self.engine.self_consumption_savings
            + self.engine.export_income
        ) * 0.99

        assert result.annual_savings == pytest.approx(
            expected
        )

    def test_scenario_annual_savings_applies_buy_price_factor_explicit(
        self,
    ):

        scenario = EconomicScenario(
            name="Compra -10%",
            buy_price_factor=0.90,
        )

        configuration = self._configuration()

        result = self.engine.calculate_scenario(
            scenario=scenario,
            configuration=configuration,
            years=25,
        )

        expected = (
            self.engine.self_consumption_savings
            * 0.99
            * 0.90
        ) + (
            self.engine.export_income
            * 0.99
        )

        assert result.annual_savings == pytest.approx(
            expected
        )

    def test_scenario_annual_savings_applies_sell_price_factor_explicit(
        self,
    ):

        scenario = EconomicScenario(
            name="Venta -10%",
            sell_price_factor=0.90,
        )

        configuration = self._configuration()

        result = self.engine.calculate_scenario(
            scenario=scenario,
            configuration=configuration,
            years=25,
        )

        expected = (
            self.engine.self_consumption_savings
            * 0.99
        ) + (
            self.engine.export_income
            * 0.99
            * 0.90
        )

        assert result.annual_savings == pytest.approx(
            expected
        )

    def test_scenario_annual_savings_excludes_maintenance_explicit(
        self,
    ):

        scenario = EconomicScenario(
            name="Base",
        )

        configuration = self._configuration()

        result = self.engine.calculate_scenario(
            scenario=scenario,
            configuration=configuration,
            years=25,
        )

        expected_gross_savings = (
            self.engine.self_consumption_savings
            + self.engine.export_income
        ) * 0.99

        expected_net_cash_flow = (
            expected_gross_savings
            - 150.0
        )

        assert result.annual_savings == pytest.approx(
            expected_gross_savings
        )

        assert result.annual_savings != pytest.approx(
            expected_net_cash_flow
        )

    def test_scenario_first_year_cash_flow_still_includes_maintenance(
        self,
    ):

        scenario = EconomicScenario(
            name="Base",
        )

        configuration = self._configuration()

        result = self.engine.calculate_scenario(
            scenario=scenario,
            configuration=configuration,
            years=25,
        )

        expected_gross_savings = (
            self.engine.self_consumption_savings
            + self.engine.export_income
        ) * 0.99

        expected_cash_flow = (
            expected_gross_savings
            - 100.0
        )

        assert result.annual_savings == pytest.approx(
            expected_gross_savings
        )

        assert expected_cash_flow < result.annual_savings

    def test_calculate_scenario_payback_is_correct(self):

        result = self._calculate_base_result()

        expected_payback = 4.11789803991689

        assert result.payback_years == pytest.approx(
            expected_payback,
            abs=0.001,
        )

    def test_calculate_scenario_payback_is_finite(self):

        result = self._calculate_base_result()

        assert np.isfinite(result.payback_years)
        assert result.payback_years > 0

    def test_calculate_scenario_payback_matches_cash_flow_payback_first_year(self):

        configuration = self._configuration()

        self.engine.net_investment = 1000.0
        self.engine.self_consumption_savings = 1200.0
        self.engine.export_income = 0.0
        self.engine.annual_savings = 1200.0

        self.engine.calculate_cash_flow(
            configuration,
            years=1,
        )

        cash_flow_payback = self.engine.calculate_payback()

        scenario_result = self.engine.calculate_scenario(
            scenario=self._scenario(),
            configuration=configuration,
            years=1,
        )

        assert scenario_result.payback_years == pytest.approx(
            cash_flow_payback
        )


    def test_calculate_scenario_payback_matches_cash_flow_payback_fractional(self):

        configuration = self._configuration()

        self.engine.net_investment = 1000.0
        self.engine.self_consumption_savings = 400.0
        self.engine.export_income = 400.0
        self.engine.annual_savings = 800.0

        self.engine.calculate_cash_flow(
            configuration,
            years=2,
        )

        cash_flow_payback = self.engine.calculate_payback()

        scenario_result = self.engine.calculate_scenario(
            scenario=self._scenario(),
            configuration=configuration,
            years=2,
        )

        assert scenario_result.payback_years == pytest.approx(
            cash_flow_payback
        )