from unittest.mock import MagicMock

import pytest

from helios.core.project import HeliosProject
from helios.core.economics_configuration import EconomicsConfiguration
from helios.solar.configuration import SolarConfiguration
from helios.solar.battery_configuration import BatteryConfiguration
from helios.solar.installation_costs import InstallationCostConfiguration
from helios.ev.configuration import EVConfiguration

from helios.solar.components_catalog import (
    ComponentCatalog,
    Inverter,
    MountingSystem,
    PhotovoltaicPanel,
)
from helios.solar.installation_component_selection import (
    InstallationComponentSelection,
)

def create_project():

    configuration = EconomicsConfiguration(
        installation_cost=12490.0
    )

    return HeliosProject(configuration)

def create_component_catalog():
    panel = PhotovoltaicPanel(
        id="panel-540",
        manufacturer="Test",
        model="Panel 540 W",
        power_wp=540,
        width_m=1.13,
        height_m=2.28,
        price_eur=92.0,
    )

    inverter = Inverter(
        id="inverter-8",
        manufacturer="Test",
        model="Inverter 8 kW",
        nominal_power_kw=8.0,
        max_pv_power_kwp=10.0,
        price_eur=900.0,
    )

    mounting = MountingSystem(
        id="mounting-tile",
        manufacturer="Test",
        model="Mounting tile",
        price_per_panel_eur=20.0,
        compatible_roof_types=("tile",),
    )

    return ComponentCatalog(
        panels=(panel,),
        inverters=(inverter,),
        mounting_systems=(mounting,),
    )

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

    project.analyzer.indicators.calculate.assert_called_once_with()

    project.analyzer.tariffs.calculate.assert_called_once_with()


def test_project_set_solar_configuration():

    project = create_project()

    configuration = SolarConfiguration(
        latitude=41.6,
        longitude=2.1,
        tilt=30,
        azimuth=0,
        reference_year=2023,
        losses=14.0,
        pv_technology="crystSi",
        mounting_place="free",
    )

    solar = MagicMock()

    project.analyzer.solar = solar

    project.set_solar_configuration(
        configuration
    )

    assert (
        project.solar_configuration
        is configuration
    )

    solar.set_configuration.assert_called_once_with(
        configuration
    )

    solar.calculate.assert_not_called()

def test_project_set_solar_configuration_rejects_invalid_configuration():

    project = create_project()

    with pytest.raises(
        TypeError,
        match="configuration must be a SolarConfiguration.",
    ):

        project.set_solar_configuration(
            MagicMock()
        )

def test_project_set_solar_configuration_replaces_previous_configuration():

    project = create_project()

    configuration_1 = SolarConfiguration(
        latitude=41.6,
        longitude=2.1,
        tilt=30,
        azimuth=0,
        reference_year=2023,
        losses=14.0,
        pv_technology="crystSi",
        mounting_place="free",
    )

    configuration_2 = SolarConfiguration(
        latitude=41.7,
        longitude=2.2,
        tilt=35,
        azimuth=10,
        reference_year=2025,
        losses=12.0,
        pv_technology="crystSi",
        mounting_place="building",
    )

    project.set_solar_configuration(
        configuration_1
    )

    project.set_solar_configuration(
        configuration_2
    )

    assert (
        project.solar_configuration
        is configuration_2
    )

    assert (
        project.solar_configuration
        is not configuration_1
    )

def test_project_set_battery_configuration():
    project = HeliosProject(
        EconomicsConfiguration(installation_cost=12490.0)
    )

    configuration = BatteryConfiguration(
        capacity_kwh=16.6,
        max_charge_power_kw=8.0,
        max_discharge_power_kw=8.0,
    )

    project.set_battery_configuration(configuration)

    assert project.battery_configuration is configuration

def test_project_links_analyzer_back_to_project():

    project = create_project()

    assert project.analyzer.project is project

def test_project_solar_controller_uses_project_configuration():

    project = create_project()

    configuration = SolarConfiguration(
        latitude=41.6,
        longitude=2.1,
        tilt=30,
        azimuth=0,
        reference_year=2023,
        losses=14.0,
        pv_technology="crystSi",
        mounting_place="free",
    )

    project.set_solar_configuration(
        configuration
    )

    assert project.solar.configuration is configuration

def test_project_set_battery_configuration():
    project = HeliosProject(
        EconomicsConfiguration(installation_cost=12490.0)
    )

    configuration = BatteryConfiguration(
        capacity_kwh=16.6,
        max_charge_power_kw=8.0,
        max_discharge_power_kw=8.0,
    )

    solar = MagicMock()

    project.analyzer.solar = solar

    project.set_battery_configuration(
        configuration
    )

    assert project.battery_configuration is configuration

    solar.invalidate_energy_balance.assert_called_once_with()

