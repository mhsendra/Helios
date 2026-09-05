import pandas as pd

import pytest

from helios.reports.solar_report_data import SolarReportData
from helios.reports.solar_report_text import SolarReportText


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
            maximum_power_kw=7.85,
            capacity_factor_percent=17.62,

            # ==================================================
            # Energy balance
            # ==================================================

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
    # Scenarios
    # ==================================================

    def test_scenario_analysis_identifies_best_and_worst(self):

        data = self._report_data()

        text = SolarReportText.scenario_analysis(data)

        assert "Optimista" in text
        assert "28,000.00 €" in text
        assert "Conservador" in text
        assert "18,000.00 €" in text

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
        assert "inversión favorable" in text

    def test_conclusion_detects_unfavorable_case(self):

        data = self._report_data()

        data = SolarReportData(
            **{
                **data.__dict__,
                "net_present_value_eur": -1000.0,
            }
        )

        text = SolarReportText.conclusion(data)

        assert "valoración prudente" in text