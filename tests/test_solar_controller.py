import pandas as pd

import pytest

from unittest.mock import MagicMock, call

from helios.solar.installation_configuration import (
    InstallationConfiguration,
)

from helios.solar.configuration import SolarConfiguration

from helios.core.controllers.solar_controller import SolarController

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

        self.analyzer.solar_engine.configuration = SolarConfiguration(
            latitude=41.6,
            longitude=2.1,
            tilt=30,
            azimuth=0,
        )

        self.analyzer.solar_engine.yearly_production = pd.Series(
            [1111.111111],
            index=pd.to_datetime(
                ["2025-12-31"]
            ),
        )

        assert self.controller.specific_production == pytest.approx(
            1111.111111
        )

    def test_specific_production_without_yearly_production(self):

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

    def test_installation_simulation_report_delegates_to_engine(
        self,
        monkeypatch,
    ):

        engine = self.analyzer.solar_engine

        configuration = object()
        recommendation = object()
        specific_production = 1500.0

        self.controller.installation_configuration = (
            configuration
        )

        self.controller.sizing_result = (
            recommendation
        )

        monkeypatch.setattr(
            type(self.controller),
            "specific_production",
            property(
                lambda self: specific_production
            ),
        )

        self.controller.installation_simulation_report()

        assert engine.mock_calls == [
            call.installation_simulation_report(
                configuration=configuration,
                recommendation=recommendation,
                specific_production=specific_production,
            ),
        ]

    def test_reset(self):

        engine = self.analyzer.solar_engine

        self.controller.reset()

        engine.reset.assert_called_once_with()

    # ==================================================
    # Dimensionamiento de instalación solar
    # ==================================================

    def _installation_configuration(self):
        """
        Configuración real de instalación utilizada
        como entrada del flujo de dimensionamiento.
        """

        return InstallationConfiguration(
            available_area_m2=50.0,
            panel_width_m=1.134,
            panel_height_m=1.722,
            panel_power_wp=540.0,
            min_panels=5,
            max_panels=15,
        )

    def _configure_solar_reference(self):
        """
        Prepara una referencia solar con una producción
        específica conocida.
        """

        self.analyzer.valid_dataset.return_value = pd.DataFrame(
            {
                "AE_kWh": [5_000.0],
            }
        )

        self.analyzer.solar_engine.configuration = SolarConfiguration(
            latitude=41.6,
            longitude=2.1,
            tilt=30,
            azimuth=0,
        )

        self.analyzer.solar_engine.yearly_production = pd.Series(
            [1111.111111],
            index=pd.to_datetime(
                ["2025-12-31"]
            ),
        )

    # --------------------------------------------------
    # Validación de entrada
    # --------------------------------------------------

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
            self.controller.recommend_installation(None)

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

    # --------------------------------------------------
    # Producción solar
    # --------------------------------------------------

    def test_recommend_installation_requires_calculated_production(
        self,
    ):

        configuration = self._installation_configuration()

        self.analyzer.solar_engine.yearly_production = None

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

        configuration = self._installation_configuration()

        self.analyzer.solar_engine.configuration = MagicMock()

        self.analyzer.solar_engine.yearly_production = pd.Series(
            [0.0],
            index=pd.to_datetime(
                ["2025-12-31"]
            ),
        )

        with pytest.raises(
            ValueError,
            match="Specific solar production must be greater than zero",
        ):
            self.controller.recommend_installation(
                configuration
            )

    # --------------------------------------------------
    # Dataset y consumo
    # --------------------------------------------------

    def test_recommend_installation_requires_dataset(
        self,
    ):

        configuration = self._installation_configuration()

        self.analyzer.valid_dataset.return_value = None

        self.analyzer.solar_engine.yearly_production = pd.Series(
            [6_000.0],
            index=pd.to_datetime(
                ["2025-12-31"]
            ),
        )

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

        configuration = self._installation_configuration()

        self.analyzer.valid_dataset.return_value = pd.DataFrame()

        self.analyzer.solar_engine.yearly_production = pd.Series(
            [6_000.0],
            index=pd.to_datetime(
                ["2025-12-31"]
            ),
        )

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

        configuration = self._installation_configuration()

        self.analyzer.valid_dataset.return_value = pd.DataFrame(
            {
                "AE_kWh": [0.0],
            }
        )

        self.analyzer.solar_engine.yearly_production = pd.Series(
            [6_000.0],
            index=pd.to_datetime(
                ["2025-12-31"]
            ),
        )

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

        configuration = self._installation_configuration()

        self.analyzer.valid_dataset.return_value = pd.DataFrame(
            {
                "AE_kWh": [-100.0],
            }
        )

        self.analyzer.solar_engine.yearly_production = pd.Series(
            [6_000.0],
            index=pd.to_datetime(
                ["2025-12-31"]
            ),
        )

        with pytest.raises(
            ValueError,
            match="Annual consumption must be greater than zero",
        ):
            self.controller.recommend_installation(
                configuration
            )

    # --------------------------------------------------
    # Integración con InstallationConfiguration
    # --------------------------------------------------

    def test_recommend_installation_converts_configuration_to_constraints(
        self,
    ):

        self._configure_solar_reference()

        configuration = self._installation_configuration()

        constraints = configuration.to_constraints()

        assert isinstance(
            constraints,
            InstallationConstraints,
        )

    # --------------------------------------------------
    # Resultado
    # --------------------------------------------------

    def test_recommend_installation_returns_result(
        self,
    ):

        self._configure_solar_reference()

        configuration = self._installation_configuration()

        result = self.controller.recommend_installation(
            configuration
        )

        assert isinstance(
            result,
            InstallationRecommendation,
        )

        assert result.annual_consumption_kwh == pytest.approx(
            5_000.0
        )

        assert result.annual_production_kwh == pytest.approx(
            5_400.0
        )

        assert result.evaluation is not None

        assert result.evaluation.candidate is not None

        assert result.evaluation.candidate.panel_count == 9

        assert result.evaluation.candidate.panel_power_wp == pytest.approx(
            540.0
        )

        assert result.evaluation.candidate.installed_power_kwp == pytest.approx(
            4.86
        )

    # --------------------------------------------------
    # Selección óptima
    # --------------------------------------------------

    def test_recommend_installation_selects_smallest_covering_configuration(
        self,
    ):

        self._configure_solar_reference()

        configuration = self._installation_configuration()

        result = self.controller.recommend_installation(
            configuration
        )

        # Producción específica:
        #
        # 6000 / 5.4 = 1111.11 kWh/kWp
        #
        # Cada panel:
        #
        # 540 Wp = 0.54 kWp
        #
        # Producción por panel:
        #
        # 0.54 * 1111.11 = 600 kWh
        #
        # Consumo:
        #
        # 5000 kWh
        #
        # 8 paneles  -> 4800 kWh
        # 9 paneles  -> 5400 kWh
        #
        # Por tanto, 9 paneles es la primera
        # configuración que cubre el consumo.

        assert result.panel_count == 9

        assert result.installed_power_kwp == pytest.approx(
            4.86
        )

        assert result.annual_production_kwh == pytest.approx(
            5_400.0
        )

    # --------------------------------------------------
    # Cálculo de producción de candidatos
    # --------------------------------------------------

    def test_calculate_installation_production(
        self,
    ):

        self._configure_solar_reference()

        candidate = MagicMock()

        candidate.installed_power_kwp = 4.86

        production = (
            self.controller._calculate_installation_production(
                candidate
            )
        )

        assert production == pytest.approx(
            5_400.0
        )

    def test_calculate_installation_production_requires_solar_production(
        self,
    ):

        self.analyzer.solar_engine.configuration = SolarConfiguration(
            latitude=41.6,
            longitude=2.1,
            tilt=30,
            azimuth=0,
        )

        self.analyzer.solar_engine.yearly_production = None

        candidate = MagicMock()

        candidate.installed_power_kwp = 4.86

        with pytest.raises(
            ValueError,
            match="Solar production must be calculated",
        ):
            self.controller._calculate_installation_production(
                candidate
            )

    # --------------------------------------------------
    # Reset
    # --------------------------------------------------

    def test_reset_clears_sizing_result(
        self,
    ):

        self._configure_solar_reference()

        configuration = self._installation_configuration()

        self.controller.recommend_installation(
            configuration
        )

        assert self.controller.sizing_result is not None

        self.controller.reset()

        assert self.controller.sizing_result is None