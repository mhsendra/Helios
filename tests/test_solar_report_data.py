import pytest

import pandas as pd

from dataclasses import FrozenInstanceError

from helios.reports.solar_report_data import (
    SolarReportData,
)


class TestSolarReportData:

    def _data(
        self,
        **overrides,
    ):

        values = {
            # ==================================================
            # Installation
            # ==================================================

            "installed_power_kwp": 8.1,
            "panel_count": 15,
            "panel_power_wp": 540.0,

            # ==================================================
            # Solar production
            # ==================================================

            "yearly_production_kwh": 12500.0,

            "monthly_production": pd.Series(
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
            ),

            "specific_production_kwh_kwp": 1543.21,

            # ==================================================
            # Energy balance
            # ==================================================

            "yearly_consumption_kwh": 19541.72,
            "self_consumption_kwh": 8500.0,
            "grid_export_kwh": 4000.0,
            "grid_import_kwh": 11041.72,
            "self_consumption_rate_percent": 68.0,
            "self_sufficiency_rate_percent": 43.5,

            # ==================================================
            # Economics
            # ==================================================

            "investment_eur": 12490.0,
            "yearly_savings_eur": 2338.0,
            "payback_years": 5.34,
            "net_present_value_eur": 22071.16,
            "internal_rate_of_return_percent": 18.80,
        }

        values.update(
            overrides
        )

        return SolarReportData(
            **values
        )


    # ==================================================
    # Construction
    # ==================================================

    def test_creates_report_data_with_expected_values(
        self,
    ):

        data = self._data()

        assert data.installed_power_kwp == 8.1
        assert data.panel_count == 15
        assert data.panel_power_wp == 540.0

        assert data.yearly_production_kwh == 12500.0
        assert (
            data.specific_production_kwh_kwp
            == 1543.21
        )

        assert (
            data.yearly_consumption_kwh
            == 19541.72
        )

        assert (
            data.self_consumption_kwh
            == 8500.0
        )

        assert data.grid_export_kwh == 4000.0
        assert data.grid_import_kwh == 11041.72

        assert (
            data.self_consumption_rate_percent
            == 68.0
        )

        assert (
            data.self_sufficiency_rate_percent
            == 43.5
        )

        assert data.investment_eur == 12490.0
        assert data.yearly_savings_eur == 2338.0
        assert data.payback_years == 5.34

        assert (
            data.net_present_value_eur
            == 22071.16
        )

        assert (
            data.internal_rate_of_return_percent
            == 18.80
        )

        assert len(data.monthly_production) == 12

        assert (
            data.monthly_production.iloc[0]
            == 850.0
        )

        assert (
            data.monthly_production.iloc[-1]
            == 780.0
        )


    # ==================================================
    # Immutability
    # ==================================================

    def test_is_immutable(
        self,
    ):

        data = self._data()

        with pytest.raises(
            FrozenInstanceError,
        ):

            data.installed_power_kwp = 10.0


    # ==================================================
    # Independent instances
    # ==================================================

    def test_instances_keep_their_own_values(
        self,
    ):

        first = self._data(
            installed_power_kwp=8.1,
            panel_count=15,
        )

        second = self._data(
            installed_power_kwp=10.8,
            panel_count=20,
        )

        assert first.installed_power_kwp == 8.1
        assert first.panel_count == 15

        assert second.installed_power_kwp == 10.8
        assert second.panel_count == 20