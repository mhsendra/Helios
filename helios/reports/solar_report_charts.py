import pandas as pd

import math

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing, String, Rect, Line
from reportlab.lib import colors


class SolarReportCharts:
    """Genera los gráficos utilizados en los informes solares."""

    # ------------------------------------------------------------------
    # HELIOS visual system
    # ------------------------------------------------------------------

    CHART_WIDTH = 500
    CHART_HEIGHT = 300

    TITLE_X = 250
    TITLE_Y = 275

    CHART_Y = 55
    CHART_AREA_HEIGHT = 185

    FONT_TITLE = "Montserrat-Bold"
    FONT_AXIS = "Lato"

    FONT_TITLE_SIZE = 15
    FONT_AXIS_SIZE = 8
    FONT_VALUE_SIZE = 8

    HELIOS_BLUE = colors.HexColor("#1f4e78")
    HELIOS_GREEN = colors.HexColor("#548235")
    HELIOS_GREEN_DARK = colors.HexColor("#38761d")
    HELIOS_GOLD = colors.HexColor("#7f6000")
    HELIOS_MUTED = colors.HexColor("#666666")
    HELIOS_BORDER = colors.HexColor("#d0d7de")
    HELIOS_GRID = colors.HexColor("#e8edf2")

    # ------------------------------------------------------------------
    # Common helpers
    # ------------------------------------------------------------------

    @classmethod
    def _create_drawing(cls) -> Drawing:
        """Crea un Drawing con las dimensiones corporativas HELIOS."""

        return Drawing(
            cls.CHART_WIDTH,
            cls.CHART_HEIGHT,
        )

    @classmethod
    def _add_title(
        cls,
        drawing: Drawing,
        title: str,
    ) -> None:
        """Añade el título corporativo común del gráfico."""

        drawing.add(
            String(
                cls.TITLE_X,
                cls.TITLE_Y,
                title,
                textAnchor="middle",
                fontName=cls.FONT_TITLE,
                fontSize=cls.FONT_TITLE_SIZE,
                fillColor=cls.HELIOS_BLUE,
            )
        )

    @classmethod
    def _add_legend(
        cls,
        drawing: Drawing,
        items,
        y: float = 252,
    ) -> None:
        """Añade una leyenda horizontal sencilla."""

        total_width = sum(
            10 + 4 + len(label) * 4.6 + 18
            for label, _ in items
        )

        x = (
            cls.CHART_WIDTH - total_width
        ) / 2

        for label, fill_color in items:

            drawing.add(
                String(
                    x,
                    y,
                    "■",
                    fontName="Helvetica",
                    fontSize=8,
                    fillColor=fill_color,
                )
            )

            x += 10

            drawing.add(
                String(
                    x,
                    y,
                    label,
                    fontName=cls.FONT_AXIS,
                    fontSize=8,
                    fillColor=cls.HELIOS_MUTED,
                )
            )

            x += len(label) * 4.6 + 18

    @classmethod
    def _style_chart(
        cls,
        chart: VerticalBarChart,
        value_format: str = "%0.0f",
    ) -> None:
        """Aplica el estilo común HELIOS al gráfico."""

        chart.categoryAxis.labels.fontName = cls.FONT_AXIS
        chart.categoryAxis.labels.fontSize = cls.FONT_AXIS_SIZE
        chart.categoryAxis.labels.fillColor = cls.HELIOS_MUTED

        chart.categoryAxis.strokeColor = cls.HELIOS_BORDER
        chart.categoryAxis.strokeWidth = 0.6

        chart.valueAxis.labels.fontName = cls.FONT_AXIS
        chart.valueAxis.labels.fontSize = cls.FONT_AXIS_SIZE
        chart.valueAxis.labels.fillColor = cls.HELIOS_MUTED

        chart.valueAxis.strokeColor = cls.HELIOS_BORDER
        chart.valueAxis.strokeWidth = 0.6
        chart.valueAxis.labelTextFormat = value_format

    @classmethod
    def _style_bars(
        cls,
        chart: VerticalBarChart,
        bar_colors,
    ) -> None:
        """Aplica colores a las series de barras."""

        if not bar_colors:
            return

        for series_index, fill_color in enumerate(
            bar_colors
        ):
            if series_index >= len(chart.data):
                break

            for category_index in range(
                len(chart.data[series_index])
            ):
                chart.bars[
                    (series_index, category_index)
                ].fillColor = fill_color

                chart.bars[
                    (series_index, category_index)
                ].strokeColor = None

                chart.bars[
                    (series_index, category_index)
                ].strokeWidth = 0

    @classmethod
    def _configure_value_axis(
        cls,
        chart: VerticalBarChart,
        maximum: float,
    ) -> None:
        """Configura el eje Y de forma homogénea."""

        chart.valueAxis.valueMin = 0

        chart.valueAxis.valueMax = max(
            maximum * 1.2,
            1,
        )

        chart.valueAxis.valueStep = max(
            maximum / 5,
            1,
        )

    # ------------------------------------------------------------------
    # Annual solar production
    # ------------------------------------------------------------------

    @classmethod
    def yearly_production(
        cls,
        production_kwh: float,
    ) -> Drawing:
        """
        Genera el gráfico de producción solar anual.

        Se conserva por compatibilidad con código existente.
        El informe definitivo utiliza el gráfico mensual comparativo.
        """

        if production_kwh < 0:
            raise ValueError(
                "production cannot be negative"
            )

        drawing = cls._create_drawing()

        cls._add_title(
            drawing,
            "Producción solar anual",
        )

        chart = VerticalBarChart()

        chart.x = 80
        chart.y = cls.CHART_Y
        chart.height = cls.CHART_AREA_HEIGHT
        chart.width = 350

        chart.data = [
            [production_kwh],
        ]

        chart.categoryAxis.categoryNames = [
            "Producción",
        ]

        cls._configure_value_axis(
            chart,
            production_kwh,
        )

        cls._style_chart(chart)

        cls._style_bars(
            chart,
            [cls.HELIOS_GREEN],
        )

        drawing.add(chart)

        return drawing

    # ------------------------------------------------------------------
    # Monthly solar production
    # ------------------------------------------------------------------

    @classmethod
    def monthly_production(
        cls,
        monthly_production: pd.Series,
    ) -> Drawing:
        """Genera el gráfico de producción solar mensual."""

        if (
            monthly_production is None
            or monthly_production.empty
        ):
            raise ValueError(
                "monthly production data is required"
            )

        if (
            monthly_production < 0
        ).any():
            raise ValueError(
                "monthly production cannot be negative"
            )

        drawing = cls._create_drawing()

        cls._add_title(
            drawing,
            "Producción solar mensual",
        )

        chart = VerticalBarChart()

        chart.x = 55
        chart.y = cls.CHART_Y
        chart.height = cls.CHART_AREA_HEIGHT
        chart.width = 400

        chart.data = [
            monthly_production.tolist(),
        ]

        chart.categoryAxis.categoryNames = [
            date.strftime("%b")
            for date in monthly_production.index
        ]

        maximum = float(
            monthly_production.max()
        )

        cls._configure_value_axis(
            chart,
            maximum,
        )

        cls._style_chart(chart)

        cls._style_bars(
            chart,
            [cls.HELIOS_GREEN],
        )

        drawing.add(chart)

        return drawing

    # ------------------------------------------------------------------
    # Monthly consumption vs production
    # ------------------------------------------------------------------

    @classmethod
    def monthly_consumption_vs_production(
        cls,
        monthly_consumption: pd.Series,
        monthly_production: pd.Series,
    ) -> Drawing:
        """
        Compara consumo y producción solar mes a mes.

        No realiza ningún cálculo energético: representa directamente
        las dos series recibidas.
        """

        if (
            monthly_consumption is None
            or monthly_consumption.empty
        ):
            raise ValueError(
                "monthly consumption data is required"
            )

        if (
            monthly_production is None
            or monthly_production.empty
        ):
            raise ValueError(
                "monthly production data is required"
            )

        if len(monthly_consumption) != len(
            monthly_production
        ):
            raise ValueError(
                "monthly consumption and production "
                "must have the same length"
            )

        if not monthly_consumption.index.month.equals(
            monthly_production.index.month
        ):
            raise ValueError(
                "monthly consumption and production "
                "must represent the same calendar months "
                "in the same order"
            )

        if (
            monthly_consumption < 0
        ).any():
            raise ValueError(
                "monthly consumption cannot be negative"
            )

        if (
            monthly_production < 0
        ).any():
            raise ValueError(
                "monthly production cannot be negative"
            )

        drawing = cls._create_drawing()

        cls._add_title(
            drawing,
            "Consumo y producción mensual",
        )

        cls._add_legend(
            drawing,
            [
                (
                    "Consumo",
                    cls.HELIOS_BLUE,
                ),
                (
                    "Producción solar",
                    cls.HELIOS_GREEN,
                ),
            ],
        )

        chart = VerticalBarChart()

        chart.x = 48
        chart.y = cls.CHART_Y
        chart.height = cls.CHART_AREA_HEIGHT
        chart.width = 410

        chart.data = [
            monthly_consumption.tolist(),
            monthly_production.tolist(),
        ]

        chart.categoryAxis.categoryNames = [
            date.strftime("%b")
            for date in monthly_production.index
        ]

        maximum = max(
            float(monthly_consumption.max()),
            float(monthly_production.max()),
        )

        cls._configure_value_axis(
            chart,
            maximum,
        )

        cls._style_chart(chart)

        cls._style_bars(
            chart,
            [
                cls.HELIOS_BLUE,
                cls.HELIOS_GREEN,
            ],
        )

        drawing.add(chart)

        return drawing

    # ------------------------------------------------------------------
    # Annual energy balance
    # ------------------------------------------------------------------

    @classmethod
    def energy_balance(
        cls,
        yearly_production_kwh: float,
        yearly_consumption_kwh: float,
        self_consumption_kwh: float,
        grid_import_kwh: float,
        grid_export_kwh: float,
        battery_losses_kwh: float = 0.0,
    ) -> Drawing:
        """Genera el balance energético anual mediante barras apiladas."""

        values = [
            yearly_production_kwh,
            yearly_consumption_kwh,
            self_consumption_kwh,
            grid_import_kwh,
            grid_export_kwh,
            battery_losses_kwh,
        ]

        if any(value < 0 for value in values):
            raise ValueError(
                "energy balance values cannot be negative"
            )

        drawing = cls._create_drawing()

        cls._add_title(
            drawing,
            "Balance energético anual",
        )

        # Cada barra representa un balance independiente:
        # 1. Producción FV = autoconsumo + exportación + pérdidas.
        # 2. Consumo = autoconsumo + importación.
        production_segments = [
            ("Autoconsumo", self_consumption_kwh, cls.HELIOS_GREEN_DARK),
            ("Vertido a red", grid_export_kwh, cls.HELIOS_GOLD),
            ("Pérdidas batería", battery_losses_kwh, cls.HELIOS_MUTED),
        ]

        consumption_segments = [
            ("Autoconsumo", self_consumption_kwh, cls.HELIOS_GREEN_DARK),
            ("Importación de red", grid_import_kwh, cls.HELIOS_BLUE),
        ]

        production_total = sum(
            value for _, value, _ in production_segments
        )
        consumption_total = sum(
            value for _, value, _ in consumption_segments
        )

        # Área de dibujo.
        left = 105
        right = 455
        bottom = 83
        top = 225
        bar_width = 72
        bar_positions = [190, 365]

        maximum = max(
            yearly_production_kwh,
            yearly_consumption_kwh,
            production_total,
            consumption_total,
            1.0,
        )
        scale_maximum = maximum * 1.15
        plot_height = top - bottom
        scale = plot_height / scale_maximum

        # Eje vertical y líneas de referencia.
        drawing.add(
            Line(
                left,
                bottom,
                left,
                top,
                strokeColor=cls.HELIOS_BORDER,
                strokeWidth=0.7,
            )
        )
        drawing.add(
            Line(
                left,
                bottom,
                right,
                bottom,
                strokeColor=cls.HELIOS_BORDER,
                strokeWidth=0.7,
            )
        )

        for tick in range(6):
            tick_value = scale_maximum * tick / 5
            y = bottom + tick_value * scale

            drawing.add(
                Line(
                    left,
                    y,
                    right,
                    y,
                    strokeColor=cls.HELIOS_GRID,
                    strokeWidth=0.5,
                )
            )
            drawing.add(
                String(
                    left - 8,
                    y - 3,
                    f"{tick_value:,.0f}",
                    textAnchor="end",
                    fontName=cls.FONT_AXIS,
                    fontSize=cls.FONT_AXIS_SIZE,
                    fillColor=cls.HELIOS_MUTED,
                )
            )

        drawing.add(
            String(
                25,
                (bottom + top) / 2,
                "kWh",
                fontName=cls.FONT_AXIS,
                fontSize=cls.FONT_AXIS_SIZE,
                fillColor=cls.HELIOS_MUTED,
            )
        )

        # Dibuja los segmentos apilados de cada barra.
        for x, segments, total, label in [
            (
                bar_positions[0],
                production_segments,
                production_total,
                "Producción FV",
            ),
            (
                bar_positions[1],
                consumption_segments,
                consumption_total,
                "Consumo vivienda",
            ),
        ]:
            current_y = bottom

            for segment_label, segment_value, segment_color in segments:
                segment_height = segment_value * scale

                if segment_height > 0:
                    drawing.add(
                        Rect(
                            x - bar_width / 2,
                            current_y,
                            bar_width,
                            segment_height,
                            fillColor=segment_color,
                            strokeColor=None,
                        )
                    )

                    # Etiqueta interna solo si hay espacio suficiente.
                    if segment_height >= 16:
                        drawing.add(
                            String(
                                x,
                                current_y + segment_height / 2 - 3,
                                f"{segment_value:,.0f}",
                                textAnchor="middle",
                                fontName=cls.FONT_AXIS,
                                fontSize=cls.FONT_AXIS_SIZE,
                                fillColor=colors.white,
                            )
                        )

                current_y += segment_height

            drawing.add(
                String(
                    x,
                    current_y + 5,
                    f"{total:,.0f} kWh",
                    textAnchor="middle",
                    fontName=cls.FONT_AXIS,
                    fontSize=cls.FONT_VALUE_SIZE,
                    fillColor=cls.HELIOS_BLUE,
                )
            )

            drawing.add(
                String(
                    x,
                    bottom - 17,
                    label,
                    textAnchor="middle",
                    fontName=cls.FONT_AXIS,
                    fontSize=cls.FONT_AXIS_SIZE,
                    fillColor=cls.HELIOS_MUTED,
                )
            )

        # Leyenda inferior.
        legend_items = [
            ("Autoconsumo", cls.HELIOS_GREEN_DARK),
            ("Vertido a red", cls.HELIOS_GOLD),
            ("Pérdidas batería", cls.HELIOS_MUTED),
            ("Importación de red", cls.HELIOS_BLUE),
        ]

        legend_positions = [
            (95, 35),
            (205, 35),
            (325, 35),
            (95, 19),
        ]

        for (label, color), (x, y) in zip(
            legend_items,
            legend_positions,
        ):
            drawing.add(
                Rect(
                    x,
                    y,
                    8,
                    8,
                    fillColor=color,
                    strokeColor=None,
                )
            )
            drawing.add(
                String(
                    x + 12,
                    y + 1,
                    label,
                    fontName=cls.FONT_AXIS,
                    fontSize=cls.FONT_AXIS_SIZE,
                    fillColor=cls.HELIOS_MUTED,
                )
            )

        return drawing

    @classmethod
    def pv_production_allocation(
        cls,
        yearly_production_kwh: float,
        self_consumption_kwh: float,
        grid_export_kwh: float,
        battery_losses_kwh: float,
    ) -> Drawing:
        """Muestra el reparto anual de la producción fotovoltaica."""

        values = [
            self_consumption_kwh,
            grid_export_kwh,
            battery_losses_kwh,
            yearly_production_kwh,
        ]

        if any(
            value < 0 or not math.isfinite(value)
            for value in values
        ):
            raise ValueError(
                "PV production allocation values must be "
                "finite and non-negative"
            )

        drawing = cls._create_drawing()

        cls._add_title(
            drawing,
            "Reparto de la producción fotovoltaica",
        )

        chart = VerticalBarChart()
        chart.x = 45
        chart.y = cls.CHART_Y
        chart.height = cls.CHART_AREA_HEIGHT
        chart.width = 410

        chart.data = [values]

        chart.categoryAxis.categoryNames = [
            "Autoconsumo",
            "Excedentes",
            "Pérdidas batería",
            "Producción total",
        ]

        cls._configure_value_axis(
            chart,
            max(values),
        )

        cls._style_chart(chart)

        cls._style_bars(
            chart,
            [
                cls.HELIOS_GREEN_DARK,
                cls.HELIOS_GOLD,
                cls.HELIOS_MUTED,
                cls.HELIOS_GREEN,
            ],
        )

        drawing.add(chart)

        return drawing

    # ------------------------------------------------------------------
    # Economic scenarios
    # ------------------------------------------------------------------

    @classmethod
    def economic_scenarios(
        cls,
        scenario_results,
    ) -> Drawing:
        """Genera el gráfico de ahorro anual por escenario."""

        if (
            scenario_results is None
            or not scenario_results
        ):
            raise ValueError(
                "economic scenario data is required"
            )

        names = [
            scenario.name
            for scenario in scenario_results
        ]

        values = [
            scenario.annual_savings
            for scenario in scenario_results
        ]

        if any(value < 0 for value in values):
            raise ValueError(
                "annual savings cannot be negative"
            )

        drawing = cls._create_drawing()

        cls._add_title(
            drawing,
            "Ahorro anual por escenario",
        )

        chart = VerticalBarChart()

        chart.x = 60
        chart.y = cls.CHART_Y
        chart.height = cls.CHART_AREA_HEIGHT
        chart.width = 390

        chart.data = [
            values,
        ]

        chart.categoryAxis.categoryNames = names

        maximum = max(values)

        cls._configure_value_axis(
            chart,
            maximum,
        )

        cls._style_chart(chart)

        cls._style_bars(
            chart,
            [cls.HELIOS_GOLD],
        )

        drawing.add(chart)

        return drawing

    # ------------------------------------------------------------------
    # Battery marginal economics
    # ------------------------------------------------------------------

    @classmethod
    def battery_marginal_savings(
        cls,
        battery_recommendations,
    ) -> Drawing:
        """
        Representa el ahorro marginal por kWh de capacidad instalada.

        Los valores negativos son válidos y representan un resultado
        marginal desfavorable. El eje vertical incluye el cero.
        """

        if (
            battery_recommendations is None
            or not battery_recommendations
        ):
            raise ValueError(
                "battery recommendation data is required"
            )

        names = [
            f"{recommendation.capacity_kwh:.1f}"
            for recommendation
            in battery_recommendations
        ]

        values = [
            float(recommendation.marginal_savings_per_kwh)
            for recommendation
            in battery_recommendations
        ]

        drawing = cls._create_drawing()

        cls._add_title(
            drawing,
            "Ahorro marginal según capacidad de batería",
        )

        chart = VerticalBarChart()

        chart.x = 55
        chart.y = cls.CHART_Y
        chart.height = cls.CHART_AREA_HEIGHT
        chart.width = 400

        chart.data = [values]
        chart.categoryAxis.categoryNames = names

        minimum = min(values)
        maximum = max(values)

        # Incluye el cero y deja margen visual a ambos extremos.
        axis_min = min(minimum * 1.2, 0)
        axis_max = max(maximum * 1.2, 0)

        if axis_min == axis_max:
            axis_min = -1
            axis_max = 1

        chart.valueAxis.valueMin = axis_min
        chart.valueAxis.valueMax = axis_max
        chart.valueAxis.valueStep = max(
            (axis_max - axis_min) / 5,
            0.1,
        )

        cls._style_chart(
            chart,
            value_format="%0.1f",
        )

        cls._style_bars(
            chart,
            [cls.HELIOS_GOLD],
        )

        drawing.add(chart)

        drawing.add(
            String(
                250,
                28,
                "Capacidad de batería (kWh)",
                textAnchor="middle",
                fontName=cls.FONT_AXIS,
                fontSize=8,
                fillColor=cls.HELIOS_MUTED,
            )
        )

        drawing.add(
            String(
                12,
                150,
                "€/kWh",
                textAnchor="middle",
                fontName=cls.FONT_AXIS,
                fontSize=8,
                fillColor=cls.HELIOS_MUTED,
            )
        )

        return drawing
