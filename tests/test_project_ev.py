import pytest

from helios.core.economics_configuration import EconomicsConfiguration
from helios.core.project import HeliosProject
from helios.ev.configuration import EVConfiguration
from helios.ev.scenario import EVScenario


def make_project() -> HeliosProject:
    return HeliosProject(
        EconomicsConfiguration(
            installation_cost=0.0,
        )
    )

class TestHeliosProjectEV:

    def test_project_starts_without_ev_configuration(self):
        project = make_project()

        assert project.ev_configuration is None

    def test_set_ev_configuration_stores_configuration(self):
        project = make_project()

        configuration = EVConfiguration(
            annual_consumption_kwh=3000.0,
        )

        project.set_ev_configuration(configuration)

        assert project.ev_configuration is configuration

    def test_build_ev_scenario_requires_configuration(self):
        project = make_project()

        with pytest.raises(
            ValueError,
            match="EV configuration has not been set",
        ):
            project.build_ev_scenario()

    def test_build_ev_scenario_returns_ev_scenario(self):
        project = make_project()

        project.set_ev_configuration(
            EVConfiguration(
                annual_consumption_kwh=3000.0,
            )
        )

        scenario = project.build_ev_scenario()

        assert isinstance(scenario, EVScenario)

    def test_build_ev_scenario_preserves_annual_consumption(self):
        project = make_project()

        project.set_ev_configuration(
            EVConfiguration(
                annual_consumption_kwh=3000.0,
            )
        )

        scenario = project.build_ev_scenario()

        assert scenario.annual_consumption == pytest.approx(
            3000.0
        )

    def test_build_ev_scenario_uses_configuration_reference_year(self):
        project = make_project()

        project.set_ev_configuration(
            EVConfiguration(
                annual_consumption_kwh=3000.0,
                reference_year=2024,
            )
        )

        scenario = project.build_ev_scenario()

        assert scenario.reference_year == 2024
        assert scenario.hourly_consumption.index[0].year == 2024
        assert len(scenario.hourly_consumption) == 8760