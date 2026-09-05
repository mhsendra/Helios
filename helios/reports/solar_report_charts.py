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

    @staticmethod
    def energy_balance(
        yearly_production_kwh: float,
        yearly_consumption_kwh: float,
        self_consumption_kwh: float,
        grid_import_kwh: float,
        grid_export_kwh: float,
    ) -> Drawing:

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

        drawing = Drawing(
            500,
            300,
        )

        title = String(
            250,
            275,
            "Balance energético anual",
            textAnchor="middle",
            fontSize=16,
        )

        chart = VerticalBarChart()

        chart.x = 45
        chart.y = 60
        chart.height = 180
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

        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = max(
            max(values) * 1.2,
            1,
        )

        chart.valueAxis.valueStep = max(
            max(values) / 5,
            1,
        )

        chart.bars[0].fillColor = colors.HexColor(
            "#7f6000"
        )

        drawing.add(title)
        drawing.add(chart)

        return drawing

    @staticmethod
    def economic_scenarios(
        scenario_results,
    ) -> Drawing:

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

        drawing = Drawing(
            500,
            300,
        )

        title = String(
            250,
            275,
            "Ahorro anual por escenario",
            textAnchor="middle",
            fontSize=16,
        )

        chart = VerticalBarChart()

        chart.x = 60
        chart.y = 60
        chart.height = 180
        chart.width = 390

        chart.data = [
            values,
        ]

        chart.categoryAxis.categoryNames = names

        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = max(
            max(values) * 1.2,
            1,
        )

        chart.valueAxis.valueStep = max(
            max(values) / 5,
            1,
        )

        chart.bars[0].fillColor = colors.HexColor(
            "#7f6000"
        )

        drawing.add(title)
        drawing.add(chart)

        return drawing