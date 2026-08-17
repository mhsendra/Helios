import pytest

from PySide6.QtWidgets import QApplication

from helios.gui.widgets.graphics_page import GraphicsPage


class FakeProfiles:

    def __init__(self):

        self.calls = []

    def plot_hourly_profile(self):

        self.calls.append(
            "plot_hourly_profile"
        )

    def plot_weekday_profile(self):

        self.calls.append(
            "plot_weekday_profile"
        )

    def plot_workday_vs_weekend_profile(self):

        self.calls.append(
            "plot_workday_vs_weekend_profile"
        )

    def plot_monthly_profile(self):

        self.calls.append(
            "plot_monthly_profile"
        )

    def plot_seasonal_profile(self):

        self.calls.append(
            "plot_seasonal_profile"
        )


class FakeComparisons:

    def __init__(self):

        self.calls = []

    def plot_monthly_comparison(self):

        self.calls.append(
            "plot_monthly_comparison"
        )

    def plot_weekly_comparison(self):

        self.calls.append(
            "plot_weekly_comparison"
        )

    def plot_yearly_comparison(self):

        self.calls.append(
            "plot_yearly_comparison"
        )

    def plot_monthly_variation(self):

        self.calls.append(
            "plot_monthly_variation"
        )

    def plot_weekly_variation(self):

        self.calls.append(
            "plot_weekly_variation"
        )


class FakeProject:

    def __init__(self):

        self.profiles = FakeProfiles()

        self.comparisons = FakeComparisons()


@pytest.fixture
def app():

    application = QApplication.instance()

    if application is None:

        application = QApplication([])

    return application


class TestGraphicsPage:

    def create_page(self):

        project = FakeProject()

        page = GraphicsPage(project)

        return project, page

    def test_page_initialization(self, app):

        project, page = self.create_page()

        assert page.project is project

        assert page.hourly_button is not None
        assert page.weekday_button is not None
        assert page.workday_weekend_button is not None
        assert page.monthly_profile_button is not None
        assert page.seasonal_button is not None

        assert page.monthly_comparison_button is not None
        assert page.weekly_comparison_button is not None
        assert page.yearly_comparison_button is not None

        assert page.monthly_variation_button is not None
        assert page.weekly_variation_button is not None

    def test_button_texts(self, app):

        _, page = self.create_page()

        assert page.hourly_button.text() == "Perfil horario"

        assert page.weekday_button.text() == "Perfil semanal"

        assert (
            page.workday_weekend_button.text()
            == "Laborables vs. fin de semana"
        )

        assert (
            page.monthly_profile_button.text()
            == "Perfil mensual"
        )

        assert (
            page.seasonal_button.text()
            == "Perfil estacional"
        )

        assert (
            page.monthly_comparison_button.text()
            == "Comparativa mensual"
        )

        assert (
            page.weekly_comparison_button.text()
            == "Comparativa semanal"
        )

        assert (
            page.yearly_comparison_button.text()
            == "Comparativa anual"
        )

        assert (
            page.monthly_variation_button.text()
            == "Variación mensual"
        )

        assert (
            page.weekly_variation_button.text()
            == "Variación semanal"
        )

    def test_profile_buttons(self, app):

        project, page = self.create_page()

        page.hourly_button.click()

        page.weekday_button.click()

        page.workday_weekend_button.click()

        page.monthly_profile_button.click()

        page.seasonal_button.click()

        assert project.profiles.calls == [
            "plot_hourly_profile",
            "plot_weekday_profile",
            "plot_workday_vs_weekend_profile",
            "plot_monthly_profile",
            "plot_seasonal_profile",
        ]

    def test_comparison_buttons(self, app):

        project, page = self.create_page()

        page.monthly_comparison_button.click()

        page.weekly_comparison_button.click()

        page.yearly_comparison_button.click()

        assert project.comparisons.calls == [
            "plot_monthly_comparison",
            "plot_weekly_comparison",
            "plot_yearly_comparison",
        ]

    def test_variation_buttons(self, app):

        project, page = self.create_page()

        page.monthly_variation_button.click()

        page.weekly_variation_button.click()

        assert project.comparisons.calls == [
            "plot_monthly_variation",
            "plot_weekly_variation",
        ]