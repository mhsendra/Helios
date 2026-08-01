import pandas as pd

from helios.reports.printer import ReportPrinter


class ConsumptionComparisons:

    def __init__(self):

        self.monthly_comparison = None
        self.monthly_variation = None

        self.weekly_comparison = None
        self.weekly_variation = None

        self.yearly_comparison = None

    def compare_months_by_year(
        self,
        dataset
    ):

        self.monthly_comparison = (
            dataset["AE_kWh"]
            .groupby([
                dataset.index.year,
                dataset.index.month
            ])
            .sum()
            .unstack(level=0)
        )

        self.monthly_comparison.index = [
            "Enero", "Febrero", "Marzo", "Abril",
            "Mayo", "Junio", "Julio", "Agosto",
            "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        self.monthly_comparison.index.name = None
        self.monthly_comparison.columns.name = None

        return self.monthly_comparison

    def compare_years(
        self,
        df
    ):

        self.yearly_comparison = (
            df["AE_kWh"]
            .groupby(df.index.year)
            .sum()
        )

        return self.yearly_comparison

    def compare_weeks_by_year(
        self,
        df
    ):

        iso = df.index.isocalendar()

        self.weekly_comparison = (
            df["AE_kWh"]
            .groupby([
                iso.year,
                iso.week
            ])
            .sum()
            .unstack(level=0)
        )

        self.weekly_comparison.index = [
            f"S{week:02d}"
            for week in self.weekly_comparison.index
        ]

        self.weekly_comparison.index.name = None
        self.weekly_comparison.columns.name = None

        return self.weekly_comparison

    # ==========================================================
    # REPORTS
    # ==========================================================

    def monthly_comparison_report(self, comparison):

        ReportPrinter.title("MONTHLY YEAR COMPARISON")
        ReportPrinter.blank()

        widths = [16] + [12] * len(comparison.columns)

        ReportPrinter.table_header(
            ["Mes"] + [str(y) for y in comparison.columns],
            widths,
            ["left"] + ["right"] * len(comparison.columns)
        )

        for month, row in comparison.iterrows():

            values = [month]

            values.extend([
                "---"
                if pd.isna(v)
                else f"{v:.2f}"
                for v in row
            ])

            ReportPrinter.table_row(
                values,
                widths,
                ["left"] + ["right"] * len(comparison.columns)
            )

    def monthly_variation_report(self, variation):

        ReportPrinter.title("MONTHLY VARIATION REPORT")
        ReportPrinter.blank()

        widths = [16] + [18] * len(variation.columns)

        ReportPrinter.table_header(
            ["Mes"] + list(variation.columns),
            widths,
            ["left"] + ["right"] * len(variation.columns)
        )

        for month, row in variation.iterrows():

            values = [month]

            values.extend([
                "---"
                if pd.isna(v)
                else f"{v:.2f} %"
                for v in row
            ])

            ReportPrinter.table_row(
                values,
                widths,
                ["left"] + ["right"] * len(variation.columns)
            )

    def yearly_comparison_report(self, yearly):

        ReportPrinter.title("YEARLY COMPARISON")
        ReportPrinter.blank()

        widths = [10, 18]

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

    def weekly_comparison_report(self, comparison):

        ReportPrinter.title("WEEKLY YEAR COMPARISON")
        ReportPrinter.blank()

        widths = [10] + [12] * len(comparison.columns)

        ReportPrinter.table_header(
            ["Semana"] + [str(y) for y in comparison.columns],
            widths,
            ["left"] + ["right"] * len(comparison.columns)
        )

        for week, row in comparison.iterrows():

            values = [week]

            values.extend([
                "---"
                if pd.isna(v)
                else f"{v:.2f}"
                for v in row
            ])

            ReportPrinter.table_row(
                values,
                widths,
                ["left"] + ["right"] * len(comparison.columns)
            )

    def weekly_variation_report(self, variation):

        ReportPrinter.title("WEEKLY VARIATION REPORT")
        ReportPrinter.blank()

        widths = [10] + [18] * len(variation.columns)

        ReportPrinter.table_header(
            ["Semana"] + list(variation.columns),
            widths,
            ["left"] + ["right"] * len(variation.columns)
        )

        for week, row in variation.iterrows():

            values = [week]

            values.extend([
                "---"
                if pd.isna(v)
                else f"{v:.2f} %"
                for v in row
            ])

            ReportPrinter.table_row(
                values,
                widths,
                ["left"] + ["right"] * len(variation.columns)
            )

    def calculate_monthly_variation(self):

        self.monthly_variation = self.calculate_variation(
            self.monthly_comparison
        )

        return self.monthly_variation

    def calculate_weekly_variation(self):

        self.weekly_variation = self.calculate_variation(
            self.weekly_comparison
        )

        return self.weekly_variation

    def calculate_variation(
    self,
    comparison
):

        variation = (
            comparison
            .pct_change(axis=1, fill_method=None)
            * 100
        )

        variation = variation.iloc[:, 1:]

        variation.columns = [
            f"{year} vs {year - 1}"
            for year in variation.columns
        ]

        return variation