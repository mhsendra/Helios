import pytest
import pandas as pd
import numpy_financial as npf

from helios.core.economics import EconomicsEngine
from helios.core.economic_scenarios import EconomicScenarioResult


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

    def test_electricity_price_factor_year_zero(self):

        class Configuration:
            annual_electricity_price_growth = 0.02

        result = self.engine.calculate_electricity_price_factor(
            0,
            Configuration()
        )

        assert result == pytest.approx(1.0)


    def test_export_price_factor_year_zero(self):

        class Configuration:
            annual_export_price_growth = 0.01

        result = self.engine.calculate_export_price_factor(
            0,
            Configuration()
        )

        assert result == pytest.approx(1.0)


    def test_maintenance_cost_year_zero(self):

        class Configuration:
            annual_maintenance_cost = 150.0
            annual_maintenance_growth = 0.02

        result = self.engine.calculate_maintenance_cost(
            0,
            Configuration()
        )

        assert result == pytest.approx(0.0)

    def test_apply_price_factors(self):

        tariff_data = pd.DataFrame(
            {
                "buy_price_eur_kwh": [
                    0.20,
                    0.30,
                ],
                "sell_price_eur_kwh": [
                    0.06,
                    0.07,
                ],
                "other": [
                    1,
                    2,
                ],
            }
        )

        result = self.engine._apply_price_factors(
            tariff_data,
            buy_price_factor=1.10,
            sell_price_factor=0.50,
        )

        assert result["buy_price_eur_kwh"].tolist() == pytest.approx(
            [0.22, 0.33]
        )

        assert result["sell_price_eur_kwh"].tolist() == pytest.approx(
            [0.03, 0.035]
        )

        assert "other" not in result.columns

        assert tariff_data["buy_price_eur_kwh"].tolist() == pytest.approx(
            [0.20, 0.30]
        )

        assert tariff_data["sell_price_eur_kwh"].tolist() == pytest.approx(
            [0.06, 0.07]
        )


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
            years=25
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
            years=25
        )

        assert len(result) == 26

        assert result.iloc[0]["year"] == 0
        assert result.iloc[-1]["year"] == 25

    def test_cash_flow_requires_net_investment(self):

        self.engine.annual_savings = 1000.0

        with pytest.raises(
            RuntimeError,
            match="Net investment has not been calculated."
        ):
            self.engine.calculate_cash_flow(
                self._configuration()
            )


    def test_cash_flow_requires_annual_savings(self):

        self.engine.net_investment = 10000.0

        with pytest.raises(
            RuntimeError,
            match="Annual savings have not been calculated."
        ):
            self.engine.calculate_cash_flow(
                self._configuration()
            )


    def test_cash_flow_requires_positive_years(self):

        self.engine.net_investment = 10000.0
        self.engine.annual_savings = 2000.0

        with pytest.raises(
            ValueError,
            match="Years must be greater than zero."
        ):
            self.engine.calculate_cash_flow(
                self._configuration(),
                years=0
            )

    def test_economic_summary_requires_cash_flow(self):

        with pytest.raises(
            RuntimeError,
            match="Cash flow has not been calculated."
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

    def test_payback_requires_cash_flow(self):

        with pytest.raises(
            RuntimeError,
            match="Cash flow has not been calculated."
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
            match="Cash flow has not been calculated."
        ):
            self.engine.calculate_npv(
                discount_rate=0.05
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

    def test_irr_handles_calculation_exception(self, monkeypatch):

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
            failing_irr
        )

        with pytest.raises(
            RuntimeError,
            match="Unable to calculate IRR."
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
            lambda cash_flows: None
        )

        with pytest.raises(
            RuntimeError,
            match="IRR could not be calculated."
        ):
            self.engine.calculate_irr()


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
            match="Cash flow has not been calculated."
        ):
            self.engine.calculate_economic_indicators(
                discount_rate=0.05
            )

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
            freq="h"
        )

        energy_balance = pd.DataFrame(
            {
                "grid_export_kwh": [
                    10.0,
                    20.0,
                    30.0,
                ],
            },
            index=index
        )

        tariff_data = pd.DataFrame(
            {
                "sell_price_eur_kwh": [
                    0.06,
                    0.06,
                    0.06,
                ],
            },
            index=index
        )

        result = self.engine.calculate_export_income(
            energy_balance,
            tariff_data
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
            freq="h"
        )

        energy_balance = pd.DataFrame(
            {
                "grid_import_kwh": [
                    10.0,
                    20.0,
                    30.0,
                ],
            },
            index=index
        )

        tariff_data = pd.DataFrame(
            {
                "buy_price_eur_kwh": [
                    0.25,
                    0.18,
                    0.12,
                ],
            },
            index=index
        )

        self.engine.export_income = 2.0

        result = self.engine.calculate_cost_with_pv(
            energy_balance,
            tariff_data
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
            - (400.0 + 100.0)
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
            match="Cost without PV has not been calculated."
        ):
            self.engine.calculate_annual_savings()

    def test_calculate_annual_savings_without_cost_with_pv(self):

        self.engine.cost_without_pv = 1000.0
        self.engine.export_income = 100.0

        with pytest.raises(
            RuntimeError,
            match="Cost with PV has not been calculated."
        ):
            self.engine.calculate_annual_savings()

    def test_calculate_annual_savings_without_export_income(self):

        self.engine.cost_without_pv = 1000.0
        self.engine.cost_with_pv = 400.0

        with pytest.raises(
            RuntimeError,
            match="Export income has not been calculated."
        ):
            self.engine.calculate_annual_savings()


