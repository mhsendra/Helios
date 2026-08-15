from unittest.mock import MagicMock

import pandas as pd
from PySide6.QtWidgets import QApplication

from helios.gui.widgets.profiles_page import ProfilesPage


class TestProfilesPage:

    @classmethod
    def setup_class(cls):

        cls.app = QApplication.instance()

        if cls.app is None:
            cls.app = QApplication([])

    def setup_method(self):

        self.project = MagicMock()

        self.profiles = self.project.profiles

        self.profiles.hourly_profile = None
        self.profiles.weekday_profile = None
        self.profiles.monthly_profile = None
        self.profiles.seasonal_profile = None

        self.page = ProfilesPage(
            self.project
        )

    # ==================================================
    # Estado inicial
    # ==================================================

    def test_page_stores_project(self):

        assert self.page.project is self.project

    def test_labels_start_with_dash(self):

        labels = [
            self.page.hour_max_label,
            self.page.hour_min_label,
            self.page.weekday_max_label,
            self.page.weekday_min_label,
            self.page.month_max_label,
            self.page.month_min_label,
            self.page.season_max_label,
            self.page.season_min_label,
        ]

        assert all(
            label.text() == "-"
            for label in labels
        )

    # ==================================================
    # update_data — datos no preparados
    # ==================================================

    def test_update_data_returns_when_profiles_are_missing(self):

        self.profiles.hourly_profile = None

        self.profiles.weekday_profile = pd.Series(
            [10, 20],
            index=["Lunes", "Martes"]
        )

        self.profiles.monthly_profile = pd.Series(
            [100, 200],
            index=["Enero", "Febrero"]
        )

        self.profiles.seasonal_profile = pd.Series(
            [300, 400],
            index=["Invierno", "Verano"]
        )

        self.page.update_data()

        assert self.page.hour_max_label.text() == "-"
        assert self.page.hour_min_label.text() == "-"

    # ==================================================
    # Perfil horario
    # ==================================================

    def test_update_data_sets_hourly_profile(self):

        self.profiles.hourly_profile = pd.Series(
            [10, 20, 50, 30],
            index=[0, 1, 2, 3]
        )

        self.profiles.weekday_profile = pd.Series(
            [10, 20],
            index=["Lunes", "Martes"]
        )

        self.profiles.monthly_profile = pd.Series(
            [100, 200],
            index=["Enero", "Febrero"]
        )

        self.profiles.seasonal_profile = pd.Series(
            [300, 400],
            index=["Invierno", "Verano"]
        )

        self.page.update_data()

        assert self.page.hour_max_label.text() == "02:00"
        assert self.page.hour_min_label.text() == "00:00"

    # ==================================================
    # Perfil semanal
    # ==================================================

    def test_update_data_sets_weekday_profile(self):

        self.profiles.hourly_profile = pd.Series(
            [10, 20],
            index=[0, 1]
        )

        self.profiles.weekday_profile = pd.Series(
            [100, 50, 80, 120],
            index=[
                "Lunes",
                "Martes",
                "Miércoles",
                "Jueves",
            ]
        )

        self.profiles.monthly_profile = pd.Series(
            [100, 200],
            index=["Enero", "Febrero"]
        )

        self.profiles.seasonal_profile = pd.Series(
            [300, 400],
            index=["Invierno", "Verano"]
        )

        self.page.update_data()

        assert self.page.weekday_max_label.text() == "Jueves"
        assert self.page.weekday_min_label.text() == "Martes"

    # ==================================================
    # Perfil mensual y estacional
    # ==================================================

    def test_update_data_sets_monthly_and_seasonal_profiles(self):

        self.profiles.hourly_profile = pd.Series(
            [10, 20],
            index=[0, 1]
        )

        self.profiles.weekday_profile = pd.Series(
            [100, 50],
            index=["Lunes", "Martes"]
        )

        self.profiles.monthly_profile = pd.Series(
            [100, 300, 200],
            index=[
                "Enero",
                "Febrero",
                "Marzo",
            ]
        )

        self.profiles.seasonal_profile = pd.Series(
            [500, 200, 350, 100],
            index=[
                "Invierno",
                "Primavera",
                "Verano",
                "Otoño",
            ]
        )

        self.page.update_data()

        assert self.page.month_max_label.text() == "Febrero"
        assert self.page.month_min_label.text() == "Enero"

        assert self.page.season_max_label.text() == "Invierno"
        assert self.page.season_min_label.text() == "Otoño"

    # ==================================================
    # Actualización de datos
    # ==================================================

    def test_update_data_replaces_previous_values(self):

        self.profiles.hourly_profile = pd.Series(
            [10, 50],
            index=[1, 5]
        )

        self.profiles.weekday_profile = pd.Series(
            [20, 80],
            index=["Lunes", "Viernes"]
        )

        self.profiles.monthly_profile = pd.Series(
            [100, 500],
            index=["Enero", "Junio"]
        )

        self.profiles.seasonal_profile = pd.Series(
            [200, 600],
            index=["Invierno", "Verano"]
        )

        self.page.update_data()

        assert self.page.hour_max_label.text() == "05:00"
        assert self.page.weekday_max_label.text() == "Viernes"
        assert self.page.month_max_label.text() == "Junio"
        assert self.page.season_max_label.text() == "Verano"

        # Segunda actualización

        self.profiles.hourly_profile = pd.Series(
            [100, 10],
            index=[2, 7]
        )

        self.profiles.weekday_profile = pd.Series(
            [90, 10],
            index=["Lunes", "Viernes"]
        )

        self.profiles.monthly_profile = pd.Series(
            [900, 100],
            index=["Enero", "Junio"]
        )

        self.profiles.seasonal_profile = pd.Series(
            [800, 100],
            index=["Invierno", "Verano"]
        )

        self.page.update_data()

        assert self.page.hour_max_label.text() == "02:00"
        assert self.page.hour_min_label.text() == "07:00"

        assert self.page.weekday_max_label.text() == "Lunes"
        assert self.page.weekday_min_label.text() == "Viernes"

        assert self.page.month_max_label.text() == "Enero"
        assert self.page.month_min_label.text() == "Junio"

        assert self.page.season_max_label.text() == "Invierno"
        assert self.page.season_min_label.text() == "Verano"