import pandas as pd

import pytest

from helios.reports.solar_report_data import SolarReportData
from helios.reports.solar_report_text import SolarReportText
from helios.reports.battery_report_data import BatteryReportData


class TestSolarReportText:

    @staticmethod
    def _report_data():

        return SolarReportData(
            # ==================================================
            # Installation
            # ==================================================

            calculation_mode="automatic",
            installed_power_kwp=8.1,
            panel_count=15,
            panel_power_wp=540.0,

            # ==================================================
            # Solar production
            # ==================================================

            yearly_production_kwh=12500.0,

            monthly_production=pd.Series(
                [
                    850,
                    1020,
                    1250,
                    1480,
                    1650,
                    1720,
                    1800,
                    1760,
                    1510,
                    1180,
                    920,
                    780,
                ],
                index=pd.date_range(
                    "2025-01-31",
                    periods=12,
                    freq="ME",
                ),
            ),

            specific_production_kwh_kwp=1543.21,

            # ==================================================
            # Solar statistics
            # ==================================================

            productive_hours=4380,
            daily_average_kwh=34.25,
            monthly_average_kwh=1041.67,
            maximum_hourly_production_kwh=7.85,
            capacity_factor_percent=17.62,

            # ==================================================
            # Energy balance
            # ==================================================

            consumption_reference_year=2025,

            monthly_consumption=pd.Series(
                [
                    1600.00,
                    1500.00,
                    1550.00,
                    1580.00,
                    1650.00,
                    1700.00,
                    1720.00,
                    1680.00,
                    1570.00,
                    1600.00,
                    1650.00,
                    1741.72,
                ],
                index=pd.date_range(
                    "2025-01-31",
                    periods=12,
                    freq="ME",
                ),
            ),

            yearly_consumption_kwh=19541.72,
            self_consumption_kwh=8500.0,
            grid_export_kwh=4000.0,
            grid_import_kwh=11041.72,
            self_consumption_rate_percent=43.5,
            self_sufficiency_rate_percent=64.0,

            # ==================================================
            # Economics
            # ==================================================

            cost_without_pv_eur=5000.00,
            grid_import_cost_eur=3000.00,
            export_income_eur=338.00,
            cost_with_pv_eur=2662.00,
            self_consumption_savings_eur=2000.00,

            investment_eur=12490.0,
            yearly_savings_eur=2338.0,
            payback_years=5.34,
            net_present_value_eur=22071.16,
            internal_rate_of_return_percent=18.8,

            # ==================================================
            # Economic assumptions
            # ==================================================

            economic_horizon_years=25,
            first_year_degradation_percent=1.00,
            annual_degradation_percent=0.35,
            annual_electricity_price_growth_percent=2.00,
            annual_export_price_growth_percent=0.00,
            annual_maintenance_cost_eur=150.00,
            annual_maintenance_growth_percent=2.00,
            discount_rate_percent=5.00,

            # ==================================================
            # Economic scenarios
            # ==================================================

            scenario_results=[
                type(
                    "ScenarioResult",
                    (),
                    {
                        "name": "Conservador",
                        "annual_savings": 2000.0,
                        "payback_years": 6.25,
                        "npv": 18000.0,
                        "irr": 0.15,
                    },
                )(),
                type(
                    "ScenarioResult",
                    (),
                    {
                        "name": "Base",
                        "annual_savings": 2338.0,
                        "payback_years": 5.34,
                        "npv": 22071.16,
                        "irr": 0.188,
                    },
                )(),
                type(
                    "ScenarioResult",
                    (),
                    {
                        "name": "Optimista",
                        "annual_savings": 2700.0,
                        "payback_years": 4.63,
                        "npv": 28000.0,
                        "irr": 0.22,
                    },
                )(),
            ],
            battery_recommendations=[
                BatteryReportData(
                    capacity_kwh=5.0,
                    max_charge_power_kw=5.0,
                    max_discharge_power_kw=5.0,
                    annual_consumption_kwh=19541.72,
                    annual_production_kwh=12500.0,
                    annual_surplus_kwh=4000.0,
                    annual_export_kwh=3000.0,
                    annual_grid_import_kwh=8500.0,
                    annual_battery_charge_kwh=1000.0,
                    annual_battery_discharge_kwh=900.0,
                    self_consumption_kwh=9500.0,
                    self_sufficiency_percent=56.0,
                    equivalent_cycles=180.0,
                    annual_cost_with_battery_eur=2400.0,
                    annual_additional_savings_eur=178.97,
                    marginal_recovered_kwh_per_kwh=180.0,
                    incremental_battery_cost_eur=1800.0,
                    incremental_savings_eur=178.97,
                    marginal_savings_per_kwh=35.79,
                    marginal_payback_years=10.06,
                    economic_npv_eur=126.77,
                    economic_irr_percent=6.01,
                    economic_payback_years=12.61,
                    combined_economic_npv_eur=2239.27,
                    combined_economic_irr_percent=6.47,
                    combined_economic_payback_years=12.79,
                ),
                BatteryReportData(
                    capacity_kwh=8.3,
                    max_charge_power_kw=5.0,
                    max_discharge_power_kw=5.0,
                    annual_consumption_kwh=19541.72,
                    annual_production_kwh=12500.0,
                    annual_surplus_kwh=4000.0,
                    annual_export_kwh=2800.0,
                    annual_grid_import_kwh=8300.0,
                    annual_battery_charge_kwh=1200.0,
                    annual_battery_discharge_kwh=1050.0,
                    self_consumption_kwh=9700.0,
                    self_sufficiency_percent=57.5,
                    equivalent_cycles=145.0,
                    annual_cost_with_battery_eur=2300.0,
                    annual_additional_savings_eur=274.00,
                    marginal_recovered_kwh_per_kwh=126.0,
                    incremental_battery_cost_eur=3000.0,
                    incremental_savings_eur=95.03,
                    marginal_savings_per_kwh=28.80,
                    marginal_payback_years=31.57,
                    economic_npv_eur=208.28,
                    economic_irr_percent=6.00,
                    economic_payback_years=12.62,
                    combined_economic_npv_eur=2320.78,
                    combined_economic_irr_percent=6.44,
                    combined_economic_payback_years=12.78,
                ),
                BatteryReportData(
                    capacity_kwh=30.0,
                    max_charge_power_kw=5.0,
                    max_discharge_power_kw=5.0,
                    annual_consumption_kwh=19541.72,
                    annual_production_kwh=12500.0,
                    annual_surplus_kwh=4000.0,
                    annual_export_kwh=1000.0,
                    annual_grid_import_kwh=6500.0,
                    annual_battery_charge_kwh=2500.0,
                    annual_battery_discharge_kwh=1800.0,
                    self_consumption_kwh=11500.0,
                    self_sufficiency_percent=66.0,
                    equivalent_cycles=83.0,
                    annual_cost_with_battery_eur=1900.0,
                    annual_additional_savings_eur=500.0,
                    marginal_recovered_kwh_per_kwh=60.0,
                    incremental_battery_cost_eur=9000.0,
                    incremental_savings_eur=100.0,
                    marginal_savings_per_kwh=3.33,
                    marginal_payback_years=float("inf"),
                    economic_npv_eur=-3707.30,
                    economic_irr_percent=-0.92,
                    economic_payback_years=float("inf"),
                    combined_economic_npv_eur=-1594.80,
                    combined_economic_irr_percent=4.23,
                    combined_economic_payback_years=15.74,
                ),
            ],
        )

    # ==================================================
    # Validation
    # ==================================================

    def test_executive_summary_rejects_none(self):

        with pytest.raises(
            ValueError,
            match="report data is required",
        ):
            SolarReportText.executive_summary(None)

    def test_production_analysis_rejects_none(self):

        with pytest.raises(
            ValueError,
            match="report data is required",
        ):
            SolarReportText.production_analysis(None)

    def test_energy_balance_analysis_rejects_none(self):

        with pytest.raises(
            ValueError,
            match="report data is required",
        ):
            SolarReportText.energy_balance_analysis(None)

    def test_economic_analysis_rejects_none(self):

        with pytest.raises(
            ValueError,
            match="report data is required",
        ):
            SolarReportText.economic_analysis(None)

    def test_scenario_analysis_rejects_none(self):

        with pytest.raises(
            ValueError,
            match="report data is required",
        ):
            SolarReportText.scenario_analysis(None)

    def test_conclusion_rejects_none(self):

        with pytest.raises(
            ValueError,
            match="report data is required",
        ):
            SolarReportText.conclusion(None)

    # ==================================================
    # Executive summary
    # ==================================================

    def test_executive_summary_contains_main_values(self):

        data = self._report_data()

        text = SolarReportText.executive_summary(data)

        assert "8.10 kWp" in text
        assert "12,500 kWh" in text
        assert "64.0 %" in text
        assert "2,338.00 €" in text
        assert "12,490.00 €" in text
        assert "5.34 años" in text
        assert "periodo de recuperación de la inversión" in text
        assert "periodo de retorno" not in text

    # ==================================================
    # Production
    # ==================================================

    def test_production_analysis_contains_main_values(self):

        data = self._report_data()

        text = SolarReportText.production_analysis(data)

        assert "12,500 kWh" in text
        assert "1,543 kWh/kWp" in text
        assert "4,380 horas" in text
        assert "1,042 kWh mensuales" in text
        assert "aprovechamiento razonable" in text

    def test_production_analysis_detects_low_capacity_factor(self):

        data = self._report_data()

        data = SolarReportData(
            **{
                **data.__dict__,
                "capacity_factor_percent": 8.0,
            }
        )

        text = SolarReportText.production_analysis(data)

        assert "aprovechamiento relativamente bajo" in text

    def test_production_analysis_detects_high_capacity_factor(self):

        data = self._report_data()

        data = SolarReportData(
            **{
                **data.__dict__,
                "capacity_factor_percent": 25.0,
            }
        )

        text = SolarReportText.production_analysis(data)

        assert "elevado aprovechamiento" in text

    # ==================================================
    # Energy balance
    # ==================================================

    def test_energy_balance_analysis_contains_main_values(self):

        data = self._report_data()

        text = SolarReportText.energy_balance_analysis(data)

        assert "19,542 kWh" in text
        assert "8,500 kWh" in text
        assert "4,000 kWh" in text
        assert "11,042 kWh" in text
        assert "43.5 %" in text
        assert "64.0 %" in text
        assert "aprovechamiento moderado" in text

    def test_energy_balance_analysis_detects_low_self_consumption(self):

        data = self._report_data()

        data = SolarReportData(
            **{
                **data.__dict__,
                "self_consumption_rate_percent": 20.0,
            }
        )

        text = SolarReportText.energy_balance_analysis(data)

        assert "relativamente baja" in text

    def test_energy_balance_analysis_detects_high_self_consumption(self):

        data = self._report_data()

        data = SolarReportData(
            **{
                **data.__dict__,
                "self_consumption_rate_percent": 70.0,
            }
        )

        text = SolarReportText.energy_balance_analysis(data)

        assert "elevada tasa de autoconsumo" in text

    def test_methodology_analysis_explains_simulation_scope(self):

        data = self._report_data()

        text = SolarReportText.methodology_analysis(data)

        assert (
            "resolución horaria"
            in text
        )

        assert (
            "hipótesis de inversión, degradación"
            in text
        )

        assert (
            "estimación del comportamiento esperado"
            in text
        )

        assert (
            "no como una garantía de resultados futuros"
            in text
        )

    def test_methodology_analysis_contains_reference_year(self):

        data = self._report_data()

        text = SolarReportText.methodology_analysis(data)

        assert (
            "perfil de consumo representativo correspondiente al año 2025"
            in text
        )

        assert "resolución horaria" in text

        assert (
            "hipótesis de inversión, degradación"
            in text
        )

        assert (
            "estimación del comportamiento esperado"
            in text
        )

        assert (
            "no como una garantía de resultados futuros"
            in text
        )

    # ==================================================
    # Economics
    # ==================================================

    def test_economic_analysis_contains_main_values(self):

        data = self._report_data()

        text = SolarReportText.economic_analysis(data)

        assert "12,490.00 €" in text
        assert "2,338.00 €" in text
        assert "5.34 años" in text
        assert "22,071.16 €" in text
        assert "18.80 %" in text
        assert "genera valor" in text
        assert "periodo de recuperación de la inversión" in text
        assert "periodo de retorno" not in text
        assert "tasa de descuento" not in text
        assert "valor del dinero en el tiempo" in text

    def test_economic_analysis_detects_negative_npv(self):

        data = self._report_data()

        data = SolarReportData(
            **{
                **data.__dict__,
                "net_present_value_eur": -500.0,
            }
        )

        text = SolarReportText.economic_analysis(data)

        assert "valor actual neto es negativo" in text

    def test_economic_analysis_detects_zero_npv(self):

        data = self._report_data()

        data = SolarReportData(
            **{
                **data.__dict__,
                "net_present_value_eur": 0.0,
            }
        )

        text = SolarReportText.economic_analysis(data)

        assert "aproximadamente nulo" in text

    def test_economic_analysis_handles_missing_irr(self):

        data = self._report_data()

        data = SolarReportData(
            **{
                **data.__dict__,
                "internal_rate_of_return_percent": None,
            }
        )

        text = SolarReportText.economic_analysis(data)

        assert "No ha sido posible determinar" in text

    # ==================================================
    # Batteries
    # ==================================================

    def test_battery_analysis_contains_main_values(self):

        data = self._report_data()

        text = SolarReportText.battery_analysis(data)

        assert "3 capacidades de batería" in text
        assert "5.0 kWh" in text
        assert "500.00 €" in text
        assert "208.28 €" in text
        assert "ahorro marginal por kWh" in text
        assert "periodo de recuperación marginal" in text
        assert "Economía conjunta FV + batería" not in text

    def test_battery_analysis_handles_empty_results(self):

        data = self._report_data()

        data = SolarReportData(
            **{
                **data.__dict__,
                "battery_recommendations": [],
            }
        )

        text = SolarReportText.battery_analysis(data)

        assert (
            "No se han realizado evaluaciones económicas"
            in text
        )

    # ==================================================
    # Scenarios
    # ==================================================

    def test_scenario_analysis_identifies_best_and_worst(self):

        data = self._report_data()

        text = SolarReportText.scenario_analysis(data)

        assert "Optimista" in text
        assert "28,000.00 €" in text
        assert "Conservador" in text
        assert "18,000.00 €" in text
        assert "periodo de recuperación de la inversión" in text
        assert "periodo de retorno" not in text

    def test_scenario_analysis_handles_empty_results(self):

        data = self._report_data()

        data = SolarReportData(
            **{
                **data.__dict__,
                "scenario_results": [],
            }
        )

        text = SolarReportText.scenario_analysis(data)

        assert (
            "No se han definido escenarios económicos"
            in text
        )

    # ==================================================
    # Conclusion
    # ==================================================

    def test_conclusion_contains_main_values(self):

        data = self._report_data()

        text = SolarReportText.conclusion(data)

        assert "12,500 kWh" in text
        assert "64.0 %" in text
        assert "2,338.00 €" in text
        assert "5.34 años" in text
        assert "El valor actual neto es positivo bajo las hipótesis utilizadas" in text
        assert "periodo de recuperación de la inversión" in text
        assert "periodo de retorno" not in text


    def test_conclusion_detects_negative_npv(self):

        data = self._report_data()

        data = SolarReportData(
            **{
                **data.__dict__,
                "net_present_value_eur": -1000.0,
            }
        )

        text = SolarReportText.conclusion(data)

        assert (
            "El valor actual neto es negativo bajo las hipótesis utilizadas"
            in text
        )

    def test_conclusion_handles_empty_battery_recommendations(self):

        data = self._report_data()

        data = SolarReportData(
            **{
                **data.__dict__,
                "battery_recommendations": [],
            }
        )

        text = SolarReportText.conclusion(data)

        assert text
        assert "batería" not in text.lower()

    # ==================================================
    # Glossary
    # ==================================================

    def test_glossary_uses_user_friendly_economic_terms(self):

        glossary = dict(SolarReportText.glossary())

        assert "Periodo de recuperación de la inversión" in glossary
        assert "Periodo de retorno (Payback)" not in glossary

        assert "Valor del dinero en el tiempo" in glossary
        assert "Tasa de descuento" not in glossary

        assert "No es lo mismo que el IPC" in (
            glossary["Valor del dinero en el tiempo"]
        )

    def test_glossary_contains_battery_terms(self):

        glossary = dict(SolarReportText.glossary())

        assert "Ahorro adicional anual de la batería" in glossary
        assert "Coste incremental de la batería" in glossary
        assert "Ahorro incremental" in glossary
        assert "Ahorro marginal por kWh de batería" in glossary
        assert "Periodo de recuperación marginal" in glossary
        assert "Ciclos equivalentes" in glossary
        assert "VAN de la batería" in glossary
        assert "Economía conjunta FV + batería" in glossary