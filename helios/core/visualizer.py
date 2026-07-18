import matplotlib.pyplot as plt
import pandas as pd


class ConsumptionVisualizer:

    def __init__(self):
        pass

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

        fig=plt.figure(figsize=(12, 5))
        fig.canvas.manager.set_window_title(f"HELIOS - {title}")

        plt.plot(
            series.index,
            series.values,
            marker="o",
            linewidth=2
        )

        # Resaltar máximo
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

        # Resaltar mínimo
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

        margin = (series.max() - series.min()) * margin_ratio

        plt.ylim(
            series.min() - margin,
            series.max() + margin
        )

        plt.grid(True, alpha=0.3)

        plt.tight_layout()

    def show(self):

        plt.show()

    def plot_hourly_profile(self, profile: pd.Series) -> None:

        self.plot_series(
            series=profile,
            title="Perfil horario de consumo",
            xlabel="Hora",
            ylabel="Consumo medio (kWh)"
        )

        plt.xticks(
            ticks=range(24),
            labels=[str(h) for h in range(24)]
        )

    def plot_weekday_profile(self, profile: pd.Series) -> None:

        self.plot_series(
            series=profile,
            title="Perfil semanal de consumo",
            xlabel="Día de la semana",
            ylabel="Consumo medio (kWh)"
        )


    def plot_workweek_profile(self, profile: pd.Series) -> None:

        self.plot_series(
            series=profile,
            title="Perfil laborables / fin de semana",
            xlabel="Tipo de día",
            ylabel="Consumo medio (kWh)"
        )


    def plot_monthly_profile(self, profile: pd.Series) -> None:

        self.plot_series(
            series=profile,
            title="Perfil mensual de consumo",
            xlabel="Mes",
            ylabel="Consumo medio (kWh)"
        )


    def plot_seasonal_profile(self, profile: pd.Series) -> None:

        self.plot_series(
            series=profile,
            title="Perfil estacional de consumo",
            xlabel="Estación",
            ylabel="Consumo medio (kWh)"
        )

    def plot_monthly_comparison(
        self,
        comparison: pd.DataFrame
    ):

        fig = plt.figure(figsize=(12, 5))
        fig.canvas.manager.set_window_title(
            "HELIOS - Comparativa mensual"
        )

        for year in comparison.columns:

            plt.plot(
                comparison.index,
                comparison[year],
                marker="o",
                linewidth=2,
                label=str(year)
            )

        plt.title("Comparativa mensual por años")
        plt.xlabel("Mes")
        plt.ylabel("Consumo (kWh)")

        plt.grid(True, alpha=0.3)

        plt.legend()

        plt.tight_layout()

    def plot_monthly_variation(
        self,
        variation: pd.DataFrame
    ):

        fig = plt.figure(figsize=(12, 5))
        fig.canvas.manager.set_window_title(
            "HELIOS - Variación mensual"
        )

        for column in variation.columns:

            plt.plot(
                variation.index,
                variation[column],
                marker="o",
                linewidth=2,
                label=column
            )

        plt.axhline(
            0,
            color="black",
            linewidth=1
        )

        plt.title("Variación interanual mensual")
        plt.xlabel("Mes")
        plt.ylabel("Variación (%)")

        plt.grid(True, alpha=0.3)

        plt.legend()

        plt.tight_layout()