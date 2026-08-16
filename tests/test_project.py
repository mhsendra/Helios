from helios.core.project import HeliosProject
from helios.core.economics_configuration import EconomicsConfiguration


def create_project():

    configuration = EconomicsConfiguration(
        installation_cost=12490.0
    )

    return HeliosProject(configuration)


def test_project_creates_analyzer():

    project = create_project()

    assert project.analyzer is not None


def test_project_exposes_validation_controller():

    project = create_project()

    assert project.validation is project.analyzer.validation


def test_project_exposes_statistics_controller():

    project = create_project()

    assert project.statistics is project.analyzer.statistics


def test_project_exposes_profiles_controller():

    project = create_project()

    assert project.profiles is project.analyzer.profiles


def test_project_exposes_comparisons_controller():

    project = create_project()

    assert project.comparisons is project.analyzer.comparisons


def test_project_exposes_indicators_controller():

    project = create_project()

    assert project.indicators is project.analyzer.indicators


def test_project_exposes_tariffs_controller():

    project = create_project()

    assert project.tariffs is project.analyzer.tariffs


def test_project_exposes_solar_controller():

    project = create_project()

    assert project.solar is project.analyzer.solar


def test_project_exposes_economics_controller():

    project = create_project()

    assert project.economics is project.analyzer.economics

from unittest.mock import MagicMock


def test_project_exposes_dataset():

    project = create_project()

    project.analyzer.dataset = "test_dataset"

    assert project.dataset == "test_dataset"


def test_project_exposes_quality():

    project = create_project()

    project.analyzer.quality = {
        "rating": "EXCELENTE"
    }

    assert project.quality == {
        "rating": "EXCELENTE"
    }


def test_project_load_data():

    project = create_project()

    project.analyzer = MagicMock()

    project.load_data(
        "test.xlsx"
    )

    project.analyzer.load_excel.assert_called_once_with(
        "test.xlsx"
    )

    project.analyzer.clean_data.assert_called_once_with()

    project.analyzer.build_datetime.assert_called_once_with()


def test_project_analyze_data():

    project = create_project()

    project.analyzer = MagicMock()

    project.analyze_data()

    project.analyzer.validation.calculate.assert_called_once_with()

    project.analyzer.statistics.calculate.assert_called_once_with()

    project.analyzer.profiles.calculate.assert_called_once_with()

    project.analyzer.comparisons.calculate.assert_called_once_with()