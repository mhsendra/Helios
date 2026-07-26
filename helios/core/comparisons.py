import pandas as pd
from helios.reports.printer import ReportPrinter


class ConsumptionComparisons:

    def __init__(self):
        pass

    def compare_months_by_year(self, df):

        comparison = (
            df["AE_kWh"]
            .groupby([
                df.index.year,
                df.index.month
            ])
            .sum()
            .unstack(level=0)
        )

        comparison.index = [
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre"
        ]

        comparison.index.name = None
        comparison.columns.name = None

        return comparison
    
    def monthly_comparison_report(self, comparison):

        ReportPrinter.title(
            "MONTHLY YEAR COMPARISON"
        )

        ReportPrinter.blank()

        widths = [16] + [12] * len(comparison.columns)

        ReportPrinter.table_header(
            ["Mes"] + [str(year) for year in comparison.columns],
            widths,
            ["left"] + ["right"] * len(comparison.columns)
        )

        for month, row in comparison.iterrows():

            values = [month]

            for value in row:

                if pd.isna(value):
                    values.append("---")
                else:
                    values.append(f"{value:.2f}")

            ReportPrinter.table_row(
                values,
                widths,
                ["left"] + ["right"] * len(comparison.columns)
            )

    def calculate_variation(self, comparison):

        variation = comparison.pct_change(
            axis=1,
            fill_method=None
        ) * 100

        variation = variation.iloc[:, 1:]

        variation.columns = [
            f"{year} vs {year - 1}"
            for year in variation.columns
        ]

        return variation
    
    def monthly_variation_report(self, variation):

        ReportPrinter.title(
            "MONTHLY VARIATION REPORT"
        )

        ReportPrinter.blank()

        widths = [16] + [18] * len(variation.columns)

        ReportPrinter.table_header(
            ["Mes"] + list(variation.columns),
            widths,
            ["left"] + ["right"] * len(variation.columns)
        )

        for month, row in variation.iterrows():

            values = [month]

            for value in row:

                if pd.isna(value):
                    values.append("---")
                else:
                    values.append(f"{value:.2f}%")

            ReportPrinter.table_row(
                values,
                widths,
                ["left"] + ["right"] * len(variation.columns)
            )
    def compare_years(self, df):

        comparison = (
            df["AE_kWh"]
            .groupby(df.index.year)
            .sum()
        )

        return comparison
    
    def yearly_comparison_report(self, yearly):

        ReportPrinter.title(
            "YEARLY COMPARISON"
        )

        ReportPrinter.blank()

        widths = [10, 16]

        ReportPrinter.table_header(
            ["Año", "Consumo"],
            widths,
            ["left", "right"]
        )

        for year, value in yearly.items():

            ReportPrinter.table_row(
                [
                    str(year),
                    f"{value:.2f} kWh"
                ],
                widths,
                ["left", "right"]
            )

    def compare_weeks_by_year(self, df):

        iso = df.index.isocalendar()

        comparison = (
            df["AE_kWh"]
            .groupby([
                iso.year,
                iso.week
            ])
            .sum()
            .unstack(level=0)
        )

        comparison.index = [
            f"S{week:02d}"
            for week in comparison.index
        ]

        comparison.index.name = None
        comparison.columns.name = None

        return comparison
    
    def weekly_comparison_report(self, comparison):

        ReportPrinter.title(
            "WEEKLY YEAR COMPARISON"
        )

        ReportPrinter.blank()

        widths = [10] + [12] * len(comparison.columns)

        ReportPrinter.table_header(
            ["Semana"] + [str(year) for year in comparison.columns],
            widths,
            ["left"] + ["right"] * len(comparison.columns)
        )

        for week, row in comparison.iterrows():

            values = [week]

            for value in row:

                if pd.isna(value):
                    values.append("---")
                else:
                    values.append(f"{value:.2f}")

            ReportPrinter.table_row(
                values,
                widths,
                ["left"] + ["right"] * len(comparison.columns)
            )

    def weekly_variation_report(self, variation):

        ReportPrinter.title(
            "WEEKLY VARIATION REPORT"
        )

        ReportPrinter.blank()

        widths = [10] + [18] * len(variation.columns)

        ReportPrinter.table_header(
            ["Semana"] + list(variation.columns),
            widths,
            ["left"] + ["right"] * len(variation.columns)
        )

        for week, row in variation.iterrows():

            values = [week]

            for value in row:

                if pd.isna(value):
                    values.append("---")
                else:
                    values.append(f"{value:.2f}%")

            ReportPrinter.table_row(
                values,
                widths,
                ["left"] + ["right"] * len(variation.columns)
            )