# ==========================================================
# Inversión
# ==========================================================


class TestEconomicsInvestment:

    def setup_method(self):

        self.engine = EconomicsEngine()

    def test_calculate_net_investment(self):

        class Configuration:

            installation_cost = 12490.0
            subsidies = 2000.0
            tax_deductions = 1000.0

        result = self.engine.calculate_net_investment(
            Configuration()
        )

        expected = (
            12490.0
            - 2000.0
            - 1000.0
        )

        assert result == pytest.approx(expected)

        assert self.engine.net_investment == pytest.approx(
            expected
        )

class TestEconomicsScenarios:

    def setup_method(self):

        self.engine = EconomicsEngine()

        self.engine.net_investment = 10000.0

        self.engine.self_consumption_savings = 1000.0

        self.engine.export_income = 200.0

    def _configuration(self):

        class Configuration:

            first_year_degradation = 0.01
            annual_degradation = 0.0035

            annual_electricity_price_growth = 0.02
            annual_export_price_growth = 0.0

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

    def test_calculate_scenario(self):

        result = self.engine.calculate_scenario(
            scenario=self._scenario(),
            configuration=self._configuration(),
            dataset=None,
            energy_balance=None,
            tariff_data=None,
            years=5,
        )

        assert result.name == "Base"

        assert result.annual_savings == pytest.approx(
            1200.0
        )

        assert result.payback_years > 0

        assert result.npv is not None

        assert result.irr is not None

    def test_calculate_scenario_with_custom_parameters(self):

        class Scenario:

            name = "Optimista"

            annual_degradation = 0.002
            discount_rate = 0.04

            buy_price_factor = 1.10
            sell_price_factor = 1.05

            annual_maintenance = None

        result = self.engine.calculate_scenario(
            scenario=Scenario(),
            configuration=self._configuration(),
            dataset=None,
            energy_balance=None,
            tariff_data=None,
            years=5,
        )

        assert result.name == "Optimista"

        assert result.annual_savings == pytest.approx(
            1200.0
        )

        assert result.npv is not None

        assert result.irr is not None

    def test_calculate_scenario_invalid_years(self):

        with pytest.raises(
            ValueError,
            match="Years must be greater than zero."
        ):

            self.engine.calculate_scenario(
                scenario=self._scenario(),
                configuration=self._configuration(),
                dataset=None,
                energy_balance=None,
                tariff_data=None,
                years=0,
            )

    def test_calculate_scenario_requires_net_investment(self):

        self.engine.net_investment = None

        with pytest.raises(
            RuntimeError,
            match="Net investment has not been calculated."
        ):

            self.engine.calculate_scenario(
                scenario=self._scenario(),
                configuration=self._configuration(),
                dataset=None,
                energy_balance=None,
                tariff_data=None,
                years=5,
            )

    def test_calculate_scenario_requires_self_consumption_savings(self):

        self.engine.self_consumption_savings = None

        with pytest.raises(
            RuntimeError,
            match="Self-consumption savings have not been calculated."
        ):

            self.engine.calculate_scenario(
                scenario=self._scenario(),
                configuration=self._configuration(),
                dataset=None,
                energy_balance=None,
                tariff_data=None,
                years=5,
            )

    def test_calculate_scenario_requires_export_income(self):

        self.engine.export_income = None

        with pytest.raises(
            RuntimeError,
            match="Export income has not been calculated."
        ):

            self.engine.calculate_scenario(
                scenario=self._scenario(),
                configuration=self._configuration(),
                dataset=None,
                energy_balance=None,
                tariff_data=None,
                years=5,
            )

    def test_calculate_scenario_irr_none(self, monkeypatch):

        class Scenario:
            name = "IRR None"

            annual_degradation = None
            discount_rate = None

            buy_price_factor = 1.0
            sell_price_factor = 1.0

            annual_maintenance = None

        class Configuration:
            first_year_degradation = 0.01
            annual_degradation = 0.0035

            annual_electricity_price_growth = 0.02
            annual_export_price_growth = 0.0

            annual_maintenance_cost = 150.0
            annual_maintenance_growth = 0.02

            discount_rate = 0.05

        self.engine.net_investment = 10000.0
        self.engine.self_consumption_savings = 2000.0
        self.engine.export_income = 500.0

        monkeypatch.setattr(
            npf,
            "irr",
            lambda cash_flows: None
        )

        with pytest.raises(
            RuntimeError,
            match="IRR could not be calculated for scenario 'IRR None'."
        ):
            self.engine.calculate_scenario(
                scenario=Scenario(),
                configuration=Configuration(),
                dataset=pd.DataFrame(),
                energy_balance=pd.DataFrame(),
                tariff_data=pd.DataFrame(),
                years=1,
            )

