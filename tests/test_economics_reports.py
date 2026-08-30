import pandas as pd

from unittest.mock import patch

from helios.reports.economics import EconomicsReports
from helios.core.economic_scenarios import EconomicScenarioResult


class TestEconomicsReports:

    def setup_method(self):

        self.reports = EconomicsReports()

    def test_annual_economics_prints_title_and_sections(self):

        cash_flow = pd.DataFrame(
            [
                {
                    "year": 0,
                    "cash_flow": -10000.0,
                    "cumulative_cash_flow": -10000.0,
                },
                {
                    "year": 1,
                    "cash_flow": 2500.0,
                    "cumulative_cash_flow": -7500.0,
                },
            ]
        )

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

            self.reports.annual_economics(
                3000.0,
                1200.0,
                300.0,
                900.0,
                2100.0,
                10000.0,
                4.5,
                cash_flow,
                15000.0,
                0.05,
                0.18,
            )

        printer.title.assert_called_once_with(
            "ECONOMIC ANALYSIS"
        )

        subtitles = [
            call.args[0]
            for call in printer.subtitle.call_args_list
        ]

        assert subtitles == [
            "ANNUAL COST",
            "SAVINGS",
            "INVESTMENT",
            "CASH FLOW",
        ]

    def test_annual_economics_prints_annual_cost_values(self):

        cash_flow = pd.DataFrame(
            [
                {
                    "year": 0,
                    "cash_flow": -10000.0,
                    "cumulative_cash_flow": -10000.0,
                }
            ]
        )

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

            self.reports.annual_economics(
                3000.0,
                1200.0,
                300.0,
                900.0,
                2100.0,
                10000.0,
                4.5,
                cash_flow,
                15000.0,
                0.05,
                0.18,
            )

        printer.value.assert_any_call(
            "Coste anual sin FV",
            3000.0,
            "€",
            decimals=2,
        )

        printer.value.assert_any_call(
            "Coste energía importada con FV",
            1200.0,
            "€",
            decimals=2,
        )

        printer.value.assert_any_call(
            "Ingresos por excedentes",
            300.0,
            "€",
            decimals=2,
        )

        printer.value.assert_any_call(
            "Coste neto con FV",
            900.0,
            "€",
            decimals=2,
        )

    def test_annual_economics_calculates_self_consumption_savings(self):

        cash_flow = pd.DataFrame(
            [
                {
                    "year": 0,
                    "cash_flow": -10000.0,
                    "cumulative_cash_flow": -10000.0,
                }
            ]
        )

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

            self.reports.annual_economics(
                3000.0,
                1200.0,
                300.0,
                900.0,
                2100.0,
                10000.0,
                4.5,
                cash_flow,
                15000.0,
                0.05,
                0.18,
            )

        printer.value.assert_any_call(
            "Ahorro por autoconsumo",
            1800.0,
            "€",
            decimals=2,
        )

        printer.value.assert_any_call(
            "Beneficio por excedentes",
            300.0,
            "€",
            decimals=2,
        )

        printer.value.assert_any_call(
            "Ahorro anual total",
            2100.0,
            "€",
            decimals=2,
        )

    def test_annual_economics_prints_investment_indicators(self):

        cash_flow = pd.DataFrame(
            [
                {
                    "year": 0,
                    "cash_flow": -10000.0,
                    "cumulative_cash_flow": -10000.0,
                }
            ]
        )

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

            self.reports.annual_economics(
                3000.0,
                1200.0,
                300.0,
                900.0,
                2100.0,
                10000.0,
                4.5,
                cash_flow,
                15000.0,
                0.05,
                0.18,
            )

        printer.value.assert_any_call(
            "Inversión neta",
            10000.0,
            "€",
            decimals=2,
        )

        printer.value.assert_any_call(
            "Periodo de amortización",
            4.5,
            "años",
            decimals=2,
        )

        printer.percent.assert_any_call(
            "Tasa de descuento",
            5.0,
        )

        printer.value.assert_any_call(
            "Valor actual neto",
            15000.0,
            "€",
            decimals=2,
        )

        printer.percent.assert_any_call(
            "Tasa interna de retorno",
            18.0,
        )

    def test_annual_economics_prints_cash_flow_header(self):

        cash_flow = pd.DataFrame(
            [
                {
                    "year": 0,
                    "cash_flow": -10000.0,
                    "cumulative_cash_flow": -10000.0,
                }
            ]
        )

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

            self.reports.annual_economics(
                3000.0,
                1200.0,
                300.0,
                900.0,
                2100.0,
                10000.0,
                4.5,
                cash_flow,
                15000.0,
                0.05,
                0.18,
            )

        printer.table_header.assert_called_once_with(
            ["Año", "Flujo", "Acumulado"],
            [10, 18, 22],
            ["right", "right", "right"],
        )

    def test_annual_economics_prints_all_cash_flow_rows(self):

        cash_flow = pd.DataFrame(
            [
                {
                    "year": 0,
                    "cash_flow": -10000.0,
                    "cumulative_cash_flow": -10000.0,
                },
                {
                    "year": 1,
                    "cash_flow": 2500.0,
                    "cumulative_cash_flow": -7500.0,
                },
                {
                    "year": 2,
                    "cash_flow": 2600.0,
                    "cumulative_cash_flow": -4900.0,
                },
            ]
        )

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

            self.reports.annual_economics(
                3000.0,
                1200.0,
                300.0,
                900.0,
                2100.0,
                10000.0,
                4.5,
                cash_flow,
                15000.0,
                0.05,
                0.18,
            )

        assert printer.table_row.call_count == 3

        calls = printer.table_row.call_args_list

        assert calls[0].args == (
            [
                "0",
                "-10000.00 €",
                "-10000.00 €",
            ],
            [10, 18, 22],
            ["right", "right", "right"],
        )

        assert calls[1].args == (
            [
                "1",
                "2500.00 €",
                "-7500.00 €",
            ],
            [10, 18, 22],
            ["right", "right", "right"],
        )

        assert calls[2].args == (
            [
                "2",
                "2600.00 €",
                "-4900.00 €",
            ],
            [10, 18, 22],
            ["right", "right", "right"],
        )

    def test_annual_economics_formats_integer_year(self):

        cash_flow = pd.DataFrame(
            [
                {
                    "year": 1.0,
                    "cash_flow": 1234.567,
                    "cumulative_cash_flow": 2345.678,
                }
            ]
        )

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

            self.reports.annual_economics(
                3000.0,
                1200.0,
                300.0,
                900.0,
                2100.0,
                10000.0,
                4.5,
                cash_flow,
                15000.0,
                0.05,
                0.18,
            )

        printer.table_row.assert_called_once_with(
            [
                "1",
                "1234.57 €",
                "2345.68 €",
            ],
            [10, 18, 22],
            ["right", "right", "right"],
        )

    def test_economic_scenarios_prints_title_and_header(self):

        scenario_results = [
            EconomicScenarioResult(
                name="Base",
                annual_savings=2000.0,
                payback_years=5.0,
                npv=15000.0,
                irr=0.18,
            )
        ]

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

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
                "TIR",
            ],
            [18, 18, 18, 18],
            ["left", "right", "right", "right"],
        )

    def test_economic_scenarios_prints_all_results(self):

        scenario_results = [
            EconomicScenarioResult(
                name="Base",
                annual_savings=2000.0,
                payback_years=5.0,
                npv=15000.0,
                irr=0.18,
            ),
            EconomicScenarioResult(
                name="Optimista",
                annual_savings=2500.0,
                payback_years=4.0,
                npv=22000.0,
                irr=0.23,
            ),
            EconomicScenarioResult(
                name="Pesimista",
                annual_savings=1500.0,
                payback_years=7.0,
                npv=8000.0,
                irr=0.12,
            ),
        ]

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

            self.reports.economic_scenarios(
                scenario_results
            )

        assert printer.table_row.call_count == 3

        calls = printer.table_row.call_args_list

        assert calls[0].args == (
            [
                "Base",
                "5.00 años",
                "15,000.00 €",
                "18.00 %",
            ],
            [18, 18, 18, 18],
            ["left", "right", "right", "right"],
        )

        assert calls[1].args == (
            [
                "Optimista",
                "4.00 años",
                "22,000.00 €",
                "23.00 %",
            ],
            [18, 18, 18, 18],
            ["left", "right", "right", "right"],
        )

        assert calls[2].args == (
            [
                "Pesimista",
                "7.00 años",
                "8,000.00 €",
                "12.00 %",
            ],
            [18, 18, 18, 18],
            ["left", "right", "right", "right"],
        )

    def test_economic_scenarios_with_empty_results(self):

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

            self.reports.economic_scenarios([])

        printer.subtitle.assert_called_once_with(
            "ECONOMIC SCENARIOS"
        )

        printer.table_header.assert_called_once()

        printer.table_row.assert_not_called()