from unittest.mock import patch, call

import pandas as pd

from helios.reports.economics import EconomicsReports


class TestEconomicsReports:

    def setup_method(self):

        self.reports = EconomicsReports()

    # ==================================================
    # annual_economics
    # ==================================================

    def _annual_economics_kwargs(
        self,
        cash_flow
    ):

        return {
            "cost_without_pv": 2000.0,
            "grid_import_cost": 1200.0,
            "export_income": 300.0,
            "cost_with_pv": 900.0,
            "annual_savings": 1100.0,
            "net_investment": 10000.0,
            "payback_years": 5.34,
            "cash_flow": cash_flow,
            "npv": 5000.0,
            "discount_rate": 0.05,
            "irr": 0.188,
        }

    def test_annual_economics_sections(self):

        cash_flow = pd.DataFrame(
            {
                "year": [0],
                "cash_flow": [-10000.0],
                "cumulative_cash_flow": [-10000.0],
            }
        )

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

            result = self.reports.annual_economics(
                **self._annual_economics_kwargs(
                    cash_flow
                )
            )

        assert result is None

        printer.title.assert_called_once_with(
            "ECONOMIC ANALYSIS"
        )

        assert printer.subtitle.call_args_list == [
            call("ANNUAL COST"),
            call("SAVINGS"),
            call("INVESTMENT"),
            call("CASH FLOW"),
        ]

        assert printer.blank.call_count == 8

    def test_annual_economics_prints_annual_cost(self):

        cash_flow = pd.DataFrame(
            {
                "year": [0],
                "cash_flow": [-10000.0],
                "cumulative_cash_flow": [-10000.0],
            }
        )

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

            self.reports.annual_economics(
                **self._annual_economics_kwargs(
                    cash_flow
                )
            )

        assert printer.value.call_args_list[:4] == [
            call(
                "Coste anual sin FV",
                2000.0,
                "€",
                decimals=2
            ),
            call(
                "Coste energía importada con FV",
                1200.0,
                "€",
                decimals=2
            ),
            call(
                "Ingresos por excedentes",
                300.0,
                "€",
                decimals=2
            ),
            call(
                "Coste neto con FV",
                900.0,
                "€",
                decimals=2
            ),
        ]

    def test_annual_economics_calculates_self_consumption_savings(
        self
    ):

        cash_flow = pd.DataFrame(
            {
                "year": [0],
                "cash_flow": [-10000.0],
                "cumulative_cash_flow": [-10000.0],
            }
        )

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

            self.reports.annual_economics(
                **self._annual_economics_kwargs(
                    cash_flow
                )
            )

        assert printer.value.call_args_list[4:7] == [
            call(
                "Ahorro por autoconsumo",
                800.0,
                "€",
                decimals=2
            ),
            call(
                "Beneficio por excedentes",
                300.0,
                "€",
                decimals=2
            ),
            call(
                "Ahorro anual total",
                1100.0,
                "€",
                decimals=2
            ),
        ]

    def test_annual_economics_prints_investment_indicators(
        self
    ):

        cash_flow = pd.DataFrame(
            {
                "year": [0],
                "cash_flow": [-10000.0],
                "cumulative_cash_flow": [-10000.0],
            }
        )

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

            self.reports.annual_economics(
                **self._annual_economics_kwargs(
                    cash_flow
                )
            )

        assert printer.value.call_args_list[7:9] == [
            call(
                "Inversión neta",
                10000.0,
                "€",
                decimals=2
            ),
            call(
                "Periodo de amortización",
                5.34,
                "años",
                decimals=2
            ),
        ]

        assert printer.percent.call_args_list == [
            call(
                "Tasa de descuento",
                5.0,
            ),
            call(
                "Tasa interna de retorno",
                18.8,
            ),
        ]

        printer.value.assert_any_call(
            "Valor actual neto",
            5000.0,
            "€",
            decimals=2
        )

    # ==================================================
    # cash flow
    # ==================================================

    def test_annual_economics_cash_flow_header(self):

        cash_flow = pd.DataFrame(
            {
                "year": [0],
                "cash_flow": [-10000.0],
                "cumulative_cash_flow": [-10000.0],
            }
        )

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

            self.reports.annual_economics(
                **self._annual_economics_kwargs(
                    cash_flow
                )
            )

        printer.table_header.assert_called_once_with(
            [
                "Año",
                "Flujo",
                "Acumulado"
            ],
            [10, 18, 22],
            ["right", "right", "right"]
        )

    def test_annual_economics_prints_cash_flow_in_order(
        self
    ):

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

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

            self.reports.annual_economics(
                **self._annual_economics_kwargs(
                    cash_flow
                )
            )

        expected_calls = [
            call(
                [
                    "0",
                    "-10000.00 €",
                    "-10000.00 €",
                ],
                [10, 18, 22],
                ["right", "right", "right"]
            ),
            call(
                [
                    "1",
                    "2300.50 €",
                    "-7699.50 €",
                ],
                [10, 18, 22],
                ["right", "right", "right"]
            ),
            call(
                [
                    "2",
                    "2350.75 €",
                    "-5348.75 €",
                ],
                [10, 18, 22],
                ["right", "right", "right"]
            ),
        ]

        assert (
            printer.table_row.call_args_list
            == expected_calls
        )

    # ==================================================
    # economic_scenarios
    # ==================================================

    def test_economic_scenarios(self):

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

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

            result = self.reports.economic_scenarios(
                scenario_results
            )

        assert result is None

        printer.subtitle.assert_called_once_with(
            "ECONOMIC SCENARIOS"
        )

        printer.blank.assert_called_once_with()

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

        expected_calls = [
            call(
                [
                    "Base",
                    "5.34 años",
                    "22,071.16 €",
                    "18.80 %",
                ],
                [18, 18, 18, 18],
                ["left", "right", "right", "right"]
            ),
            call(
                [
                    "Optimista",
                    "4.50 años",
                    "30,000.00 €",
                    "22.00 %",
                ],
                [18, 18, 18, 18],
                ["left", "right", "right", "right"]
            ),
        ]

        assert (
            printer.table_row.call_args_list
            == expected_calls
        )

    def test_economic_scenarios_preserves_result_order(
        self
    ):

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
                "Conservador",
                7.25,
                10000.0,
                0.12
            ),
            ScenarioResult(
                "Base",
                5.34,
                22071.16,
                0.188
            ),
            ScenarioResult(
                "Optimista",
                4.50,
                30000.0,
                0.22
            ),
        ]

        with patch(
            "helios.reports.economics.ReportPrinter"
        ) as printer:

            self.reports.economic_scenarios(
                scenario_results
            )

        calls = printer.table_row.call_args_list

        assert calls[0].args[0][0] == "Conservador"
        assert calls[1].args[0][0] == "Base"
        assert calls[2].args[0][0] == "Optimista"

        assert len(calls) == 3