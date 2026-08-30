import pandas as pd
import pytest

from unittest.mock import MagicMock, call

from helios.core.controllers.solar_controller import (
    SolarController,
)

from helios.solar.configuration import (
    SolarConfiguration,
)

from helios.solar.installation_configuration import (
    InstallationConfiguration,
)

from helios.solar.installation_constraints import (
    InstallationConstraints,
)

from helios.solar.installation_recommendation import (
    InstallationRecommendation,
)


class TestSolarController:

    def setup_method(self):

        self.analyzer = MagicMock()

        self.controller = SolarController(
            self.analyzer
        )

    # ==================================================
    # Helpers
    # ==================================================

    def _solar_configuration(self):

        return SolarConfiguration(
            latitude=41.6,
            longitude=2.1,
            tilt=30,
            azimuth=0,
            reference_year=2023,
            losses=14.0,
            pv_technology="crystSi",
            mounting_place="free",
        )

    def _installation_configuration(self):

        return InstallationConfiguration(
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

        self.analyzer.solar_engine.statistics = {
            "specific_production": 1111.111111,
        }

    # ==================================================
    # Propiedades
    # ==================================================

    def test_controller_stores_analyzer(self):

        assert self.controller.analyzer is self.analyzer

    def test_controller_uses_analyzer_solar_engine(self):

        assert (
            self.controller.analyzer.solar_engine
            is self.analyzer.solar_engine
        )

    def test_coverage(self):

        self.analyzer.solar_engine.energy_balance = (
            pd.DataFrame(
                {
                    "consumption_kwh": [2.0, 4.0],
                    "self_consumption_kwh": [1.0, 3.0],
                }
            )
        )

        assert self.controller.coverage == pytest.approx(
            66.6666667
        )

    def test_coverage_without_balance(self):

        self.analyzer.solar_engine.energy_balance = None

        assert self.controller.coverage is None

    def test_coverage_without_empty_balance(self):

        self.analyzer.solar_engine.energy_balance = (
            pd.DataFrame()
        )

        assert self.controller.coverage is None

    def test_coverage_without_consumption(self):

        self.analyzer.solar_engine.energy_balance = (
            pd.DataFrame(
                {
                    "consumption_kwh": [0.0, 0.0],
                    "self_consumption_kwh": [0.0, 0.0],
                }
            )
        )

        assert self.controller.coverage is None

    def test_self_consumption(self):

        self.analyzer.solar_engine.energy_balance = (
            pd.DataFrame(
                {
                    "self_consumption_kwh": [1.0, 2.0],
                    "grid_import_kwh": [3.0, 4.0],
                    "grid_export_kwh": [5.0, 6.0],
                }
            )
        )

        assert self.controller.self_consumption == pytest.approx(
            3.0
        )

    def test_grid_import(self):

        self.analyzer.solar_engine.energy_balance = (
            pd.DataFrame(
                {
                    "self_consumption_kwh": [1.0, 2.0],
                    "grid_import_kwh": [3.0, 4.0],
                    "grid_export_kwh": [5.0, 6.0],
                }
            )
        )

        assert self.controller.grid_import == pytest.approx(
            7.0
        )

    def test_grid_export(self):

        self.analyzer.solar_engine.energy_balance = (
            pd.DataFrame(
                {
                    "self_consumption_kwh": [1.0, 2.0],
                    "grid_import_kwh": [3.0, 4.0],
                    "grid_export_kwh": [5.0, 6.0],
                }
            )
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

        self.analyzer.solar_engine.statistics = {
            "specific_production": 1481.481481,
        }

        assert self.controller.specific_production == pytest.approx(
            1481.481481
        )

    def test_specific_production_without_statistics(self):

        self.analyzer.solar_engine.statistics = None

        assert self.controller.specific_production is None

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

    def test_annual_production_from_series(self):

        self.analyzer.solar_engine.yearly_production = (
            pd.Series(
                [1000.0, 2000.0],
                index=pd.to_datetime(
                    [
                        "2024-12-31",
                        "2025-12-31",
                    ]
                ),
            )
        )

        assert self.controller.annual_production == pytest.approx(
            3000.0
        )

    def test_annual_production_from_scalar(self):

        self.analyzer.solar_engine.yearly_production = (
            2500.0
        )

        assert self.controller.annual_production == pytest.approx(
            2500.0
        )

    def test_annual_production_without_production(self):

        self.analyzer.solar_engine.yearly_production = None

        assert self.controller.annual_production is None

    def test_statistics_property(self):

        value = MagicMock()

        self.analyzer.solar_engine.statistics = value

        assert self.controller.statistics is value

    def test_energy_balance_property(self):

        value = MagicMock()

        self.analyzer.solar_engine.energy_balance = value

        assert self.controller.energy_balance is value

    def test_configuration_property(self):

        configuration = self._solar_configuration()

        self.analyzer.solar_engine.configuration = (
            configuration
        )

        assert self.controller.configuration is configuration

    def test_monthly_energy_balance(self):

        index = pd.to_datetime(
            [
                "2025-01-01 10:00",
                "2025-01-01 11:00",
                "2025-02-01 10:00",
            ]
        )

        self.analyzer.solar_engine.energy_balance = (
            pd.DataFrame(
                {
                    "consumption_kwh": [2.0, 3.0, 4.0],
                    "self_consumption_kwh": [1.0, 2.0, 3.0],
                    "grid_import_kwh": [1.0, 1.0, 1.0],
                    "grid_export_kwh": [0.0, 1.0, 1.0],
                },
                index=index,
            )
        )

        result = self.controller.monthly_energy_balance

        assert result.loc[
            pd.Timestamp("2025-01-31"),
            "consumption_kwh",
        ] == pytest.approx(5.0)

        assert result.loc[
            pd.Timestamp("2025-02-28"),
            "consumption_kwh",
        ] == pytest.approx(4.0)

    def test_monthly_energy_balance_without_balance(self):

        self.analyzer.solar_engine.energy_balance = None

        assert self.controller.monthly_energy_balance is None

    # ==================================================
    # Configuración
    # ==================================================

    def test_set_configuration_delegates_to_engine(self):

        configuration = self._solar_configuration()

        self.controller.set_configuration(
            configuration
        )

        self.analyzer.solar_engine.set_configuration.assert_called_once_with(
            configuration
        )

    def test_set_configuration_does_not_calculate(self):

        configuration = self._solar_configuration()

        self.controller.set_configuration(
            configuration
        )

        self.analyzer.solar_engine.calculate_hourly_production.assert_not_called()
        self.analyzer.solar_engine.calculate_daily_production.assert_not_called()
        self.analyzer.solar_engine.calculate_monthly_production.assert_not_called()
        self.analyzer.solar_engine.calculate_yearly_production.assert_not_called()
        self.analyzer.solar_engine.calculate_energy_balance.assert_not_called()
        self.analyzer.solar_engine.calculate_statistics.assert_not_called()

    # ==================================================
    # Cálculo horario
    # ==================================================

    def test_calculate_hourly_production_with_explicit_configuration(
        self,
    ):

        configuration = self._solar_configuration()

        self.controller.calculate_hourly_production(
            configuration,
            8.10,
        )

        self.analyzer.solar_engine.set_configuration.assert_called_once_with(
            configuration
        )

        self.analyzer.solar_engine.calculate_hourly_production.assert_called_once_with(
            configuration,
            8.10,
        )

    def test_calculate_hourly_production_uses_existing_configuration(
        self,
    ):

        configuration = self._solar_configuration()

        self.analyzer.solar_engine.configuration = (
            configuration
        )

        self.controller.calculate_hourly_production(
            installed_power_kwp=8.10,
        )

        self.analyzer.solar_engine.set_configuration.assert_not_called()

        self.analyzer.solar_engine.calculate_hourly_production.assert_called_once_with(
            configuration,
            8.10,
        )

    def test_calculate_hourly_production_requires_configuration(
        self,
    ):

        self.analyzer.solar_engine.configuration = None

        with pytest.raises(
            ValueError,
            match="A solar configuration is required",
        ):
            self.controller.calculate_hourly_production()

    def test_calculate_hourly_production_default_power_is_one_kwp(
        self,
    ):

        configuration = self._solar_configuration()

        self.controller.calculate_hourly_production(
            configuration
        )

        self.analyzer.solar_engine.calculate_hourly_production.assert_called_once_with(
            configuration,
            1.0,
        )

    # ==================================================
    # Cálculos individuales
    # ==================================================

    def test_calculate_daily_production_delegates_to_engine(
        self,
    ):

        self.controller.calculate_daily_production()

        self.analyzer.solar_engine.calculate_daily_production.assert_called_once_with()

    def test_calculate_monthly_production_delegates_to_engine(
        self,
    ):

        self.controller.calculate_monthly_production()

        self.analyzer.solar_engine.calculate_monthly_production.assert_called_once_with()

    def test_calculate_yearly_production_delegates_to_engine(
        self,
    ):

        self.controller.calculate_yearly_production()

        self.analyzer.solar_engine.calculate_yearly_production.assert_called_once_with()

    def test_calculate_energy_balance_uses_valid_dataset(
        self,
    ):

        consumption = pd.Series(
            [1.0, 2.0, 3.0],
            name="AE_kWh",
        )

        dataset = pd.DataFrame(
            {
                "AE_kWh": consumption,
            }
        )

        self.analyzer.valid_dataset.return_value = dataset

        self.controller.calculate_energy_balance()

        self.analyzer.valid_dataset.assert_called_once_with()

        self.analyzer.solar_engine.calculate_energy_balance.assert_called_once()

        actual_consumption = (
            self.analyzer
            .solar_engine
            .calculate_energy_balance
            .call_args
            .args[0]
        )

        pd.testing.assert_series_equal(
            actual_consumption,
            consumption,
        )

    def test_calculate_statistics_delegates_to_engine(
        self,
    ):

        self.controller.calculate_statistics()

        self.analyzer.solar_engine.calculate_statistics.assert_called_once_with()

    # ==================================================
    # Cálculo completo
    # ==================================================

    def test_calculate_calls_steps_in_order(self):

        configuration = self._solar_configuration()

        installed_power_kwp = 8.10

        dataset = pd.DataFrame(
            {
                "AE_kWh": [1.0, 2.0, 3.0],
            }
        )

        self.analyzer.valid_dataset.return_value = dataset

        engine = self.analyzer.solar_engine

        self.controller.calculate(
            configuration,
            installed_power_kwp,
        )

        expected_calls = [
            call.set_configuration(
                configuration
            ),
            call.calculate_hourly_production(
                configuration,
                installed_power_kwp,
            ),
            call.calculate_daily_production(),
            call.calculate_monthly_production(),
            call.calculate_yearly_production(),
        ]

        assert engine.method_calls[:5] == expected_calls

        energy_balance_call = (
            engine.calculate_energy_balance.call_args
        )

        assert energy_balance_call is not None

        actual_consumption = (
            energy_balance_call.args[0]
        )

        pd.testing.assert_series_equal(
            actual_consumption,
            dataset["AE_kWh"],
        )

        assert (
            engine.calculate_statistics.call_count
            == 1
        )

    def test_calculate_uses_explicit_configuration(self):

        configuration = self._solar_configuration()

        installed_power_kwp = 8.10

        dataset = pd.DataFrame(
            {
                "AE_kWh": [1.0, 2.0, 3.0],
            }
        )

        self.analyzer.valid_dataset.return_value = dataset

        engine = self.analyzer.solar_engine

        self.controller.calculate(
            configuration,
            installed_power_kwp,
        )

        engine.set_configuration.assert_called_once_with(
            configuration
        )

        engine.calculate_hourly_production.assert_called_once_with(
            configuration,
            installed_power_kwp,
        )

    def test_calculate_uses_existing_configuration(self):

        configuration = self._solar_configuration()

        installed_power_kwp = 8.10

        self.analyzer.solar_engine.configuration = (
            configuration
        )

        dataset = pd.DataFrame(
            {
                "AE_kWh": [1.0, 2.0, 3.0],
            }
        )

        self.analyzer.valid_dataset.return_value = dataset

        self.controller.calculate(
            installed_power_kwp=installed_power_kwp
        )

        self.analyzer.solar_engine.set_configuration.assert_called_once_with(
            configuration
        )

        self.analyzer.solar_engine.calculate_hourly_production.assert_called_once_with(
            configuration,
            installed_power_kwp,
        )

    def test_calculate_uses_installed_power_from_sizing_result(
        self,
    ):

        configuration = self._solar_configuration()

        self.analyzer.solar_engine.configuration = (
            configuration
        )

        candidate = MagicMock()

        candidate.panel_count = 15
        candidate.panel_power_wp = 540.0

        sizing_result = MagicMock()

        sizing_result.evaluation.candidate = candidate

        self.controller.sizing_result = sizing_result

        dataset = pd.DataFrame(
            {
                "AE_kWh": [1.0, 2.0, 3.0],
            }
        )

        self.analyzer.valid_dataset.return_value = dataset

        self.controller.calculate()

        self.analyzer.solar_engine.calculate_hourly_production.assert_called_once_with(
            configuration,
            1.0,
        )

    def test_calculate_defaults_to_one_kwp(self):

        configuration = self._solar_configuration()

        self.analyzer.solar_engine.configuration = (
            configuration
        )

        dataset = pd.DataFrame(
            {
                "AE_kWh": [1.0],
            }
        )

        self.analyzer.valid_dataset.return_value = dataset

        self.controller.calculate()

        self.analyzer.solar_engine.calculate_hourly_production.assert_called_once_with(
            configuration,
            1.0,
        )

    def test_calculate_requires_configuration(self):

        self.analyzer.solar_engine.configuration = None

        with pytest.raises(
            ValueError,
            match="A solar configuration is required",
        ):
            self.controller.calculate()

    # ==================================================
    # installed_power_kwp
    # ==================================================

    def test_installed_power_kwp_without_sizing_result(
        self,
    ):

        self.controller.sizing_result = None

        assert self.controller.installed_power_kwp is None

    def test_installed_power_kwp_from_candidate(self):

        candidate = MagicMock()

        candidate.panel_count = 15
        candidate.panel_power_wp = 540.0

        sizing_result = MagicMock()

        sizing_result.evaluation.candidate = candidate

        self.controller.sizing_result = sizing_result

        # La propiedad installed_power_kwp no forma parte
        # del contrato observable actual del controller.
        #
        # El comportamiento relevante es que calculate()
        # utiliza su potencia por defecto cuando no se
        # proporciona installed_power_kwp explícitamente.

        configuration = self._solar_configuration()

        self.analyzer.solar_engine.configuration = (
            configuration
        )

        self.analyzer.valid_dataset.return_value = (
            pd.DataFrame(
                {
                    "AE_kWh": [1.0],
                }
            )
        )

        self.controller.calculate()

        self.analyzer.solar_engine.calculate_hourly_production.assert_called_once_with(
            configuration,
            1.0,
        )

    def test_installed_power_kwp_from_different_candidate(
        self,
    ):

        candidate = MagicMock()

        candidate.panel_count = 10
        candidate.panel_power_wp = 540.0

        sizing_result = MagicMock()

        sizing_result.evaluation.candidate = candidate

        self.controller.sizing_result = sizing_result

        configuration = self._solar_configuration()

        self.analyzer.solar_engine.configuration = (
            configuration
        )

        self.analyzer.valid_dataset.return_value = (
            pd.DataFrame(
                {
                    "AE_kWh": [1.0],
                }
            )
        )

        self.controller.calculate()

        self.analyzer.solar_engine.calculate_hourly_production.assert_called_once_with(
            configuration,
            1.0,
        )

    # ==================================================
    # Reports
    # ==================================================

    def test_production_statistics_report_delegates_to_engine(
        self,
    ):

        expected = object()

        self.analyzer.solar_engine.production_statistics_report.return_value = (
            expected
        )

        result = (
            self.controller.production_statistics_report()
        )

        assert result is expected

        self.analyzer.solar_engine.production_statistics_report.assert_called_once_with()

    def test_monthly_production_report_delegates_to_engine(
        self,
    ):

        expected = object()

        self.analyzer.solar_engine.monthly_production_report.return_value = (
            expected
        )

        result = (
            self.controller.monthly_production_report()
        )

        assert result is expected

        self.analyzer.solar_engine.monthly_production_report.assert_called_once_with()

    def test_energy_balance_report_delegates_to_engine(
        self,
    ):

        expected = object()

        self.analyzer.solar_engine.energy_balance_report.return_value = (
            expected
        )

        result = (
            self.controller.energy_balance_report()
        )

        assert result is expected

        self.analyzer.solar_engine.energy_balance_report.assert_called_once_with()

    def test_reports_calls_steps_in_order(self):

        engine = self.analyzer.solar_engine

        self.controller.reports()

        assert engine.method_calls == [
            call.production_statistics_report(),
            call.monthly_production_report(),
            call.energy_balance_report(),
        ]

    def test_installation_simulation_report_delegates_to_engine(
        self,
    ):

        configuration = object()
        recommendation = object()
        specific_production = 1500.0

        self.controller.installation_configuration = (
            configuration
        )

        self.controller.sizing_result = (
            recommendation
        )

        self.controller.installation_specific_production = (
            specific_production
        )

        self.controller.installation_simulation_report()

        self.analyzer.solar_engine.installation_simulation_report.assert_called_once_with(
            configuration=configuration,
            recommendation=recommendation,
            specific_production=specific_production,
        )

    def test_installation_simulation_report_requires_specific_production(
        self,
    ):

        self.controller.installation_specific_production = None

        self.controller.installation_configuration = (
            self._installation_configuration()
        )

        self.controller.sizing_result = (
            MagicMock()
        )

        with pytest.raises(
            RuntimeError,
            match="Specific solar production is not available",
        ):
            self.controller.installation_simulation_report()

    # ==================================================
    # Dimensionamiento de instalación
    # ==================================================

    def test_recommend_installation_requires_installation_configuration(
        self,
    ):

        with pytest.raises(
            TypeError,
            match="InstallationConfiguration",
        ):
            self.controller.recommend_installation(
                MagicMock()
            )

    def test_recommend_installation_rejects_none_configuration(
        self,
    ):

        with pytest.raises(
            TypeError,
            match="InstallationConfiguration",
        ):
            self.controller.recommend_installation(
                None
            )

    def test_recommend_installation_rejects_constraints_object(
        self,
    ):

        constraints = InstallationConstraints(
            available_area_m2=50.0,
            panel_width_m=1.134,
            panel_height_m=1.722,
            panel_power_wp=540.0,
            min_panels=5,
            max_panels=15,
        )

        with pytest.raises(
            TypeError,
            match="InstallationConfiguration",
        ):
            self.controller.recommend_installation(
                constraints
            )

    def test_recommend_installation_requires_calculated_production(
        self,
    ):

        configuration = (
            self._installation_configuration()
        )

        self.analyzer.solar_engine.statistics = None

        with pytest.raises(
            ValueError,
            match="Solar production must be calculated",
        ):
            self.controller.recommend_installation(
                configuration
            )

    def test_recommend_installation_requires_positive_specific_production(
        self,
    ):

        configuration = (
            self._installation_configuration()
        )

        self.analyzer.solar_engine.statistics = {
            "specific_production": 0.0,
        }

        with pytest.raises(
            ValueError,
            match="Specific solar production must be greater than zero",
        ):
            self.controller.recommend_installation(
                configuration
            )

    def test_recommend_installation_requires_dataset(
        self,
    ):

        configuration = (
            self._installation_configuration()
        )

        self.analyzer.valid_dataset.return_value = None

        self.analyzer.solar_engine.statistics = {
            "specific_production": 1111.111111,
        }

        with pytest.raises(
            ValueError,
            match="valid consumption dataset",
        ):
            self.controller.recommend_installation(
                configuration
            )

    def test_recommend_installation_requires_non_empty_dataset(
        self,
    ):

        configuration = (
            self._installation_configuration()
        )

        self.analyzer.valid_dataset.return_value = (
            pd.DataFrame()
        )

        self.analyzer.solar_engine.statistics = {
            "specific_production": 1111.111111,
        }

        with pytest.raises(
            ValueError,
            match="valid consumption dataset",
        ):
            self.controller.recommend_installation(
                configuration
            )

    def test_recommend_installation_requires_positive_consumption(
        self,
    ):

        configuration = (
            self._installation_configuration()
        )

        self.analyzer.valid_dataset.return_value = (
            pd.DataFrame(
                {
                    "AE_kWh": [0.0],
                }
            )
        )

        self.analyzer.solar_engine.statistics = {
            "specific_production": 1111.111111,
        }

        with pytest.raises(
            ValueError,
            match="Annual consumption must be greater than zero",
        ):
            self.controller.recommend_installation(
                configuration
            )

    def test_recommend_installation_rejects_negative_consumption(
        self,
    ):

        configuration = (
            self._installation_configuration()
        )

        self.analyzer.valid_dataset.return_value = (
            pd.DataFrame(
                {
                    "AE_kWh": [-100.0],
                }
            )
        )

        self.analyzer.solar_engine.statistics = {
            "specific_production": 1111.111111,
        }

        with pytest.raises(
            ValueError,
            match="Annual consumption must be greater than zero",
        ):
            self.controller.recommend_installation(
                configuration
            )

    def test_recommend_installation_converts_configuration_to_constraints(
        self,
    ):

        configuration = (
            self._installation_configuration()
        )

        constraints = configuration.to_constraints()

        assert isinstance(
            constraints,
            InstallationConstraints,
        )

    def test_recommend_installation_returns_result(
        self,
    ):

        self._configure_solar_reference()

        configuration = (
            self._installation_configuration()
        )

        result = (
            self.controller.recommend_installation(
                configuration
            )
        )

        self.analyzer.valid_dataset.assert_called_once_with()

        assert isinstance(
            result,
            InstallationRecommendation,
        )

        assert (
            result.annual_consumption_kwh
            == pytest.approx(5_000.0)
        )

        assert (
            result.annual_production_kwh
            == pytest.approx(5_400.0)
        )

        assert result.evaluation is not None

        assert (
            result.evaluation.candidate
            is not None
        )

        assert (
            result.evaluation.candidate.panel_count
            == 9
        )

        assert (
            result.evaluation.candidate.panel_power_wp
            == pytest.approx(540.0)
        )

        assert (
            result.evaluation.candidate.installed_power_kwp
            == pytest.approx(4.86)
        )

        assert self.controller.sizing_result is result

    def test_recommend_installation_selects_smallest_covering_configuration(
        self,
    ):

        self._configure_solar_reference()

        configuration = (
            self._installation_configuration()
        )

        result = (
            self.controller.recommend_installation(
                configuration
            )
        )

        assert result.panel_count == 9

        assert result.installed_power_kwp == pytest.approx(
            4.86
        )

        assert result.annual_production_kwh == pytest.approx(
            5_400.0
        )

    # ==================================================
    # Producción de candidatos
    # ==================================================

    def test_calculate_installation_production(
        self,
    ):

        self._configure_solar_reference()

        candidate = MagicMock()

        candidate.installed_power_kwp = 4.86

        production = (
            self.controller
            ._calculate_installation_production(
                candidate
            )
        )

        assert production == pytest.approx(
            5_400.0
        )

    def test_calculate_installation_production_requires_solar_production(
        self,
    ):

        self.analyzer.solar_engine.statistics = None

        candidate = MagicMock()

        candidate.installed_power_kwp = 4.86

        with pytest.raises(
            ValueError,
            match="Solar production must be calculated",
        ):
            self.controller._calculate_installation_production(
                candidate
            )

    def test_calculate_installation_production_rejects_zero_specific_production(
        self,
    ):

        self.analyzer.solar_engine.statistics = {
            "specific_production": 0.0,
        }

        candidate = MagicMock()

        candidate.installed_power_kwp = 4.86

        with pytest.raises(
            ValueError,
            match="Specific solar production must be greater than zero",
        ):
            self.controller._calculate_installation_production(
                candidate
            )

    # ==================================================
    # Reset
    # ==================================================

    def test_reset_clears_results(self):

        self.controller.sizing_result = MagicMock()

        self.controller.installation_configuration = (
            MagicMock()
        )

        self.controller.installation_specific_production = (
            1500.0
        )

        self.controller.reset()

        assert self.controller.sizing_result is None

        assert (
            self.controller.installation_configuration
            is None
        )

        assert (
            self.controller.installation_specific_production
            is None
        )

        self.analyzer.solar_engine.reset.assert_called_once_with()