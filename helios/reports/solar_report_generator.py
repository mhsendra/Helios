from pathlib import Path

from helios.reports.solar_report_charts import SolarReportCharts
from helios.reports.solar_report_data import SolarReportData
from helios.reports.solar_report_text import SolarReportText

from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

HELIOS_BLUE = "#1f4e78"
HELIOS_GREEN = "#548235"
HELIOS_GREEN_DARK = "#38761d"
HELIOS_GOLD = "#7f6000"
HELIOS_PURPLE = "#7030a0"
HELIOS_PURPLE_LIGHT = "#674ea7"
HELIOS_TEXT = "#333333"
HELIOS_MUTED = "#666666"
HELIOS_BORDER = "#d0d7de"
HELIOS_BACKGROUND = "#f8f9fa"
HELIOS_KPI_BACKGROUND = "#f4f6f8"

class NumberedCanvas(canvas.Canvas):
    """Canvas de ReportLab que permite mostrar 'Página X de Y'."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        """Guarda el estado de la página actual."""

        self._saved_page_states.append(
            self.__dict__.copy()
        )

        self._startPage()

    def save(self):
        """Genera las páginas definitivas con encabezado y pie."""

        total_pages = len(self._saved_page_states)

        for page_state in self._saved_page_states:

            self.__dict__.update(page_state)

            self._draw_header_footer(
                total_pages
            )

            canvas.Canvas.showPage(self)

        canvas.Canvas.save(self)

    def _draw_header_footer(self, total_pages: int):
        """Dibuja encabezado y pie de página."""

        page_number = self._pageNumber

        if page_number == 1:
            return

        width, height = A4

        self.saveState()

        # Encabezado
        self.setFont(
            "Helvetica-Bold",
            8,
        )

        self.setFillColor(
            colors.HexColor(HELIOS_BLUE)
        )

        self.drawString(
            18 * mm,
            height - 11 * mm,
            "HELIOS — Solar Performance Report",
        )

        self.setStrokeColor(
            colors.HexColor(HELIOS_BORDER)
        )

        self.setLineWidth(0.5)

        self.line(
            18 * mm,
            height - 14 * mm,
            width - 18 * mm,
            height - 14 * mm,
        )

        # Pie
        self.setFont(
            "Helvetica",
            7.5,
        )

        self.setFillColor(
            colors.HexColor(HELIOS_MUTED)
        )

        self.drawString(
            18 * mm,
            9 * mm,
            "HELIOS Energy Analytics",
        )

        self.drawRightString(
            width - 18 * mm,
            9 * mm,
            f"Página {page_number} de {total_pages}",
        )

        self.restoreState()

class SolarReportGenerator:
    """Genera informes PDF a partir de datos solares previamente calculados."""

    @staticmethod
    def _style_table(
        table: Table,
        header_color: str,
        header_rows: int = 1,
    ) -> None:
        """Aplica el estilo visual común a las tablas del informe."""

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, header_rows - 1),
                        colors.HexColor(header_color),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, header_rows - 1),
                        colors.white,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, header_rows - 1),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor(HELIOS_BORDER),
                    ),
                    (
                        "BACKGROUND",
                        (0, header_rows),
                        (-1, -1),
                        colors.HexColor(HELIOS_BACKGROUND),
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
                        7,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                ]
            )
        )

    @staticmethod
    def _section_header(
        title: str,
        styles,
        color: str = HELIOS_BLUE,
    ) -> KeepTogether:
        """Crea un encabezado de sección con separador visual."""

        return KeepTogether(
            [
                Spacer(1, 6 * mm),
                Paragraph(
                    title,
                    styles["HeliosSectionTitle"],
                ),
                HRFlowable(
                    width="100%",
                    thickness=1,
                    color=colors.HexColor(color),
                    spaceBefore=1,
                    spaceAfter=7,
                ),
            ]
        )

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
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        styles = getSampleStyleSheet()

        styles.add(
            ParagraphStyle(
                name="HeliosCoverTitle",
                parent=styles["Title"],
                fontName="Helvetica-Bold",
                fontSize=28,
                leading=32,
                alignment=TA_CENTER,
                textColor=colors.HexColor(HELIOS_BLUE),
            )
        )

        styles.add(
            ParagraphStyle(
                name="HeliosCoverSubtitle",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=14,
                leading=18,
                alignment=TA_CENTER,
                textColor=colors.HexColor(HELIOS_MUTED),
            )
        )

        styles.add(
            ParagraphStyle(
                name="HeliosKpiLabel",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=8,
                leading=10,
                alignment=TA_CENTER,
                textColor=colors.HexColor(HELIOS_MUTED),
            )
        )

        styles.add(
            ParagraphStyle(
                name="HeliosKpiValue",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=15,
                leading=18,
                alignment=TA_CENTER,
                textColor=colors.HexColor(HELIOS_BLUE),
            )
        )

        styles.add(
            ParagraphStyle(
                name="HeliosSectionTitle",
                parent=styles["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=17,
                leading=21,
                spaceBefore=8,
                spaceAfter=5,
                textColor=colors.HexColor(HELIOS_BLUE),
            )
        )

        document = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
        )

        story = [

            Spacer(1, 45 * mm),

            Paragraph(
                "HELIOS",
                styles["HeliosCoverTitle"],
            ),

            Spacer(1, 7 * mm),

            Paragraph(
                "Informe de rendimiento solar",
                styles["HeliosCoverSubtitle"],
            ),

            Spacer(1, 12 * mm),

            HRFlowable(
                width="55%",
                thickness=1.2,
                color=colors.HexColor(HELIOS_BLUE),
                hAlign="CENTER",
            ),

            Spacer(1, 10 * mm),

            Paragraph(
                f"Instalación fotovoltaica — "
                f"{data.installed_power_kwp:.2f} kWp",
                styles["HeliosCoverSubtitle"],
            ),

            Spacer(1, 45 * mm),
        ]

        kpi_data = [
            [
                Paragraph(
                    "Producción anual",
                    styles["HeliosKpiLabel"],
                ),
                Paragraph(
                    "Potencia instalada",
                    styles["HeliosKpiLabel"],
                ),
                Paragraph(
                    "Ahorro anual",
                    styles["HeliosKpiLabel"],
                ),
            ],
            [
                Paragraph(
                    f"{data.yearly_production_kwh:,.0f} kWh",
                    styles["HeliosKpiValue"],
                ),
                Paragraph(
                    f"{data.installed_power_kwp:.2f} kWp",
                    styles["HeliosKpiValue"],
                ),
                Paragraph(
                    f"{data.yearly_savings_eur:,.0f} €",
                    styles["HeliosKpiValue"],
                ),
            ],
            [
                Paragraph(
                    "Periodo de retorno",
                    styles["HeliosKpiLabel"],
                ),
                Paragraph(
                    "VAN",
                    styles["HeliosKpiLabel"],
                ),
                Paragraph(
                    "TIR",
                    styles["HeliosKpiLabel"],
                ),
            ],
            [
                Paragraph(
                    f"{data.payback_years:.2f} años",
                    styles["HeliosKpiValue"],
                ),
                Paragraph(
                    f"{data.net_present_value_eur:,.0f} €",
                    styles["HeliosKpiValue"],
                ),
                Paragraph(
                    (
                        f"{data.internal_rate_of_return_percent:.2f} %"
                        if data.internal_rate_of_return_percent is not None
                        else "N/D"
                    ),
                    styles["HeliosKpiValue"],
                ),
            ],
        ]

        kpi_table = Table(
            kpi_data,
            colWidths=[
                56 * mm,
                56 * mm,
                56 * mm,
            ],
        )

        kpi_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.HexColor(HELIOS_KPI_BACKGROUND),
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.6,
                        colors.HexColor(HELIOS_BORDER),
                    ),
                    (
                        "INNERGRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.HexColor(HELIOS_BORDER),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                ]
            )
        )

        story.extend(
            [
                kpi_table,

                PageBreak(),

                self._section_header(
                    "Resumen ejecutivo",
                    styles,
                ),

                Paragraph(
                    SolarReportText.executive_summary(data),
                    styles["BodyText"],
                ),

                Spacer(1, 12),

                self._section_header(
                    "Resumen de la instalación",
                    styles,
                ),

                Spacer(1, 4),
            ]
        )

        # ==================================================
        # Instalación
        # ==================================================

        if data.calculation_mode == "automatic":

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
                [
                    "Tecnología fotovoltaica",
                    "Silicio cristalino",
                ],
                [
                    "Tipo de montaje",
                    "Coplanar a cubierta",
                ],
            ]

        elif data.calculation_mode == "manual":

            installation_data = [
                ["Concepto", "Valor"],
                [
                    "Potencia instalada",
                    f"{data.installed_power_kwp:.2f} kWp",
                ],
                [
                    "Latitud",
                    f"{data.latitude:.5f}°",
                ],
                [
                    "Longitud",
                    f"{data.longitude:.5f}°",
                ],
                [
                    "Inclinación",
                    f"{data.tilt}°",
                ],
                [
                    "Azimut",
                    f"{data.azimuth}°",
                ],
                [
                    "Año de referencia",
                    str(data.reference_year),
                ],
                [
                    "Pérdidas del sistema",
                    f"{data.losses:.1f} %",
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

        else:

            raise ValueError(
                "unsupported calculation mode"
            )

        installation_table = Table(
            installation_data,
            colWidths=[260, 180],
        )

        self._style_table(
            installation_table,
            HELIOS_BLUE,
        )

        story.append(installation_table)

        # ==================================================
        # Nueva página: detalle técnico
        # ==================================================

        story.append(PageBreak())

        # ==================================================
        # Producción solar
        # ==================================================

        story.extend(
            [
                Spacer(1, 25),
                self._section_header(
                    "Producción solar",
                    styles,
                    HELIOS_GREEN,
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

        self._style_table(
            production_table,
            HELIOS_GREEN,
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

        story.append(
            Spacer(
                1,
                15,
            )
        )

        story.append(
            Paragraph(
                SolarReportText.production_analysis(data),
                styles["BodyText"],
            )
        )

        # ==================================================
        # Estadísticas solares
        # ==================================================

        story.extend(
            [
                Spacer(1, 25),
                self._section_header(
                    "Estadísticas solares",
                    styles,
                    HELIOS_GREEN_DARK,
                ),
                Spacer(1, 10),
            ]
        )

        solar_statistics_data = [
            ["Métrica", "Valor"],
            [
                "Horas productivas",
                f"{data.productive_hours:,}",
            ],
            [
                "Producción media diaria",
                f"{data.daily_average_kwh:,.2f} kWh/día",
            ],
            [
                "Producción media mensual",
                f"{data.monthly_average_kwh:,.2f} kWh/mes",
            ],
            [
                "Máxima producción horaria",
                f"{data.maximum_power_kw:,.2f} kW",
            ],
            [
                "Factor de capacidad",
                f"{data.capacity_factor_percent:.2f} %",
            ],
        ]

        solar_statistics_table = Table(
            solar_statistics_data,
            colWidths=[260, 180],
        )

        self._style_table(
            solar_statistics_table,
            HELIOS_GREEN_DARK,
        )

        story.append(solar_statistics_table)

        story.append(PageBreak())

        # ==================================================
        # Balance energético
        # ==================================================

        story.extend(
            [
                Spacer(1, 25),
                self._section_header(
                    "Consumo y balance energético",
                    styles,
                    HELIOS_GOLD,
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

        self._style_table(
            balance_table,
            HELIOS_GOLD,
        )

        story.append(balance_table)

        story.append(
            Spacer(
                1,
                15,
            )
        )

        story.append(
            SolarReportCharts.energy_balance(
                data.yearly_production_kwh,
                data.yearly_consumption_kwh,
                data.self_consumption_kwh,
                data.grid_import_kwh,
                data.grid_export_kwh,
            )
        )

        story.append(
            Spacer(
                1,
                15,
            )
        )

        story.append(
            Paragraph(
                SolarReportText.energy_balance_analysis(data),
                styles["BodyText"],
            )
        )

        # ==================================================
        # Rentabilidad económica
        # ==================================================

        story.extend(
            [
                Spacer(1, 25),
                self._section_header(
                    "Rentabilidad económica",
                    styles,
                    HELIOS_PURPLE,
                ),
                Spacer(1, 10),
            ]
        )

        economics_data = [
            ["Concepto", "Valor"],
            [
                "Coste anual sin FV",
                f"{data.cost_without_pv_eur:,.2f} €",
            ],
            [
                "Coste energía importada con FV",
                f"{data.grid_import_cost_eur:,.2f} €",
            ],
            [
                "Ingresos por excedentes",
                f"{data.export_income_eur:,.2f} €",
            ],
            [
                "Coste neto con FV",
                f"{data.cost_with_pv_eur:,.2f} €",
            ],
            [
                "Ahorro por autoconsumo",
                f"{data.self_consumption_savings_eur:,.2f} €",
            ],
            [
                "Ahorro anual total",
                f"{data.yearly_savings_eur:,.2f} €",
            ],
            [
                "Inversión neta",
                f"{data.investment_eur:,.2f} €",
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
                (
                    f"{data.internal_rate_of_return_percent:.2f} %"
                    if data.internal_rate_of_return_percent
                    is not None
                    else "N/D"
                ),
            ],
        ]

        economics_table = Table(
            economics_data,
            colWidths=[260, 180],
        )

        self._style_table(
            economics_table,
            HELIOS_PURPLE,
        )

        story.append(economics_table)

        story.append(
            Spacer(
                1,
                15,
            )
        )

        story.append(
            Paragraph(
                SolarReportText.economic_analysis(data),
                styles["BodyText"],
            )
        )

        # ==================================================
        # Hipótesis económicas
        # ==================================================

        economic_assumptions_data = [
            ["Hipótesis", "Valor"],
            [
                "Horizonte económico",
                f"{data.economic_horizon_years} años",
            ],
            [
                "Degradación primer año",
                f"{data.first_year_degradation_percent:.2f} %",
            ],
            [
                "Degradación anual",
                f"{data.annual_degradation_percent:.2f} %",
            ],
            [
                "Incremento anual precio electricidad",
                (
                    f"{data.annual_electricity_price_growth_percent:.2f} %"
                ),
            ],
            [
                "Incremento anual precio excedentes",
                (
                    f"{data.annual_export_price_growth_percent:.2f} %"
                ),
            ],
            [
                "Coste anual de mantenimiento",
                f"{data.annual_maintenance_cost_eur:,.2f} €",
            ],
            [
                "Incremento anual del mantenimiento",
                f"{data.annual_maintenance_growth_percent:.2f} %",
            ],
            [
                "Tasa de descuento",
                f"{data.discount_rate_percent:.2f} %",
            ],
        ]

        economic_assumptions_table = Table(
            economic_assumptions_data,
            colWidths=[260, 180],
        )

        self._style_table(
            economic_assumptions_table,
            HELIOS_PURPLE,
        )

        story.append(
            KeepTogether(
                [
                    Spacer(1, 25),
                    self._section_header(
                        "Hipótesis económicas",
                        styles,
                        HELIOS_PURPLE,
                    ),
                    Spacer(1, 10),
                    economic_assumptions_table,
                ]
            )
        )

        # ==================================================
        # Escenarios económicos
        # ==================================================

        story.extend(
            [
                Spacer(1, 25),
                self._section_header(
                    "Escenarios económicos",
                    styles,
                    HELIOS_PURPLE_LIGHT,
                ),
                Spacer(1, 10),
            ]
        )

        scenarios_data = [
            [
                "Escenario",
                "Ahorro anual",
                "Payback",
                "VAN",
                "TIR",
            ],
        ]

        for result in data.scenario_results:

            scenarios_data.append(
                [
                    result.name,
                    f"{result.annual_savings:,.2f} €",
                    f"{result.payback_years:.2f} años",
                    f"{result.npv:,.2f} €",
                    f"{result.irr * 100:.2f} %",
                ]
            )

        scenarios_table = Table(
            scenarios_data,
            colWidths=[
                105,
                105,
                85,
                105,
                80,
            ],
        )

        scenarios_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor(HELIOS_PURPLE_LIGHT),
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
                        "ALIGN",
                        (1, 1),
                        (-1, -1),
                        "RIGHT",
                    ),
                    (
                        "ALIGN",
                        (0, 0),
                        (0, -1),
                        "LEFT",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
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

        story.append(scenarios_table)

        story.append(
            Spacer(
                1,
                15,
            )
        )

        story.append(
            SolarReportCharts.economic_scenarios(
                data.scenario_results,
            )
        )

        story.append(
            Spacer(
                1,
                15,
            )
        )

        story.append(
            Paragraph(
                SolarReportText.scenario_analysis(data),
                styles["BodyText"],
            )
        )

                # ==================================================
        # Conclusión
        # ==================================================

        story.append(
            Spacer(
                1,
                25,
            )
        )

        story.append(
            self._section_header(
                "Conclusión",
                styles,
            ),
        )

        story.append(
            Spacer(
                1,
                10,
            )
        )

        story.append(
            Paragraph(
                SolarReportText.conclusion(data),
                styles["BodyText"],
            )
        )

        story.append(PageBreak())

        # ==================================================
        # Glosario y definiciones
        # ==================================================

        story.append(
            self._section_header(
                "Glosario y definiciones",
                styles,
            )
        )

        story.append(
            Spacer(
                1,
                10,
            )
        )

        glossary_data = [
            ["Término", "Definición"],
        ]

        for term, definition in SolarReportText.glossary():

            glossary_data.append(
                [
                    Paragraph(
                        term,
                        styles["BodyText"],
                    ),
                    Paragraph(
                        definition,
                        styles["BodyText"],
                    ),
                ]
            )

        glossary_table = Table(
            glossary_data,
            colWidths=[
                55 * mm,
                125 * mm,
            ],
            repeatRows=1,
        )

        self._style_table(
            glossary_table,
            HELIOS_BLUE,
        )

        story.append(glossary_table)

        # ==================================================
        # Generación
        # ==================================================

        document.build(
            story,
            canvasmaker=NumberedCanvas,
        )