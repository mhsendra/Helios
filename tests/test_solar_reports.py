import pandas as pd
import pytest

from unittest.mock import patch, call, MagicMock

from helios.reports.solar_reports import SolarReports

class TestSolarReports:

    def setup_method(self):

        self.reports = SolarReports()

        class Configuration:
            pv_technology = "crystSi"
            installed_power_kwp = 5.4
            tilt = 30
            azimuth = 0
            losses = 14

        self.configuration = Configuration()

    # ==================================================
    # production_statistics
    # ==================================================

    def test_production_statistics_requires_statistics(self):

        with pytest.raises(
            ValueError,
            match="Solar statistics have not been calculated."
        ):

            self.reports.production_statistics(
                None,
                self.configuration
            )

        with pytest.raises(
            ValueError,
            match="Solar statistics have not been calculated."
        ):

            self.reports.production_statistics(
                {},
                self.configuration
            )

    @patch(
        "helios.reports.solar_reports.ReportPrinter"
    )
    def test_production_statistics(self, printer):

        statistics = {
            "hours": 100,
            "annual_production": 5000.0,
            "period_production": 4800.0,
            "daily_average": 13.15,
            "maximum_power": 5.2,
            "minimum_power": 0.1,
            "equivalent_hours": 960.0,
            "capacity_factor": 11.0,
        }

        result = self.reports.production_statistics(
            statistics,
            self.configuration
        )

        assert result is None

        # --------------------------------------------------
        # Estructura
        # --------------------------------------------------

        printer.title.assert_called_once_with(
            "SOLAR PRODUCTION REPORT"
        )

        assert printer.blank.call_count == 3

        printer.subtitle.assert_called_once_with(
            "PRODUCCIÓN"
        )

        # --------------------------------------------------
        # Configuración FV
        # --------------------------------------------------

        printer.text.assert_called_once_with(
            "Tecnología FV",
            "crystSi"
        )

        printer.value.assert_any_call(
            "Potencia instalada",
            5.4,
            "kWp",
            decimals=2
        )

        printer.value.assert_any_call(
            "Inclinación",
            30,
            "°"
        )

        printer.value.assert_any_call(
            "Orientación",
            0,
            "°"
        )

        printer.percent.assert_any_call(
            "Pérdidas consideradas",
            14,
            decimals=1
        )

        # --------------------------------------------------
        # Estadísticas de producción
        # --------------------------------------------------

        printer.count.assert_called_once_with(
            "Horas del periodo analizado",
            100
        )

        printer.energy.assert_any_call(
            "Producción estimada anual (PVGIS)",
            5000.0
        )

        printer.energy.assert_any_call(
            "Producción simulada del periodo",
            4800.0
        )

        printer.energy.assert_any_call(
            "Producción media diaria",
            13.15
        )

        printer.value.assert_any_call(
            "Potencia máxima",
            5.2,
            "kW",
            decimals=2
        )

        printer.value.assert_any_call(
            "Potencia mínima (>0)",
            0.1,
            "kW",
            decimals=2
        )

        printer.value.assert_any_call(
            "Horas equivalentes",
            960.0,
            "h",
            decimals=2
        )

        printer.percent.assert_any_call(
            "Factor de capacidad",
            11.0
        )

        # 4 energy calls:
        # annual production
        # period production
        # daily average
        # (the remaining values use value)
        assert printer.energy.call_count == 3

        # 4 percent/value calls for configuration/statistics
        assert printer.percent.call_count == 2
        assert printer.value.call_count == 6

    # ==================================================
    # energy_balance
    # ==================================================

    def test_energy_balance_requires_statistics(self):

        with pytest.raises(
            RuntimeError,
            match="Energy statistics have not been calculated."
        ):

            self.reports.energy_balance(None)

    @patch(
        "helios.reports.solar_reports.ReportPrinter"
    )
    def test_energy_balance(self, printer):

        statistics = {
            "consumption": 1000.0,
            "period_production": 1200.0,
            "self_consumption": 800.0,
            "grid_import": 200.0,
            "grid_export": 400.0,
            "self_sufficiency": 80.0,
            "self_consumption_ratio": 66.67,
            "coverage_ratio": 120.0,
            "surplus_ratio": 33.33,
        }

        result = self.reports.energy_balance(
            statistics
        )

        assert result is None

        # --------------------------------------------------
        # Estructura
        # --------------------------------------------------

        printer.title.assert_called_once_with(
            "ENERGY BALANCE"
        )

        assert printer.blank.call_count == 3

        # --------------------------------------------------
        # Energía
        # --------------------------------------------------

        assert printer.energy.call_count == 5

        expected_energy_calls = [
            call(
                "Consumo total periodo",
                1000.0
            ),
            call(
                "Producción periodo",
                1200.0
            ),
            call(
                "Autoconsumo total",
                800.0
            ),
            call(
                "Importación de red",
                200.0
            ),
            call(
                "Exportación a red",
                400.0
            ),
        ]

        assert (
            printer.energy.call_args_list
            == expected_energy_calls
        )

        # --------------------------------------------------
        # Ratios
        # --------------------------------------------------

        assert printer.percent.call_count == 4

        expected_percent_calls = [
            call(
                "Autosuficiencia",
                80.0
            ),
            call(
                "Autoconsumo FV",
                66.67
            ),
            call(
                "Cobertura FV",
                120.0
            ),
            call(
                "Excedentes",
                33.33
            ),
        ]

        assert (
            printer.percent.call_args_list
            == expected_percent_calls
        )

    # ==================================================
    # monthly_production
    # ==================================================

    @patch(
        "helios.reports.solar_reports.ReportPrinter"
    )
    def test_monthly_production(self, printer):

        monthly_production = pd.Series(
            [
                100.0,
                200.0,
                300.0,
            ],
            index=pd.to_datetime(
                [
                    "2025-01-31",
                    "2025-02-28",
                    "2025-03-31",
                ]
            )
        )

        result = self.reports.monthly_production(
            monthly_production
        )

        assert result is None

        printer.title.assert_called_once_with(
            "MONTHLY PV PRODUCTION"
        )

        assert printer.blank.call_count == 1

        assert printer.energy.call_count == 3

        expected_calls = [
            call(
                "01-2025",
                100.0
            ),
            call(
                "02-2025",
                200.0
            ),
            call(
                "03-2025",
                300.0
            ),
        ]

        assert (
            printer.energy.call_args_list
            == expected_calls
        )

    # ==================================================
    # installation_simulation
    # ==================================================

    def test_installation_simulation_requires_configuration(self):

        recommendation = MagicMock()

        with pytest.raises(
            ValueError,
            match="Installation configuration is not available."
        ):
            self.reports.installation_simulation(
                configuration=None,
                recommendation=recommendation,
                solar_configuration=None,
                specific_production=None,
            )


    def test_installation_simulation_requires_recommendation(self):

        configuration = MagicMock()

        with pytest.raises(
            ValueError,
            match="Solar installation simulation has not been calculated."
        ):
            self.reports.installation_simulation(
                configuration=configuration,
                recommendation=None,
                solar_configuration=None,
                specific_production=None,
            )


    @patch(
        "helios.reports.solar_reports.ReportPrinter"
    )
    def test_installation_simulation_prints_basic_configuration(
        self,
        printer,
    ):

        configuration = MagicMock()

        configuration.available_area_m2 = 42.0
        configuration.roof_width_m = None
        configuration.roof_height_m = None
        configuration.panel_width_m = 1.134
        configuration.panel_height_m = 2.273
        configuration.panel_power_wp = 540
        configuration.min_panels = 2
        configuration.max_panels = 10
        configuration.panel_orientation = "vertical"

        configuration.maintenance_passage_required = False

        recommendation = MagicMock()

        recommendation.panel_count = 6
        recommendation.installed_power_kwp = 3.24
        recommendation.annual_consumption_kwh = 5000.0
        recommendation.annual_production_kwh = 5500.0
        recommendation.self_sufficiency_percent = 75.0
        recommendation.production_coverage_percent = 110.0
        recommendation.energy_surplus_kwh = 500.0
        recommendation.energy_deficit_kwh = 0.0
        recommendation.remaining_area_m2 = 35.0

        recommendation.evaluation.layout = None

        result = self.reports.installation_simulation(
            configuration=configuration,
            recommendation=recommendation,
            solar_configuration=None,
            specific_production=None,
        )

        assert result is None

        printer.title.assert_called_once_with(
            "SOLAR INSTALLATION SIMULATION"
        )

        printer.value.assert_any_call(
            "Superficie disponible",
            42.0,
            "m²",
            decimals=2,
        )

        printer.value.assert_any_call(
            "Anchura del panel",
            1.134,
            "m",
            decimals=3,
        )

        printer.value.assert_any_call(
            "Altura del panel",
            2.273,
            "m",
            decimals=3,
        )

        printer.value.assert_any_call(
            "Potencia del panel",
            540,
            "Wp",
            decimals=0,
        )

        printer.count.assert_any_call(
            "Mínimo de paneles",
            2,
        )

        printer.count.assert_any_call(
            "Máximo de paneles",
            10,
        )

        printer.text.assert_any_call(
            "Orientación de paneles",
            "vertical",
        )


    @patch(
        "helios.reports.solar_reports.ReportPrinter"
    )
    def test_installation_simulation_prints_roof_dimensions(
        self,
        printer,
    ):

        configuration = MagicMock()

        configuration.available_area_m2 = 42.0
        configuration.roof_width_m = 10.0
        configuration.roof_height_m = 8.0
        configuration.panel_width_m = 1.134
        configuration.panel_height_m = 2.273
        configuration.panel_power_wp = 540
        configuration.min_panels = 2
        configuration.max_panels = None
        configuration.panel_orientation = "vertical"

        configuration.maintenance_passage_required = False

        recommendation = MagicMock()

        recommendation.panel_count = 6
        recommendation.installed_power_kwp = 3.24
        recommendation.annual_consumption_kwh = 5000.0
        recommendation.annual_production_kwh = 5500.0
        recommendation.self_sufficiency_percent = 75.0
        recommendation.production_coverage_percent = 110.0
        recommendation.energy_surplus_kwh = 500.0
        recommendation.energy_deficit_kwh = 0.0
        recommendation.remaining_area_m2 = 35.0

        recommendation.evaluation.layout = None

        self.reports.installation_simulation(
            configuration=configuration,
            recommendation=recommendation,
            solar_configuration=None,
            specific_production=None,
        )

        printer.value.assert_any_call(
            "Anchura del tejado",
            10.0,
            "m",
            decimals=2,
        )

        printer.value.assert_any_call(
            "Altura del tejado",
            8.0,
            "m",
            decimals=2,
        )

        printer.count.assert_not_called()


    @patch(
        "helios.reports.solar_reports.ReportPrinter"
    )
    def test_installation_simulation_prints_maintenance(
        self,
        printer,
    ):

        configuration = MagicMock()

        configuration.available_area_m2 = 42.0
        configuration.roof_width_m = 10.0
        configuration.roof_height_m = 8.0
        configuration.panel_width_m = 1.134
        configuration.panel_height_m = 2.273
        configuration.panel_power_wp = 540
        configuration.min_panels = 2
        configuration.max_panels = 10
        configuration.panel_orientation = "vertical"

        configuration.maintenance_passage_required = True
        configuration.maintenance_passage_width_m = 0.45
        configuration.maintenance_passage_orientation = "vertical"

        recommendation = MagicMock()

        recommendation.panel_count = 6
        recommendation.installed_power_kwp = 3.24
        recommendation.annual_consumption_kwh = 5000.0
        recommendation.annual_production_kwh = 5500.0
        recommendation.self_sufficiency_percent = 75.0
        recommendation.production_coverage_percent = 110.0
        recommendation.energy_surplus_kwh = 500.0
        recommendation.energy_deficit_kwh = 0.0
        recommendation.remaining_area_m2 = 35.0

        recommendation.evaluation.layout = None

        self.reports.installation_simulation(
            configuration=configuration,
            recommendation=recommendation,
            solar_configuration=None,
            specific_production=None,
        )

        printer.text.assert_any_call(
            "Pasillo de mantenimiento",
            "Sí",
        )

        printer.value.assert_any_call(
            "Anchura del pasillo",
            0.45,
            "m",
            decimals=2,
        )

        printer.text.assert_any_call(
            "Orientación del pasillo",
            "vertical",
        )


    @patch(
        "helios.reports.solar_reports.ReportPrinter"
    )
    def test_installation_simulation_omits_maintenance_details_when_not_required(
        self,
        printer,
    ):

        configuration = MagicMock()

        configuration.available_area_m2 = 42.0
        configuration.roof_width_m = None
        configuration.roof_height_m = None
        configuration.panel_width_m = 1.134
        configuration.panel_height_m = 2.273
        configuration.panel_power_wp = 540
        configuration.min_panels = 2
        configuration.max_panels = None
        configuration.panel_orientation = "vertical"

        configuration.maintenance_passage_required = False

        recommendation = MagicMock()

        recommendation.panel_count = 6
        recommendation.installed_power_kwp = 3.24
        recommendation.annual_consumption_kwh = 5000.0
        recommendation.annual_production_kwh = 5500.0
        recommendation.self_sufficiency_percent = 75.0
        recommendation.production_coverage_percent = 110.0
        recommendation.energy_surplus_kwh = 500.0
        recommendation.energy_deficit_kwh = 0.0
        recommendation.remaining_area_m2 = 35.0

        recommendation.evaluation.layout = None

        self.reports.installation_simulation(
            configuration=configuration,
            recommendation=recommendation,
            solar_configuration=None,
            specific_production=None,
        )

        printer.text.assert_any_call(
            "Pasillo de mantenimiento",
            "No",
        )

        printer.value.assert_not_called()


    @patch(
        "helios.reports.solar_reports.ReportPrinter"
    )
    def test_installation_simulation_prints_solar_configuration_and_specific_production(
        self,
        printer,
    ):

        configuration = MagicMock()

        configuration.available_area_m2 = 42.0
        configuration.roof_width_m = None
        configuration.roof_height_m = None
        configuration.panel_width_m = 1.134
        configuration.panel_height_m = 2.273
        configuration.panel_power_wp = 540
        configuration.min_panels = 2
        configuration.max_panels = 10
        configuration.panel_orientation = "vertical"
        configuration.maintenance_passage_required = False

        solar_configuration = MagicMock()

        solar_configuration.pv_technology = "crystSi"
        solar_configuration.tilt = 30
        solar_configuration.azimuth = 0
        solar_configuration.losses = 14
        solar_configuration.reference_year = 2023

        recommendation = MagicMock()

        recommendation.panel_count = 6
        recommendation.installed_power_kwp = 3.24
        recommendation.annual_consumption_kwh = 5000.0
        recommendation.annual_production_kwh = 5500.0
        recommendation.self_sufficiency_percent = 75.0
        recommendation.production_coverage_percent = 110.0
        recommendation.energy_surplus_kwh = 500.0
        recommendation.energy_deficit_kwh = 0.0
        recommendation.remaining_area_m2 = 35.0

        recommendation.evaluation.layout = None

        self.reports.installation_simulation(
            configuration=configuration,
            recommendation=recommendation,
            solar_configuration=solar_configuration,
            specific_production=1250.0,
        )

        printer.text.assert_any_call(
            "Tecnología FV",
            "crystSi",
        )

        printer.value.assert_any_call(
            "Inclinación",
            30,
            "°",
        )

        printer.value.assert_any_call(
            "Orientación",
            0,
            "°",
        )

        printer.percent.assert_any_call(
            "Pérdidas",
            14,
            decimals=1,
        )

        printer.value.assert_any_call(
            "Año de referencia",
            2023,
            "",
            decimals=0,
        )

        printer.value.assert_any_call(
            "Producción específica",
            1250.0,
            "kWh/kWp/año",
            decimals=2,
        )


    @patch(
        "helios.reports.solar_reports.ReportPrinter"
    )
    def test_installation_simulation_handles_layout_without_physical_layout(
        self,
        printer,
    ):

        configuration = MagicMock()

        configuration.available_area_m2 = 42.0
        configuration.roof_width_m = None
        configuration.roof_height_m = None
        configuration.panel_width_m = 1.134
        configuration.panel_height_m = 2.273
        configuration.panel_power_wp = 540
        configuration.min_panels = 2
        configuration.max_panels = None
        configuration.panel_orientation = "vertical"
        configuration.maintenance_passage_required = False

        recommendation = MagicMock()

        recommendation.panel_count = 6
        recommendation.installed_power_kwp = 3.24
        recommendation.annual_consumption_kwh = 5000.0
        recommendation.annual_production_kwh = 5500.0
        recommendation.self_sufficiency_percent = 75.0
        recommendation.production_coverage_percent = 110.0
        recommendation.energy_surplus_kwh = 500.0
        recommendation.energy_deficit_kwh = 0.0
        recommendation.remaining_area_m2 = 35.0

        recommendation.evaluation.layout = None

        self.reports.installation_simulation(
            configuration=configuration,
            recommendation=recommendation,
            solar_configuration=None,
            specific_production=None,
        )

        printer.text.assert_any_call(
            "Distribución física",
            "No disponible",
        )

    # ==================================================
    # Dimensiones del tejado
    # ==================================================

    @patch(
        "helios.reports.solar_reports.ReportPrinter"
    )
    def test_installation_simulation_prints_roof_dimensions(
        self,
        printer,
    ):

        configuration = MagicMock()

        configuration.available_area_m2 = 42.0
        configuration.roof_width_m = 10.0
        configuration.roof_height_m = 8.0
        configuration.panel_width_m = 1.134
        configuration.panel_height_m = 2.273
        configuration.panel_power_wp = 540
        configuration.min_panels = 2
        configuration.max_panels = None
        configuration.panel_orientation = "vertical"

        configuration.maintenance_passage_required = False

        recommendation = MagicMock()

        recommendation.panel_count = 6
        recommendation.installed_power_kwp = 3.24
        recommendation.annual_consumption_kwh = 5000.0
        recommendation.annual_production_kwh = 5500.0
        recommendation.self_sufficiency_percent = 75.0
        recommendation.production_coverage_percent = 110.0
        recommendation.energy_surplus_kwh = 500.0
        recommendation.energy_deficit_kwh = 0.0
        recommendation.remaining_area_m2 = 35.0

        recommendation.evaluation.layout = None

        self.reports.installation_simulation(
            configuration=configuration,
            recommendation=recommendation,
            solar_configuration=None,
            specific_production=None,
        )

        printer.value.assert_any_call(
            "Anchura del tejado",
            10.0,
            "m",
            decimals=2,
        )

        printer.value.assert_any_call(
            "Altura del tejado",
            8.0,
            "m",
            decimals=2,
        )

        printer.count.assert_any_call(
            "Mínimo de paneles",
            2,
        )

        printer.count.assert_any_call(
            "Paneles recomendados",
            6,
        )


    # ==================================================
    # Pasillo de mantenimiento
    # ==================================================

    @patch(
        "helios.reports.solar_reports.ReportPrinter"
    )
    def test_installation_simulation_omits_maintenance_details_when_not_required(
        self,
        printer,
    ):

        configuration = MagicMock()

        configuration.available_area_m2 = 42.0
        configuration.roof_width_m = None
        configuration.roof_height_m = None
        configuration.panel_width_m = 1.134
        configuration.panel_height_m = 2.273
        configuration.panel_power_wp = 540
        configuration.min_panels = 2
        configuration.max_panels = None
        configuration.panel_orientation = "vertical"

        configuration.maintenance_passage_required = False

        recommendation = MagicMock()

        recommendation.panel_count = 6
        recommendation.installed_power_kwp = 3.24
        recommendation.annual_consumption_kwh = 5000.0
        recommendation.annual_production_kwh = 5500.0
        recommendation.self_sufficiency_percent = 75.0
        recommendation.production_coverage_percent = 110.0
        recommendation.energy_surplus_kwh = 500.0
        recommendation.energy_deficit_kwh = 0.0
        recommendation.remaining_area_m2 = 35.0

        recommendation.evaluation.layout = None

        self.reports.installation_simulation(
            configuration=configuration,
            recommendation=recommendation,
            solar_configuration=None,
            specific_production=None,
        )

        printer.text.assert_any_call(
            "Pasillo de mantenimiento",
            "No",
        )

        assert (
            "Anchura del pasillo",
            0.45,
            "m",
        ) not in [
            call.args
            for call in printer.value.call_args_list
        ]

        assert (
            "Orientación del pasillo",
            "vertical",
        ) not in [
            call.args
            for call in printer.text.call_args_list
        ]

    # ==================================================
    # Distribución física
    # ==================================================

    @patch(
        "helios.reports.solar_reports.ReportPrinter"
    )
    def test_installation_simulation_prints_physical_layout(
        self,
        printer,
    ):

        configuration = MagicMock()

        configuration.available_area_m2 = 42.0
        configuration.roof_width_m = 10.0
        configuration.roof_height_m = 8.0
        configuration.panel_width_m = 1.134
        configuration.panel_height_m = 2.273
        configuration.panel_power_wp = 540
        configuration.min_panels = 2
        configuration.max_panels = 10
        configuration.panel_orientation = "vertical"

        configuration.maintenance_passage_required = False

        layout = MagicMock()

        layout.rows = 2
        layout.columns = 3
        layout.orientation = "vertical"
        layout.occupied_width_m = 3.402
        layout.occupied_height_m = 4.546
        layout.walkway_width_m = 0.0

        evaluation = MagicMock()
        evaluation.layout = layout
        evaluation.occupied_area_m2 = 15.47

        recommendation = MagicMock()

        recommendation.panel_count = 6
        recommendation.installed_power_kwp = 3.24
        recommendation.annual_consumption_kwh = 5000.0
        recommendation.annual_production_kwh = 5500.0
        recommendation.self_sufficiency_percent = 75.0
        recommendation.production_coverage_percent = 110.0
        recommendation.energy_surplus_kwh = 500.0
        recommendation.energy_deficit_kwh = 0.0
        recommendation.remaining_area_m2 = 26.53

        recommendation.evaluation = evaluation

        result = self.reports.installation_simulation(
            configuration=configuration,
            recommendation=recommendation,
            solar_configuration=None,
            specific_production=None,
        )

        assert result is None

        printer.subtitle.assert_any_call(
            "PHYSICAL LAYOUT"
        )

        printer.count.assert_any_call(
            "Filas",
            2,
        )

        printer.count.assert_any_call(
            "Columnas",
            3,
        )

        printer.text.assert_any_call(
            "Orientación",
            "vertical",
        )

        printer.value.assert_any_call(
            "Superficie ocupada",
            15.47,
            "m²",
            decimals=2,
        )

        printer.text.assert_any_call(
            "Dimensiones ocupadas",
            "3.40 × 4.55 m",
        )

        printer.value.assert_any_call(
            "Superficie restante",
            26.53,
            "m²",
            decimals=2,
        )


    @patch(
        "helios.reports.solar_reports.ReportPrinter"
    )
    def test_installation_simulation_prints_physical_layout_with_walkway(
        self,
        printer,
    ):

        configuration = MagicMock()

        configuration.available_area_m2 = 42.0
        configuration.roof_width_m = 10.0
        configuration.roof_height_m = 8.0
        configuration.panel_width_m = 1.134
        configuration.panel_height_m = 2.273
        configuration.panel_power_wp = 540
        configuration.min_panels = 2
        configuration.max_panels = 10
        configuration.panel_orientation = "vertical"

        configuration.maintenance_passage_required = True
        configuration.maintenance_passage_width_m = 0.45
        configuration.maintenance_passage_orientation = "vertical"

        layout = MagicMock()

        layout.rows = 2
        layout.columns = 3
        layout.orientation = "vertical"
        layout.occupied_width_m = 3.852
        layout.occupied_height_m = 4.546
        layout.walkway_width_m = 0.45
        layout.walkway_position = "vertical"

        evaluation = MagicMock()
        evaluation.layout = layout
        evaluation.occupied_area_m2 = 17.51

        recommendation = MagicMock()

        recommendation.panel_count = 6
        recommendation.installed_power_kwp = 3.24
        recommendation.annual_consumption_kwh = 5000.0
        recommendation.annual_production_kwh = 5500.0
        recommendation.self_sufficiency_percent = 75.0
        recommendation.production_coverage_percent = 110.0
        recommendation.energy_surplus_kwh = 500.0
        recommendation.energy_deficit_kwh = 0.0
        recommendation.remaining_area_m2 = 24.49

        recommendation.evaluation = evaluation

        self.reports.installation_simulation(
            configuration=configuration,
            recommendation=recommendation,
            solar_configuration=None,
            specific_production=None,
        )

        printer.value.assert_any_call(
            "Pasillo de mantenimiento",
            0.45,
            "m",
            decimals=2,
        )

        printer.text.assert_any_call(
            "Posición del pasillo",
            "vertical",
        )

        printer.value.assert_any_call(
            "Superficie restante",
            24.49,
            "m²",
            decimals=2,
        )


    @patch(
        "helios.reports.solar_reports.ReportPrinter"
    )
    def test_installation_simulation_does_not_print_walkway_when_layout_has_no_walkway(
        self,
        printer,
    ):

        configuration = MagicMock()

        configuration.available_area_m2 = 42.0
        configuration.roof_width_m = 10.0
        configuration.roof_height_m = 8.0
        configuration.panel_width_m = 1.134
        configuration.panel_height_m = 2.273
        configuration.panel_power_wp = 540
        configuration.min_panels = 2
        configuration.max_panels = 10
        configuration.panel_orientation = "vertical"

        configuration.maintenance_passage_required = False

        layout = MagicMock()

        layout.rows = 2
        layout.columns = 3
        layout.orientation = "horizontal"
        layout.occupied_width_m = 4.546
        layout.occupied_height_m = 3.402
        layout.walkway_width_m = 0.0

        evaluation = MagicMock()
        evaluation.layout = layout
        evaluation.occupied_area_m2 = 15.47

        recommendation = MagicMock()

        recommendation.panel_count = 6
        recommendation.installed_power_kwp = 3.24
        recommendation.annual_consumption_kwh = 5000.0
        recommendation.annual_production_kwh = 5500.0
        recommendation.self_sufficiency_percent = 75.0
        recommendation.production_coverage_percent = 110.0
        recommendation.energy_surplus_kwh = 500.0
        recommendation.energy_deficit_kwh = 0.0
        recommendation.remaining_area_m2 = 26.53

        recommendation.evaluation = evaluation

        self.reports.installation_simulation(
            configuration=configuration,
            recommendation=recommendation,
            solar_configuration=None,
            specific_production=None,
        )

        assert (
            "Pasillo de mantenimiento",
            0.0,
            "m",
        ) not in [
            call.args
            for call in printer.value.call_args_list
        ]

        assert (
            "Posición del pasillo",
            "vertical",
        ) not in [
            call.args
            for call in printer.text.call_args_list
        ]