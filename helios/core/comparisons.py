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

    def detailed_weekly_insights(self):
        weekly = self.weekly_comparison

        # (semana, año)
        max_week = weekly.stack().idxmax()
        min_week = weekly.stack().idxmin()

        max_value = weekly.loc[max_week[0], max_week[1]]
        min_value = weekly.loc[min_week[0], min_week[1]]

        # Variación respecto al año anterior
        prev_year = max_week[1] - 1
        if prev_year in weekly.columns:
            prev_value = weekly.loc[max_week[0], prev_year]
            variation_prev = ((max_value - prev_value) / prev_value) * 100
        else:
            variation_prev = None

        # Media del año
        mean_year = weekly[max_week[1]].mean()
        variation_mean = ((max_value - mean_year) / mean_year) * 100

        return {
            "max": {
                "week": max_week[0],
                "year": max_week[1],
                "value": max_value,
                "variation_prev": variation_prev,
                "variation_mean": variation_mean
            },
            "min": {
                "week": min_week[0],
                "year": min_week[1],
                "value": min_value
            }
        }

    def monthly_trends(self):
        monthly = self.monthly_comparison

        trends = {}

        for year in monthly.columns:
            series = monthly[year].dropna()

            diffs = series.diff().dropna()

            positive = (diffs > 0).sum()
            negative = (diffs < 0).sum()

            if positive == len(diffs):
                classification = "Creciente"
            elif negative == len(diffs):
                classification = "Decreciente"
            else:
                classification = "Irregular"

            trends[year] = {
                "classification": classification,
                "positive_steps": positive,
                "negative_steps": negative,
                "max_increase": diffs.max(),
                "max_decrease": diffs.min()
            }

        return trends

    def weekly_trends(self):
        weekly = self.weekly_comparison

        trends = {}

        for year in weekly.columns:
            series = weekly[year].dropna()

            diffs = series.diff().dropna()

            positive = (diffs > 0).sum()
            negative = (diffs < 0).sum()

            if positive == len(diffs):
                classification = "Creciente"
            elif negative == len(diffs):
                classification = "Decreciente"
            else:
                classification = "Irregular"

            trends[year] = {
                "classification": classification,
                "positive_steps": positive,
                "negative_steps": negative,
                "max_increase": diffs.max(),
                "max_decrease": diffs.min()
            }

        return trends

    def yearly_trend(self):
        yearly = self.yearly_comparison

        diffs = yearly.diff().dropna()

        positive = (diffs > 0).sum()
        negative = (diffs < 0).sum()

        if positive == len(diffs):
            classification = "Creciente"
        elif negative == len(diffs):
            classification = "Decreciente"
        else:
            classification = "Irregular"

        return {
            "classification": classification,
            "positive_steps": positive,
            "negative_steps": negative,
            "max_increase": diffs.max(),
            "max_decrease": diffs.min()
        }

    def detect_monthly_anomalies(self):
        monthly = self.monthly_comparison
        variation = self.monthly_variation  # 2025 vs 2024, 2026 vs 2025

        anomalies = []

        # 1. Variaciones extremas (> 50% o < -50%)
        for col in variation.columns:
            for month, value in variation[col].items():
                if pd.isna(value):
                    anomalies.append({
                        "type": "missing",
                        "month": month,
                        "year": col.split(" vs ")[1],
                        "detail": "Valor faltante"
                    })
                elif value > 50:
                    anomalies.append({
                        "type": "extreme_increase",
                        "month": month,
                        "year": col.split(" vs ")[1],
                        "value": value,
                        "detail": f"Aumento extremo (+{value:.2f}%)"
                    })
                elif value < -50:
                    anomalies.append({
                        "type": "extreme_decrease",
                        "month": month,
                        "year": col.split(" vs ")[1],
                        "value": value,
                        "detail": f"Caída extrema ({value:.2f}%)"
                    })

        # 2. Picos y valles estadísticos
        for year in monthly.columns:
            series = monthly[year].dropna()
            mean = series.mean()
            std = series.std()

            for month, value in series.items():
                if value > mean + 2 * std:
                    anomalies.append({
                        "type": "statistical_peak",
                        "month": month,
                        "year": year,
                        "value": value,
                        "detail": "Pico estadístico (> 2σ)"
                    })
                elif value < mean - 2 * std:
                    anomalies.append({
                        "type": "statistical_valley",
                        "month": month,
                        "year": year,
                        "value": value,
                        "detail": "Valle estadístico (< -2σ)"
                    })

        return anomalies

    def annual_stability(self):
        monthly = self.monthly_comparison

        stability = {}

        for year in monthly.columns:
            series = monthly[year].dropna()

            min_val = series.min()
            max_val = series.max()
            range_val = max_val - min_val

            std_val = series.std()
            mean_val = series.mean()

            cv = std_val / mean_val if mean_val != 0 else None

            # Clasificación
            if cv is None:
                classification = "Indeterminado"
            elif cv < 0.10:
                classification = "Muy estable"
            elif cv < 0.25:
                classification = "Estable"
            elif cv < 0.40:
                classification = "Moderadamente inestable"
            else:
                classification = "Muy inestable"

            stability[year] = {
                "min": min_val,
                "max": max_val,
                "range": range_val,
                "std": std_val,
                "cv": cv,
                "classification": classification
            }

        return stability

    def monthly_stability(self):
        monthly = self.monthly_comparison

        stability = {}

        # Para cada mes (fila)
        for month, row in monthly.iterrows():
            series = row.dropna()

            if len(series) < 2:
                # No se puede calcular estabilidad con un solo año
                stability[month] = {
                    "std": None,
                    "cv": None,
                    "classification": "Indeterminado"
                }
                continue

            std_val = series.std()
            mean_val = series.mean()
            cv = std_val / mean_val if mean_val != 0 else None

            # Clasificación
            if cv is None:
                classification = "Indeterminado"
            elif cv < 0.10:
                classification = "Muy estable"
            elif cv < 0.25:
                classification = "Estable"
            elif cv < 0.40:
                classification = "Moderadamente volátil"
            else:
                classification = "Muy volátil"

            stability[month] = {
                "std": std_val,
                "cv": cv,
                "classification": classification
            }

        return stability

    def monthly_stability_extremes(self):
        stability = self.monthly_stability()

        # Filtrar meses con CV válido
        valid = {m: s for m, s in stability.items() if s["cv"] is not None}

        if not valid:
            return None

        # Mes más estable → menor CV
        most_stable = min(valid.items(), key=lambda x: x[1]["cv"])
        # Mes más volátil → mayor CV
        most_volatile = max(valid.items(), key=lambda x: x[1]["cv"])

        return {
            "stable": {
                "month": most_stable[0],
                "cv": most_stable[1]["cv"],
                "std": most_stable[1]["std"],
                "classification": most_stable[1]["classification"]
            },
            "volatile": {
                "month": most_volatile[0],
                "cv": most_volatile[1]["cv"],
                "std": most_volatile[1]["std"],
                "classification": most_volatile[1]["classification"]
            }
        }

    def weekly_stability(self):
        weekly = self.weekly_comparison

        stability = {}

        # Para cada semana (fila)
        for week, row in weekly.iterrows():
            series = row.dropna()

            if len(series) < 2:
                stability[week] = {
                    "std": None,
                    "cv": None,
                    "classification": "Indeterminado"
                }
                continue

            std_val = series.std()
            mean_val = series.mean()
            cv = std_val / mean_val if mean_val != 0 else None

            # Clasificación
            if cv is None:
                classification = "Indeterminado"
            elif cv < 0.10:
                classification = "Muy tranquila"
            elif cv < 0.25:
                classification = "Tranquila"
            elif cv < 0.40:
                classification = "Moderadamente crítica"
            else:
                classification = "Muy crítica"

            stability[week] = {
                "std": std_val,
                "cv": cv,
                "classification": classification
            }

        return stability

    def weekly_stability_extremes(self):
        stability = self.weekly_stability()

        valid = {w: s for w, s in stability.items() if s["cv"] is not None}

        if not valid:
            return None

        # Semana más tranquila → menor CV
        most_stable = min(valid.items(), key=lambda x: x[1]["cv"])
        # Semana más crítica → mayor CV
        most_volatile = max(valid.items(), key=lambda x: x[1]["cv"])

        return {
            "stable": {
                "week": most_stable[0],
                "cv": most_stable[1]["cv"],
                "std": most_stable[1]["std"],
                "classification": most_stable[1]["classification"]
            },
            "volatile": {
                "week": most_volatile[0],
                "cv": most_volatile[1]["cv"],
                "std": most_volatile[1]["std"],
                "classification": most_volatile[1]["classification"]
            }
        }
