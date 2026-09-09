import pandas as pd

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing, String
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

    CHART_Y = 60
    CHART_AREA_HEIGHT = 180

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
    def _style_chart(
        cls,
        chart: VerticalBarChart,
    ) -> None:
        """Aplica el estilo común HELIOS al gráfico."""

        # Eje de categorías
        chart.categoryAxis.labels.fontName = cls.FONT_AXIS
        chart.categoryAxis.labels.fontSize = cls.FONT_AXIS_SIZE
        chart.categoryAxis.labels.fillColor = cls.HELIOS_MUTED

        chart.categoryAxis.strokeColor = cls.HELIOS_BORDER
        chart.categoryAxis.strokeWidth = 0.6

        # Eje de valores
        chart.valueAxis.labels.fontName = cls.FONT_AXIS
        chart.valueAxis.labels.fontSize = cls.FONT_AXIS_SIZE
        chart.valueAxis.labels.fillColor = cls.HELIOS_MUTED

        chart.valueAxis.strokeColor = cls.HELIOS_BORDER
        chart.valueAxis.strokeWidth = 0.6

    @classmethod
    def _style_bars(
        cls,
        chart: VerticalBarChart,
        bar_colors,
    ) -> None:
        """Aplica el acabado visual HELIOS a la serie de barras."""

        if not bar_colors:
            return

        chart.bars[0].fillColor = bar_colors[0]
        chart.bars[0].strokeColor = None
        chart.bars[0].strokeWidth = 0

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
        """Genera el gráfico de producción solar anual."""

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
    ) -> Drawing:
        """Genera el gráfico de balance energético anual."""

        values = [
            yearly_production_kwh,
            yearly_consumption_kwh,
            self_consumption_kwh,
            grid_import_kwh,
            grid_export_kwh,
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

        chart = VerticalBarChart()

        chart.x = 45
        chart.y = cls.CHART_Y
        chart.height = cls.CHART_AREA_HEIGHT
        chart.width = 410

        chart.data = [
            values,
        ]

        chart.categoryAxis.categoryNames = [
            "Producción",
            "Consumo",
            "Autoconsumo",
            "Importación",
            "Exportación",
        ]

        maximum = max(values)

        cls._configure_value_axis(
            chart,
            maximum,
        )

        cls._style_chart(chart)

        # Colores individuales por categoría.
        bar_colors = [
            cls.HELIOS_GREEN,
            cls.HELIOS_BLUE,
            cls.HELIOS_GREEN_DARK,
            cls.HELIOS_MUTED,
            cls.HELIOS_GOLD,
        ]

        for index, fill_color in enumerate(bar_colors):
            chart.bars[(0, index)].fillColor = fill_color
            chart.bars[(0, index)].strokeColor = None
            chart.bars[(0, index)].strokeWidth = 0

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