class TestScenarioAnnualSavings:

    def setup_method(self):
        self.engine = EconomicsEngine()

        self.engine.cost_without_pv = 3000.0

        self.energy_balance = pd.DataFrame(
            {
                "grid_import_kwh": [
                    100.0,
                    200.0,
                ],
                "grid_export_kwh": [
                    50.0,
                    100.0,
                ],
            }
        )

        self.tariff_data = pd.DataFrame(
            {
                "buy_price_eur_kwh": [
                    0.20,
                    0.20,
                ],
                "sell_price_eur_kwh": [
                    0.05,
                    0.05,
                ],
            }
        )

    def test_scenario_annual_savings_default_factors(self):

        result = (
            self.engine.calculate_scenario_annual_savings(
                self.energy_balance,
                self.tariff_data,
            )
        )

        expected_grid_import_cost = (
            100.0 * 0.20
            + 200.0 * 0.20
        )

        expected_export_income = (
            50.0 * 0.05
            + 100.0 * 0.05
        )

        expected_cost_with_pv = (
            expected_grid_import_cost
            - expected_export_income
        )

        expected_self_consumption_savings = (
            3000.0
            - (
                expected_cost_with_pv
                + expected_export_income
            )
        )

        expected = (
            expected_self_consumption_savings
            + expected_export_income
        )

        assert result == pytest.approx(
            expected
        )

    def test_scenario_annual_savings_buy_price_factor(self):

        result = (
            self.engine.calculate_scenario_annual_savings(
                self.energy_balance,
                self.tariff_data,
                buy_price_factor=1.10,
            )
        )

        expected_grid_import_cost = (
            (100.0 * 0.20 * 1.10)
            + (200.0 * 0.20 * 1.10)
        )

        expected_export_income = 7.5

        expected_cost_with_pv = (
            expected_grid_import_cost
            - expected_export_income
        )

        expected_self_consumption_savings = (
            3000.0
            - (
                expected_cost_with_pv
                + expected_export_income
            )
        )

        expected = (
            expected_self_consumption_savings
            + expected_export_income
        )

        assert result == pytest.approx(
            expected
        )

    def test_scenario_annual_savings_sell_price_factor(self):

        result = (
            self.engine.calculate_scenario_annual_savings(
                self.energy_balance,
                self.tariff_data,
                sell_price_factor=1.20,
            )
        )

        expected_grid_import_cost = 60.0

        expected_export_income = (
            (50.0 * 0.05 * 1.20)
            + (100.0 * 0.05 * 1.20)
        )

        expected_cost_with_pv = (
            expected_grid_import_cost
            - expected_export_income
        )

        expected_self_consumption_savings = (
            3000.0
            - (
                expected_cost_with_pv
                + expected_export_income
            )
        )

        expected = (
            expected_self_consumption_savings
            + expected_export_income
        )

        assert result == pytest.approx(
            expected
        )

    def test_scenario_annual_savings_combined_factors(self):

        result = (
            self.engine.calculate_scenario_annual_savings(
                self.energy_balance,
                self.tariff_data,
                buy_price_factor=1.10,
                sell_price_factor=0.80,
            )
        )

        expected_grid_import_cost = (
            60.0 * 1.10
        )

        expected_export_income = (
            7.5 * 0.80
        )

        expected_cost_with_pv = (
            expected_grid_import_cost
            - expected_export_income
        )

        expected_self_consumption_savings = (
            3000.0
            - (
                expected_cost_with_pv
                + expected_export_income
            )
        )

        expected = (
            expected_self_consumption_savings
            + expected_export_income
        )

        assert result == pytest.approx(
            expected
        )
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

    def _energy_balance(self):

        return pd.DataFrame(
            {
                "grid_import_kwh": [100.0],
                "grid_export_kwh": [50.0],
            }
        )

    def _tariff_data(self):

        return pd.DataFrame(
            {
                "buy_price_eur_kwh": [0.20],
                "sell_price_eur_kwh": [0.05],
            }
        )

    def test_calculate_scenario_returns_result(self):

        result = self.engine.calculate_scenario(
            scenario=self._scenario(),
            configuration=self._configuration(),
            dataset=pd.DataFrame(),
            energy_balance=self._energy_balance(),
            tariff_data=self._tariff_data(),
            years=5,
        )

        assert result.name == "Base"

        assert isinstance(
            result,
            EconomicScenarioResult
        )

    def test_calculate_scenario_annual_savings(self):

        result = self.engine.calculate_scenario(
            scenario=self._scenario(),
            configuration=self._configuration(),
            dataset=pd.DataFrame(),
            energy_balance=self._energy_balance(),
            tariff_data=self._tariff_data(),
            years=5,
        )

        expected = (
            self.engine.self_consumption_savings
            + self.engine.export_income
        )

        assert result.annual_savings == pytest.approx(
            expected
        )

    def test_calculate_scenario_payback_is_calculated(self):

        result = self.engine.calculate_scenario(
            scenario=self._scenario(),
            configuration=self._configuration(),
            dataset=pd.DataFrame(),
            energy_balance=self._energy_balance(),
            tariff_data=self._tariff_data(),
            years=5,
        )

        assert result.payback_years != float("inf")

        assert result.payback_years > 0

    def test_calculate_scenario_npv_is_calculated(self):

        result = self.engine.calculate_scenario(
            scenario=self._scenario(),
            configuration=self._configuration(),
            dataset=pd.DataFrame(),
            energy_balance=self._energy_balance(),
            tariff_data=self._tariff_data(),
            years=5,
        )

        assert isinstance(
            result.npv,
            float
        )

    def test_calculate_scenario_irr_is_calculated(self):

        result = self.engine.calculate_scenario(
            scenario=self._scenario(),
            configuration=self._configuration(),
            dataset=pd.DataFrame(),
            energy_balance=self._energy_balance(),
            tariff_data=self._tariff_data(),
            years=5,
        )

        assert isinstance(
            result.irr,
            float
        )

    def test_calculate_scenario_custom_parameters(self):

        class Scenario:

            name = "Optimista"

            annual_degradation = 0.002
            discount_rate = 0.04

            buy_price_factor = 1.10
            sell_price_factor = 1.20

            annual_maintenance = 80.0

        result = self.engine.calculate_scenario(
            scenario=Scenario(),
            configuration=self._configuration(),
            dataset=pd.DataFrame(),
            energy_balance=self._energy_balance(),
            tariff_data=self._tariff_data(),
            years=5,
        )

        assert result.name == "Optimista"

        assert isinstance(
            result.npv,
            float
        )

        assert isinstance(
            result.irr,
            float
        )

    def test_calculate_scenario_requires_net_investment(self):

        self.engine.net_investment = None

        with pytest.raises(
            RuntimeError,
            match="Net investment has not been calculated."
        ):
            self.engine.calculate_scenario(
                scenario=self._scenario(),
                configuration=self._configuration(),
                dataset=pd.DataFrame(),
                energy_balance=self._energy_balance(),
                tariff_data=self._tariff_data(),
                years=5,
            )

    def test_calculate_scenario_requires_self_consumption_savings(self):

        self.engine.self_consumption_savings = None

        with pytest.raises(
            RuntimeError,
            match="Self-consumption savings have not been calculated."
        ):
            self.engine.calculate_scenario(
                scenario=self._scenario(),
                configuration=self._configuration(),
                dataset=pd.DataFrame(),
                energy_balance=self._energy_balance(),
                tariff_data=self._tariff_data(),
                years=5,
            )

    def test_calculate_scenario_requires_export_income(self):

        self.engine.export_income = None

        with pytest.raises(
            RuntimeError,
            match="Export income has not been calculated."
        ):
            self.engine.calculate_scenario(
                scenario=self._scenario(),
                configuration=self._configuration(),
                dataset=pd.DataFrame(),
                energy_balance=self._energy_balance(),
                tariff_data=self._tariff_data(),
                years=5,
            )

    def test_calculate_scenario_requires_positive_years(self):

        with pytest.raises(
            ValueError,
            match="Years must be greater than zero."
        ):
            self.engine.calculate_scenario(
                scenario=self._scenario(),
                configuration=self._configuration(),
                dataset=pd.DataFrame(),
                energy_balance=self._energy_balance(),
                tariff_data=self._tariff_data(),
                years=0,
            )
