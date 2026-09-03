from pathlib import Path

from helios.reports.solar_report_charts import SolarReportCharts

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from helios.reports.solar_report_data import SolarReportData


class SolarReportGenerator:
    """Genera informes PDF a partir de datos solares previamente calculados."""

    def generate(
        self,
        data: SolarReportData,
        output_path: str | Path,
    ) -> None:
        if data is None:
            raise ValueError("report data is required")

        if output_path is None:
            raise ValueError("output path is required")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        styles = getSampleStyleSheet()

        document = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
        )

        story = [
            Paragraph(
                "Informe solar",
                styles["Title"],
            ),
            Spacer(1, 20),
            Paragraph(
                "Resumen de la instalación",
                styles["Heading2"],
            ),
            Spacer(1, 10),
        ]

        installation_data = [
            ["Concepto", "Valor"],
            [
                "Potencia instalada",
                f"{data.installed_power_kwp:.2f} kWp",
            ],
            [
                "Número de paneles",
                str(data.panel_count),
            ],
            [
                "Potencia por panel",
                f"{data.panel_power_wp:.0f} Wp",
            ],
        ]

        installation_table = Table(
            installation_data,
            colWidths=[260, 180],
        )

        installation_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#1f4e78"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        colors.whitesmoke,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(installation_table)

        story.extend(
            [
                Spacer(1, 25),
                Paragraph(
                    "Producción solar",
                    styles["Heading2"],
                ),
                Spacer(1, 10),
            ]
        )

        production_data = [
            ["Concepto", "Valor"],
            [
                "Producción anual",
                f"{data.yearly_production_kwh:,.2f} kWh",
            ],
            [
                "Producción específica",
                f"{data.specific_production_kwh_kwp:,.2f} "
                "kWh/kWp",
            ],
            [
                "Potencia instalada",
                f"{data.installed_power_kwp:.2f} kWp",
            ],
        ]

        production_table = Table(
            production_data,
            colWidths=[260, 180],
        )

        production_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#548235"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        colors.whitesmoke,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(production_table)

        story.append(
            Spacer(
                1,
                15,
            )
        )

        story.append(
            SolarReportCharts.yearly_production(
                data.yearly_production_kwh,
            )
        )

        story.append(
            Spacer(
                1,
                15,
            )
        )

        story.append(
            SolarReportCharts.monthly_production(
                data.monthly_production,
            )
        )

        story.extend(
            [
                Spacer(1, 25),
                Paragraph(
                    "Consumo y balance energético",
                    styles["Heading2"],
                ),
                Spacer(1, 10),
            ]
        )

        balance_data = [
            ["Concepto", "Valor"],
            [
                "Consumo anual",
                f"{data.yearly_consumption_kwh:,.2f} kWh",
            ],
            [
                "Autoconsumo",
                f"{data.self_consumption_kwh:,.2f} kWh",
            ],
            [
                "Energía vertida a red",
                f"{data.grid_export_kwh:,.2f} kWh",
            ],
            [
                "Energía importada de red",
                f"{data.grid_import_kwh:,.2f} kWh",
            ],
            [
                "Tasa de autoconsumo",
                f"{data.self_consumption_rate_percent:.2f} %",
            ],
            [
                "Tasa de autosuficiencia",
                f"{data.self_sufficiency_rate_percent:.2f} %",
            ],
        ]

        balance_table = Table(
            balance_data,
            colWidths=[260, 180],
        )

        balance_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#7f6000"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        colors.whitesmoke,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(balance_table)

        story.extend(
            [
                Spacer(1, 25),
                Paragraph(
                    "Rentabilidad económica",
                    styles["Heading2"],
                ),
                Spacer(1, 10),
            ]
        )

        economics_data = [
            ["Concepto", "Valor"],
            [
                "Inversión neta",
                f"{data.investment_eur:,.2f} €",
            ],
            [
                "Ahorro anual",
                f"{data.yearly_savings_eur:,.2f} €",
            ],
            [
                "Periodo de retorno",
                f"{data.payback_years:.2f} años",
            ],
            [
                "Valor actual neto (VAN)",
                f"{data.net_present_value_eur:,.2f} €",
            ],
            [
                "Tasa interna de retorno (TIR)",
                f"{data.internal_rate_of_return_percent:.2f} %",
            ],
        ]

        economics_table = Table(
            economics_data,
            colWidths=[260, 180],
        )

        economics_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#7030a0"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        colors.whitesmoke,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(economics_table)

        document.build(story)