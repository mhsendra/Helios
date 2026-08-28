import pytest

from helios.solar.configuration import SolarConfiguration


class TestSolarConfiguration:

    def test_required_parameters(self):

        configuration = SolarConfiguration(
            latitude=41.4,
            longitude=2.1,
            tilt=30,
            azimuth=0,
        )

        assert configuration.latitude == pytest.approx(41.4)
        assert configuration.longitude == pytest.approx(2.1)
        assert configuration.tilt == 30
        assert configuration.azimuth == 0

    def test_default_values(self):

        configuration = SolarConfiguration(
            latitude=41.4,
            longitude=2.1,
            tilt=30,
            azimuth=0,
        )

        assert configuration.reference_year == 2023
        assert configuration.losses == pytest.approx(14)
        assert configuration.pv_technology == "crystSi"
        assert configuration.mounting_place == "building"

    def test_custom_values(self):

        configuration = SolarConfiguration(
            latitude=41.4,
            longitude=2.1,
            tilt=25,
            azimuth=-10,
            reference_year=2025,
            losses=12.5,
            pv_technology="crystSi",
            mounting_place="free",
        )

        assert configuration.latitude == pytest.approx(41.4)
        assert configuration.longitude == pytest.approx(2.1)
        assert configuration.tilt == 25
        assert configuration.azimuth == -10

        assert configuration.reference_year == 2025
        assert configuration.losses == pytest.approx(12.5)
        assert configuration.pv_technology == "crystSi"
        assert configuration.mounting_place == "free"