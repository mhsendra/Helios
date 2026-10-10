from pathlib import Path

from helios.reports.solar_report_charts import SolarReportCharts
from helios.reports.solar_report_data import SolarReportData
from helios.reports.solar_report_text import SolarReportText

from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Flowable,
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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

HELIOS_ASSETS = Path(__file__).resolve().parents[2] / "assets"

HELIOS_LOGO = HELIOS_ASSETS / "Logo_Helios.png"
HELIOS_FONTS = HELIOS_ASSETS / "fonts"

pdfmetrics.registerFont(
    TTFont(
        "Montserrat",
        str(HELIOS_FONTS / "Montserrat-Regular.ttf"),
    )
)

pdfmetrics.registerFont(
    TTFont(
        "Montserrat-Bold",
        str(HELIOS_FONTS / "Montserrat-Bold.ttf"),
    )
)

pdfmetrics.registerFont(
    TTFont(
        "Lato",
        str(HELIOS_FONTS / "Lato-Regular.ttf"),
    )
)

pdfmetrics.registerFont(
    TTFont(
        "Lato-Bold",
        str(HELIOS_FONTS / "Lato-Bold.ttf"),
    )
)

class HeliosDocTemplate(SimpleDocTemplate):
    """Plantilla de documento con índice y marcadores PDF."""

    def afterFlowable(self, flowable):
        """Registra automáticamente las secciones en el índice."""

        if not isinstance(flowable, Paragraph):
            return

        toc_level = getattr(
            flowable,
            "_toc_level",
            None,
        )

        if toc_level is None:
            return

        title = flowable.getPlainText()
        key = getattr(
            flowable,
            "_toc_key",
            None,
        )

        if key is None:
            return

        self.canv.bookmarkPage(key)

        self.canv.addOutlineEntry(
            title,
            key,
            level=toc_level,
            closed=False,
        )

        self.notify(
            "TOCEntry",
            (
                toc_level,
                title,
                self.page,
                key,
            ),
        )

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

        # ==================================================
        # Encabezado
        # ==================================================

        logo_width = 38 * mm
        logo_height = logo_width * 345 / 1170

        self.drawImage(
            str(HELIOS_LOGO),
            18 * mm,
            height - 12 * mm - logo_height,
            width=logo_width,
            height=logo_height,
            preserveAspectRatio=True,
            mask="auto",
        )

        self.setFont(
            "Montserrat-Bold",
            8,
        )

        self.setFillColor(
            colors.HexColor(HELIOS_BLUE)
        )

        self.drawRightString(
            width - 18 * mm,
            height - 9 * mm,
            "Solar Performance Report",
        )

        self.setStrokeColor(
            colors.HexColor(HELIOS_BORDER)
        )

        self.setLineWidth(0.5)

        self.line(
            18 * mm,
            height - 24 * mm,
            width - 18 * mm,
            height - 24 * mm,
        )

        # ==================================================
        # Pie
        # ==================================================

        self.setFont(
            "Lato",
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

class FlowableLogo(Flowable):
    """Inserta el logo HELIOS centrado."""

    def __init__(
        self,
        image_path: str,
        image_width: float,
        image_height: float,
    ):
        super().__init__()

        self.image_path = image_path
        self.image_width = image_width
        self.image_height = image_height
        self.available_width = 0

    def wrap(self, availWidth, availHeight):
        self.available_width = availWidth
        return availWidth, self.image_height

    def draw(self):
        x = (
            self.available_width - self.image_width
        ) / 2

        self.canv.drawImage(
            self.image_path,
            x,
            0,
            width=self.image_width,
            height=self.image_height,
            preserveAspectRatio=True,
            mask="auto",
        )

class ExecutiveKpiGrid(Flowable):
    """Dibuja una cuadrícula horizontal de cuatro KPI ejecutivos."""

    def __init__(
        self,
        kpis: list[tuple[str, str, str]],
        width: float,
        height: float = 25 * mm,
    ):
        super().__init__()

        self.kpis = kpis
        self.width = width
        self.height = height

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        canvas = self.canv

        gap = 2 * mm
        card_width = (self.width - (3 * gap)) / 4

        for index, (label, value, accent_color) in enumerate(self.kpis):
            x = index * (card_width + gap)
            y = 0

            canvas.setFillColor(
                colors.HexColor(HELIOS_KPI_BACKGROUND)
            )
            canvas.setStrokeColor(
                colors.HexColor(HELIOS_BORDER)
            )
            canvas.setLineWidth(0.8)

            canvas.roundRect(
                x,
                y,
                card_width,
                self.height,
                2 * mm,
                stroke=1,
                fill=1,
            )

            canvas.setFillColor(
                colors.HexColor(accent_color)
            )

            canvas.roundRect(
                x,
                y,
                3,
                self.height,
                1.5,
                stroke=0,
                fill=1,
            )

            canvas.setFillColor(
                colors.HexColor(HELIOS_MUTED)
            )
            canvas.setFont("Helvetica", 8)

            canvas.drawCentredString(
                x + card_width / 2,
                y + self.height - 9 * mm,
                label,
            )

            canvas.setFillColor(
                colors.HexColor(HELIOS_BLUE)
            )
            canvas.setFont("Helvetica-Bold", 13)

            canvas.drawCentredString(
                x + card_width / 2,
                y + 7 * mm,
                value,
            )

class ConclusionBlock(Flowable):
    """Dibuja un bloque visual destacado para la conclusión del informe."""

    def __init__(
        self,
        text: str,
        width: float,
        accent_color: str = HELIOS_GREEN,
    ):
        super().__init__()

        self.text = (
            "<b>Conclusión de la sección</b><br/><br/>"
            f"{text}"
        )
        self.width = width
        self.accent_color = accent_color

        self.padding_horizontal = 9 * mm
        self.padding_vertical = 6 * mm

        self.text_width = (
            self.width
            - (2 * self.padding_horizontal)
        )

        text_style = ParagraphStyle(
            "ConclusionBlockText",
            parent=getSampleStyleSheet()["BodyText"],
            fontName="Lato",
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor(HELIOS_TEXT),
            alignment=TA_LEFT,
        )

        self.paragraph = Paragraph(
            self.text,
            text_style,
        )

        _, paragraph_height = self.paragraph.wrap(
            self.text_width,
            1000 * mm,
        )

        self.height = (
            paragraph_height
            + (2 * self.padding_vertical)
        )

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        canvas = self.canv

        canvas.setFillColor(
            colors.HexColor(HELIOS_BACKGROUND)
        )
        canvas.setStrokeColor(
            colors.HexColor(HELIOS_BORDER)
        )
        canvas.setLineWidth(0.8)

        canvas.roundRect(
            0,
            0,
            self.width,
            self.height,
            2 * mm,
            stroke=1,
            fill=1,
        )

        canvas.setFillColor(
            colors.HexColor(self.accent_color)
        )

        canvas.roundRect(
            0,
            0,
            4,
            self.height,
            2,
            stroke=0,
            fill=1,
        )

        self.paragraph.drawOn(
            canvas,
            self.padding_horizontal,
            self.height
            - self.padding_vertical
            - self.paragraph.height,
        )

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
    def _kpi_card(
        label: str,
        value: str,
        styles,
        accent_color: str = HELIOS_BLUE,
    ) -> Table:
        """Crea una tarjeta visual reutilizable para un KPI."""

        content = [
            Paragraph(
                label,
                styles["HeliosKpiLabel"],
            ),
            Spacer(1, 2 * mm),
            Paragraph(
                value,
                styles["HeliosKpiValue"],
            ),
        ]

        card = Table(
            [[content]],
            colWidths=[42 * mm],
            rowHeights=[25 * mm],
        )

        card.setStyle(
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
                        0.8,
                        colors.HexColor(HELIOS_BORDER),
                    ),
                    (
                        "LINEBEFORE",
                        (0, 0),
                        (0, -1),
                        3,
                        colors.HexColor(accent_color),
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
                        4,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                ]
            )
        )

        return card

    @staticmethod
    def _section_header(
        title: str,
        styles,
        color: str = HELIOS_BLUE,
        toc_level: int = 0,
    ) -> KeepTogether:
        """Crea un encabezado de sección registrado en el índice PDF."""

        heading = Paragraph(
            title,
            styles["HeliosSectionTitle"],
        )

        # Metadatos utilizados por ``afterFlowable`` para construir
        # automáticamente el índice y los marcadores del PDF.
        heading._toc_level = toc_level
        heading._toc_key = f"helios-section-{id(heading)}"

        return KeepTogether(
            [
                Spacer(1, 6 * mm),
                heading,
                HRFlowable(
                    width="100%",
                    thickness=1,
                    color=colors.HexColor(color),
                    spaceBefore=1,
                    spaceAfter=7,
                ),
            ]
        )


    def _build_executive_summary(
        self,
        data: SolarReportData,
        styles,
    ) -> list:
        return [
            self._section_header(
                "Resumen ejecutivo",
                styles,
                toc_level=0,
            ),
            ExecutiveKpiGrid(
                [
                    (
                        "Producción solar",
                        f"{data.yearly_production_kwh:,.0f} kWh/año",
                        HELIOS_GREEN,
                    ),
                    (
                        "Autosuficiencia",
                        f"{data.self_sufficiency_rate_percent:.1f} %",
                        HELIOS_GREEN_DARK,
                    ),
                    (
                        "Ahorro anual",
                        f"{data.yearly_savings_eur:,.2f} €/año",
                        HELIOS_GOLD,
                    ),
                    (
                        "Retorno",
                        f"{data.payback_years:.2f} años",
                        HELIOS_BLUE,
                    ),
                ],
                width=174 * mm,
                height=25 * mm,
            ),
            Spacer(1, 5 * mm),
            self._section_conclusion(
                SolarReportText.quick_diagnostic(data),
                HELIOS_GOLD,
            ),
            Spacer(1, 5 * mm),
            Paragraph(
                SolarReportText.executive_summary(data),
                styles["BodyText"],
            ),
        ]

    def _build_energy_situation(
        self,
        data: SolarReportData,
        styles,
    ) -> list:
        return [
            Spacer(1, 12),
            self._keep_section_content(
                self._section_header(
                    "Situación energética actual",
                    styles,
                    HELIOS_GOLD,
                    0,
                ),
                Spacer(1, 10),
                Paragraph(
                    SolarReportText.energy_situation_analysis(data),
                    styles["HeliosBodyText"],
                ),
            ),
            self._keep_section_content(
                Spacer(1, 12),
                self._section_conclusion(
                    SolarReportText.energy_situation_conclusion(data),
                    HELIOS_GOLD,
                ),
            ),
        ]
    
    def _build_pv_section(
        self,
        data: SolarReportData,
        styles,
    ) -> list:
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

        elif data.calculation_mode in (
            "manual",
            "project",
        ):
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
                f"{data.maximum_hourly_production_kwh:,.2f} kWh",
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

        story = [
            self._keep_section_content(
                self._section_header(
                    "Instalación fotovoltaica",
                    styles,
                    HELIOS_BLUE,
                    0,
                ),
                Spacer(1, 10),
                self._keep_table(installation_table),
            ),

            self._keep_section_content(
                Spacer(1, 12),
                self._section_conclusion(
                    SolarReportText.installation_conclusion(data),
                    HELIOS_BLUE,
                ),
            ),

            Spacer(1, 25),

            self._keep_section_content(
                self._section_header(
                    "Producción solar",
                    styles,
                    HELIOS_GREEN,
                    1,
                ),
                Spacer(1, 10),
                self._keep_table(production_table),
            ),

            Spacer(1, 15),

            SolarReportCharts.monthly_consumption_vs_production(
                data.monthly_consumption,
                data.monthly_production,
            ),

            Spacer(1, 15),

            Paragraph(
                SolarReportText.production_analysis(data),
                styles["BodyText"],
            ),

            Spacer(1, 15),

            solar_statistics_table,

            self._keep_section_content(
                Spacer(1, 12),
                self._section_conclusion(
                    SolarReportText.production_conclusion(data),
                    HELIOS_GREEN,
                ),
            ),
        ]

        return story

    def _build_energy_balance(
        self,
        data: SolarReportData,
        styles,
    ) -> list:
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

        story = [
            Spacer(1, 25),

            self._keep_section_content(
                self._section_header(
                    "Balance energético",
                    styles,
                    HELIOS_GOLD,
                    0,
                ),
                Spacer(1, 10),
                self._keep_table(
                    balance_table
                ),
            ),

            Spacer(1, 15),

            self._keep_section_content(
                Paragraph(
                    "Dónde va la energía",
                    styles["HeliosSubsectionTitle"],
                ),
                Spacer(1, 6),
                Paragraph(
                    SolarReportText.energy_flow_summary(data),
                    styles["HeliosBodyText"],
                ),
            ),

            Spacer(1, 10),

            SolarReportCharts.energy_balance(
                data.yearly_production_kwh,
                data.yearly_consumption_kwh,
                data.self_consumption_kwh,
                data.grid_import_kwh,
                data.grid_export_kwh,
            ),

            Spacer(1, 15),

            Paragraph(
                SolarReportText.energy_balance_analysis(data),
                styles["BodyText"],
            ),

            self._keep_section_content(
                Spacer(1, 12),
                self._section_conclusion(
                    SolarReportText.energy_balance_conclusion(data),
                    HELIOS_GOLD,
                ),
            ),
        ]

        return story
    
    def _build_economic_section(
        self,
        data: SolarReportData,
        styles,
    ) -> list:
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
                    if data.internal_rate_of_return_percent is not None
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

        story = [
            Spacer(1, 25),
        ]

        # ==================================================
        # Rentabilidad económica
        # ==================================================

        story.extend(
            [
                self._keep_section_content(
                    self._section_header(
                        "Rentabilidad económica",
                        styles,
                        HELIOS_PURPLE,
                        0,
                    ),
                    Spacer(1, 10),
                    self._keep_table(
                        economics_table
                    ),
                ),

                Spacer(1, 15),

                Paragraph(
                    SolarReportText.economic_analysis(data),
                    styles["BodyText"],
                ),

                self._keep_section_content(
                    Spacer(1, 12),
                    self._section_conclusion(
                        SolarReportText.economic_conclusion(data),
                        HELIOS_PURPLE,
                    ),
                ),
            ]
        )

        # ==================================================
        # Escenarios económicos
        # ==================================================

        scenarios_data = [
            [
                "Escenario",
                "Ahorro anual",
                "Payback",
                "VAN",
                "TIR",
            ]
        ]

        for scenario in data.scenario_results:
            scenarios_data.append(
                [
                    scenario.name,
                    f"{scenario.annual_savings:,.2f} €",
                    f"{scenario.payback_years:.2f} años",
                    f"{scenario.npv:,.2f} €",
                    f"{scenario.irr * 100:.2f} %",
                ]
            )

        scenarios_table = Table(
            scenarios_data,
            colWidths=[
                90,
                90,
                80,
                90,
                70,
            ],
        )

        self._style_table(
            scenarios_table,
            HELIOS_PURPLE_LIGHT,
        )

        story.extend(
            [
                Spacer(1, 25),

                self._keep_section_content(
                    self._section_header(
                        "Escenarios económicos",
                        styles,
                        HELIOS_PURPLE_LIGHT,
                        1,
                    ),
                    Spacer(1, 10),
                    self._keep_table(
                        scenarios_table
                    ),
                ),

                self._keep_section_content(
                    Spacer(1, 12),
                    self._section_conclusion(
                        SolarReportText.scenario_conclusion(data),
                        HELIOS_PURPLE_LIGHT,
                    ),
                ),
            ]
        )

        return story

    def _build_battery_section(
        self,
        data: SolarReportData,
        styles,
    ) -> list:
        if not data.battery_recommendations:
            return []

        battery_analysis_text = (
            SolarReportText.battery_analysis(data)
        )

        battery_operational_data = [
            [
                "Capacidad",
                "Coste anual",
                "Ahorro adicional",
                "Coste incremental",
                "Ahorro incremental",
                "Ahorro marginal/kWh",
                "Recuperación marginal",
            ],
        ]

        battery_economic_data = [
            [
                "Capacidad",
                "VAN batería",
                "TIR batería",
                "Recuperación económica",
            ],
        ]

        battery_combined_data = [
            [
                "Capacidad",
                "VAN conjunto",
                "TIR conjunta",
                "Recuperación conjunta",
            ],
        ]

        for recommendation in data.battery_recommendations:
            marginal_payback = (
                "N/D"
                if recommendation.marginal_payback_years == float("inf")
                else (
                    f"{recommendation.marginal_payback_years:.2f} años"
                )
            )

            economic_payback = (
                "N/D"
                if recommendation.economic_payback_years == float("inf")
                else (
                    f"{recommendation.economic_payback_years:.2f} años"
                )
            )

            combined_payback = (
                "N/D"
                if recommendation.combined_economic_payback_years
                == float("inf")
                else (
                    f"{recommendation.combined_economic_payback_years:.2f} años"
                )
            )

            capacity = (
                f"{recommendation.capacity_kwh:.1f} kWh"
            )

            battery_operational_data.append(
                [
                    capacity,
                    (
                        f"{recommendation.annual_cost_with_battery_eur:,.2f} €"
                    ),
                    Paragraph(
                        (
                            f"<b>{recommendation.annual_additional_savings_eur:,.2f} €</b>"
                            "<br/>"
                            f"<font size='6'>"
                            f"Menor importación: "
                            f"{recommendation.annual_import_savings_eur:,.2f} €"
                            "<br/>"
                            f"Compensación perdida: "
                            f"{recommendation.annual_export_compensation_lost_eur:,.2f} €"
                            f"</font>"
                        )
                        if (
                            recommendation.annual_import_savings_eur is not None
                            and recommendation.annual_export_compensation_lost_eur is not None
                        )
                        else (
                            f"{recommendation.annual_additional_savings_eur:,.2f} €"
                        ),
                        ParagraphStyle(
                            name="BatterySavingsBreakdown",
                            parent=styles["Normal"],
                            fontSize=7,
                            leading=8,
                            alignment=TA_CENTER,
                        ),
                    ),
                    (
                        f"{recommendation.incremental_battery_cost_eur:,.2f} €"
                    ),
                    (
                        f"{recommendation.incremental_savings_eur:,.2f} €"
                    ),
                    (
                        f"{recommendation.marginal_savings_per_kwh:,.2f} €/kWh"
                    ),
                    marginal_payback,
                ]
            )

            battery_economic_data.append(
                [
                    capacity,
                    f"{recommendation.economic_npv_eur:,.2f} €",
                    f"{recommendation.economic_irr_percent:.2f} %",
                    economic_payback,
                ]
            )

            battery_combined_data.append(
                [
                    capacity,
                    f"{recommendation.combined_economic_npv_eur:,.2f} €",
                    f"{recommendation.combined_economic_irr_percent:.2f} %",
                    combined_payback,
                ]
            )

        battery_header_style = ParagraphStyle(
            name="BatteryTableHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=8.5,
            textColor=colors.white,
            alignment=TA_CENTER,
        )

        battery_operational_data[0] = [
            Paragraph("Capacidad", battery_header_style),
            Paragraph("Coste<br/>anual", battery_header_style),
            Paragraph("Ahorro<br/>adicional", battery_header_style),
            Paragraph("Coste<br/>incremental", battery_header_style),
            Paragraph("Ahorro<br/>incremental", battery_header_style),
            Paragraph("Ahorro marginal<br/>/ kWh", battery_header_style),
            Paragraph("Recuperación<br/>marginal", battery_header_style),
        ]

        battery_economic_data[0] = [
            Paragraph("Capacidad", battery_header_style),
            Paragraph("VAN<br/>batería", battery_header_style),
            Paragraph("TIR<br/>batería", battery_header_style),
            Paragraph(
                "Recuperación<br/>económica",
                battery_header_style,
            ),
        ]

        battery_combined_data[0] = [
            Paragraph("Capacidad", battery_header_style),
            Paragraph("VAN<br/>conjunto", battery_header_style),
            Paragraph("TIR<br/>conjunta", battery_header_style),
            Paragraph(
                "Recuperación<br/>conjunta",
                battery_header_style,
            ),
        ]

        battery_operational_table = Table(
            battery_operational_data,
            colWidths=[
                60,
                65,
                72,
                72,
                72,
                72,
                77,
            ],
            repeatRows=1,
        )

        battery_economic_table = Table(
            battery_economic_data,
            colWidths=[
                65,
                140,
                105,
                180,
            ],
            repeatRows=1,
        )

        battery_combined_table = Table(
            battery_combined_data,
            colWidths=[
                65,
                140,
                105,
                180,
            ],
            repeatRows=1,
        )

        for table in (
            battery_operational_table,
            battery_economic_table,
            battery_combined_table,
            
        ):
            self._style_table(
                table,
                HELIOS_PURPLE,
            )
            table.setStyle(
                TableStyle(
                    [
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
                            "CENTER",
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
                            4,
                        ),
                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            4,
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, 0),
                            5,
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, 0),
                            5,
                        ),
                    ]
                )
            )

        return [
            Spacer(1, 25),

            self._keep_section_content(
                self._section_header(
                    "Evaluación económica de baterías",
                    styles,
                    HELIOS_PURPLE,
                    0,
                ),
                Spacer(1, 10),
                Paragraph(
                    battery_analysis_text,
                    styles["HeliosBodyText"],
                ),
            ),

            Spacer(1, 12),
            self._keep_table(
                battery_operational_table
            ),
            Spacer(1, 12),
            self._keep_table(
                battery_economic_table
            ),
            Spacer(1, 12),
            self._keep_section_content(
                Paragraph(
                    "Economía conjunta FV + batería",
                    styles["HeliosSubsectionTitle"],
                ),
                Spacer(1, 6),
                self._keep_table(
                    battery_combined_table
                ),
            ),

            Spacer(1, 15),

            SolarReportCharts.battery_marginal_savings(
                data.battery_recommendations,
            ),

            self._keep_section_content(
                Spacer(1, 12),
                self._section_conclusion(
                    SolarReportText.battery_conclusion(data),
                    HELIOS_PURPLE,
                ),
            ),

            Spacer(1, 10),
        ]

    def _build_methodology_section(
        self,
        data: SolarReportData,
        styles,
    ) -> list:
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

        return [
            PageBreak(),

            self._keep_section_content(
                self._section_header(
                    "Hipótesis y metodología",
                    styles,
                    HELIOS_PURPLE,
                    0,
                ),
                Spacer(1, 10),
                Paragraph(
                    (
                        "La simulación utiliza el perfil de consumo "
                        "representativo generado para el año de referencia "
                        f"{data.consumption_reference_year}. Este año es "
                        "independiente del año meteorológico utilizado "
                        f"por PVGIS ({data.reference_year})."
                    ),
                    styles["HeliosBodyText"],
                ),
            ),

            Spacer(1, 10),
            self._keep_section_content(
                Paragraph(
                    "Hipótesis económicas",
                    styles["HeliosSubsectionTitle"],
                ),
                Spacer(1, 6),
                self._keep_table(
                    economic_assumptions_table
                ),
            ),
            Spacer(1, 12),
            Paragraph(
                SolarReportText.methodology_analysis(data),
                styles["HeliosBodyText"],
            ),
            self._keep_section_content(
                Spacer(1, 12),
                self._section_conclusion(
                    SolarReportText.methodology_conclusion(data),
                    HELIOS_PURPLE,
                ),
            ),
        ]

    @staticmethod
    def _keep_table(
        table: Table,
    ) -> KeepTogether:
        """
        Mantiene una tabla corta como una unidad indivisible.

        Evita que ReportLab coloque la cabecera al final de una página
        y el cuerpo de la tabla en la página siguiente.
        """

        return KeepTogether(
            [table]
        )

    @staticmethod
    def _keep_section_content(
        *flowables,
    ) -> KeepTogether:
        """
        Mantiene juntos un encabezado y su contenido inmediato.

        Se utiliza para evitar encabezados huérfanos al final de una
        página cuando el contenido asociado comienza en la siguiente.
        """

        return KeepTogether(
            list(flowables)
        )

    @staticmethod
    def _section_conclusion(
        text: str,
        accent_color: str,
    ) -> ConclusionBlock:
        return ConclusionBlock(
            text,
            width=174 * mm,
            accent_color=accent_color,
        )

    def _build_conclusion(
        self,
        data: SolarReportData,
        styles,
    ) -> list:
        return [
            Spacer(1, 25),
            self._keep_section_content(
                self._section_header(
                    "Conclusión",
                    styles,
                    HELIOS_GREEN,
                    toc_level=0,
                ),
                Spacer(1, 10),
                self._section_conclusion(
                    SolarReportText.final_recommendation(data),
                    HELIOS_GREEN,
                ),
            ),
        ]

    def _build_glossary(
        self,
        data: SolarReportData,
        styles,
    ) -> list:
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

        return [
            PageBreak(),
            self._section_header(
                "Glosario y definiciones",
                styles,
                toc_level=0,
            ),
            Spacer(1, 10),
            glossary_table,
        ]

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
                fontName="Montserrat-Bold",
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
                fontName="Lato",
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
                fontName="Lato",
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
                fontName="Montserrat-Bold",
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
                fontName="Montserrat-Bold",
                fontSize=17,
                leading=21,
                spaceBefore=8,
                spaceAfter=5,
                textColor=colors.HexColor(HELIOS_BLUE),
            )
        )

        styles.add(
            ParagraphStyle(
                name="HeliosBodyText",
                parent=styles["BodyText"],
                fontName="Lato",
                fontSize=9,
                leading=13,
                textColor=colors.HexColor(HELIOS_TEXT),
                spaceAfter=4,
            )
        )

        styles.add(
            ParagraphStyle(
                name="HeliosSubsectionTitle",
                parent=styles["Heading3"],
                fontName="Montserrat-Bold",
                fontSize=11,
                leading=14,
                textColor=colors.HexColor(HELIOS_PURPLE),
                spaceBefore=4,
                spaceAfter=4,
            )
        )

        document = HeliosDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=25 * mm,
            bottomMargin=18 * mm,
        )

        logo = ImageReader(str(HELIOS_LOGO))

        cover_logo_width = 80 * mm
        cover_logo_height = (
            cover_logo_width * 345 / 1170
        )

        toc = TableOfContents()

        toc.levelStyles = [
            ParagraphStyle(
                name="HeliosTocLevel0",
                fontName="Lato-Bold",
                fontSize=10,
                leading=14,
                leftIndent=0,
                firstLineIndent=0,
                spaceBefore=4,
                spaceAfter=4,
                textColor=colors.HexColor(HELIOS_BLUE),
            ),
            ParagraphStyle(
                name="HeliosTocLevel1",
                fontName="Lato",
                fontSize=9,
                leading=12,
                leftIndent=12,
                firstLineIndent=0,
                spaceBefore=2,
                spaceAfter=2,
                textColor=colors.HexColor(HELIOS_TEXT),
            ),
        ]

        story = [

            Spacer(1, 38 * mm),

            FlowableLogo(
                str(HELIOS_LOGO),
                image_width=80 * mm,
                image_height=80 * mm * 345 / 1170,
            ),

            Spacer(1, 10 * mm),

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

                Paragraph(
                    "Índice",
                    styles["HeliosSectionTitle"],
                ),

                HRFlowable(
                    width="100%",
                    thickness=1,
                    color=colors.HexColor(HELIOS_BLUE),
                    spaceBefore=1,
                    spaceAfter=10,
                ),

                toc,
                PageBreak(),
            ]
        )

        story.extend(
            self._build_executive_summary(
                data,
                styles,
            )
        )

        story.extend(
            self._build_energy_situation(
                data,
                styles,
            )
        )

        story.extend(
            self._build_pv_section(
                data,
                styles,
            )
        )

        story.extend(
            self._build_energy_balance(
                data,
                styles,
            )
        )

        story.extend(
            self._build_economic_section(
                data,
                styles,
            )
        )

        story.extend(
            self._build_battery_section(
                data,
                styles,
            )
        )

        story.extend(
            self._build_methodology_section(
                data,
                styles,
            )
        )

        story.extend(
            self._build_conclusion(
                data,
                styles,
            )
        )

        story.extend(
            self._build_glossary(
                data,
                styles,
            )
        )

        document.multiBuild(
            story,
            canvasmaker=NumberedCanvas,
        )