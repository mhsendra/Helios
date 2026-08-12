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
    payback_years
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