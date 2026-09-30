from dataclasses import replace

import pandas as pd

import pytest

from helios.reports.solar_report_data import SolarReportData
from helios.reports.solar_report_generator import (
    SolarReportGenerator,
)
from helios.reports.solar_report_charts import SolarReportCharts

from reportlab.platypus import KeepTogether

from helios.solar.battery_recommendation import (
    BatteryRecommendation,
)

class TestSolarReportGenerator:

    @staticmethod
    def _report_data():

        battery_recommendations = [
            BatteryRecommendation(
                capacity_kwh=5.0,
                max_charge_power_kw=8.3,
                max_discharge_power_kw=8.3,
                annual_consumption_kwh=8911.90,
                annual_production_kwh=12003.99,
                annual_surplus_kwh=8626.64,
                annual_export_kwh=7121.49,
                annual_grid_import_kwh=4176.15,
                annual_battery_charge_kwh=1505.15,
                annual_battery_discharge_kwh=1429.89,
                self_consumption_kwh=4735.75,
                self_sufficiency_percent=53.14,
                equivalent_cycles=357.47,
                annual_cost_with_battery_eur=320.86,
                annual_additional_savings_eur=102.38,
                marginal_recovered_kwh_per_kwh=0.0,
                incremental_battery_cost_eur=0.0,
                incremental_savings_eur=0.0,
                marginal_savings_per_kwh=0.0,
                marginal_payback_years=float("inf"),
                economic_npv_eur=260.10,
                economic_irr_percent=6.80,
                economic_payback_years=12.47,
            ),
            BatteryRecommendation(
                capacity_kwh=8.3,
                max_charge_power_kw=8.3,
                max_discharge_power_kw=8.3,
                annual_consumption_kwh=8911.90,
                annual_production_kwh=12003.99,
                annual_surplus_kwh=8626.64,
                annual_export_kwh=6220.50,
                annual_grid_import_kwh=3363.01,
                annual_battery_charge_kwh=2406.14,
                annual_battery_discharge_kwh=2285.83,
                self_consumption_kwh=5548.89,
                self_sufficiency_percent=62.26,
                equivalent_cycles=344.25,
                annual_cost_with_battery_eur=253.45,
                annual_additional_savings_eur=169.79,
                marginal_recovered_kwh_per_kwh=0.0,
                incremental_battery_cost_eur=67.41,
                incremental_savings_eur=67.41,
                marginal_savings_per_kwh=20.43,
                marginal_payback_years=12.22,
                economic_npv_eur=429.40,
                economic_irr_percent=6.79,
                economic_payback_years=12.48,
            ),
            BatteryRecommendation(
                capacity_kwh=16.6,
                max_charge_power_kw=8.3,
                max_discharge_power_kw=8.3,
                annual_consumption_kwh=8911.90,
                annual_production_kwh=12003.99,
                annual_surplus_kwh=8626.64,
                annual_export_kwh=4698.08,
                annual_grid_import_kwh=1989.02,
                annual_battery_charge_kwh=3928.56,
                annual_battery_discharge_kwh=3732.13,
                self_consumption_kwh=6922.88,
                self_sufficiency_percent=77.68,
                equivalent_cycles=281.03,
                annual_cost_with_battery_eur=172.61,
                annual_additional_savings_eur=250.63,
                marginal_recovered_kwh_per_kwh=0.0,
                incremental_battery_cost_eur=80.84,
                incremental_savings_eur=80.84,
                marginal_savings_per_kwh=9.74,
                marginal_payback_years=25.64,
                economic_npv_eur=-451.89,
                economic_irr_percent=4.00,
                economic_payback_years=17.06,
            ),
            BatteryRecommendation(
                capacity_kwh=24.9,
                max_charge_power_kw=8.3,
                max_discharge_power_kw=8.3,
                annual_consumption_kwh=8911.90,
                annual_production_kwh=12003.99,
                annual_surplus_kwh=8626.64,
                annual_export_kwh=4008.33,
                annual_grid_import_kwh=1366.52,
                annual_battery_charge_kwh=4618.31,
                annual_battery_discharge_kwh=4387.40,
                self_consumption_kwh=7495.38,
                self_sufficiency_percent=84.67,
                equivalent_cycles=220.25,
                annual_cost_with_battery_eur=146.01,
                annual_additional_savings_eur=277.23,
                marginal_recovered_kwh_per_kwh=0.0,
                incremental_battery_cost_eur=26.60,
                incremental_savings_eur=26.60,
                marginal_savings_per_kwh=3.20,
                marginal_payback_years=77.93,
                economic_npv_eur=-2132.50,
                economic_irr_percent=1.62,
                economic_payback_years=23.42,
            ),
            BatteryRecommendation(
                capacity_kwh=30.0,
                max_charge_power_kw=8.3,
                max_discharge_power_kw=8.3,
                annual_consumption_kwh=8911.90,
                annual_production_kwh=12003.99,
                annual_surplus_kwh=8626.64,
                annual_export_kwh=3884.71,
                annual_grid_import_kwh=1254.96,
                annual_battery_charge_kwh=4741.92,
                annual_battery_discharge_kwh=4504.83,
                self_consumption_kwh=7627.07,
                self_sufficiency_percent=85.92,
                equivalent_cycles=187.70,
                annual_cost_with_battery_eur=141.57,
                annual_additional_savings_eur=281.67,
                marginal_recovered_kwh_per_kwh=0.0,
                incremental_battery_cost_eur=4.44,
                incremental_savings_eur=4.44,
                marginal_savings_per_kwh=0.87,
                marginal_payback_years=286.50,
                economic_npv_eur=-3340.47,
                economic_irr_percent=0.43,
                economic_payback_years=28.02,
            ),
        ]

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
                ),
            ],
            battery_recommendations=battery_recommendations,
        )

    @staticmethod
    def _manual_report_data():

        return replace(
            TestSolarReportGenerator._report_data(),
            calculation_mode="manual",
            panel_count=None,
            panel_power_wp=None,
            latitude=41.62000,
            longitude=2.09000,
            tilt=30,
            azimuth=0,
            reference_year=2023,
            losses=14.0,
            pv_technology="crystSi",
            mounting_place="building",
        )

    @staticmethod
    def _capture_story(monkeypatch):

        captured = {}

        class FakeDocument:

            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

            def build(self, story, canvasmaker=None):
                captured["story"] = story

        monkeypatch.setattr(
            "helios.reports.solar_report_generator.SimpleDocTemplate",
            FakeDocument,
        )

        return captured

    @staticmethod
    def _story_text(story):

        texts = []

        def collect(flowables):

            for item in flowables:

                if hasattr(item, "text"):
                    texts.append(item.text)

                if hasattr(item, "_cellvalues"):

                    for row in item._cellvalues:

                        for cell in row:

                            if isinstance(cell, str):
                                texts.append(cell)

                            elif hasattr(cell, "text"):
                                texts.append(cell.text)

                if isinstance(item, KeepTogether):
                    collect(item._content)

        collect(story)

        return "\n".join(texts)

    @staticmethod
    def _get_tables(story):

        tables = []

        def collect(flowables):

            for item in flowables:

                if hasattr(item, "_cellvalues"):
                    tables.append(item)

                if isinstance(item, KeepTogether):
                    collect(item._content)

        collect(story)

        return tables

    @staticmethod
    def _get_paragraphs(story):

        paragraphs = []

        def collect(flowables):

            for item in flowables:

                if hasattr(item, "text"):
                    paragraphs.append(item)

                if isinstance(item, KeepTogether):
                    collect(item._content)

        collect(story)

        return paragraphs

    @staticmethod
    def _table_rows(table):

        return [
            [
                cell.text.replace("<br/>", " ").replace(" / ", "/")
                if hasattr(cell, "text")
                else cell
                for cell in row
            ]
            for row in table._cellvalues
        ]

    def test_generate_creates_pdf(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.exists()
        assert output_path.stat().st_size > 0

        with open(output_path, "rb") as file:
            assert file.read(4) == b"%PDF"

    def test_generate_creates_parent_directories(
        self,
        tmp_path,
    ):

        output_path = (
            tmp_path
            / "reports"
            / "solar"
            / "solar_report.pdf"
        )

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.exists()

    def test_generate_overwrites_existing_file(
        self,
        tmp_path,
    ):

        output_path = tmp_path / "solar_report.pdf"

        output_path.write_bytes(b"old content")

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.exists()

        with open(output_path, "rb") as file:
            assert file.read(4) == b"%PDF"

    def test_generate_rejects_none_data(
        self,
        tmp_path,
    ):

        generator = SolarReportGenerator()

        with pytest.raises(
            ValueError,
            match="report data is required",
        ):
            generator.generate(
                None,
                tmp_path / "report.pdf",
            )

    def test_generate_rejects_none_output_path(self):

        generator = SolarReportGenerator()

        with pytest.raises(
            ValueError,
            match="output path is required",
        ):
            generator.generate(
                self._report_data(),
                None,
            )

    def test_generate_does_not_modify_data(
        self,
        tmp_path,
    ):

        data = self._report_data()

        original_monthly = data.monthly_production.copy()

        generator = SolarReportGenerator()

        generator.generate(
            data,
            tmp_path / "solar_report.pdf",
        )

        assert data.monthly_production.equals(
            original_monthly
        )

        assert data.installed_power_kwp == 8.1
        assert data.yearly_production_kwh == 12500.0
        assert data.productive_hours == 4380
        assert data.capacity_factor_percent == 17.62

    def test_report_contains_twelve_tables_including_cover_kpis(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            tmp_path / "report.pdf",
        )

        tables = self._get_tables(
            captured["story"]
        )

        assert len(tables) == 12

    def test_economic_assumptions_table_contains_exact_values(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            tmp_path / "report.pdf",
        )

        tables = self._get_tables(
            captured["story"]
        )

        rows = self._table_rows(tables[6])

        assert rows == [
            ["Hipótesis", "Valor"],
            [
                "Horizonte económico",
                "25 años",
            ],
            [
                "Degradación primer año",
                "1.00 %",
            ],
            [
                "Degradación anual",
                "0.35 %",
            ],
            [
                "Incremento anual precio electricidad",
                "2.00 %",
            ],
            [
                "Incremento anual precio excedentes",
                "0.00 %",
            ],
            [
                "Coste anual de mantenimiento",
                "150.00 €",
            ],
            [
                "Incremento anual del mantenimiento",
                "2.00 %",
            ],
            [
                "Tasa de descuento",
                "5.00 %",
            ],
        ]

    def test_report_tables_have_expected_row_counts(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            tmp_path / "report.pdf",
        )

        tables = self._get_tables(
            captured["story"]
        )

        row_counts = [
            len(table._cellvalues)
            for table in tables
        ]

        assert row_counts == [
            4,   # KPI de portada
            6,   # Instalación
            4,   # Producción
            6,   # Estadísticas
            7,   # Balance
            11,  # Economía
            9,   # Hipótesis económicas
            6,   # Baterías: resultados marginales
            6,   # Baterías: economía
            6,   # Baterías: economía conjunta FV + batería
            4,   # Escenarios
            26,  # Glosario y definiciones
        ]

    def test_report_tables_have_expected_headers(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            tmp_path / "report.pdf",
        )

        tables = self._get_tables(
            captured["story"]
        )

        body_tables = tables[1:]

        headers = [
            [
                cell.text.replace("<br/>", " ").replace(" / ", "/")
                if hasattr(cell, "text")
                else cell
                for cell in table._cellvalues[0]
            ]
            for table in body_tables
        ]

        assert headers == [
            ["Concepto", "Valor"],
            ["Concepto", "Valor"],
            ["Métrica", "Valor"],
            ["Concepto", "Valor"],
            ["Concepto", "Valor"],
            ["Hipótesis", "Valor"],
            [
                "Capacidad",
                "Coste anual",
                "Ahorro adicional",
                "Coste incremental",
                "Ahorro incremental",
                "Ahorro marginal/kWh",
                "Recuperación marginal",
            ],
            [
                "Capacidad",
                "VAN batería",
                "TIR batería",
                "Recuperación económica",
            ],
            [
                "Capacidad",
                "VAN conjunto",
                "TIR conjunta",
                "Recuperación conjunta",
            ],
            [
                "Escenario",
                "Ahorro anual",
                "Payback",
                "VAN",
                "TIR",
            ],
            ["Término", "Definición"],
        ]

    def test_installation_table_contains_exact_values(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            tmp_path / "report.pdf",
        )

        tables = self._get_tables(
            captured["story"]
        )

        rows = self._table_rows(tables[1])

        assert rows == [
            ["Concepto", "Valor"],
            [
                "Potencia instalada",
                "8.10 kWp",
            ],
            [
                "Número de paneles",
                "15",
            ],
            [
                "Potencia por panel",
                "540 Wp",
            ],
            [
                "Tecnología fotovoltaica",
                "Silicio cristalino",
            ],
            [
                "Tipo de montaje",
                "Coplanar a cubierta",
            ],
        ]

    def test_production_table_contains_exact_values(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            tmp_path / "report.pdf",
        )

        tables = self._get_tables(
            captured["story"]
        )

        rows = self._table_rows(tables[2])

        assert rows == [
            ["Concepto", "Valor"],
            [
                "Producción anual",
                "12,500.00 kWh",
            ],
            [
                "Producción específica",
                "1,543.21 kWh/kWp",
            ],
            [
                "Potencia instalada",
                "8.10 kWp",
            ],
        ]

    def test_solar_statistics_table_contains_exact_values(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            tmp_path / "solar_report.pdf",
        )

        tables = self._get_tables(
            captured["story"]
        )

        rows = self._table_rows(tables[3])

        assert rows == [
            ["Métrica", "Valor"],
            [
                "Horas productivas",
                "4,380",
            ],
            [
                "Producción media diaria",
                "34.25 kWh/día",
            ],
            [
                "Producción media mensual",
                "1,041.67 kWh/mes",
            ],
            [
                "Máxima producción horaria",
                "7.85 kWh",
            ],
            [
                "Factor de capacidad",
                "17.62 %",
            ],
        ]

    def test_energy_balance_table_contains_exact_values(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            tmp_path / "solar_report.pdf",
        )

        tables = self._get_tables(
            captured["story"]
        )

        rows = self._table_rows(tables[4])

        assert rows == [
            ["Concepto", "Valor"],
            [
                "Consumo anual",
                "19,541.72 kWh",
            ],
            [
                "Autoconsumo",
                "8,500.00 kWh",
            ],
            [
                "Energía vertida a red",
                "4,000.00 kWh",
            ],
            [
                "Energía importada de red",
                "11,041.72 kWh",
            ],
            [
                "Tasa de autoconsumo",
                "43.50 %",
            ],
            [
                "Tasa de autosuficiencia",
                "64.00 %",
            ],
        ]

    def test_economics_table_contains_exact_values(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            tmp_path / "solar_report.pdf",
        )

        tables = self._get_tables(
            captured["story"]
        )

        rows = self._table_rows(tables[5])

        assert rows == [
            ["Concepto", "Valor"],
            [
                "Coste anual sin FV",
                "5,000.00 €",
            ],
            [
                "Coste energía importada con FV",
                "3,000.00 €",
            ],
            [
                "Ingresos por excedentes",
                "338.00 €",
            ],
            [
                "Coste neto con FV",
                "2,662.00 €",
            ],
            [
                "Ahorro por autoconsumo",
                "2,000.00 €",
            ],
            [
                "Ahorro anual total",
                "2,338.00 €",
            ],
            [
                "Inversión neta",
                "12,490.00 €",
            ],
            [
                "Periodo de retorno",
                "5.34 años",
            ],
            [
                "Valor actual neto (VAN)",
                "22,071.16 €",
            ],
            [
                "Tasa interna de retorno (TIR)",
                "18.80 %",
            ],
        ]

    def test_economic_scenarios_table_contains_exact_values(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            tmp_path / "report.pdf",
        )

        tables = self._get_tables(
            captured["story"]
        )

        rows = self._table_rows(tables[10])

        assert rows == [
            [
                "Escenario",
                "Ahorro anual",
                "Payback",
                "VAN",
                "TIR",
            ],
            [
                "Conservador",
                "2,000.00 €",
                "6.25 años",
                "18,000.00 €",
                "15.00 %",
            ],
            [
                "Base",
                "2,338.00 €",
                "5.34 años",
                "22,071.16 €",
                "18.80 %",
            ],
            [
                "Optimista",
                "2,700.00 €",
                "4.63 años",
                "28,000.00 €",
                "22.00 %",
            ],
        ]

    def test_report_contains_expected_sections(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            tmp_path / "report.pdf",
        )

        text = self._story_text(
            captured["story"]
        )

        assert "Informe de rendimiento solar" in text
        assert "Resumen de la instalación" in text
        assert "Producción solar" in text
        assert "Estadísticas solares" in text
        assert "Consumo y balance energético" in text
        assert "Rentabilidad económica" in text

    def test_report_sections_are_in_expected_order(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            tmp_path / "report.pdf",
        )

        paragraphs = self._get_paragraphs(
            captured["story"]
        )

        paragraph_text = [
            paragraph.text
            for paragraph in paragraphs
        ]

        expected_sections = [
            "Informe de rendimiento solar",
            "Instalación fotovoltaica — 8.10 kWp",
            "Resumen ejecutivo",
            "Resumen de la instalación",
            "Producción solar",
            "Estadísticas solares",
            "Consumo y balance energético",
            "Rentabilidad económica",
            "Hipótesis económicas",
            "Escenarios económicos",
            "Conclusión",
            "Glosario y definiciones",
        ]

        positions = [
            paragraph_text.index(section)
            for section in expected_sections
        ]

        assert positions == sorted(positions)

    def test_report_contains_expected_number_of_section_headings(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            tmp_path / "report.pdf",
        )

        paragraphs = self._get_paragraphs(
            captured["story"]
        )

        section_titles = {
            "Resumen ejecutivo",
            "Resumen de la instalación",
            "Producción solar",
            "Estadísticas solares",
            "Consumo y balance energético",
            "Rentabilidad económica",
            "Hipótesis económicas",
            "Escenarios económicos",
            "Conclusión",
        }

        found = [
            paragraph.text
            for paragraph in paragraphs
            if paragraph.text in section_titles
        ]

        assert found == [
            "Resumen ejecutivo",
            "Resumen de la instalación",
            "Producción solar",
            "Estadísticas solares",
            "Consumo y balance energético",
            "Rentabilidad económica",
            "Hipótesis económicas",
            "Escenarios económicos",
            "Conclusión",
        ]

    def test_report_contains_energy_balance_chart_data(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        balance_called = {}

        def fake_energy_balance(
            yearly_production_kwh,
            yearly_consumption_kwh,
            self_consumption_kwh,
            grid_import_kwh,
            grid_export_kwh,
        ):

            balance_called["yearly_production_kwh"] = (
                yearly_production_kwh
            )
            balance_called["yearly_consumption_kwh"] = (
                yearly_consumption_kwh
            )
            balance_called["self_consumption_kwh"] = (
                self_consumption_kwh
            )
            balance_called["grid_import_kwh"] = (
                grid_import_kwh
            )
            balance_called["grid_export_kwh"] = (
                grid_export_kwh
            )

            return object()

        monkeypatch.setattr(
            SolarReportCharts,
            "energy_balance",
            fake_energy_balance,
        )

        output_path = (
            tmp_path
            / "solar_report.pdf"
        )

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert balance_called == {
            "yearly_production_kwh": 12500.0,
            "yearly_consumption_kwh": 19541.72,
            "self_consumption_kwh": 8500.0,
            "grid_import_kwh": 11041.72,
            "grid_export_kwh": 4000.0,
        }

        assert any(
            item.__class__.__name__ == "object"
            for item in captured["story"]
        )

    def test_report_story_contains_expected_text(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            tmp_path / "report.pdf",
        )

        text = self._story_text(
            captured["story"]
        )

        expected_values = [
            "8.10 kWp",
            "15",
            "540 Wp",
            "12,500.00 kWh",
            "1,543.21 kWh/kWp",
            "4,380",
            "34.25 kWh/día",
            "1,041.67 kWh/mes",
            "7.85 kW",
            "17.62 %",
            "19,541.72 kWh",
            "8,500.00 kWh",
            "4,000.00 kWh",
            "11,041.72 kWh",
            "43.50 %",
            "64.00 %",
            "12,490.00 €",
            "2,338.00 €",
            "5.34 años",
            "22,071.16 €",
            "18.80 %",
        ]

        for value in expected_values:
            assert value in text

    def test_report_contains_economic_scenarios(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            tmp_path / "solar_report.pdf",
        )

        text = self._story_text(
            captured["story"]
        )

        expected_values = [
            "Conservador",
            "Base",
            "Optimista",
            "2,000.00 €",
            "2,338.00 €",
            "2,700.00 €",
            "6.25 años",
            "5.34 años",
            "4.63 años",
            "18,000.00 €",
            "22,071.16 €",
            "28,000.00 €",
            "15.00 %",
            "18.80 %",
            "22.00 %",
        ]

        for value in expected_values:
            assert value in text

    # ==================================================
    # Manual calculation mode
    # ==================================================

    def test_manual_report_creates_pdf(
        self,
        tmp_path,
    ):

        output_path = (
            tmp_path
            / "manual_solar_report.pdf"
        )

        generator = SolarReportGenerator()

        generator.generate(
            self._manual_report_data(),
            output_path,
        )

        assert output_path.exists()
        assert output_path.stat().st_size > 0

        with open(output_path, "rb") as file:
            assert file.read(4) == b"%PDF"

    def test_manual_installation_table_contains_exact_values(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        generator = SolarReportGenerator()

        generator.generate(
            self._manual_report_data(),
            tmp_path / "manual_report.pdf",
        )

        tables = self._get_tables(
            captured["story"]
        )

        rows = self._table_rows(tables[1])

        assert rows == [
            ["Concepto", "Valor"],
            [
                "Potencia instalada",
                "8.10 kWp",
            ],
            [
                "Latitud",
                "41.62000°",
            ],
            [
                "Longitud",
                "2.09000°",
            ],
            [
                "Inclinación",
                "30°",
            ],
            [
                "Azimut",
                "0°",
            ],
            [
                "Año de referencia",
                "2023",
            ],
            [
                "Pérdidas del sistema",
                "14.0 %",
            ],
            [
                "Tecnología fotovoltaica",
                "Silicio cristalino",
            ],
            [
                "Tipo de montaje",
                "Coplanar a cubierta",
            ],
        ]

    def test_manual_installation_table_has_expected_row_count(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        generator = SolarReportGenerator()

        generator.generate(
            self._manual_report_data(),
            tmp_path / "manual_report.pdf",
        )

        tables = self._get_tables(
            captured["story"]
        )

        installation_table = tables[1]

        assert len(
            installation_table._cellvalues
        ) == 10

    def test_manual_installation_does_not_contain_panel_data(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        generator = SolarReportGenerator()

        generator.generate(
            self._manual_report_data(),
            tmp_path / "manual_report.pdf",
        )

        installation_table = self._get_tables(
            captured["story"]
        )[1]

        rows = self._table_rows(
            installation_table
        )

        text = "\n".join(
            cell
            for row in rows
            for cell in row
        )

        assert "Número de paneles" not in text
        assert "Potencia por panel" not in text

    def test_manual_report_contains_pvgis_configuration(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        generator = SolarReportGenerator()

        generator.generate(
            self._manual_report_data(),
            tmp_path / "manual_report.pdf",
        )

        text = self._story_text(
            captured["story"]
        )

        expected_values = [
            "41.62000°",
            "2.09000°",
            "30°",
            "0°",
            "2023",
            "14.0 %",
            "Silicio cristalino",
            "Coplanar a cubierta",
        ]

        for value in expected_values:
            assert value in text

    def test_manual_report_keeps_common_sections(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        generator = SolarReportGenerator()

        generator.generate(
            self._manual_report_data(),
            tmp_path / "manual_report.pdf",
        )

        paragraphs = self._get_paragraphs(
            captured["story"]
        )

        paragraph_text = [
            paragraph.text
            for paragraph in paragraphs
        ]

        expected_sections = [
            "Informe de rendimiento solar",
            "Instalación fotovoltaica — 8.10 kWp",
            "Resumen ejecutivo",
            "La instalación fotovoltaica analizada tiene una potencia instalada de 8.10 kWp y una producción solar estimada de 12,500 kWh anuales. Esta producción permite cubrir directamente 64.0 % del consumo eléctrico anual mediante energía solar. El ahorro económico estimado alcanza 2,338.00 € al año, con una inversión de 12,490.00 € y un periodo de recuperación de la inversión de 5.34 años.",
            "Resumen de la instalación",
            "Producción solar",
            "La instalación genera aproximadamente 12,500 kWh al año, equivalentes a 1,543 kWh/kWp de producción específica. Se registran aproximadamente 4,380 horas productivas al año y una producción media de 1,042 kWh mensuales. El factor de capacidad refleja un nivel de aprovechamiento razonable de la potencia instalada para una instalación fotovoltaica.",
            "Estadísticas solares",
            "Consumo y balance energético",
            "El consumo eléctrico anual asciende a 19,542 kWh. De la producción fotovoltaica, 8,500 kWh se consumen directamente en la instalación, mientras que 4,000 kWh se vierten a la red. La energía importada de la red asciende a 11,042 kWh. La tasa de autoconsumo es del 43.5 % y la autosuficiencia alcanza el 64.0 %. La tasa de autoconsumo muestra un aprovechamiento moderado de la energía generada directamente en la instalación.",
            "Rentabilidad económica",
            "La inversión neta asciende a 12,490.00 € y genera un ahorro anual estimado de 2,338.00 €. El periodo de recuperación de la inversión es de 5.34 años. El valor actual neto alcanza 22,071.16 €. La tasa interna de retorno estimada es del 18.80 %. El valor actual neto es positivo, lo que indica que la inversión genera valor por encima del valor exigido, una vez tenido en cuenta el valor del dinero en el tiempo.",
            "Hipótesis económicas",
            "Evaluación económica de baterías",
            "Se han evaluado 5 capacidades de batería entre 5.0 kWh y 30.0 kWh. La batería permite almacenar parte del excedente fotovoltaico para utilizarlo posteriormente, reduciendo la energía que debe importarse de la red. La capacidad de 30.0 kWh alcanza el mayor ahorro adicional anual, con 281.67 € respecto a la instalación fotovoltaica sin batería. En términos del valor actual neto de la propia batería, la capacidad de 8.3 kWh obtiene 429.40 € bajo las hipótesis económicas utilizadas. 2 de las 5 capacidades evaluadas presentan un valor actual neto de la batería igual o superior a cero. El ahorro marginal por kWh representa el ahorro adicional obtenido por cada kWh de capacidad de batería añadido, mientras que el periodo de recuperación marginal expresa el tiempo estimado necesario para recuperar el coste incremental de esa capacidad mediante el ahorro incremental. Los indicadores económicos conjuntos permiten además analizar el resultado de la inversión fotovoltaica y la batería como un único sistema.",
            "Economía conjunta FV + batería",
            "Escenarios económicos",
            "El análisis de escenarios muestra cómo la rentabilidad de la instalación varía en función de las hipótesis económicas consideradas. En el escenario «Base», el ahorro anual estimado es de 2,338.00 €, con un periodo de recuperación de la inversión de 5.34 años y un VAN de 22,071.16 €. En el escenario «Conservador», el VAN se sitúa en 18,000.00 €, mientras que el escenario «Optimista» alcanza 28,000.00 €. En conjunto, los resultados muestran que la inversión mantiene una rentabilidad positiva bajo las diferentes hipótesis analizadas, aunque su atractivo económico varía según la evolución de los precios de la energía, los costes de mantenimiento y el resto de supuestos considerados.",
            "Conclusión",
            "La instalación fotovoltaica analizada, con una potencia instalada de 8.10 kWp, alcanza una producción solar anual estimada de 12,500 kWh. Esta generación permite cubrir mediante energía solar el 64.0 % del consumo eléctrico anual, reduciendo la dependencia de la red eléctrica.<br/><br/>Desde el punto de vista económico, la instalación genera un ahorro anual estimado de 2,338.00 €, con una inversión neta de 12,490.00 € y un periodo de recuperación de la inversión de 5.34 años. La inversión favorable bajo las hipótesis utilizadas.<br/><br/>También se ha evaluado el almacenamiento mediante 5 capacidades de batería, entre 5.0 y 30.0 kWh. El mayor ahorro adicional anual obtenido en la simulación corresponde a una capacidad de 30.0 kWh, con un ahorro adicional anual de 281.67 €.<br/><br/>Desde el punto de vista económico de la propia batería, la capacidad de 8.3 kWh presenta el mayor valor actual neto, de 429.40 €, con una TIR del 6.79 % y un periodo de recuperación de 12.48 años. En total, 2 de las 5 capacidades evaluadas presentan un valor actual neto de la batería igual o superior a cero.<br/><br/>Estos resultados muestran que aumentar la capacidad de almacenamiento puede incrementar el ahorro anual, pero ese incremento no implica necesariamente una mejora proporcional de la rentabilidad económica de la batería.<br/><br/>En conjunto, los resultados indican que la instalación presenta una capacidad significativa para reducir el coste energético anual y mejorar el grado de autosuficiencia eléctrica del sistema. La valoración final debe entenderse dentro de las hipótesis de producción, consumo, tarifas, degradación y evolución de precios utilizadas en el análisis.",
            "Glosario y definiciones",
        ]

        assert paragraph_text == expected_sections

    def test_manual_report_keeps_common_tables(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        generator = SolarReportGenerator()

        generator.generate(
            self._manual_report_data(),
            tmp_path / "manual_report.pdf",
        )

        tables = self._get_tables(
            captured["story"]
        )

        assert len(tables) == 12

        assert [
            len(table._cellvalues)
            for table in tables
        ] == [
            4,   # KPI de portada
            10,  # Instalación manual
            4,   # Producción
            6,   # Estadísticas
            7,   # Balance
            11,  # Economía
            9,   # Hipótesis económicas
            6,   # Baterías: resultados marginales
            6,   # Baterías: economía
            6,   # Baterías: economía conjunta FV + batería
            4,   # Escenarios
            26,  # Glosario y definiciones
        ]

    def test_invalid_calculation_mode_is_rejected(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        data = replace(
            self._report_data(),
            calculation_mode="invalid",
        )

        generator = SolarReportGenerator()

        with pytest.raises(
            ValueError,
            match="unsupported calculation mode",
        ):
            generator.generate(
                data,
                tmp_path / "invalid_report.pdf",
            )

        assert "story" not in captured

    def test_battery_economic_tables_contain_exact_values(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            tmp_path / "report.pdf",
        )

        tables = self._get_tables(
            captured["story"]
        )

        operational_table = tables[7]
        economic_table = tables[8]
        combined_table = tables[9]

        operational_rows = self._table_rows(
            operational_table
        )

        assert operational_rows == [
            [
                "Capacidad",
                "Coste anual",
                "Ahorro adicional",
                "Coste incremental",
                "Ahorro incremental",
                "Ahorro marginal/kWh",
                "Recuperación marginal",
            ],
            [
                "5.0 kWh",
                "320.86 €",
                "102.38 €",
                "0.00 €",
                "0.00 €",
                "0.00 €/kWh",
                "N/D",
            ],
            [
                "8.3 kWh",
                "253.45 €",
                "169.79 €",
                "67.41 €",
                "67.41 €",
                "20.43 €/kWh",
                "12.22 años",
            ],
            [
                "16.6 kWh",
                "172.61 €",
                "250.63 €",
                "80.84 €",
                "80.84 €",
                "9.74 €/kWh",
                "25.64 años",
            ],
            [
                "24.9 kWh",
                "146.01 €",
                "277.23 €",
                "26.60 €",
                "26.60 €",
                "3.20 €/kWh",
                "77.93 años",
            ],
            [
                "30.0 kWh",
                "141.57 €",
                "281.67 €",
                "4.44 €",
                "4.44 €",
                "0.87 €/kWh",
                "286.50 años",
            ],
        ]
        economic_rows = self._table_rows(
            economic_table
        )

        assert economic_rows == [
            [
                "Capacidad",
                "VAN batería",
                "TIR batería",
                "Recuperación económica",
            ],
            [
                "5.0 kWh",
                "260.10 €",
                "6.80 %",
                "12.47 años",
            ],
            [
                "8.3 kWh",
                "429.40 €",
                "6.79 %",
                "12.48 años",
            ],
            [
                "16.6 kWh",
                "-451.89 €",
                "4.00 %",
                "17.06 años",
            ],
            [
                "24.9 kWh",
                "-2,132.50 €",
                "1.62 %",
                "23.42 años",
            ],
            [
                "30.0 kWh",
                "-3,340.47 €",
                "0.43 %",
                "28.02 años",
            ],
        ]

        combined_rows = self._table_rows(
            combined_table
        )

        print(combined_rows)

    def test_battery_economic_table_formats_infinite_payback_as_not_available(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        data = self._report_data()

        recommendation = data.battery_recommendations[0]

        data.battery_recommendations[0] = replace(
            recommendation,
            marginal_payback_years=float("inf"),
            economic_payback_years=float("inf"),
        )

        generator = SolarReportGenerator()

        generator.generate(
            data,
            tmp_path / "report.pdf",
        )

        tables = self._get_tables(
            captured["story"]
        )

        operational_rows = self._table_rows(
            tables[7]
        )

        economic_rows = self._table_rows(
            tables[8]
        )

        assert operational_rows[1][-1] == "N/D"
        assert economic_rows[1][-1] == "N/D"