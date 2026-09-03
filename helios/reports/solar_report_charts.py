import pandas as pd
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing, String
from reportlab.lib import colors


class SolarReportCharts:
    """Genera los gráficos utilizados en los informes solares."""

    @staticmethod
    def yearly_production(
        production_kwh: float,
    ) -> Drawing:

        if production_kwh < 0:
            raise ValueError(
                "production cannot be negative"
            )

        drawing = Drawing(
            500,
            300,
        )

        title = String(
            250,
            275,
            "Producción solar anual",
            textAnchor="middle",
            fontSize=16,
        )

        chart = VerticalBarChart()

        chart.x = 80
        chart.y = 60
        chart.height = 180
        chart.width = 350

        chart.data = [
            [production_kwh],
        ]

        chart.categoryAxis.categoryNames = [
            "Producción",
        ]

        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = max(
            production_kwh * 1.2,
            1,
        )

        chart.valueAxis.valueStep = max(
            production_kwh / 5,
            1,
        )

        chart.bars[0].fillColor = colors.HexColor(
            "#548235"
        )

        drawing.add(title)
        drawing.add(chart)

        return drawing

    @staticmethod
    def monthly_production(
        monthly_production: pd.Series,
    ) -> Drawing:

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

        drawing = Drawing(
            500,
            300,
        )

        title = String(
            250,
            275,
            "Producción solar mensual",
            textAnchor="middle",
            fontSize=16,
        )

        chart = VerticalBarChart()

        chart.x = 55
        chart.y = 60
        chart.height = 180
        chart.width = 400

        chart.data = [
            monthly_production.tolist(),
        ]

        chart.categoryAxis.categoryNames = [
            date.strftime("%b")
            for date in monthly_production.index
        ]

        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = max(
            float(monthly_production.max()) * 1.2,
            1,
        )

        chart.valueAxis.valueStep = max(
            float(monthly_production.max()) / 5,
            1,
        )

        chart.bars[0].fillColor = colors.HexColor(
            "#548235"
        )

        drawing.add(title)
        drawing.add(chart)

        return drawing