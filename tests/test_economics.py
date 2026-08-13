import pytest

import pandas as pd

import numpy_financial as npf

from helios.core.economics import EconomicsEngine


class TestEconomicsFactors:

    def setup_method(self):
        self.engine = EconomicsEngine()

    def test_degradation_year_1(self):
        class Configuration:
            first_year_degradation = 0.01
            annual_degradation = 0.0035

        result = self.engine.calculate_degradation_factor(
            1,
            Configuration()
        )

        assert result == pytest.approx(0.99)

    def test_degradation_year_2(self):
        class Configuration:
            first_year_degradation = 0.01
            annual_degradation = 0.0035

        result = self.engine.calculate_degradation_factor(
            2,
            Configuration()
        )

        assert result == pytest.approx(0.9865)

    def test_degradation_year_25(self):
        class Configuration:
            first_year_degradation = 0.01
            annual_degradation = 0.0035

        result = self.engine.calculate_degradation_factor(
            25,
            Configuration()
        )

        expected = (
            1
            - 0.01
            - (0.0035 * 24)
        )

        assert result == pytest.approx(expected)

    def test_degradation_year_zero(self):
        class Configuration:
            first_year_degradation = 0.01
            annual_degradation = 0.0035

        result = self.engine.calculate_degradation_factor(
            0,
            Configuration()
        )

        assert result == pytest.approx(1.0)

    def test_electricity_price_factor(self):
        class Configuration:
            annual_electricity_price_growth = 0.02

        assert (
            self.engine.calculate_electricity_price_factor(
                1,
                Configuration()
            )
            == pytest.approx(1.0)
        )

        assert (
            self.engine.calculate_electricity_price_factor(
                2,
                Configuration()
            )
            == pytest.approx(1.02)
        )

    def test_electricity_price_factor(self):
        class Configuration:
            annual_electricity_price_growth = 0.02

        assert (
            self.engine.calculate_electricity_price_factor(
                1,
                Configuration()
            )
            == pytest.approx(1.0)
        )

        assert (
            self.engine.calculate_electricity_price_factor(
                2,
                Configuration()
            )
            == pytest.approx(1.02)
        )

    def test_maintenance_cost(self):
        class Configuration:
            annual_maintenance_cost = 150.0
            annual_maintenance_growth = 0.02

        assert (
            self.engine.calculate_maintenance_cost(
                1,
                Configuration()
            )
            == pytest.approx(150.0)
        )

        assert (
            self.engine.calculate_maintenance_cost(
                2,
                Configuration()
            )
            == pytest.approx(153.0)
        )

        assert (
            self.engine.calculate_maintenance_cost(
                3,
                Configuration()
            )
            == pytest.approx(156.06)
        )

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
            years=25
        )

        row = result.iloc[0]

        assert row["year"] == 0

        assert (
            row["cash_flow"]
            == pytest.approx(-12490.0)
        )

        assert (
            row["cumulative_cash_flow"]
            == pytest.approx(-12490.0)
        )

    def test_cash_flow_year_1(self):

        self._prepare_engine()

        result = self.engine.calculate_cash_flow(
            self._configuration(),
            years=25
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

        assert (
            row["self_consumption_savings"]
            == pytest.approx(
                expected_self_consumption
            )
        )

        assert (
            row["export_income"]
            == pytest.approx(
                expected_export
            )
        )

        assert (
            row["maintenance_cost"]
            == pytest.approx(
                expected_maintenance
            )
        )

        assert (
            row["cash_flow"]
            == pytest.approx(
                expected_cash_flow
            )
        )

    def test_cash_flow_year_2(self):

        self._prepare_engine()

        result = self.engine.calculate_cash_flow(
            self._configuration(),
            years=25
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

        expected_maintenance = (
            150.0
            * 1.02
        )

        expected_cash_flow = (
            expected_self_consumption
            + expected_export
            - expected_maintenance
        )

        assert (
            row["self_consumption_savings"]
            == pytest.approx(
                expected_self_consumption
            )
        )

        assert (
            row["export_income"]
            == pytest.approx(
                expected_export
            )
        )

        assert (
            row["maintenance_cost"]
            == pytest.approx(
                expected_maintenance
            )
        )

        assert (
            row["cash_flow"]
            == pytest.approx(
                expected_cash_flow
            )
        )

    def test_cash_flow_has_26_rows(self):

        self._prepare_engine()

        result = self.engine.calculate_cash_flow(
            self._configuration(),
            years=25
        )

        assert len(result) == 26

        assert result.iloc[0]["year"] == 0
        assert result.iloc[-1]["year"] == 25

class TestEconomicsPayback:

    def setup_method(self):
        self.engine = EconomicsEngine()

    def test_payback(self):

        self.engine.cash_flow = pd.DataFrame(
            {
                "year": [
                    0,
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                ],
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
            abs=0.001
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

        assert result == pytest.approx(
            expected
        )

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