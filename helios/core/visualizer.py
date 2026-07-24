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
        plt.xticks(series.index)
        plt.ylabel(ylabel)

        margin = (series.max() - series.min()) * margin_ratio

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
                f"Helios - {title}"
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
        ylabel: str
    ) -> None:

        positive_color = "tab:green"
        negative_color = "tab:red"

        for column in dataframe.columns:

            series = dataframe[column]

            colors = [
                positive_color if pd.notna(value) and value >= 0
                else negative_color
                for value in series
            ]

            plt.figure(figsize=(12, 5))

            x = list(range(len(series)))

            plt.bar(
                x,
                series.values,
                color=colors
            )

            plt.axhline(
                y=0,
                color="black",
                linewidth=1
            )

            plt.title(f"{title} - {column}")

            plt.xlabel(xlabel)

            plt.ylabel(ylabel)

            plt.grid(
                axis="y",
                alpha=0.3
            )

            manager = plt.get_current_fig_manager()

            try:
                manager.set_window_title(
                    f"Helios - {title} - {column}"
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
    ) -> None:

        self.plot_comparison_lines(
            dataframe=comparison,
            title="Comparativa mensual",
            xlabel="Mes",
            ylabel="Consumo (kWh)"
        )

    def plot_monthly_variation(
        self,
        variation: pd.DataFrame
    ) -> None:

        self.plot_variation_bars(
            dataframe=variation,
            title="Variación mensual",
            xlabel="Mes",
            ylabel="Variación (%)"
        )

    def plot_yearly_comparison(
    self,
    comparison: pd.Series
):

        self.plot_series(
            series=comparison,
            title="Comparativa anual",
            xlabel="Año",
            ylabel="Consumo (kWh)"
        )
    def plot_weekly_comparison(
        self,
        comparison: pd.DataFrame
    ) -> None:

        self.plot_comparison_lines(
            dataframe=comparison,
            title="Comparativa semanal",
            xlabel="Semana",
            ylabel="Consumo (kWh)"
        )

    def plot_weekly_variation(
        self,
        variation: pd.DataFrame
    ) -> None:

        self.plot_variation_bars(
            dataframe=variation,
            title="Variación semanal",
            xlabel="Semana",
            ylabel="Variación (%)"
        )