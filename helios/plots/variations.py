import pandas as pd


class VariationPlots:

    def __init__(self, plotter):

        self.plotter = plotter

    def plot_monthly_variation(
        self,
        variation: pd.DataFrame
    ):

        self.plotter.plot_variation_bars(
            dataframe=variation,
            title="Variación mensual",
            xlabel="Mes",
            ylabel="Variación (%)"
        )

    def plot_weekly_variation(
        self,
        variation: pd.DataFrame
    ):

        self.plotter.plot_variation_bars(
            dataframe=variation,
            title="Variación semanal",
            xlabel="Semana",
            ylabel="Variación (%)"
        )