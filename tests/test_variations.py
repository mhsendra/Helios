from unittest.mock import Mock

import pandas as pd

from helios.plots.variations import VariationPlots


def test_plot_monthly_variation():

    plotter = Mock()
    variation_plots = VariationPlots(plotter)

    variation = pd.DataFrame(
        {
            "Variación (%)": [10.0, -5.0]
        },
        index=["Enero", "Febrero"]
    )

    variation_plots.plot_monthly_variation(
        variation
    )

    plotter.plot_variation_bars.assert_called_once_with(
        dataframe=variation,
        title="Variación mensual",
        xlabel="Mes",
        ylabel="Variación (%)"
    )


def test_plot_weekly_variation():

    plotter = Mock()
    variation_plots = VariationPlots(plotter)

    variation = pd.DataFrame(
        {
            "Variación (%)": [10.0, -5.0]
        },
        index=["Semana 1", "Semana 2"]
    )

    variation_plots.plot_weekly_variation(
        variation
    )

    plotter.plot_variation_bars.assert_called_once_with(
        dataframe=variation,
        title="Variación semanal",
        xlabel="Semana",
        ylabel="Variación (%)"
    )