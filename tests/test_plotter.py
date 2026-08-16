import pandas as pd
from unittest.mock import MagicMock, patch

from helios.plots.plotter import Plotter


class TestPlotter:

    # ==================================================
    # Inicialización
    # ==================================================

    def test_initial_state(self):

        plotter = Plotter()

        assert plotter.profiles is not None
        assert plotter.comparisons is not None
        assert plotter.variations is not None

        assert plotter.profiles.plotter is plotter
        assert plotter.comparisons.plotter is plotter
        assert plotter.variations.plotter is plotter

    # ==================================================
    # plot_series
    # ==================================================

    @patch("helios.plots.plotter.plt")
    def test_plot_series(self, plt):

        series = pd.Series(
            [10.0, 20.0, 15.0],
            index=["A", "B", "C"]
        )

        fig = MagicMock()
        manager = MagicMock()

        fig.canvas.manager = manager
        plt.figure.return_value = fig

        plotter = Plotter()

        plotter.plot_series(
            series=series,
            title="Prueba",
            xlabel="X",
            ylabel="Y"
        )

        plt.figure.assert_called_once_with(
            figsize=(12, 5)
        )

        manager.set_window_title.assert_called_once_with(
            "HELIOS - Prueba"
        )

        assert plt.plot.call_count == 1

        plot_call = plt.plot.call_args

        assert plot_call.args[0].equals(series.index)
        assert (plot_call.args[1] == series.values).all()

        assert plot_call.kwargs == {
            "marker": "o",
            "linewidth": 2
        }

        assert plt.scatter.call_count == 2
        assert plt.annotate.call_count == 2

        plt.title.assert_called_once_with(
            "Prueba"
        )

        plt.xlabel.assert_called_once_with(
            "X"
        )

        plt.ylabel.assert_called_once_with(
            "Y"
        )

        plt.xticks.assert_called_once_with(
            series.index
        )

        plt.ylim.assert_called_once_with(
            9.0,
            21.0
        )

        plt.grid.assert_called_once_with(
            True,
            alpha=0.3
        )

        plt.tight_layout.assert_called_once()

    # ==================================================
    # plot_series sin máximos
    # ==================================================

    @patch("helios.plots.plotter.plt")
    def test_plot_series_without_highlights(self, plt):

        series = pd.Series(
            [10.0, 20.0, 15.0],
            index=["A", "B", "C"]
        )

        fig = MagicMock()
        manager = MagicMock()

        fig.canvas.manager = manager
        plt.figure.return_value = fig

        plotter = Plotter()

        plotter.plot_series(
            series=series,
            title="Prueba",
            xlabel="X",
            ylabel="Y",
            highlight_max=False,
            highlight_min=False
        )

        plt.scatter.assert_not_called()
        plt.annotate.assert_not_called()

        plt.plot.assert_called_once()

    # ==================================================
    # plot_comparison_lines
    # ==================================================

    @patch("helios.plots.plotter.plt")
    def test_plot_comparison_lines(self, plt):

        dataframe = pd.DataFrame(
            {
                2024: [100.0, 120.0],
                2025: [110.0, 130.0],
            },
            index=["Enero", "Febrero"]
        )

        manager = MagicMock()

        plt.get_current_fig_manager.return_value = manager

        plotter = Plotter()

        plotter.plot_comparison_lines(
            dataframe=dataframe,
            title="Comparativa",
            xlabel="Mes",
            ylabel="Consumo"
        )

        plt.figure.assert_called_once_with(
            figsize=(12, 5)
        )

        manager.set_window_title.assert_called_once_with(
            "HELIOS - Comparativa"
        )

        assert plt.plot.call_count == 2

        calls = plt.plot.call_args_list

        assert calls[0].args[0].equals(
            dataframe.index
        )

        assert calls[0].args[1].equals(
            dataframe[2024]
        )

        assert calls[0].kwargs == {
            "marker": "o",
            "linewidth": 2,
            "label": "2024"
        }

        assert calls[1].args[0].equals(
            dataframe.index
        )

        assert calls[1].args[1].equals(
            dataframe[2025]
        )

        assert calls[1].kwargs == {
            "marker": "o",
            "linewidth": 2,
            "label": "2025"
        }

        plt.title.assert_called_once_with(
            "Comparativa"
        )

        plt.xlabel.assert_called_once_with(
            "Mes"
        )

        plt.ylabel.assert_called_once_with(
            "Consumo"
        )

        plt.grid.assert_called_once_with(
            True,
            alpha=0.3
        )

        plt.legend.assert_called_once_with(
            title="Año"
        )

        plt.xticks.assert_called_once_with(
            rotation=90
        )

        plt.tight_layout.assert_called_once()

    # ==================================================
    # plot_comparison_lines - error ventana
    # ==================================================

    @patch("helios.plots.plotter.plt")
    def test_plot_comparison_lines_handles_window_error(
        self,
        plt
    ):

        dataframe = pd.DataFrame(
            {
                2024: [100.0, 120.0],
            },
            index=["Enero", "Febrero"]
        )

        manager = MagicMock()

        manager.set_window_title.side_effect = Exception(
            "Window error"
        )

        plt.get_current_fig_manager.return_value = manager

        plotter = Plotter()

        plotter.plot_comparison_lines(
            dataframe=dataframe,
            title="Comparativa",
            xlabel="Mes",
            ylabel="Consumo"
        )

        manager.set_window_title.assert_called_once_with(
            "HELIOS - Comparativa"
        )

        plt.plot.assert_called_once()

        plt.title.assert_called_once_with(
            "Comparativa"
        )

    # ==================================================
    # plot_variation_bars
    # ==================================================

    @patch("helios.plots.plotter.plt")
    def test_plot_variation_bars(self, plt):

        dataframe = pd.DataFrame(
            {
                "2025 vs 2024": [
                    10.0,
                    -5.0,
                    float("nan"),
                ]
            },
            index=["Enero", "Febrero", "Marzo"]
        )

        manager = MagicMock()

        plt.get_current_fig_manager.return_value = manager

        plotter = Plotter()

        plotter.plot_variation_bars(
            dataframe=dataframe,
            title="Variación",
            xlabel="Mes",
            ylabel="%"
        )

        plt.figure.assert_called_once_with(
            figsize=(12, 5)
        )

        plt.bar.assert_called_once()

        bar_call = plt.bar.call_args

        assert bar_call.args[0] == [0, 1, 2]

        values = bar_call.args[1]

        assert values[0] == 10.0
        assert values[1] == -5.0
        assert pd.isna(values[2])

        assert bar_call.kwargs["color"] == [
            "tab:green",
            "tab:red",
            "tab:red",
        ]

        plt.axhline.assert_called_once_with(
            y=0,
            color="black",
            linewidth=1
        )

        plt.title.assert_called_once_with(
            "Variación - 2025 vs 2024"
        )

        plt.xlabel.assert_called_once_with(
            "Mes"
        )

        plt.ylabel.assert_called_once_with(
            "%"
        )

        plt.grid.assert_called_once_with(
            axis="y",
            alpha=0.3
        )

        manager.set_window_title.assert_called_once_with(
            "HELIOS - Variación - 2025 vs 2024"
        )

        xticks_call = plt.xticks.call_args

        assert xticks_call.kwargs["ticks"] == [0, 1, 2]
        assert list(xticks_call.kwargs["labels"]) == [
            "Enero",
            "Febrero",
            "Marzo"
        ]
        assert xticks_call.kwargs["rotation"] == 90

        plt.tight_layout.assert_called_once()

    # ==================================================
    # plot_variation_bars - varias columnas
    # ==================================================

    @patch("helios.plots.plotter.plt")
    def test_plot_variation_bars_multiple_columns(self, plt):

        dataframe = pd.DataFrame(
            {
                "2025 vs 2024": [10.0, -5.0],
                "2026 vs 2025": [-2.0, 8.0],
            },
            index=["Enero", "Febrero"]
        )

        manager = MagicMock()

        plt.get_current_fig_manager.return_value = manager

        plotter = Plotter()

        plotter.plot_variation_bars(
            dataframe=dataframe,
            title="Variación",
            xlabel="Mes",
            ylabel="%"
        )

        assert plt.figure.call_count == 2
        assert plt.bar.call_count == 2
        assert plt.axhline.call_count == 2
        assert plt.title.call_count == 2
        assert plt.xlabel.call_count == 2
        assert plt.ylabel.call_count == 2
        assert plt.grid.call_count == 2
        assert plt.xticks.call_count == 2
        assert plt.tight_layout.call_count == 2

        assert manager.set_window_title.call_count == 2

    # ==================================================
    # plot_variation_bars - error ventana
    # ==================================================

    @patch("helios.plots.plotter.plt")
    def test_plot_variation_bars_handles_window_error(
        self,
        plt
    ):

        dataframe = pd.DataFrame(
            {
                "2025 vs 2024": [10.0, -5.0],
            },
            index=["Enero", "Febrero"]
        )

        manager = MagicMock()

        manager.set_window_title.side_effect = Exception(
            "Window error"
        )

        plt.get_current_fig_manager.return_value = manager

        plotter = Plotter()

        plotter.plot_variation_bars(
            dataframe=dataframe,
            title="Variación",
            xlabel="Mes",
            ylabel="%"
        )

        manager.set_window_title.assert_called_once()

        plt.bar.assert_called_once()

        plt.tight_layout.assert_called_once()

    # ==================================================
    # show
    # ==================================================

    @patch("helios.plots.plotter.plt")
    def test_show(self, plt):

        plotter = Plotter()

        plotter.show()

        plt.show.assert_called_once_with()