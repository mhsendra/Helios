import pandas as pd
import pytest
from unittest.mock import MagicMock, call

from helios.core.controllers.solar_controller import SolarController

from helios.solar.installation_constraints import (
    InstallationConstraints,
)

from helios.solar.solar_installation_sizing import (
    SolarSizingResult,
)

class TestSolarController:

    def setup_method(self):

        self.analyzer = MagicMock()

        self.controller = SolarController(
            self.analyzer
        )

        self.constraints = InstallationConstraints(
            available_area_m2=100.0,
            panel_width_m=1.10,
            panel_height_m=1.70,
            panel_power_wp=500.0,
        )

    # ==================================================
    # Propiedades
    # ==================================================

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

    def test_annual_production_without_yearly_production(self):

        self.analyzer.solar_engine.yearly_production = None

        assert self.controller.annual_production is None

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

    def test_energy_balance_totals_without_balance(self):

        self.analyzer.solar_engine.energy_balance = None

        assert self.controller.self_consumption is None
        assert self.controller.grid_import is None
        assert self.controller.grid_export is None

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

    def test_specific_production_without_annual_production(self):

        self.analyzer.solar_engine.yearly_production = None

        assert self.controller.specific_production is None

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

    def test_monthly_energy_balance_without_balance(self):

        self.analyzer.solar_engine.energy_balance = None

        assert self.controller.monthly_energy_balance is None

    def test_hourly_production_property(self):

        value = MagicMock()

        self.analyzer.solar_engine.hourly_production = value

        assert self.controller.hourly_production is value


    def test_daily_production_property(self):

        value = MagicMock()

        self.analyzer.solar_engine.daily_production = value

        assert self.controller.daily_production is value


    def test_monthly_production_property(self):

        value = MagicMock()

        self.analyzer.solar_engine.monthly_production = value

        assert self.controller.monthly_production is value


    def test_yearly_production_property(self):

        value = MagicMock()

        self.analyzer.solar_engine.yearly_production = value

        assert self.controller.yearly_production is value

    def test_recommend_installation_requires_dataset(self):

        self.analyzer.valid_dataset.return_value = pd.DataFrame()

        self.analyzer.solar_engine.yearly_production = pd.Series(
            [10000.0],
            index=pd.to_datetime(["2025-12-31"])
        )

        self.analyzer.solar_engine.configuration = MagicMock()

        self.analyzer.solar_engine.configuration.installed_power_kwp = 5.0

        with pytest.raises(
            ValueError,
            match="valid consumption dataset",
        ):
            self.controller.recommend_installation(
                constraints=self.constraints
            )
            
    def test_statistics_property(self):

        value = MagicMock()

        self.analyzer.solar_engine.statistics = value

        assert self.controller.statistics is value


    def test_energy_balance_property(self):

        value = MagicMock()

        self.analyzer.solar_engine.energy_balance = value

        assert self.controller.energy_balance is value

    def test_coverage_without_empty_balance(self):

        self.analyzer.solar_engine.energy_balance = pd.DataFrame()

        assert self.controller.coverage is None


    def test_annual_production_without_empty_yearly_production(self):

        self.analyzer.solar_engine.yearly_production = pd.Series(
            dtype=float
        )

        assert self.controller.annual_production is None

    # ==================================================
    # Cálculos
    # ==================================================

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

    # ==================================================
    # Reports
    # ==================================================

    def test_reports_calls_steps_in_order(self):

        engine = self.analyzer.solar_engine

        self.controller.reports()

        assert engine.mock_calls == [
            call.production_statistics_report(),
            call.monthly_production_report(),
            call.energy_balance_report(),
        ]

    def test_reset(self):

        engine = self.analyzer.solar_engine

        self.controller.reset()

        engine.reset.assert_called_once_with()

        # ==================================================
    # Dimensionamiento de instalación solar
    # ==================================================

    def _sizing_constraints(self):

        return InstallationConstraints(
            available_area_m2=50.0,
            panel_width_m=1.134,
            panel_height_m=1.722,
            panel_power_wp=540.0,
            min_panels=5,
            max_panels=15,
        )

    def _configure_solar_reference(self):

        self.analyzer.valid_dataset.return_value = pd.DataFrame(
            {
                "AE_kWh": [5_000.0],
            }
        )

        self.analyzer.solar_engine.configuration = MagicMock()

        self.analyzer.solar_engine.configuration.installed_power_kwp = (
            5.4
        )

        self.analyzer.solar_engine.yearly_production = pd.Series(
            [6_000.0],
            index=pd.to_datetime(
                ["2025-12-31"]
            )
        )

    def test_recommend_installation_returns_result(self):

        self._configure_solar_reference()

        result = self.controller.recommend_installation(
            self._sizing_constraints()
        )

        assert isinstance(
            result,
            SolarSizingResult,
        )

        assert result.panel_count >= 5
        assert result.panel_count <= 15
        assert result.installed_power_kwp > 0
        assert result.annual_production_kwh > 0

    def test_recommend_installation_selects_smallest_covering_configuration(
        self,
    ):

        self._configure_solar_reference()

        result = self.controller.recommend_installation(
            self._sizing_constraints()
        )

        # Producción específica:
        # 6000 / 5.4 = 1111.11 kWh/kWp
        #
        # 5 paneles  = 3000 kWh
        # 6 paneles  = 3600 kWh
        # ...
        # 9 paneles  = 5400 kWh
        #
        # Por tanto, 9 es la primera configuración
        # capaz de cubrir los 5000 kWh.

        assert result.panel_count == 9

        assert result.installed_power_kwp == pytest.approx(
            4.86
        )

        assert result.annual_production_kwh == pytest.approx(
            5_400.0
        )

    def test_recommend_installation_stores_result(self):

        self._configure_solar_reference()

        result = self.controller.recommend_installation(
            self._sizing_constraints()
        )

        assert self.controller.sizing_result is result
            
    def test_recommend_installation_requires_solar_configuration(
        self,
    ):

        self.analyzer.valid_dataset.return_value = pd.DataFrame(
            {
                "AE_kWh": [5_000.0],
            }
        )

        self.analyzer.solar_engine.configuration = None

        with pytest.raises(
            ValueError,
            match="solar configuration",
        ):

            self.controller.recommend_installation(
                self._sizing_constraints()
            )

    def test_recommend_installation_requires_calculated_production(
        self,
    ):

        self.analyzer.valid_dataset.return_value = pd.DataFrame(
            {
                "AE_kWh": [5_000.0],
            }
        )

        self.analyzer.solar_engine.configuration = MagicMock()

        self.analyzer.solar_engine.yearly_production = None

        with pytest.raises(
            ValueError,
            match="Solar production must be calculated",
        ):

            self.controller.recommend_installation(
                self._sizing_constraints()
            )

    def test_recommend_installation_requires_valid_constraints(
        self,
    ):

        self._configure_solar_reference()

        with pytest.raises(
            TypeError,
            match="InstallationConstraints",
        ):

            self.controller.recommend_installation(
                MagicMock()
            )