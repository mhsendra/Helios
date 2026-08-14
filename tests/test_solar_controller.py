import pandas as pd
import pytest
from unittest.mock import MagicMock, call

from helios.core.controllers.solar_controller import SolarController


class TestSolarController:

    def setup_method(self):

        self.analyzer = MagicMock()

        self.controller = SolarController(
            self.analyzer
        )

    def test_coverage(self):

        self.analyzer.solar_engine.energy_balance = pd.DataFrame(
            {
                "consumption_kwh": [2.0, 4.0],
                "self_consumption_kwh": [1.0, 3.0],
            }
        )

        assert self.controller.coverage == pytest.approx(
            66.6666667
        )

    def test_coverage_without_balance(self):

        self.analyzer.solar_engine.energy_balance = None

        assert self.controller.coverage is None

    def test_coverage_without_consumption(self):

        self.analyzer.solar_engine.energy_balance = pd.DataFrame(
            {
                "consumption_kwh": [0.0, 0.0],
                "self_consumption_kwh": [0.0, 0.0],
            }
        )

        assert self.controller.coverage is None

    def test_annual_production(self):

        self.analyzer.solar_engine.yearly_production = pd.Series(
            [1000.0, 1200.0, 1500.0],
            index=pd.to_datetime(
                [
                    "2023-12-31",
                    "2024-12-31",
                    "2025-12-31",
                ]
            )
        )

        assert self.controller.annual_production == pytest.approx(
            1500.0
        )

    def test_self_consumption_grid_import_and_export(self):

        self.analyzer.solar_engine.energy_balance = pd.DataFrame(
            {
                "self_consumption_kwh": [1.0, 2.0],
                "grid_import_kwh": [3.0, 4.0],
                "grid_export_kwh": [5.0, 6.0],
            }
        )

        assert self.controller.self_consumption == pytest.approx(
            3.0
        )

        assert self.controller.grid_import == pytest.approx(
            7.0
        )

        assert self.controller.grid_export == pytest.approx(
            11.0
        )

    def test_specific_production(self):

        self.analyzer.solar_engine.yearly_production = pd.Series(
            [8100.0],
            index=pd.to_datetime(
                ["2025-12-31"]
            )
        )

        self.analyzer.solar_engine.configuration = MagicMock()

        self.analyzer.solar_engine.configuration.installed_power_kwp = (
            8.1
        )

        assert self.controller.specific_production == pytest.approx(
            1000.0
        )

    def test_monthly_energy_balance(self):

        index = pd.to_datetime(
            [
                "2025-01-01 10:00",
                "2025-01-01 11:00",
                "2025-02-01 10:00",
            ]
        )

        self.analyzer.solar_engine.energy_balance = pd.DataFrame(
            {
                "consumption_kwh": [2.0, 3.0, 4.0],
                "self_consumption_kwh": [1.0, 2.0, 3.0],
                "grid_import_kwh": [1.0, 1.0, 1.0],
                "grid_export_kwh": [0.0, 1.0, 1.0],
            },
            index=index
        )

        result = self.controller.monthly_energy_balance

        assert result.loc[
            pd.Timestamp("2025-01-31"),
            "consumption_kwh"
        ] == pytest.approx(5.0)

        assert result.loc[
            pd.Timestamp("2025-02-28"),
            "consumption_kwh"
        ] == pytest.approx(4.0)

    def test_calculate_calls_steps_in_order(self):

        configuration = MagicMock()

        engine = self.analyzer.solar_engine

        self.controller.calculate(
            configuration
        )

        assert engine.mock_calls == [
            call.calculate_hourly_production(
                configuration
            ),
            call.calculate_daily_production(),
            call.calculate_monthly_production(),
            call.calculate_yearly_production(),
            call.calculate_energy_balance(
                self.analyzer.valid_dataset.return_value[
                    "AE_kWh"
                ]
            ),
            call.calculate_statistics(),
        ]

    def test_reports_calls_steps_in_order(self):

        engine = self.analyzer.solar_engine

        self.controller.reports()

        assert engine.mock_calls == [
            call.production_statistics_report(),
            call.monthly_production_report(),
            call.energy_balance_report(),
        ]