class TestCalculateScenarios:

    def setup_method(self):
        self.engine = EconomicsEngine()

        self.engine.net_investment = 10000.0

        self.engine.self_consumption_savings = 2000.0

        self.engine.export_income = 500.0

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

    def _scenario(self, name):

        class Scenario:
            pass

        scenario = Scenario()

        scenario.name = name
        scenario.annual_degradation = None
        scenario.discount_rate = None
        scenario.buy_price_factor = 1.0
        scenario.sell_price_factor = 1.0
        scenario.annual_maintenance = None

        return scenario

    def test_calculate_scenarios(self):

        scenarios = [
            self._scenario("Base"),
            self._scenario("Optimista"),
        ]

        result = self.engine.calculate_scenarios(
            scenarios=scenarios,
            configuration=self._configuration(),
            dataset=pd.DataFrame(),
            energy_balance=pd.DataFrame(),
            tariff_data=pd.DataFrame(),
            years=5,
        )

        assert len(result) == 2

        assert result is self.engine.scenario_results

        assert result[0].name == "Base"

        assert result[1].name == "Optimista"

        assert all(
            isinstance(
                scenario_result,
                EconomicScenarioResult
            )
            for scenario_result in result
        )

    def test_calculate_scenarios_resets_previous_results(self):

        self.engine.scenario_results = [
            "old_result"
        ]

        scenarios = [
            self._scenario("Base")
        ]

        result = self.engine.calculate_scenarios(
            scenarios=scenarios,
            configuration=self._configuration(),
            dataset=pd.DataFrame(),
            energy_balance=pd.DataFrame(),
            tariff_data=pd.DataFrame(),
            years=5,
        )

        assert len(result) == 1

        assert result[0].name == "Base"

        assert "old_result" not in result

    def test_default_economic_scenarios(self):

        scenarios = EconomicScenarioResult.default_economic_scenarios()

        assert len(scenarios) == 3

        conservative = scenarios[0]

        assert conservative.name == "Conservador"
        assert conservative.buy_price_factor == 0.90
        assert conservative.sell_price_factor == 0.90
        assert conservative.annual_maintenance == 200.0
        assert conservative.annual_degradation == 0.005

        base = scenarios[1]

        assert base.name == "Base"
        assert base.buy_price_factor == 1.0
        assert base.sell_price_factor == 1.0
        assert base.annual_maintenance is None
        assert base.annual_degradation is None
        assert base.discount_rate is None

        optimistic = scenarios[2]

        assert optimistic.name == "Optimista"
        assert optimistic.buy_price_factor == 1.10
        assert optimistic.sell_price_factor == 1.10
        assert optimistic.annual_maintenance == 100.0
        assert optimistic.annual_degradation == 0.0025
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

