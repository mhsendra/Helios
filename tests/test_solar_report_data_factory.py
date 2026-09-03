from unittest.mock import MagicMock

import pytest

import pandas as pd

from helios.reports.solar_report_data import SolarReportData
from helios.reports.solar_report_data_factory import (
    SolarReportDataFactory,
)


class TestSolarReportDataFactory:

    def _solar_controller(self):

        solar = MagicMock()

        sizing = MagicMock()

        sizing.installed_power_kwp = 8.1
        sizing.panel_count = 15
        sizing.annual_production_kwh = 12500.0
        sizing.annual_consumption_kwh = 19541.72
        sizing.self_sufficiency_percent = 64.0

        sizing.evaluation.candidate.panel_power_wp = (
            540.0
        )

        solar.sizing_result = sizing

        solar.specific_production = 1543.21
        solar.self_consumption = 8500.0
        solar.grid_export = 4000.0
        solar.grid_import = 11041.72
        solar.coverage = 43.5

        solar.monthly_production = pd.Series(
            [
                850.0,
                1020.0,
                1250.0,
                1480.0,
                1650.0,
                1720.0,
                1800.0,
                1760.0,
                1510.0,
                1180.0,
                920.0,
                780.0,
            ],
            index=pd.date_range(
                "2025-01-31",
                periods=12,
                freq="ME",
            ),
        )

        return solar


    def _economics_controller(self):

        economics = MagicMock()

        engine = MagicMock()

        engine.net_investment = 12490.0
        engine.annual_savings = 2338.0
        engine.payback_years = 5.34
        engine.npv = 22071.16
        engine.irr = 0.188

        economics.analyzer.economics_engine = engine

        return economics


    # ==================================================
    # Creation
    # ==================================================

    def test_create_returns_solar_report_data(self):

        result = SolarReportDataFactory.create(
            self._solar_controller(),
            self._economics_controller(),
        )

        assert isinstance(
            result,
            SolarReportData,
        )


    # ==================================================
    # Installation
    # ==================================================

    def test_create_uses_sizing_result(self):

        result = SolarReportDataFactory.create(
            self._solar_controller(),
            self._economics_controller(),
        )

        assert result.installed_power_kwp == 8.1
        assert result.panel_count == 15
        assert result.panel_power_wp == 540.0


    # ==================================================
    # Production
    # ==================================================

    def test_create_uses_solar_production_results(self):

        solar = self._solar_controller()

        result = SolarReportDataFactory.create(
            solar,
            self._economics_controller(),
        )

        assert result.yearly_production_kwh == 12500.0

        assert (
            result.monthly_production
            is solar.monthly_production
        )

        assert (
            result.specific_production_kwh_kwp
            == 1543.21
        )

    # ==================================================
    # Energy balance
    # ==================================================

    def test_create_uses_energy_balance_results(self):

        result = SolarReportDataFactory.create(
            self._solar_controller(),
            self._economics_controller(),
        )

        assert (
            result.yearly_consumption_kwh
            == 19541.72
        )

        assert (
            result.self_consumption_kwh
            == 8500.0
        )

        assert result.grid_export_kwh == 4000.0
        assert result.grid_import_kwh == 11041.72

        assert (
            result.self_consumption_rate_percent
            == 43.5
        )

        assert (
            result.self_sufficiency_rate_percent
            == 64.0
        )


    # ==================================================
    # Economics
    # ==================================================

    def test_create_uses_economic_engine_results(self):

        result = SolarReportDataFactory.create(
            self._solar_controller(),
            self._economics_controller(),
        )

        assert result.investment_eur == 12490.0
        assert result.yearly_savings_eur == 2338.0
        assert result.payback_years == 5.34
        assert result.net_present_value_eur == 22071.16

        assert (
            result.internal_rate_of_return_percent
            == 18.8
        )


    # ==================================================
    # No calculations
    # ==================================================

    def test_create_does_not_calculate_solar_data(
        self,
    ):

        solar = self._solar_controller()
        economics = self._economics_controller()

        SolarReportDataFactory.create(
            solar,
            economics,
        )

        solar.calculate.assert_not_called()


    def test_create_does_not_calculate_economics(
        self,
    ):

        solar = self._solar_controller()
        economics = self._economics_controller()

        SolarReportDataFactory.create(
            solar,
            economics,
        )

        (
            economics
            .analyzer
            .economics_engine
            .calculate
            .assert_not_called()
        )


    # ==================================================
    # Validation
    # ==================================================

    def test_create_requires_solar_controller(self):

        with pytest.raises(
            ValueError,
            match="solar controller is required",
        ):

            SolarReportDataFactory.create(
                None,
                self._economics_controller(),
            )


    def test_create_requires_economics_controller(self):

        with pytest.raises(
            ValueError,
            match="economics controller is required",
        ):

            SolarReportDataFactory.create(
                self._solar_controller(),
                None,
            )


    def test_create_requires_sizing_result(self):

        solar = self._solar_controller()

        solar.sizing_result = None

        with pytest.raises(
            ValueError,
            match="solar installation sizing is required",
        ):

            SolarReportDataFactory.create(
                solar,
                self._economics_controller(),
            )