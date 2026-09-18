import pandas as pd
import pytest

from helios.solar.configuration import SolarConfiguration
from helios.solar.PVGIS_production import PVGISProductionService
from helios.solar.production_profile import SolarProductionProfile
from helios.solar.pvgis_production_profile import (
    PVGISProductionProfileService,
)


class FakePVGISClient:

    def __init__(self, response):
        self.response = response

    def fetch(self, configuration):
        return self.response


class TestPVGISProductionProfile:

    @staticmethod
    def configuration():
        return SolarConfiguration(
            latitude=41.62,
            longitude=2.09,
            tilt=30,
            azimuth=0,
            losses=14.0,
            pv_technology="crystSi",
            mounting_place="building",
            reference_year=2025,
        )

    @staticmethod
    def response(value=1000.0, year=2025):
        hourly = []

        index = pd.date_range(
            start=f"{year}-01-01 00:00:00",
            end=f"{year}-12-31 23:00:00",
            freq="h",
        )

        if pd.Timestamp(f"{year}-12-31").is_leap_year:
            index = index[
                ~(
                    (index.month == 2)
                    & (index.day == 29)
                )
            ]

        for timestamp in index:
            hourly.append(
                {
                    "time": timestamp.strftime("%Y%m%d:%H%M"),
                    "P": value,
                    "G(i)": 100.0,
                    "T2m": 20.0,
                    "WS10m": 2.0,
                    "Int": 0,
                }
            )

        return {
            "outputs": {
                "hourly": hourly,
            }
        }

    def service(self):
        production_service = PVGISProductionService(
            client=FakePVGISClient(
                self.response()
            )
        )

        return PVGISProductionProfileService(
            production_service=production_service
        )

    def test_returns_solar_production_profile(self):
        service = self.service()

        result = service.get_production_profile(
            self.configuration()
        )

        assert isinstance(
            result,
            SolarProductionProfile,
        )

    def test_profile_contains_exactly_8760_hours(self):
        service = self.service()

        result = service.get_production_profile(
            self.configuration()
        )

        assert len(result.hourly_production) == 8760

    def test_profile_has_datetime_index(self):
        service = self.service()

        result = service.get_production_profile(
            self.configuration()
        )

        assert isinstance(
            result.hourly_production.index,
            pd.DatetimeIndex,
        )

    def test_profile_preserves_reference_year(self):
        service = self.service()

        result = service.get_production_profile(
            self.configuration()
        )

        assert result.reference_year == 2025

    def test_profile_uses_one_kwp_reference_power(self):
        service = self.service()

        result = service.get_production_profile(
            self.configuration()
        )

        assert result.installed_power_kwp == pytest.approx(1.0)

    def test_profile_preserves_hourly_production(self):
        service = self.service()

        result = service.get_production_profile(
            self.configuration()
        )

        assert (
            result.hourly_production == 1.0
        ).all()

    def test_profile_annual_production_is_hourly_sum(self):
        service = self.service()

        result = service.get_production_profile(
            self.configuration()
        )

        assert result.annual_production == pytest.approx(
            8760.0
        )

    def test_rejects_invalid_configuration(self):
        service = self.service()

        with pytest.raises(TypeError):
            service.get_production_profile(None)

    def test_rejects_empty_pvgis_response(self):
        production_service = PVGISProductionService(
            client=FakePVGISClient(
                {
                    "outputs": {
                        "hourly": [],
                    }
                }
            )
        )

        service = PVGISProductionProfileService(
            production_service=production_service
        )

        with pytest.raises(ValueError):
            service.get_production_profile(
                self.configuration()
            )

    def test_rejects_profile_with_less_than_8760_hours(self):
        response = self.response()

        response["outputs"]["hourly"] = (
            response["outputs"]["hourly"][:-1]
        )

        production_service = PVGISProductionService(
            client=FakePVGISClient(response)
        )

        service = PVGISProductionProfileService(
            production_service=production_service
        )

        with pytest.raises(ValueError, match="8760"):
            service.get_production_profile(
                self.configuration()
            )

    def test_rejects_profile_with_more_than_8760_hours(self):
        response = self.response()

        response["outputs"]["hourly"].append(
            {
                "time": "20260101:00",
                "P": 1000.0,
                "G(i)": 100.0,
                "T2m": 20.0,
                "WS10m": 2.0,
                "Int": 0,
            }
        )

        production_service = PVGISProductionService(
            client=FakePVGISClient(response)
        )

        service = PVGISProductionProfileService(
            production_service=production_service
        )

        with pytest.raises(ValueError, match="8760"):
            service.get_production_profile(
                self.configuration()
            )

    def test_rejects_profile_with_nan_values(self):
        response = self.response()

        response["outputs"]["hourly"][100]["P"] = float("nan")

        production_service = PVGISProductionService(
            client=FakePVGISClient(response)
        )

        service = PVGISProductionProfileService(
            production_service=production_service
        )

        with pytest.raises(
            ValueError,
            match="NaN",
        ):
            service.get_production_profile(
                self.configuration()
            )

    def test_rejects_profile_with_negative_production(self):
        response = self.response()

        response["outputs"]["hourly"][100]["P"] = -100.0

        production_service = PVGISProductionService(
            client=FakePVGISClient(response)
        )

        service = PVGISProductionProfileService(
            production_service=production_service
        )

        with pytest.raises(
            ValueError,
            match="negative",
        ):
            service.get_production_profile(
                self.configuration()
            )

    def test_leap_year_profile_removes_february_29(self):

        response = self.response(year=2024)

        production_service = PVGISProductionService(
            client=FakePVGISClient(response)
        )

        service = PVGISProductionProfileService(
            production_service=production_service
        )

        configuration = SolarConfiguration(
            latitude=41.62,
            longitude=2.09,
            tilt=30,
            azimuth=0,
            losses=14.0,
            pv_technology="crystSi",
            mounting_place="building",
            reference_year=2024,
        )

        result = service.get_production_profile(configuration)

        assert len(result.hourly_production) == 8760
        assert result.hourly_production.index[0] == pd.Timestamp(
            "2024-01-01 00:00:00"
        )
        assert result.hourly_production.index[-1] == pd.Timestamp(
            "2024-12-31 23:00:00"
        )
        assert not (
            (result.hourly_production.index.month == 2)
            & (result.hourly_production.index.day == 29)
        ).any()