class TestApplyPriceFactors:

    def setup_method(self):
        self.engine = EconomicsEngine()

    def test_apply_price_factors(self):

        tariff_data = pd.DataFrame(
            {
                "buy_price_eur_kwh": [
                    0.20,
                    0.30,
                ],
                "sell_price_eur_kwh": [
                    0.05,
                    0.06,
                ],
                "other_column": [
                    10,
                    20,
                ],
            }
        )

        result = self.engine._apply_price_factors(
            tariff_data,
            buy_price_factor=1.10,
            sell_price_factor=0.50,
        )

        assert list(result.columns) == [
            "buy_price_eur_kwh",
            "sell_price_eur_kwh",
        ]

        assert result["buy_price_eur_kwh"].tolist() == pytest.approx(
            [0.22, 0.33]
        )

        assert result["sell_price_eur_kwh"].tolist() == pytest.approx(
            [0.025, 0.03]
        )

    def test_apply_price_factors_does_not_modify_original(self):

        tariff_data = pd.DataFrame(
            {
                "buy_price_eur_kwh": [0.20],
                "sell_price_eur_kwh": [0.05],
            }
        )

        original = tariff_data.copy()

        self.engine._apply_price_factors(
            tariff_data,
            buy_price_factor=2.0,
            sell_price_factor=3.0,
        )

        pd.testing.assert_frame_equal(
            tariff_data,
            original
        )

    def test_calculate_scenario_with_custom_annual_maintenance(self):

        class Scenario:
            name = "Custom maintenance"

            annual_degradation = None
            discount_rate = None

            buy_price_factor = 1.0
            sell_price_factor = 1.0

            annual_maintenance = 300.0

        class Configuration:
            first_year_degradation = 0.01
            annual_degradation = 0.0035

            annual_electricity_price_growth = 0.02
            annual_export_price_growth = 0.0

            annual_maintenance_cost = 150.0
            annual_maintenance_growth = 0.02

            discount_rate = 0.05

        configuration = Configuration()

        self.engine.net_investment = 10000.0

        self.engine.self_consumption_savings = 2000.0

        self.engine.export_income = 500.0

        result = self.engine.calculate_scenario(
            scenario=Scenario(),
            configuration=configuration,
            dataset=pd.DataFrame(),
            energy_balance=pd.DataFrame(),
            tariff_data=pd.DataFrame(),
            years=2,
        )

        assert result.name == "Custom maintenance"

        assert result.annual_savings == pytest.approx(
            2500.0
        )

        assert result.payback_years > 0

        assert result.npv is not None

        assert result.irr is not None

    def test_calculate_scenario_annual_savings_without_energy_balance(self):

        tariff_data = pd.DataFrame(
            {
                "buy_price_eur_kwh": [0.20],
                "sell_price_eur_kwh": [0.06],
            }
        )

        with pytest.raises(
            RuntimeError,
            match="Energy balance has not been calculated."
        ):
            self.engine.calculate_scenario_annual_savings(
                energy_balance=None,
                tariff_data=tariff_data,
            )