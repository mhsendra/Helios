import pandas as pd
from unittest.mock import MagicMock

from helios.plots.profiles import ProfilesPlots


class TestProfilesPlots:

    def setup_method(self):

        self.plotter = MagicMock()
        self.plots = ProfilesPlots(self.plotter)

    # ==================================================
    # Perfil horario
    # ==================================================

    def test_plot_hourly_profile(self):

        profile = pd.Series(
            [1.0, 2.0, 3.0],
            index=[0, 1, 2]
        )

        self.plots.plot_hourly_profile(profile)

        self.plotter.plot_series.assert_called_once_with(
            series=profile,
            title="Perfil horario de consumo",
            xlabel="Hora",
            ylabel="Consumo medio (kWh)"
        )

    # ==================================================
    # Perfil semanal
    # ==================================================

    def test_plot_weekday_profile(self):

        profile = pd.Series(
            [1.0, 2.0, 3.0],
            index=["Lunes", "Martes", "Miércoles"]
        )

        self.plots.plot_weekday_profile(profile)

        assert self.plotter.plot_series.call_count == 1

        calls = self.plotter.plot_series.call_args_list

        assert calls[0].kwargs == {
            "series": profile,
            "title": "Perfil semanal de consumo",
            "xlabel": "Día de la semana",
            "ylabel": "Consumo medio (kWh)"
        }

    # ==================================================
    # Laborables vs fin de semana
    # ==================================================

    def test_plot_workday_vs_weekend_profile(self):

        profile = {
            "workdays": 10.0,
            "weekend": 12.0
        }

        self.plots.plot_workday_vs_weekend_profile(profile)

        self.plotter.plot_variation_bars.assert_called_once()

        call = (
            self.plotter
            .plot_variation_bars
            .call_args
        )

        dataframe = call.kwargs["dataframe"]

        assert list(dataframe.index) == [
            "Laborables",
            "Fin de semana"
        ]

        assert list(dataframe["Consumo"]) == [
            10.0,
            12.0
        ]

        assert call.kwargs["title"] == (
            "Consumo: Laborables vs Fin de semana"
        )

        assert call.kwargs["xlabel"] == "Tipo de día"

        assert call.kwargs["ylabel"] == "kWh"

    # ==================================================
    # Perfil mensual
    # ==================================================

    def test_plot_monthly_profile(self):

        profile = pd.Series(
            [100.0, 120.0],
            index=["Enero", "Febrero"]
        )

        self.plots.plot_monthly_profile(profile)

        self.plotter.plot_series.assert_called_once_with(
            series=profile,
            title="Perfil mensual de consumo",
            xlabel="Mes",
            ylabel="Consumo medio (kWh)"
        )

    # ==================================================
    # Perfil estacional
    # ==================================================

    def test_plot_seasonal_profile(self):

        profile = pd.Series(
            [100.0, 120.0],
            index=["Invierno", "Verano"]
        )

        self.plots.plot_seasonal_profile(profile)

        self.plotter.plot_series.assert_called_once_with(
            series=profile,
            title="Perfil estacional de consumo",
            xlabel="Estación",
            ylabel="Consumo medio (kWh)"
        )