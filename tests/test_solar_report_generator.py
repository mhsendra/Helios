from dataclasses import replace

import pandas as pd

import pytest

from helios.reports.solar_report_data import SolarReportData
from helios.reports.solar_report_generator import (
    SolarReportGenerator,
)
from helios.reports.solar_report_charts import SolarReportCharts


class TestSolarReportGenerator:

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

            def build(self, story):
                captured["story"] = story

        monkeypatch.setattr(
            "helios.reports.solar_report_generator.SimpleDocTemplate",
            FakeDocument,
        )

        return captured

    @staticmethod
    def _story_text(story):

        texts = []

        for item in story:

            if hasattr(item, "text"):
                texts.append(item.text)

            if hasattr(item, "_cellvalues"):

                for row in item._cellvalues:

                    for cell in row:

                        if isinstance(cell, str):
                            texts.append(cell)

                        elif hasattr(cell, "text"):
                            texts.append(cell.text)

        return "\n".join(texts)

    @staticmethod
    def _get_tables(story):

        return [
            item
            for item in story
            if hasattr(item, "_cellvalues")
        ]

    @staticmethod
    def _get_paragraphs(story):

        return [
            item
            for item in story
            if hasattr(item, "text")
        ]

    @staticmethod
    def _table_rows(table):

        return [
            [
                cell.text
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
            tmp_path / "report.pdf",
        )

        assert data.monthly_production.equals(
            original_monthly
        )

        assert data.installed_power_kwp == 8.1
        assert data.yearly_production_kwh == 12500.0
        assert data.productive_hours == 4380
        assert data.capacity_factor_percent == 17.62

    def test_report_contains_seven_main_tables(
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

        assert len(tables) == 7

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

        rows = self._table_rows(tables[5])

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
            4,
            4,
            6,
            7,
            11,
            9,
            4,
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

        headers = [
            table._cellvalues[0]
            for table in tables
        ]

        assert headers == [
            ["Concepto", "Valor"],
            ["Concepto", "Valor"],
            ["Métrica", "Valor"],
            ["Concepto", "Valor"],
            ["Concepto", "Valor"],
            ["Hipótesis", "Valor"],
            [
                "Escenario",
                "Ahorro anual",
                "Payback",
                "VAN",
                "TIR",
            ],
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

        rows = self._table_rows(tables[0])

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

        rows = self._table_rows(tables[1])

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
            tmp_path / "report.pdf",
        )

        tables = self._get_tables(
            captured["story"]
        )

        rows = self._table_rows(tables[2])

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
                "7.85 kW",
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
            tmp_path / "report.pdf",
        )

        tables = self._get_tables(
            captured["story"]
        )

        rows = self._table_rows(tables[3])

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
            tmp_path / "report.pdf",
        )

        tables = self._get_tables(
            captured["story"]
        )

        rows = self._table_rows(tables[4])

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

        rows = self._table_rows(tables[6])

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

        assert "Informe solar" in text
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
            "Informe solar",
            "Resumen de la instalación",
            "Producción solar",
            "Estadísticas solares",
            "Consumo y balance energético",
            "Rentabilidad económica",
            "Escenarios económicos",
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
            "Informe solar",
            "Resumen de la instalación",
            "Producción solar",
            "Estadísticas solares",
            "Consumo y balance energético",
            "Rentabilidad económica",
            "Escenarios económicos",
        }

        found = [
            paragraph.text
            for paragraph in paragraphs
            if paragraph.text in section_titles
        ]

        assert found == [
            "Informe solar",
            "Resumen de la instalación",
            "Producción solar",
            "Estadísticas solares",
            "Consumo y balance energético",
            "Rentabilidad económica",
            "Escenarios económicos",
        ]

    def test_report_contains_chart_data(
        self,
        monkeypatch,
        tmp_path,
    ):

        captured = self._capture_story(monkeypatch)

        yearly_called = {}
        monthly_called = {}

        def fake_yearly_chart(value):

            yearly_called["value"] = value

            return object()

        def fake_monthly_chart(value):

            monthly_called["value"] = value

            return object()

        monkeypatch.setattr(
            SolarReportCharts,
            "yearly_production",
            fake_yearly_chart,
        )

        monkeypatch.setattr(
            SolarReportCharts,
            "monthly_production",
            fake_monthly_chart,
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

        assert yearly_called["value"] == 12500.0

        pd.testing.assert_series_equal(
            monthly_called["value"],
            self._report_data().monthly_production,
        )

        assert "story" in captured

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
            tmp_path / "report.pdf",
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

        rows = self._table_rows(tables[0])

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
                "Tecnología FV",
                "crystSi",
            ],
            [
                "Tipo de montaje",
                "building",
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

        installation_table = tables[0]

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
        )[0]

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
            "crystSi",
            "building",
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
            "Informe solar",
            "Resumen de la instalación",
            "Producción solar",
            "Estadísticas solares",
            "Consumo y balance energético",
            "Rentabilidad económica",
            "Hipótesis económicas",
            "Escenarios económicos",
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

        assert len(tables) == 7

        assert [
            len(table._cellvalues)
            for table in tables
        ] == [
            10,
            4,
            6,
            7,
            11,
            9,
            4,
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