import pandas as pd


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

        print()
        print("=============================================")
        print("HELIOS - MONTHLY YEAR COMPARISON")
        print("=============================================")
        print()

        # Cabecera
        print(f"{'Mes':<12}", end="")

        for year in comparison.columns:
            print(f"{year:>12}", end="")

        print()
        print("-" * (12 + 12 * len(comparison.columns)))

        # Filas
        for month, row in comparison.iterrows():

            print(f"{month:<12}", end="")

            for value in row:

                if pd.isna(value):
                    print(f"{'---':>12}", end="")
                else:
                    print(f"{value:>12.2f}", end="")

            print()

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

        print()
        print("=============================================")
        print("HELIOS - MONTHLY VARIATION REPORT")
        print("=============================================")
        print()

        # Cabecera
        print(f"{'Mes':<12}", end="")

        for column in variation.columns:
            print(f"{column:>18}", end="")

        print()
        print("-" * (12 + 18 * len(variation.columns)))

        # Datos
        for month, row in variation.iterrows():

            print(f"{month:<12}", end="")

            for value in row:

                if pd.isna(value):
                    print(f"{'---':>18}", end="")
                else:
                    print(f"{value:>17.2f}%", end="")

            print()

    def compare_years(self, df):

        comparison = (
            df["AE_kWh"]
            .groupby(df.index.year)
            .sum()
        )

        return comparison
    
    def yearly_comparison_report(self, comparison):

        print()
        print("=============================================")
        print("HELIOS - YEARLY COMPARISON")
        print("=============================================")
        print()

        print(f"{'Año':<10}{'Consumo':>15}")
        print("-" * 25)

        for year, value in comparison.items():

            print(f"{year:<10}{value:>15.2f} kWh")

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

        print()
        print("=============================================")
        print("HELIOS - WEEKLY YEAR COMPARISON")
        print("=============================================")
        print()

        # Cabecera
        print(f"{'Semana':<10}", end="")

        for year in comparison.columns:
            print(f"{year:>12}", end="")

        print()

        print("-" * (10 + 12 * len(comparison.columns)))

        # Datos
        for week, row in comparison.iterrows():

            print(f"{week:<10}", end="")

            for value in row:

                if pd.isna(value):
                    print(f"{'---':>12}", end="")
                else:
                    print(f"{value:>12.2f}", end="")

            print()

    def weekly_variation_report(self, variation):

        print()
        print("=============================================")
        print("HELIOS - WEEKLY VARIATION REPORT")
        print("=============================================")
        print()

        print(f"{'Semana':<10}", end="")

        for column in variation.columns:
            print(f"{column:>18}", end="")

        print()
        print("-" * (10 + 18 * len(variation.columns)))

        for week, row in variation.iterrows():

            print(f"{week:<10}", end="")

            for value in row:

                if pd.isna(value):
                    print(f"{'---':>18}", end="")
                else:
                    print(f"{value:>17.2f}%", end="")

            print()