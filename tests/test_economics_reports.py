from unittest.mock import patch

import pandas as pd

from helios.reports.economics import EconomicsReports


class TestEconomicsReports:

    def setup_method(self):
        self.reports = EconomicsReports()

    def test_annual_economics_prints_annual_cost(self):

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

            cash_flow = pd.DataFrame(
                {
                    "year": [0],
                    "cash_flow": [-10000.0],
                    "cumulative_cash_flow": [-10000.0],
                }
            )

            self.reports.annual_economics(
                cost_without_pv=2000.0,
                grid_import_cost=1200.0,
                export_income=300.0,
                cost_with_pv=900.0,
                annual_savings=1100.0,
                net_investment=10000.0,
                payback_years=5.0,
                cash_flow=cash_flow,
                npv=5000.0,
                discount_rate=0.05,
                irr=0.15,
            )

            printer.title.assert_called_once_with(
                "ECONOMIC ANALYSIS"
            )

            printer.subtitle.assert_any_call(
                "ANNUAL COST"
            )

            printer.value.assert_any_call(
                "Coste anual sin FV",
                2000.0,
                "€",
                decimals=2
            )

            printer.value.assert_any_call(
                "Coste energía importada con FV",
                1200.0,
                "€",
                decimals=2
            )

            printer.value.assert_any_call(
                "Ingresos por excedentes",
                300.0,
                "€",
                decimals=2
            )

            printer.value.assert_any_call(
                "Coste neto con FV",
                900.0,
                "€",
                decimals=2
            )

    def test_annual_economics_calculates_self_consumption_savings(self):

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

            cash_flow = pd.DataFrame(
                {
                    "year": [0],
                    "cash_flow": [-10000.0],
                    "cumulative_cash_flow": [-10000.0],
                }
            )

            self.reports.annual_economics(
                cost_without_pv=2000.0,
                grid_import_cost=1200.0,
                export_income=300.0,
                cost_with_pv=900.0,
                annual_savings=1100.0,
                net_investment=10000.0,
                payback_years=5.0,
                cash_flow=cash_flow,
                npv=5000.0,
                discount_rate=0.05,
                irr=0.15,
            )

            printer.value.assert_any_call(
                "Ahorro por autoconsumo",
                800.0,
                "€",
                decimals=2
            )

            printer.value.assert_any_call(
                "Beneficio por excedentes",
                300.0,
                "€",
                decimals=2
            )

            printer.value.assert_any_call(
                "Ahorro anual total",
                1100.0,
                "€",
                decimals=2
            )

    def test_annual_economics_prints_investment_indicators(self):

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

            cash_flow = pd.DataFrame(
                {
                    "year": [0],
                    "cash_flow": [-10000.0],
                    "cumulative_cash_flow": [-10000.0],
                }
            )

            self.reports.annual_economics(
                cost_without_pv=2000.0,
                grid_import_cost=1200.0,
                export_income=300.0,
                cost_with_pv=900.0,
                annual_savings=1100.0,
                net_investment=10000.0,
                payback_years=5.34,
                cash_flow=cash_flow,
                npv=5000.0,
                discount_rate=0.05,
                irr=0.188,
            )

            printer.value.assert_any_call(
                "Inversión neta",
                10000.0,
                "€",
                decimals=2
            )

            printer.value.assert_any_call(
                "Periodo de amortización",
                5.34,
                "años",
                decimals=2
            )

            printer.percent.assert_any_call(
                "Tasa de descuento",
                5.0,
            )

            printer.value.assert_any_call(
                "Valor actual neto",
                5000.0,
                "€",
                decimals=2
            )

            printer.percent.assert_any_call(
                "Tasa interna de retorno",
                18.8,
            )

    def test_annual_economics_prints_cash_flow(self):

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

            cash_flow = pd.DataFrame(
                {
                    "year": [0, 1, 2],
                    "cash_flow": [
                        -10000.0,
                        2300.50,
                        2350.75,
                    ],
                    "cumulative_cash_flow": [
                        -10000.0,
                        -7699.50,
                        -5348.75,
                    ],
                }
            )

            self.reports.annual_economics(
                cost_without_pv=2000.0,
                grid_import_cost=1200.0,
                export_income=300.0,
                cost_with_pv=900.0,
                annual_savings=1100.0,
                net_investment=10000.0,
                payback_years=5.0,
                cash_flow=cash_flow,
                npv=5000.0,
                discount_rate=0.05,
                irr=0.15,
            )

            assert printer.table_row.call_count == 3

            printer.table_row.assert_any_call(
                [
                    "0",
                    "-10000.00 €",
                    "-10000.00 €",
                ],
                [10, 18, 22],
                ["right", "right", "right"]
            )

            printer.table_row.assert_any_call(
                [
                    "1",
                    "2300.50 €",
                    "-7699.50 €",
                ],
                [10, 18, 22],
                ["right", "right", "right"]
            )

            printer.table_row.assert_any_call(
                [
                    "2",
                    "2350.75 €",
                    "-5348.75 €",
                ],
                [10, 18, 22],
                ["right", "right", "right"]
            )

    def test_economic_scenarios(self):

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

            class ScenarioResult:

                def __init__(
                    self,
                    name,
                    payback_years,
                    npv,
                    irr
                ):
                    self.name = name
                    self.payback_years = payback_years
                    self.npv = npv
                    self.irr = irr

            scenario_results = [
                ScenarioResult(
                    "Base",
                    5.34,
                    22071.16,
                    0.188
                ),
                ScenarioResult(
                    "Optimista",
                    4.50,
                    30000.00,
                    0.22
                ),
            ]

            self.reports.economic_scenarios(
                scenario_results
            )

            printer.subtitle.assert_called_once_with(
                "ECONOMIC SCENARIOS"
            )

            printer.table_header.assert_called_once_with(
                [
                    "Escenario",
                    "Payback",
                    "VAN",
                    "TIR"
                ],
                [18, 18, 18, 18],
                ["left", "right", "right", "right"]
            )

            assert printer.table_row.call_count == 2

            printer.table_row.assert_any_call(
                [
                    "Base",
                    "5.34 años",
                    "22,071.16 €",
                    "18.80 %",
                ],
                [18, 18, 18, 18],
                ["left", "right", "right", "right"]
            )

            printer.table_row.assert_any_call(
                [
                    "Optimista",
                    "4.50 años",
                    "30,000.00 €",
                    "22.00 %",
                ],
                [18, 18, 18, 18],
                ["left", "right", "right", "right"]
            )