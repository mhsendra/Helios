from helios.reports.printer import ReportPrinter


class EconomicsReports:

    def annual_economics(
    self,
    cost_without_pv,
    grid_import_cost,
    export_income,
    cost_with_pv,
    annual_savings,
    net_investment,
    payback_years,
    cash_flow,
    npv,
    discount_rate,
    irr
):

        ReportPrinter.title(
            "ECONOMIC ANALYSIS"
        )

        ReportPrinter.blank()

        ReportPrinter.subtitle(
            "ANNUAL COST"
        )

        ReportPrinter.blank()

        ReportPrinter.value(
            "Coste anual sin FV",
            cost_without_pv,
            "€",
            decimals=2
        )

        ReportPrinter.value(
            "Coste energía importada con FV",
            grid_import_cost,
            "€",
            decimals=2
        )

        ReportPrinter.value(
            "Ingresos por excedentes",
            export_income,
            "€",
            decimals=2
        )

        ReportPrinter.value(
            "Coste neto con FV",
            cost_with_pv,
            "€",
            decimals=2
        )

        ReportPrinter.blank()

        ReportPrinter.subtitle(
            "SAVINGS"
        )

        ReportPrinter.blank()

        self_consumption_savings = (
            cost_without_pv
            - grid_import_cost
        )

        ReportPrinter.value(
            "Ahorro por autoconsumo",
            self_consumption_savings,
            "€",
            decimals=2
        )

        ReportPrinter.value(
            "Beneficio por excedentes",
            export_income,
            "€",
            decimals=2
        )

        ReportPrinter.value(
            "Ahorro anual total",
            annual_savings,
            "€",
            decimals=2
        )
        
        ReportPrinter.blank()

        ReportPrinter.subtitle(
            "INVESTMENT"
        )

        ReportPrinter.blank()

        ReportPrinter.value(
            "Inversión neta",
            net_investment,
            "€",
            decimals=2
        )
        
        ReportPrinter.value(
            "Periodo de amortización",
            payback_years,
            "años",
            decimals=2
        )
        
        ReportPrinter.percent(
            "Tasa de descuento",
            discount_rate * 100,
        )
                
        ReportPrinter.value(
            "Valor actual neto",
            npv,
            "€",
            decimals=2
        )
        
        ReportPrinter.percent(
            "Tasa interna de retorno",
            irr * 100,
        )

        ReportPrinter.blank()
        
        ReportPrinter.subtitle(
            "CASH FLOW"
        )

        ReportPrinter.blank()

        widths = [10, 18, 22]

        ReportPrinter.table_header(
            ["Año", "Flujo", "Acumulado"],
            widths,
            ["right", "right", "right"]
        )

        for _, row in cash_flow.iterrows():

            ReportPrinter.table_row(
                [
                    str(int(row["year"])),
                    f"{row['cash_flow']:.2f} €",
                    f"{row['cumulative_cash_flow']:.2f} €"
                ],
                widths,
                ["right", "right", "right"]
            )

    def economic_scenarios(
        self,
        scenario_results,
    ):

        ReportPrinter.subtitle(
            "ECONOMIC SCENARIOS"
        )

        ReportPrinter.blank()

        widths = [18, 18, 18, 18]

        ReportPrinter.table_header(
            [
                "Escenario",
                "Payback",
                "VAN",
                "TIR"
            ],
            widths,
            ["left", "right", "right", "right"]
        )

        for result in scenario_results:

            ReportPrinter.table_row(
                [
                    result.name,
                    f"{result.payback_years:.2f} años",
                    f"{result.npv:,.2f} €",
                    f"{result.irr * 100:.2f} %",
                ],
                widths,
                ["left", "right", "right", "right"]
            )

    