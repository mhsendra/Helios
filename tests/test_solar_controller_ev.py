import pandas as pd
import pytest

from helios.core.consumption_scenario import ConsumptionScenario
from helios.core.economics_configuration import EconomicsConfiguration
from helios.core.project import HeliosProject
from helios.ev.configuration import EVConfiguration
from helios.ev.scenario import EVScenario
from helios.solar.battery_configuration import BatteryConfiguration
from helios.solar.configuration import SolarConfiguration
from helios.solar.production_profile import SolarProductionProfile
from helios.solar.balance import SolarBalanceEngine


def make_consumption_scenario() -> ConsumptionScenario:
    index = pd.date_range(
        "2025-01-01 00:00:00",
        periods=8760,
        freq="h",
    )

    return ConsumptionScenario(
        hourly_consumption=pd.Series(
            1.0,
            index=index,
            dtype=float,
        ),
        reference_year=2025,
    )


def make_project() -> HeliosProject:
    return HeliosProject(
        EconomicsConfiguration(
            installation_cost=0.0,
        )
    )


def make_solar_configuration() -> SolarConfiguration:
    return SolarConfiguration(
        latitude=41.62,
        longitude=2.09,
        tilt=30.0,
        azimuth=0.0,
        reference_year=2025,
        losses=14.0,
        pv_technology="crystSi",
        mounting_place="building",
    )


def make_production_profile() -> SolarProductionProfile:
    index = pd.date_range(
        "2025-01-01 00:00:00",
        periods=8760,
        freq="h",
    )

    return SolarProductionProfile(
        hourly_production=pd.Series(
            0.0,
            index=index,
            dtype=float,
        ),
        reference_year=2025,
        installed_power_kwp=1.0,
    )


def make_battery() -> BatteryConfiguration:
    return BatteryConfiguration(
        capacity_kwh=10.0,
        max_charge_power_kw=10.0,
        max_discharge_power_kw=10.0,
        charge_efficiency=1.0,
        discharge_efficiency=1.0,
        min_soc=0.0,
        max_soc=1.0,
        initial_soc=0.5,
    )


class TestSolarControllerEV:

    def test_energy_balance_without_ev_preserves_existing_flow(
        self,
        monkeypatch,
    ):
        project = make_project()

        consumption = make_consumption_scenario()
        production = make_production_profile()

        project.analyzer.calculate_representative_consumption_scenario = (
            lambda: consumption
        )

        project.solar.set_configuration(
            make_solar_configuration()
        )

        monkeypatch.setattr(
            type(project.solar.analyzer.solar_engine),
            "hourly_production",
            property(
                lambda self: pd.DataFrame(
                    {
                        "production_kwh": production.hourly_production,
                    }
                )
            ),
        )

        monkeypatch.setattr(
            type(project.solar.analyzer.solar_engine),
            "installed_power_kwp",
            property(
                lambda self: 1.0
            ),
        )

        captured = {}

        def fake_calculate(
            consumption_scenario,
            production_profile,
            battery_configuration=None,
            ev_scenario=None,
        ):
            captured["consumption"] = consumption_scenario
            captured["production"] = production_profile
            captured["battery"] = battery_configuration
            captured["ev"] = ev_scenario

            return pd.DataFrame(
                index=consumption.hourly_consumption.index
            )

        monkeypatch.setattr(
            SolarBalanceEngine,
            "calculate",
            staticmethod(fake_calculate),
        )

        project.solar.calculate_energy_balance()

        assert captured["consumption"] is consumption
        assert isinstance(
            captured["production"],
            SolarProductionProfile,
        )
        assert captured["battery"] is None
        assert captured["ev"] is None

    def test_energy_balance_builds_ev_scenario(
        self,
        monkeypatch,
    ):
        project = make_project()

        consumption = make_consumption_scenario()
        production = make_production_profile()

        project.analyzer.calculate_representative_consumption_scenario = (
            lambda: consumption
        )

        project.solar.set_configuration(
            make_solar_configuration()
        )

        monkeypatch.setattr(
            type(project.solar.analyzer.solar_engine),
            "hourly_production",
            property(
                lambda self: pd.DataFrame(
                    {
                        "production_kwh": production.hourly_production,
                    }
                )
            ),
        )

        monkeypatch.setattr(
            type(project.solar.analyzer.solar_engine),
            "installed_power_kwp",
            property(
                lambda self: 1.0
            ),
        )

        project.set_ev_configuration(
            EVConfiguration(
                annual_consumption_kwh=3000.0,
                reference_year=2025,
            )
        )

        captured = {}

        def fake_calculate(
            consumption_scenario,
            production_profile,
            battery_configuration=None,
            ev_scenario=None,
        ):
            captured["ev"] = ev_scenario

            return pd.DataFrame(
                index=consumption.hourly_consumption.index
            )

        monkeypatch.setattr(
            SolarBalanceEngine,
            "calculate",
            staticmethod(fake_calculate),
        )

        project.solar.calculate_energy_balance()

        assert isinstance(
            captured["ev"],
            EVScenario,
        )

        assert captured["ev"].annual_consumption == pytest.approx(
            3000.0
        )

    def test_energy_balance_passes_ev_and_battery(
        self,
        monkeypatch,
    ):
        project = make_project()

        consumption = make_consumption_scenario()
        production = make_production_profile()
        battery = make_battery()

        project.analyzer.calculate_representative_consumption_scenario = (
            lambda: consumption
        )

        project.solar.set_configuration(
            make_solar_configuration()
        )

        monkeypatch.setattr(
            type(project.solar.analyzer.solar_engine),
            "hourly_production",
            property(
                lambda self: pd.DataFrame(
                    {
                        "production_kwh": production.hourly_production,
                    }
                )
            ),
        )

        monkeypatch.setattr(
            type(project.solar.analyzer.solar_engine),
            "installed_power_kwp",
            property(
                lambda self: 1.0
            ),
        )

        project.set_battery_configuration(
            battery
        )

        project.set_ev_configuration(
            EVConfiguration(
                annual_consumption_kwh=3000.0,
                reference_year=2025,
            )
        )

        captured = {}

        def fake_calculate(
            consumption_scenario,
            production_profile,
            battery_configuration=None,
            ev_scenario=None,
        ):
            captured["battery"] = battery_configuration
            captured["ev"] = ev_scenario

            return pd.DataFrame(
                index=consumption.hourly_consumption.index
            )

        monkeypatch.setattr(
            SolarBalanceEngine,
            "calculate",
            staticmethod(fake_calculate),
        )

        project.solar.calculate_energy_balance()

        assert captured["battery"] is battery
        assert isinstance(
            captured["ev"],
            EVScenario,
        )