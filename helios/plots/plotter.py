import matplotlib.pyplot as plt
import pandas as pd

from helios.plots.profiles import ProfilesPlots
from helios.plots.comparisons import ComparisonPlots
from helios.plots.variations import VariationPlots


class Plotter:

    def __init__(self):

        self.profiles = ProfilesPlots(self)
        self.comparisons = ComparisonPlots(self)
        self.variations = VariationPlots(self)

    def plot_series(
        self,
        series: pd.Series,
        title: str,
        xlabel: str,
        ylabel: str,
        highlight_max: bool = True,
        highlight_min: bool = True
    ) -> None:

        margin_ratio = 0.10

        fig = plt.figure(figsize=(12, 5))
        fig.canvas.manager.set_window_title(
            f"HELIOS - {title}"
        )

        plt.plot(
            series.index,
            series.values,
            marker="o",
            linewidth=2
        )

        if highlight_max:

            max_x = series.idxmax()
            max_y = series.max()

            plt.scatter(
                max_x,
                max_y,
                color="red",
                s=120,
                zorder=5
            )

            plt.annotate(
                f"{max_x}\n{max_y:.3f}",
                (max_x, max_y),
                xytext=(0, 10),
                textcoords="offset points",
                ha="center"
            )

        if highlight_min:

            min_x = series.idxmin()
            min_y = series.min()

            plt.scatter(
                min_x,
                min_y,
                color="green",
                s=120,
                zorder=5
            )

            plt.annotate(
                f"{min_y:.3f}",
                (min_x, min_y),
                xytext=(0, -18),
                textcoords="offset points",
                ha="center"
            )

        plt.title(title)

        plt.xlabel(xlabel)

        plt.ylabel(ylabel)

        plt.xticks(series.index)

        margin = (
            series.max() - series.min()
        ) * margin_ratio

        plt.ylim(
            series.min() - margin,
            series.max() + margin
        )

        plt.grid(True, alpha=0.3)

        plt.tight_layout()

    def plot_comparison_lines(
        self,
        dataframe: pd.DataFrame,
        title: str,
        xlabel: str,
        ylabel: str
    ) -> None:

        plt.figure(figsize=(12, 5))

        manager = plt.get_current_fig_manager()

        try:

            manager.set_window_title(
                f"HELIOS - {title}"
            )

        except Exception:

            pass

        for column in dataframe.columns:

            plt.plot(
                dataframe.index,
                dataframe[column],
                marker="o",
                linewidth=2,
                label=str(column)
            )

        plt.title(title)

        plt.xlabel(xlabel)

        plt.ylabel(ylabel)

        plt.grid(True, alpha=0.3)

        plt.legend(title="Año")

        plt.xticks(rotation=90)

        plt.tight_layout()

    def plot_variation_bars(
        self,
        dataframe: pd.DataFrame,
        title: str,
        xlabel: str,
        ylabel: str,
        bar_width: float = 0.8,
        bar_spacing: float = 1.0
    ) -> None:

        positive_color = "tab:green"
        negative_color = "tab:red"

        for column in dataframe.columns:

            series = dataframe[column]

            colors = [

                positive_color
                if pd.notna(value) and value >= 0
                else negative_color

                for value in series

            ]

            plt.figure(figsize=(12, 5))

            x = [
                i * bar_spacing
                for i in range(len(series))
            ]

            plt.bar(
                x,
                series.values,
                color=colors,
                width=bar_width
            )

            plt.axhline(
                y=0,
                color="black",
                linewidth=1
            )

            plt.title(
                f"{title} - {column}"
            )

            plt.xlabel(xlabel)

            plt.ylabel(ylabel)

            plt.grid(
                axis="y",
                alpha=0.3
            )

            manager = plt.get_current_fig_manager()

            try:

                manager.set_window_title(
                    f"HELIOS - {title} - {column}"
                )

            except Exception:

                pass

            plt.xticks(
                ticks=x,
                labels=series.index,
                rotation=90
            )

            plt.tight_layout()

    def show(self):

        plt.show()