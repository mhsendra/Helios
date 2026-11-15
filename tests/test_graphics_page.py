import pytest

from PySide6.QtWidgets import QApplication, QGridLayout, QScrollArea

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


class FakeAnalyzer:

    def __init__(self):

        self.show_plots_calls = 0

    def show_plots(self):

        self.show_plots_calls += 1


class FakeProject:

    def __init__(self):

        self.profiles = FakeProfiles()

        self.comparisons = FakeComparisons()

        self.analyzer = FakeAnalyzer()


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

    @pytest.mark.parametrize("android", [False, True])
    def test_layout_by_platform(self, app, monkeypatch, android):
        """Comprueba la disposición de los grupos en cada plataforma."""

        monkeypatch.setattr(
            "helios.gui.widgets.graphics_page.is_android",
            lambda: android,
        )

        _, page = self.create_page()

        try:
            if android:
                assert isinstance(page.scroll_area, QScrollArea)
                content = page.scroll_area.widget()
                layout = content.layout()
            else:
                assert not hasattr(page, "scroll_area")
                layout = page.layout()

            expected_columns = 1 if android else 2

            # Los tres grupos deben conservarse.
            groups = [
                layout.itemAt(1).widget(),
                layout.itemAt(2).widget(),
                layout.itemAt(3).widget(),
            ]

            for group in groups:
                grid = group.layout()

                assert isinstance(grid, QGridLayout)
                assert grid.columnCount() == expected_columns

            # Comprobar la posición de los botones.
            profiles_grid = groups[0].layout()

            if android:
                assert profiles_grid.getItemPosition(1)[:2] == (1, 0)
            else:
                assert profiles_grid.getItemPosition(1)[:2] == (0, 1)

        finally:
            page.close()

    def test_android_vertical_scrolling(self, app, monkeypatch):
        """Comprueba el desplazamiento vertical en Android."""

        monkeypatch.setattr(
            "helios.gui.widgets.graphics_page.is_android",
            lambda: True,
        )

        _, page = self.create_page()

        try:
            # Simular una pantalla Android de altura reducida.
            page.resize(400, 350)
            page.show()

            QApplication.processEvents()

            scroll_area = page.scroll_area
            scrollbar = scroll_area.verticalScrollBar()

            assert scroll_area.isVisible()
            assert scroll_area.widgetResizable()
            assert scrollbar.maximum() > 0

        finally:
            page.close()

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

        assert project.analyzer.show_plots_calls == 5

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

        assert project.analyzer.show_plots_calls == 3

    def test_variation_buttons(self, app):

        project, page = self.create_page()

        page.monthly_variation_button.click()
        page.weekly_variation_button.click()

        assert project.comparisons.calls == [
            "plot_monthly_variation",
            "plot_weekly_variation",
        ]

        assert project.analyzer.show_plots_calls == 2