def test_project_set_ev_configuration():

    project = create_project()

    configuration = EVConfiguration(
        annual_consumption_kwh=3000.0,
        reference_year=2025,
    )

    project.set_ev_configuration(
        configuration
    )

    assert project.ev_configuration is configuration


def test_project_set_ev_configuration_replaces_previous_configuration():

    project = create_project()

    configuration_1 = EVConfiguration(
        annual_consumption_kwh=3000.0,
        reference_year=2025,
    )

    configuration_2 = EVConfiguration(
        annual_consumption_kwh=4500.0,
        reference_year=2025,
    )

    project.set_ev_configuration(
        configuration_1
    )

    project.set_ev_configuration(
        configuration_2
    )

    assert project.ev_configuration is configuration_2

    assert project.ev_configuration is not configuration_1

def test_set_installation_cost_configuration():
    project = HeliosProject(
        EconomicsConfiguration(
            installation_cost=0.0,
        )
    )

    configuration = InstallationCostConfiguration(
        panel_unit_cost_eur=100.0,
        structure_unit_cost_eur=50.0,
    )

    project.set_installation_cost_configuration(
        configuration
    )

    assert project.installation_cost_configuration == configuration

def test_set_installation_cost_configuration_rejects_invalid_type():
    project = HeliosProject(
        EconomicsConfiguration(
            installation_cost=0.0,
        )
    )

    with pytest.raises(TypeError):
        project.set_installation_cost_configuration(
            object()
        )

def test_project_set_component_catalog():
    project = create_project()
    catalog = create_component_catalog()

    project.set_component_catalog(catalog)

    assert project.component_catalog is catalog


def test_project_set_component_catalog_rejects_invalid_type():
    project = create_project()

    with pytest.raises(TypeError):
        project.set_component_catalog(object())


def test_project_set_component_selection():
    project = create_project()
    catalog = create_component_catalog()

    selection = InstallationComponentSelection(
        catalog=catalog,
        panel_id="panel-540",
        inverter_id="inverter-8",
        mounting_system_id="mounting-tile",
        roof_type="tile",
    )

    project.set_component_catalog(catalog)
    project.set_component_selection(selection)

    assert project.component_selection is selection


def test_project_set_component_selection_rejects_missing_catalog():
    project = create_project()
    catalog = create_component_catalog()

    selection = InstallationComponentSelection(
        catalog=catalog,
        panel_id="panel-540",
        inverter_id="inverter-8",
        mounting_system_id="mounting-tile",
        roof_type="tile",
    )

    with pytest.raises(ValueError):
        project.set_component_selection(selection)


def test_project_set_component_selection_rejects_invalid_type():
    project = create_project()

    with pytest.raises(TypeError):
        project.set_component_selection(object())


def test_project_set_component_selection_rejects_foreign_catalog():
    project = create_project()
    project_catalog = create_component_catalog()
    foreign_catalog = create_component_catalog()

    selection = InstallationComponentSelection(
        catalog=foreign_catalog,
        panel_id="panel-540",
        inverter_id="inverter-8",
        mounting_system_id="mounting-tile",
        roof_type="tile",
    )

    project.set_component_catalog(project_catalog)

    with pytest.raises(ValueError):
        project.set_component_selection(selection)


def test_project_set_component_selection_can_be_cleared():
    project = create_project()
    catalog = create_component_catalog()

    selection = InstallationComponentSelection(
        catalog=catalog,
        panel_id="panel-540",
        inverter_id="inverter-8",
        mounting_system_id="mounting-tile",
        roof_type="tile",
    )

    project.set_component_catalog(catalog)
    project.set_component_selection(selection)
    project.set_component_selection(None)

    assert project.component_selection is None

def test_project_rejects_replacing_catalog_with_active_selection():
    project = create_project()
    original_catalog = create_component_catalog()
    replacement_catalog = create_component_catalog()

    selection = InstallationComponentSelection(
        catalog=original_catalog,
        panel_id="panel-540",
        inverter_id="inverter-8",
        mounting_system_id="mounting-tile",
        roof_type="tile",
    )

    project.set_component_catalog(original_catalog)
    project.set_component_selection(selection)

    with pytest.raises(ValueError):
        project.set_component_catalog(replacement_catalog)

    assert project.component_catalog is original_catalog
    assert project.component_selection is selection