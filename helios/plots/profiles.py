import matplotlib.pyplot as plt
import pandas as pd


class ProfilesPlots:

    def __init__(self, plotter):

        self.plotter = plotter

    def plot_hourly_profile(
        self,
        profile: pd.Series
    ) -> None:

        self.plotter.plot_series(
            series=profile,
            title="Perfil horario de consumo",
            xlabel="Hora",
            ylabel="Consumo medio (kWh)"
        )

        plt.xticks(
            ticks=range(24),
            labels=[str(h) for h in range(24)]
        )

    def plot_weekday_profile(
        self,
        profile: pd.Series
    ) -> None:

        self.plotter.plot_series(
            series=profile,
            title="Perfil semanal de consumo",
            xlabel="Día de la semana",
            ylabel="Consumo medio (kWh)"
        )

        self.plotter.plot_series(
            series=profile,
            title="Perfil laborables / fin de semana",
            xlabel="Tipo de día",
            ylabel="Consumo medio (kWh)"
        )

    def plot_monthly_profile(
        self,
        profile: pd.Series
    ) -> None:

        self.plotter.plot_series(
            series=profile,
            title="Perfil mensual de consumo",
            xlabel="Mes",
            ylabel="Consumo medio (kWh)"
        )

    def plot_seasonal_profile(
        self,
        profile: pd.Series
    ) -> None:

        self.plotter.plot_series(
            series=profile,
            title="Perfil estacional de consumo",
            xlabel="Estación",
            ylabel="Consumo medio (kWh)"
        )