from types import SimpleNamespace

import pandas as pd

from helios.reports.solar_report_data import SolarReportData
from helios.reports.solar_report_data_builder import (
    SolarReportDataBuilder,
)


class TestSolarReportDataBuilder:

    @staticmethod
    def create_project():
        solar_configuration = SimpleNamespace(
            latitude=41.62,
            longitude=2.09,
            tilt=30,
            azimuth=0,
            reference_year=2023,
            losses=14,
            pv_technology="crystSi",
            mounting_place="building",
        )

        monthly_production = pd.Series(
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
                "2023-01-01",
                periods=12,
                freq="MS",
            ),
        )

        solar_statistics = {
            "hours": 8760,
            "productive_hours": 4380,
            "period_production": 12500.0,
            "specific_production": 1543.21,
            "daily_average": 34.25,
            "monthly_average": 1041.67,
            "maximum_power": 8.1,
            "capacity_factor": 17.6,
        }

        energy_balance = {
            "consumption_kwh": 19541.72,
            "self_consumption_kwh": 8500.0,
            "grid_export_kwh": 4000.0,
            "grid_import_kwh": 11041.72,
        }

        solar = SimpleNamespace(
            annual_production=12500.0,
            monthly_production=monthly_production,
            specific_production=1543.21,
            statistics=solar_statistics,
            energy_balance=pd.DataFrame(
                energy_balance,
                index=pd.date_range(
                    "2023-01-01",
                    periods=1,
                    freq="D",
                ),
            ),
            installed_power_kwp=8.1,
        )

        economics_configuration = SimpleNamespace(
            installation_cost=12490.0,
            first_year_degradation=0.01,
            annual_degradation=0.0035,
            annual_electricity_price_growth=0.02,
            annual_export_price_growth=0.0,
            annual_maintenance_cost=150.0,
            annual_maintenance_growth=0.02,
            discount_rate=0.05,
        )

        economics_engine = SimpleNamespace(
            cost_without_pv=4676.0,
            grid_import_cost=2338.0,
            export_income=0.0,
            cost_with_pv=2338.0,
            self_consumption_savings=2338.0,
            annual_savings=2338.0,
            net_investment=12490.0,
            payback_years=5.34,
            npv=22071.16,
            irr=0.188,
            scenario_results=[],
        )

        economics = SimpleNamespace(
            configuration=economics_configuration,
            cost_without_pv=economics_engine.cost_without_pv,
            grid_import_cost=economics_engine.grid_import_cost,
            export_income=economics_engine.export_income,
            cost_with_pv=economics_engine.cost_with_pv,
            self_consumption_savings=(
                economics_engine.self_consumption_savings
            ),
            annual_savings=economics_engine.annual_savings,
            net_investment=economics_engine.net_investment,
            payback_years=economics_engine.payback_years,
            npv=economics_engine.npv,
            irr=economics_engine.irr,
            scenario_results=economics_engine.scenario_results,
        )

        sizing_result = SimpleNamespace(
            installed_power_kwp=8.1,
            panel_count=15,
        )

        installation_configuration = SimpleNamespace(
            panel_power_wp=540.0,
        )

        solar.sizing_result = sizing_result
        solar.installation_configuration = (
            installation_configuration
        )

        return SimpleNamespace(
            solar=solar,
            solar_configuration=solar_configuration,
            economics=economics,
        )

    def test_from_project_returns_solar_report_data(self):
        project = self.create_project()

        result = SolarReportDataBuilder.from_project(
            project
        )

        assert isinstance(
            result,
            SolarReportData,
        )

    def test_from_project_maps_solar_configuration(self):
        project = self.create_project()

        result = SolarReportDataBuilder.from_project(
            project
        )

        assert result.latitude == 41.62
        assert result.longitude == 2.09
        assert result.tilt == 30
        assert result.azimuth == 0
        assert result.reference_year == 2023
        assert result.losses == 14
        assert result.pv_technology == "crystSi"
        assert result.mounting_place == "building"

    def test_from_project_maps_installation_data(self):
        project = self.create_project()

        result = SolarReportDataBuilder.from_project(
            project
        )

        assert result.installed_power_kwp == 8.1
        assert result.panel_count == 15
        assert result.panel_power_wp == 540.0

    def test_from_project_maps_production_data(self):
        project = self.create_project()

        result = SolarReportDataBuilder.from_project(
            project
        )

        assert result.yearly_production_kwh == 12500.0
        assert result.specific_production_kwh_kwp == 1543.21
        assert result.productive_hours == 4380
        assert result.daily_average_kwh == 34.25
        assert result.monthly_average_kwh == 1041.67
        assert result.maximum_power_kw == 8.1
        assert result.capacity_factor_percent == 17.6

        assert result.monthly_production.equals(
            project.solar.monthly_production
        )

    def test_from_project_maps_energy_balance(self):
        project = self.create_project()

        result = SolarReportDataBuilder.from_project(
            project
        )

        assert result.yearly_consumption_kwh == 19541.72
        assert result.self_consumption_kwh == 8500.0
        assert result.grid_export_kwh == 4000.0
        assert result.grid_import_kwh == 11041.72

    def test_from_project_maps_economics(self):
        project = self.create_project()

        result = SolarReportDataBuilder.from_project(
            project
        )

        assert result.cost_without_pv_eur == 4676.0
        assert result.grid_import_cost_eur == 2338.0
        assert result.export_income_eur == 0.0
        assert result.cost_with_pv_eur == 2338.0
        assert result.self_consumption_savings_eur == 2338.0
        assert result.investment_eur == 12490.0
        assert result.yearly_savings_eur == 2338.0
        assert result.payback_years == 5.34
        assert result.net_present_value_eur == 22071.16
        assert result.internal_rate_of_return_percent == 0.188

    def test_from_project_maps_economic_configuration(self):
        project = self.create_project()

        result = SolarReportDataBuilder.from_project(
            project
        )

        configuration = project.economics.configuration

        first_year_degradation_percent = float(
            configuration.first_year_degradation
        )

        annual_degradation_percent = float(
            configuration.annual_degradation
        )

        annual_electricity_price_growth_percent = float(
            configuration.annual_electricity_price_growth
        )

        annual_export_price_growth_percent = float(
            configuration.annual_export_price_growth
        )

        annual_maintenance_cost_eur = float(
            configuration.annual_maintenance_cost
        )

        annual_maintenance_growth_percent = float(
            configuration.annual_maintenance_growth
        )

        discount_rate_percent = float(
            configuration.discount_rate
        )

    def test_from_project_uses_25_year_economic_horizon(self):
        project = self.create_project()

        result = SolarReportDataBuilder.from_project(
            project
        )

        assert result.economic_horizon_years == 25

    def test_from_project_maps_calculation_mode(self):
        project = self.create_project()

        result = SolarReportDataBuilder.from_project(
            project
        )

        assert result.calculation_mode == "project"