import pandas as pd


class ComparisonPlots:

    def __init__(self, plotter):

        self.plotter = plotter

    def plot_monthly_comparison(
        self,
        comparison: pd.DataFrame
    ):

        self.plotter.plot_comparison_lines(
            dataframe=comparison,
            title="Comparativa mensual",
            xlabel="Mes",
            ylabel="Consumo (kWh)"
        )

    def plot_weekly_comparison(
        self,
        comparison: pd.DataFrame
    ):

        self.plotter.plot_comparison_lines(
            dataframe=comparison,
            title="Comparativa semanal",
            xlabel="Semana",
            ylabel="Consumo (kWh)"
        )

    def plot_yearly_comparison(
        self,
        comparison: pd.Series
    ):

        self.plotter.plot_series(
            series=comparison,
            title="Comparativa anual",
            xlabel="Año",
            ylabel="Consumo (kWh)"
        )