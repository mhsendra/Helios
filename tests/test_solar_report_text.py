import pandas as pd

import math

import pytest

from dataclasses import replace

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
            economic_analysis_calculated=True,

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
                    economic_analysis_calculated=True,
                    combined_economic_analysis_calculated=True,
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
                    economic_analysis_calculated=True,
                    combined_economic_analysis_calculated=True,
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
                    economic_analysis_calculated=True,
                    combined_economic_analysis_calculated=True,
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
        assert "mayor VAN de batería" in text
        assert "mayor VAN conjunto del sistema FV + batería" in text
        assert "208.28 €" in text

    def test_battery_analysis_includes_savings_breakdown(self):
        data = self._report_data()

        recommendations = list(data.battery_recommendations)

        # La batería de 30 kWh es la que tiene mayor ahorro neto.
        best_index = max(
            range(len(recommendations)),
            key=lambda index: (
                recommendations[index].annual_additional_savings_eur
            ),
        )

        recommendations[best_index] = replace(
            recommendations[best_index],
            annual_import_savings_eur=220.0,
            annual_export_compensation_lost_eur=41.03,
        )

        data = replace(
            data,
            battery_recommendations=recommendations,
        )

        text = SolarReportText.battery_analysis(data)

        assert "220.00 €" in text
        assert "41.03 €" in text
        assert "ahorro neto" in text
        assert "compensación de excedentes no percibida" in text

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

    # ==================================================
    # Section conclusions
    # ==================================================

    def test_energy_situation_conclusion_contains_interpretation(self):

        text = SolarReportText.energy_situation_conclusion(
            self._report_data()
        )

        assert "perfil de consumo de referencia" in text
        assert "autosuficiencia alcanzable" in text
        assert "distribución temporal" in text
        assert "producción fotovoltaica" in text
        assert "19,542 kWh anuales" not in text
        assert "kWh mensuales" not in text

    def test_installation_conclusion_summarizes_configuration(self):

        text = SolarReportText.installation_conclusion(
            self._report_data()
        )

        assert "8.10 kWp" in text
        assert "producción solar" in text
        assert "aprovechamiento energético" in text
        assert "apartados siguientes" in text

        # La cobertura y la coincidencia temporal se analizan
        # en la sección de producción, no aquí.
        assert "64.0 %" not in text
        assert "coincidencia horaria" not in text
        assert "consumo eléctrico de referencia" not in text

    def test_production_conclusion_interprets_annual_generation(
        self,
    ):

        text = SolarReportText.production_conclusion(
            self._report_data()
        )

        assert "12,500 kWh/año" in text
        assert "64.0 %" in text
        assert "autosuficiencia energética" in text
        assert "no siempre coinciden temporalmente" in text
        assert "aprovechar directamente" in text

        # Las medidas de mejora se desarrollan en el balance.
        assert "cargas flexibles" not in text
        assert "almacenarse" not in text

    def test_production_statistics_conclusion_interprets_performance(
        self,
    ):

        text = SolarReportText.production_statistics_conclusion(
            self._report_data()
        )

        assert "estadísticas" in text
        assert "producción anual" in text
        assert "rendimiento de la instalación" in text
        assert "distribuye la generación" in text

        # Las cifras ya aparecen en la tabla y el análisis.
        assert "4,380 horas" not in text
        assert "17.62 %" not in text

    def test_energy_balance_conclusion_identifies_temporal_mismatch(
        self,
    ):

        text = SolarReportText.energy_balance_conclusion(
            self._report_data()
        )

        assert "no siempre coinciden temporalmente" in text
        assert "Desplazar consumos" in text
        assert "incorporar almacenamiento" in text
        assert "perfil horario" in text
        assert "costes" in text

        # Los valores cuantitativos ya aparecen en la tabla,
        # el resumen de flujos y el análisis del balance.
        assert "4,000 kWh" not in text
        assert "11,042 kWh" not in text

    def test_economic_conclusion_summarizes_profitability_without_repeating_values(
        self,
    ):
        text = SolarReportText.economic_conclusion(
            self._report_data()
        )

        assert "VAN positivo" in text
        assert "genera valor" in text
        assert "precios de la electricidad" in text
        assert "costes de mantenimiento" in text
        assert "tasa de descuento" in text
        assert "escenarios económicos" in text

        # Los indicadores numéricos ya se muestran en la tabla
        # y se interpretan en economic_analysis().
        assert "12,490.00 €" not in text
        assert "2,338.00 €" not in text
        assert "5.34 años" not in text

    def test_scenario_conclusion_interprets_sensitivity_without_repeating_values(
        self,
    ):
        text = SolarReportText.scenario_conclusion(
            self._report_data()
        )

        assert "Todos los escenarios evaluados presentan un VAN positivo" in text
        assert "rentabilidad" in text
        assert "sensibilidad de la inversión" in text
        assert "no garantías de resultados futuros" in text

        # Los valores concretos ya figuran en la tabla de escenarios.
        assert "18,000.00 €" not in text
        assert "28,000.00 €" not in text

    def test_battery_conclusion_recommends_highest_positive_npv(self):
        text = SolarReportText.battery_conclusion(
            self._report_data()
        )

        assert "mayor VAN positivo" in text
        assert "constituye la recomendación económica" in text
        assert "recuperación económica estimada" in text

    def test_methodology_conclusion_defines_interpretation_scope(self):
        text = SolarReportText.methodology_conclusion(
            self._report_data()
        )

        assert "resultados reales pueden diferir" in text
        assert "variaciones meteorológicas" in text
        assert "hábitos de consumo" in text
        assert "precios de la electricidad" in text
        assert "condiciones concretas de la instalación" in text
        assert "hipótesis económicas" in text

    def test_final_recommendation_recommends_positive_npv_installation(self):

        text = SolarReportText.final_recommendation(
            self._report_data()
        )

        assert "<b>Recomendación final</b>" in text
        assert "Se recomienda la instalación fotovoltaica" in text
        assert "63.98 %" not in text
        assert "64.0 %" in text
        assert "63.9 %" not in text
        assert "63.99 %" not in text
        assert "63.9 %" not in text
        assert "valor actual neto es positivo" in text
        assert "12,500 kWh" in text
        assert "producción anual" in text
        assert "gestión temporal de la energía" in text

    def test_final_recommendation_detects_negative_npv(self):

        data = self._report_data()

        data = SolarReportData(
            **{
                **data.__dict__,
                "net_present_value_eur": -1000.0,
            }
        )

        text = SolarReportText.final_recommendation(data)

        assert "No se recomienda ejecutar la instalación" in text
        assert "valor actual neto es negativo" in text


    def test_final_recommendation_detects_zero_npv(self):

        data = self._report_data()

        data = SolarReportData(
            **{
                **data.__dict__,
                "net_present_value_eur": 0.0,
            }
        )

        text = SolarReportText.final_recommendation(data)

        assert "punto de equilibrio" in text
        assert "La decisión de ejecutar la instalación requiere" in text


    def test_final_recommendation_recommends_positive_npv_installation(self):

        text = SolarReportText.final_recommendation(
            self._report_data()
        )

        assert "<b>Recomendación final</b>" in text
        assert "Se recomienda la instalación fotovoltaica" in text
        assert "64.0 %" in text
        assert "valor actual neto es positivo" in text
        assert "12,500 kWh" in text
        assert "gestión temporal de la energía" in text

    def test_quick_diagnostic_identifies_energy_opportunity(self):

        text = SolarReportText.quick_diagnostic(
            self._report_data()
        )

        assert "producción anual" in text
        assert "consumo anual de referencia" in text
        assert "producción anual cubre aproximadamente" in text
        assert "almacenamiento" in text

    def test_quick_diagnostic_rejects_none(self):

        with pytest.raises(
            ValueError,
            match="report data is required",
        ):
            SolarReportText.quick_diagnostic(None)

    def test_energy_flow_summary_contains_generation_distribution(self):

        text = SolarReportText.energy_flow_summary(
            self._report_data()
        )

        assert "12,500 kWh" in text
        assert "8,500 kWh" in text
        assert "4,000 kWh" in text
        assert "11,042 kWh" in text
        assert "68.0 %" in text
        assert "32.0 %" in text

    def test_energy_flow_summary_rejects_none(self):

        with pytest.raises(
            ValueError,
            match="report data is required",
        ):
            SolarReportText.energy_flow_summary(None)

    def test_battery_analysis_handles_different_economic_optima(self):
        data = self._report_data()
        recommendations = list(data.battery_recommendations)

        recommendations[-1] = replace(
            recommendations[-1],
            combined_economic_npv_eur=3000.0,
        )

        data = replace(
            data,
            battery_recommendations=recommendations,
        )

        text = SolarReportText.battery_analysis(data)

        assert "mayor VAN de batería" in text
        assert "30.0 kWh" in text
        assert "mayor VAN conjunto del sistema FV + batería" in text
        assert "3,000.00 €" in text
        assert "Ambos indicadores deben considerarse conjuntamente" in text

    def test_battery_analysis_handles_different_economic_optima(self):
        data = self._report_data()
        recommendations = list(data.battery_recommendations)

        recommendations[-1] = replace(
            recommendations[-1],
            combined_economic_npv_eur=3000.0,
        )

        data = replace(
            data,
            battery_recommendations=recommendations,
        )

        text = SolarReportText.battery_analysis(data)

        assert "mayor VAN de batería" in text
        assert "30.0 kWh" in text
        assert "mayor VAN conjunto del sistema FV + batería" in text
        assert "3,000.00 €" in text
        assert "Ambos indicadores deben considerarse conjuntamente" in text

    def _report_data_without_economic_analysis(self):
        """Devuelve datos de informe con el análisis económico pendiente."""
        from dataclasses import replace

        data = self._report_data()

        return replace(
            data,
            economic_analysis_calculated=False,
            net_present_value_eur=5000.0,
            internal_rate_of_return_percent=12.5,
            payback_years=7.5,
        )

    def test_executive_recommendation_does_not_recommend_pv_without_economics(
        self,
    ):
        data = self._report_data_without_economic_analysis()

        text = SolarReportText.executive_recommendation(data)

        assert (
            "no puede establecerse una recomendación económica"
            in text.lower()
        )
        assert "La instalación fotovoltaica es recomendable" not in text
        assert "no resulta rentable" not in text

    def test_executive_summary_does_not_present_payback_without_economics(
        self,
    ):
        data = self._report_data_without_economic_analysis()

        text = SolarReportText.executive_summary(data)

        assert "no se ha calculado" in text
        assert "7.50 años" not in text

    def test_quick_diagnostic_does_not_interpret_npv_without_economics(
        self,
    ):
        data = self._report_data_without_economic_analysis()

        text = SolarReportText.quick_diagnostic(data)

        assert "no se ha calculado" in text
        assert "VAN positivo" not in text
        assert "VAN negativo" not in text
        assert "VAN aproximadamente nulo" not in text

    def test_economic_analysis_does_not_show_indicators_without_economics(
        self,
    ):
        data = self._report_data_without_economic_analysis()

        text = SolarReportText.economic_analysis(data)

        assert "no se ha calculado" in text
        assert "5,000.00 €" not in text
        assert "12.50 %" not in text
        assert "7.50 años" not in text

    def test_economic_conclusion_does_not_interpret_npv_without_economics(
        self,
    ):
        data = self._report_data_without_economic_analysis()

        text = SolarReportText.economic_conclusion(data)

        assert "no se ha calculado" in text
        assert "VAN resulta positivo" not in text
        assert "VAN resulta negativo" not in text
        assert "7.50 años" not in text

    def test_scenario_conclusion_does_not_show_scenario_npvs_without_economics(
        self,
    ):
        from dataclasses import replace

        data = self._report_data_without_economic_analysis()

        data = replace(
            data,
            scenario_results=(),
        )

        text = SolarReportText.scenario_conclusion(data)

        assert "no se ha calculado" in text
        assert "intervalo de VAN" not in text

    def test_final_recommendation_mentions_future_16_6_kwh_battery_when_combined_npv_is_within_one_percent(
        self,
    ):
        data = self._report_data()

        recommendations = [
            replace(
                battery,
                combined_economic_npv_eur=500.0,
                combined_economic_analysis_calculated=True,
            )
            for battery in data.battery_recommendations
        ]

        battery_16_6 = replace(
            recommendations[1],
            capacity_kwh=16.6,
            incremental_battery_cost_eur=1800.0,
            combined_economic_npv_eur=-0.39,
            combined_economic_analysis_calculated=True,
        )

        recommendations.append(battery_16_6)

        data = replace(
            data,
            battery_recommendations=recommendations,
            economic_analysis_calculated=True,
        )

        text = SolarReportText.final_recommendation(data)

        assert "Escenario de incremento futuro del consumo" in text
        assert (
            "no constituye una recomendación de ampliación inmediata"
            in text
        )


    def test_final_recommendation_uses_total_pv_and_battery_investment_for_one_percent_margin(
        self,
    ):
        data = self._report_data()

        recommendations = [
            replace(
                battery,
                combined_economic_npv_eur=500.0,
                combined_economic_analysis_calculated=True,
            )
            for battery in data.battery_recommendations
        ]

        battery_16_6 = replace(
            recommendations[1],
            capacity_kwh=16.6,
            incremental_battery_cost_eur=1800.0,
            combined_economic_npv_eur=142.0,
            combined_economic_analysis_calculated=True,
        )

        recommendations.append(battery_16_6)

        data = replace(
            data,
            battery_recommendations=recommendations,
            economic_analysis_calculated=True,
        )

        text = SolarReportText.final_recommendation(data)

        # Inversión total: 12.490 € + 1.800 € = 14.290 €.
        # El margen del 1 % es 142,90 €.
        # El VAN conjunto de 142 € está dentro de ese margen.
        assert "Escenario de incremento futuro del consumo" in text

    def test_final_recommendation_does_not_mention_future_battery_when_all_combined_npvs_are_outside_margin(
        self,
    ):
        data = self._report_data()

        recommendations = [
            replace(
                battery,
                combined_economic_npv_eur=500.0,
                combined_economic_analysis_calculated=True,
            )
            for battery in data.battery_recommendations
        ]

        data = replace(
            data,
            battery_recommendations=recommendations,
            economic_analysis_calculated=True,
        )

        text = SolarReportText.final_recommendation(data)

        assert "Escenario de incremento futuro del consumo" not in text
        assert "16,6 kWh" not in text

    def test_final_recommendation_uses_total_pv_and_battery_investment_for_one_percent_margin(
        self,
    ):
        data = self._report_data()

        recommendations = [
            replace(
                battery,
                combined_economic_npv_eur=500.0,
                combined_economic_analysis_calculated=True,
            )
            for battery in data.battery_recommendations
        ]

        battery_16_6 = replace(
            recommendations[1],
            capacity_kwh=16.6,
            incremental_battery_cost_eur=1800.0,
            combined_economic_npv_eur=142.0,
            combined_economic_analysis_calculated=True,
        )

        recommendations.append(battery_16_6)

        data = replace(
            data,
            battery_recommendations=recommendations,
            economic_analysis_calculated=True,
        )

        text = SolarReportText.final_recommendation(data)

        # 12.490 € + 1.800 € = 14.290 €.
        # El 1 % de 14.290 € son 142,90 €.
        # Un VAN conjunto de 142 € debe quedar dentro del margen.
        assert "Escenario de incremento futuro del consumo" in text

    def test_final_recommendation_does_not_use_standalone_battery_npv_for_future_scenario(
        self,
    ):
        data = self._report_data()

        recommendations = [
            replace(
                battery,
                economic_npv_eur=0.0,
                combined_economic_npv_eur=500.0,
                combined_economic_analysis_calculated=True,
            )
            for battery in data.battery_recommendations
        ]

        data = replace(
            data,
            battery_recommendations=recommendations,
            economic_analysis_calculated=True,
        )

        text = SolarReportText.final_recommendation(data)

        assert "Escenario de incremento futuro del consumo" not in text

    def test_final_recommendation_does_not_show_future_battery_without_combined_economics(
        self,
    ):
        data = self._report_data()

        recommendations = [
            replace(
                battery,
                combined_economic_npv_eur=-0.39,
                combined_economic_analysis_calculated=False,
            )
            for battery in data.battery_recommendations
        ]

        data = replace(
            data,
            battery_recommendations=recommendations,
            economic_analysis_calculated=True,
        )

        text = SolarReportText.final_recommendation(data)

        assert "Escenario de incremento futuro del consumo" not in text
        assert "16,6 kWh" not in text

    def test_battery_conclusion_recommends_capacity_with_best_combined_npv(
        self,
    ):
        data = self._report_data()

        text = SolarReportText.battery_conclusion(data)

        assert "mayor VAN positivo de batería" in text
        assert "mayor VAN conjunto FV + batería" in text
        assert "constituye la opción recomendada" in text
        assert "208.28 €" in text
        assert "2,320.78 €" in text

    def test_battery_conclusion_distinguishes_different_economic_optima(
        self,
    ):
        data = self._report_data()
        recommendations = list(data.battery_recommendations)

        recommendations[0] = replace(
            recommendations[0],
            economic_npv_eur=500.0,
            combined_economic_npv_eur=1000.0,
        )
        recommendations[1] = replace(
            recommendations[1],
            economic_npv_eur=208.28,
            combined_economic_npv_eur=2000.0,
        )

        data = replace(
            data,
            battery_recommendations=recommendations,
        )

        text = SolarReportText.battery_conclusion(data)

        assert "mayor VAN positivo de batería" in text
        assert "difiere de la que maximiza el VAN incremental" in text
        assert "priorizar el resultado conjunto" in text
