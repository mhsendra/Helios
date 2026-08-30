import pandas as pd

import pytest

from unittest.mock import MagicMock

from PySide6.QtWidgets import QApplication

from helios.gui.widgets.solar_page import SolarPage

from helios.solar.configuration import SolarConfiguration


class TestSolarPage:

    @classmethod
    def setup_class(cls):

        cls.app = QApplication.instance()

        if cls.app is None:
            cls.app = QApplication([])

    def setup_method(self):

        self.project = MagicMock()

        self.page = SolarPage(
            self.project
        )

    # ==================================================
    # Estado inicial
    # ==================================================

    def test_page_stores_project(self):

        assert self.page.project is self.project

    def test_initial_tabs_state(self):

        assert self.page.tabs.isTabEnabled(
            self.page.tabs.indexOf(
                self.page.configuration_tab
            )
        )

        assert self.page.tabs.isTabEnabled(
            self.page.tabs.indexOf(
                self.page.production_tab
            )
        )

        assert not self.page.tabs.isTabEnabled(
            self.page.tabs.indexOf(
                self.page.balance_tab
            )
        )

        assert not self.page.tabs.isTabEnabled(
            self.page.tabs.indexOf(
                self.page.statistics_tab
            )
        )

    def test_initial_production_status(self):

        assert self.page.source_label.text() == "PVGIS"

        assert self.page.database_label.text() == "SARAH3"

        assert self.page.reference_year_label.text() == "-"

        assert self.page.last_update_label.text() == "Nunca"

        assert self.page.production_status_label.text() == "No calculada"

        assert self.page.production_annual_label.text() == "-"

        assert self.page.production_specific_label.text() == "-"

        assert self.page.production_coverage_label.text() == "-"

    # ==================================================
    # Configuración
    # ==================================================

    def test_get_configuration(self):

        self.page.latitude_spinbox.setValue(41.3851)
        self.page.longitude_spinbox.setValue(2.1734)
        self.page.tilt_spinbox.setValue(30)
        self.page.azimuth_spinbox.setValue(10)
        self.page.system_losses_spinbox.setValue(14.5)

        self.page.pv_technology_combobox.setCurrentIndex(0)
        self.page.mounting_place_combobox.setCurrentIndex(0)

        configuration = self.page.get_configuration()

        assert configuration.latitude == 41.3851
        assert configuration.longitude == 2.1734
        assert configuration.tilt == 30
        assert configuration.azimuth == 10
        assert configuration.reference_year == 2023
        assert configuration.losses == 14.5
        assert configuration.pv_technology == "crystSi"
        assert configuration.mounting_place == "free"

    def test_configuration_widgets_have_expected_ranges(self):

        assert self.page.system_losses_spinbox.minimum() == 0.0
        assert self.page.system_losses_spinbox.maximum() == 100.0

        assert self.page.tilt_spinbox.minimum() == 0
        assert self.page.tilt_spinbox.maximum() == 90

        assert self.page.azimuth_spinbox.minimum() == -180
        assert self.page.azimuth_spinbox.maximum() == 180

        assert self.page.latitude_spinbox.minimum() == -90.0
        assert self.page.latitude_spinbox.maximum() == 90.0

        assert self.page.longitude_spinbox.minimum() == -180.0
        assert self.page.longitude_spinbox.maximum() == 180.0

    def test_pv_technology_options(self):

        assert self.page.pv_technology_combobox.count() == 3

        assert (
            self.page.pv_technology_combobox.itemData(0)
            == "crystSi"
        )

        assert (
            self.page.pv_technology_combobox.itemData(1)
            == "CIS"
        )

        assert (
            self.page.pv_technology_combobox.itemData(2)
            == "CdTe"
        )

    def test_mounting_place_options(self):

        assert self.page.mounting_place_combobox.count() == 2

        assert (
            self.page.mounting_place_combobox.itemData(0)
            == "free"
        )

        assert (
            self.page.mounting_place_combobox.itemData(1)
            == "building"
        )

    # ==================================================
    # Estado de producción
    # ==================================================

    def test_update_production_status_with_values(self):

        self.page.update_production_status(
            source="PVGIS",
            database="SARAH3",
            reference_year=2023,
            last_update="Ahora",
            status="Disponible",
            annual_production=12500.456,
            specific_production=1543.21,
            coverage=67.89,
        )

        assert self.page.source_label.text() == "PVGIS"
        assert self.page.database_label.text() == "SARAH3"
        assert self.page.reference_year_label.text() == "2023"
        assert self.page.last_update_label.text() == "Ahora"
        assert self.page.production_status_label.text() == "Disponible"

        assert (
            self.page.production_annual_label.text()
            == "12,500.5 kWh"
        )

        assert (
            self.page.production_specific_label.text()
            == "1,543.2 kWh/kWp"
        )

        assert (
            self.page.production_coverage_label.text()
            == "67.9 %"
        )

    def test_update_production_status_with_none_values(self):

        self.page.update_production_status(
            source="PVGIS",
            database="SARAH3",
            reference_year=None,
            last_update="-",
            status="Error",
            annual_production=None,
            specific_production=None,
            coverage=None,
        )

        assert self.page.reference_year_label.text() == "-"
        assert self.page.production_annual_label.text() == "-"
        assert self.page.production_specific_label.text() == "-"
        assert self.page.production_coverage_label.text() == "-"

    # ==================================================
    # Producción mensual
    # ==================================================

    def test_populate_monthly_table(self):

        series = pd.Series(
            [100.0, 200.0, 300.0],
            index=pd.to_datetime(
                [
                    "2025-01-31",
                    "2025-02-28",
                    "2025-03-31",
                ]
            ),
        )

        self.page.populate_monthly_table(
            self.page.monthly_production_table,
            series,
        )

        table = self.page.monthly_production_table

        assert table.rowCount() == 4

        assert table.item(0, 0).text() == "Enero"
        assert table.item(0, 1).text() == "100.00"

        assert table.item(1, 0).text() == "Febrero"
        assert table.item(1, 1).text() == "200.00"

        assert table.item(2, 0).text() == "Marzo"
        assert table.item(2, 1).text() == "300.00"

        assert table.item(3, 0).text() == "TOTAL"
        assert table.item(3, 1).text() == "600.00"

    def test_populate_monthly_table_empty(self):

        series = pd.Series(dtype=float)

        self.page.populate_monthly_table(
            self.page.monthly_production_table,
            series,
        )

        assert self.page.monthly_production_table.rowCount() == 0

    # ==================================================
    # Balance mensual
    # ==================================================

    def test_populate_balance_table(self):

        balance = pd.DataFrame(
            {
                "consumption_kwh": [100.0, 200.0],
                "production_kwh": [150.0, 250.0],
                "self_consumption_kwh": [80.0, 120.0],
                "grid_import_kwh": [20.0, 30.0],
                "grid_export_kwh": [70.0, 130.0],
            },
            index=pd.to_datetime(
                [
                    "2025-01-31",
                    "2025-02-28",
                ]
            ),
        )

        self.page.populate_balance_table(
            self.page.balance_table,
            balance,
        )

        table = self.page.balance_table

        assert table.rowCount() == 3

        assert table.item(0, 0).text() == "Enero"
        assert table.item(0, 1).text() == "80.00"
        assert table.item(0, 2).text() == "20.00"
        assert table.item(0, 3).text() == "70.00"

        assert table.item(1, 0).text() == "Febrero"
        assert table.item(1, 1).text() == "120.00"
        assert table.item(1, 2).text() == "30.00"
        assert table.item(1, 3).text() == "130.00"

        assert table.item(2, 0).text() == "TOTAL"
        assert table.item(2, 1).text() == "200.00"
        assert table.item(2, 2).text() == "50.00"
        assert table.item(2, 3).text() == "200.00"

    def test_populate_balance_table_empty(self):

        balance = pd.DataFrame()

        self.page.populate_balance_table(
            self.page.balance_table,
            balance,
        )

        assert self.page.balance_table.rowCount() == 0

    # ==================================================
    # Resumen del balance
    # ==================================================

    def test_update_balance_summary(self):

        self.project.solar.energy_balance = pd.DataFrame(
            {
                "consumption_kwh": [100.0, 200.0],
                "production_kwh": [150.0, 250.0],
                "self_consumption_kwh": [80.0, 120.0],
                "grid_import_kwh": [20.0, 30.0],
                "grid_export_kwh": [70.0, 130.0],
            }
        )

        self.project.solar.coverage = 66.6667

        self.page.update_balance_summary()

        assert (
            self.page.balance_total_consumption_label.text()
            == "300.00 kWh"
        )

        assert (
            self.page.balance_total_production_label.text()
            == "400.00 kWh"
        )

        assert (
            self.page.balance_self_consumption_label.text()
            == "200.00 kWh"
        )

        assert (
            self.page.balance_grid_import_label.text()
            == "50.00 kWh"
        )

        assert (
            self.page.balance_grid_export_label.text()
            == "200.00 kWh"
        )

        assert (
            self.page.balance_coverage_label.text()
            == "66.7 %"
        )

    def test_update_balance_summary_without_balance(self):

        self.project.solar.energy_balance = None

        self.page.update_balance_summary()

        assert self.page.balance_total_consumption_label.text() == "-"
        assert self.page.balance_total_production_label.text() == "-"
        assert self.page.balance_self_consumption_label.text() == "-"
        assert self.page.balance_grid_import_label.text() == "-"
        assert self.page.balance_grid_export_label.text() == "-"
        assert self.page.balance_coverage_label.text() == "-"

    def test_update_balance_summary_without_coverage(self):

        self.project.solar.energy_balance = pd.DataFrame(
            {
                "consumption_kwh": [500.0],
                "production_kwh": [400.0],
                "self_consumption_kwh": [300.0],
                "grid_import_kwh": [200.0],
                "grid_export_kwh": [100.0],
            }
        )

        self.project.solar.coverage = None

        self.page.update_balance_summary()

        assert self.page.balance_coverage_label.text() == "-"

    # ==================================================
    # Estadísticas
    # ==================================================

    def test_update_statistics(self):

        self.project.solar.statistics = {
            "period_production": 8000.0,
            "specific_yield": 1000.0,
            "equivalent_hours": 1000.0,
            "capacity_factor": 11.4,
            "coverage_ratio": 60.0,
            "self_consumption_ratio": 7.5,
            "self_sufficiency": 60.0,
            "import_ratio": 40.0,
            "surplus_ratio": 92.5,
            "self_consumption": 600.0,
            "consumption": 1000.0,
            "grid_import": 400.0,
            "grid_export": 7400.0,
        }

        self.page.update_statistics()

        assert (
            self.page.stats_annual_production_label.text()
            == "8,000.00 kWh"
        )

        assert (
            self.page.stats_specific_production_label.text()
            == "1,000.00 kWh/kWp"
        )

        assert (
            self.page.stats_equivalent_hours_label.text()
            == "1,000 h"
        )

        assert (
            self.page.stats_capacity_factor_label.text()
            == "11.4 %"
        )

        assert (
            self.page.stats_coverage_label.text()
            == "60.0 %"
        )

        assert (
            self.page.stats_self_consumption_ratio_label.text()
            == "7.5 %"
        )

        assert (
            self.page.stats_self_sufficiency_ratio_label.text()
            == "60.0 %"
        )

        assert (
            self.page.stats_import_label.text()
            == "400.00 kWh"
        )

        assert (
            self.page.stats_export_label.text()
            == "7,400.00 kWh"
        )

        assert (
            self.page.stats_self_consumption_label.text()
            == "600.00 kWh"
        )

        assert (
            self.page.stats_total_consumption_label.text()
            == "1,000.00 kWh"
        )

    def test_update_statistics_without_statistics(self):

        self.project.solar.statistics = None

        self.page.update_statistics()

        labels = [
            self.page.stats_annual_production_label,
            self.page.stats_specific_production_label,
            self.page.stats_equivalent_hours_label,
            self.page.stats_capacity_factor_label,
            self.page.stats_coverage_label,
            self.page.stats_self_consumption_ratio_label,
            self.page.stats_self_sufficiency_ratio_label,
            self.page.stats_import_label,
            self.page.stats_export_label,
            self.page.stats_self_consumption_label,
            self.page.stats_total_consumption_label,
        ]

        assert all(
            label.text() == "-"
            for label in labels
        )

    # ==================================================
    # Disponibilidad de resultados
    # ==================================================

    def test_set_results_available(self):

        self.page.set_results_available(True)

        assert self.page.tabs.isTabEnabled(
            self.page.tabs.indexOf(
                self.page.balance_tab
            )
        )

        assert self.page.tabs.isTabEnabled(
            self.page.tabs.indexOf(
                self.page.statistics_tab
            )
        )

        self.page.set_results_available(False)

        assert not self.page.tabs.isTabEnabled(
            self.page.tabs.indexOf(
                self.page.balance_tab
            )
        )

        assert not self.page.tabs.isTabEnabled(
            self.page.tabs.indexOf(
                self.page.statistics_tab
            )
        )

    # ==================================================
    # Flujo de cálculo
    # ==================================================

    def test_calculate_production_uses_stored_configuration(self):

        configuration = SolarConfiguration(
            latitude=41.6,
            longitude=2.1,
            tilt=30,
            azimuth=0,
            reference_year=2023,
            losses=14.0,
            pv_technology="crystSi",
            mounting_place="free",
        )

        self.project.solar_configuration = configuration

        self.project.solar.calculate = MagicMock()

        self.page.refresh_production_results = MagicMock()
        self.page.set_results_available = MagicMock()

        self.page.calculate_production()

        self.project.solar.calculate.assert_called_once_with(
            configuration
        )

        self.page.refresh_production_results.assert_called_once_with()

        self.page.set_results_available.assert_called_once_with(
            True
        )

    def test_calculate_production_handles_error(self):

        configuration = self.page.get_configuration()

        self.page.get_configuration = MagicMock(
            return_value=configuration
        )

        self.project.solar.calculate.side_effect = (
            RuntimeError("Error de prueba")
        )

        self.page.calculate_production()

        assert (
            self.page.production_status_label.text()
            == "Error: Error de prueba"
        )

        assert (
            self.page.production_annual_label.text()
            == "-"
        )

        assert (
            self.page.production_specific_label.text()
            == "-"
        )

        assert (
            self.page.production_coverage_label.text()
            == "-"
        )

    # ==================================================
    # Actualización de resultados
    # ==================================================

    def test_refresh_production_results(self):

        self.project.solar.statistics = {
            "period_production": 12000.0,
            "specific_yield": 1500.0,
            "equivalent_hours": 1500.0,
            "capacity_factor": 17.12,
            "coverage_ratio": 65.0,
            "self_consumption_ratio": 80.0,
            "self_sufficiency": 80.0,
            "import_ratio": 20.0,
            "surplus_ratio": 92.0,
            "self_consumption": 80.0,
            "consumption": 100.0,
            "grid_import": 20.0,
            "grid_export": 920.0,
        }

        self.project.solar.annual_production = 12000.0
        self.project.solar.specific_production = 1500.0
        self.project.solar.coverage = 65.0

        self.project.solar.monthly_production = pd.Series(
            [1000.0],
            index=pd.to_datetime(
                ["2025-01-31"]
            ),
        )

        self.project.solar.energy_balance = pd.DataFrame(
            {
                "consumption_kwh": [100.0],
                "production_kwh": [1000.0],
                "self_consumption_kwh": [80.0],
                "grid_import_kwh": [20.0],
                "grid_export_kwh": [920.0],
            },
            index=pd.to_datetime(
                ["2025-01-31"]
            ),
        )

        self.page.refresh_production_results()

        assert (
            self.page.production_annual_label.text()
            == "12,000.0 kWh"
        )

        assert (
            self.page.production_specific_label.text()
            == "1,500.0 kWh/kWp"
        )

        assert (
            self.page.production_coverage_label.text()
            == "65.0 %"
        )

    # ==================================================
    # Reset
    # ==================================================

    def test_reset(self):

        self.controller = getattr(
            self.page,
            "controller",
            None,
        )

        self.page.set_results_available(True)

        if self.controller is not None:
            self.controller.reset()