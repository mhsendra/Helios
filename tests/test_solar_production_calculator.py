import pandas as pd
import pytest

from helios.solar.installation_candidate import (
    InstallationCandidate,
)

from helios.solar.production_profile import (
    SolarProductionProfile,
)

from helios.solar.production_calculator import (
    SolarProductionCalculator,
)

from helios.solar.PVGIS_production import PVGISProductionService
from helios.solar.pvgis_production_profile import (
    PVGISProductionProfileService,
)
from helios.solar.installation_candidate import InstallationCandidate
from helios.solar.production_calculator import SolarProductionCalculator
from helios.solar.configuration import SolarConfiguration


class TestSolarProductionCalculator:

    # ==================================================
    # Helpers
    # ==================================================

    @staticmethod
    def make_base_profile(
        value: float = 1.0,
    ) -> SolarProductionProfile:

        index = pd.date_range(
            start="2025-01-01 00:00:00",
            periods=8760,
            freq="h",
        )

        series = pd.Series(
            value,
            index=index,
            name="production_kwh",
        )

        return SolarProductionProfile(
            hourly_production=series,
            reference_year=2025,
            installed_power_kwp=1.0,
        )

    @staticmethod
    def candidate(
        panel_count: int = 15,
        panel_power_wp: int = 540,
    ) -> InstallationCandidate:

        return InstallationCandidate(
            panel_count=panel_count,
            panel_power_wp=panel_power_wp,
            panel_area_m2=1.134 * 1.762,
        )

    @staticmethod
    def calculator(
        profile: SolarProductionProfile,
    ) -> SolarProductionCalculator:

        return SolarProductionCalculator(
            base_profile=profile,
        )

    # ==================================================
    # Constructor
    # ==================================================

    def test_constructor_accepts_valid_profile(self):

        profile = self.make_base_profile()

        calculator = self.calculator(profile)

        assert calculator.base_profile is profile

    @pytest.mark.parametrize(
        "profile",
        [
            None,
            object(),
            "profile",
            123,
        ],
    )
    def test_constructor_rejects_invalid_profile(
        self,
        profile,
    ):

        with pytest.raises(TypeError):

            self.calculator(profile)

    # ==================================================
    # Calculation
    # ==================================================

    def test_calculate_returns_solar_production_profile(self):

        calculator = self.calculator(
            self.make_base_profile()
        )

        candidate = self.candidate(
            panel_count=15,
        )

        result = calculator.calculate(
            candidate
        )

        assert isinstance(
            result,
            SolarProductionProfile,
        )

    def test_calculate_scales_profile_to_candidate_power(self):

        calculator = self.calculator(
            self.make_base_profile(
                value=1.0,
            )
        )

        candidate = self.candidate(
            panel_count=15,
            panel_power_wp=540,
        )

        result = calculator.calculate(
            candidate
        )

        # 15 × 540 W = 8.10 kWp
        assert result.installed_power_kwp == pytest.approx(
            8.1
        )

        assert (
            result.hourly_production == 8.1
        ).all()

    def test_calculate_preserves_reference_year(self):

        calculator = self.calculator(
            self.make_base_profile()
        )

        result = calculator.calculate(
            self.candidate(
                panel_count=15,
            )
        )

        assert result.reference_year == 2025

    def test_calculate_preserves_8760_hour_structure(self):

        calculator = self.calculator(
            self.make_base_profile()
        )

        result = calculator.calculate(
            self.candidate(
                panel_count=15,
            )
        )

        assert len(
            result.hourly_production
        ) == 8760

        assert isinstance(
            result.hourly_production.index,
            pd.DatetimeIndex,
        )

    def test_calculate_scales_annual_production(self):

        calculator = self.calculator(
            self.make_base_profile(
                value=1.0,
            )
        )

        result = calculator.calculate(
            self.candidate(
                panel_count=15,
                panel_power_wp=540,
            )
        )

        assert result.annual_production == pytest.approx(
            8760.0 * 8.1
        )

    def test_calculate_preserves_temporal_shape(self):

        profile = self.make_base_profile(
            value=1.0,
        )

        profile.hourly_production.iloc[100] = 2.0
        profile.hourly_production.iloc[200] = 5.0

        calculator = self.calculator(
            profile
        )

        result = calculator.calculate(
            self.candidate(
                panel_count=15,
                panel_power_wp=540,
            )
        )

        assert result.hourly_production.iloc[100] == pytest.approx(
            16.2
        )

        assert result.hourly_production.iloc[200] == pytest.approx(
            40.5
        )

    # ==================================================
    # Candidate validation
    # ==================================================

    @pytest.mark.parametrize(
        "candidate",
        [
            None,
            object(),
            "candidate",
            123,
        ],
    )
    def test_calculate_rejects_invalid_candidate(
        self,
        candidate,
    ):

        calculator = self.calculator(
            self.make_base_profile()
        )

        with pytest.raises(TypeError):

            calculator.calculate(
                candidate
            )

    def test_pvgis_profile_can_be_used_by_production_calculator(self):
        
        class FakePVGISClient:

            def fetch(self, configuration):
                index = pd.date_range(
                    start="2025-01-01 00:00:00",
                    periods=8760,
                    freq="h",
                )

                hourly = [
                    {
                        "time": timestamp.strftime("%Y%m%d:%H%M"),
                        "P": 1000.0,
                        "G(i)": 100.0,
                        "T2m": 20.0,
                        "WS10m": 2.0,
                        "Int": 0,
                    }
                    for timestamp in index
                ]

                return {
                    "outputs": {
                        "hourly": hourly,
                    }
                }

        configuration = SolarConfiguration(
            latitude=41.62,
            longitude=2.09,
            tilt=30,
            azimuth=0,
            losses=14.0,
            pv_technology="crystSi",
            mounting_place="building",
            reference_year=2025,
        )

        profile_service = PVGISProductionProfileService(
            production_service=PVGISProductionService(
                client=FakePVGISClient()
            )
        )

        profile = profile_service.get_production_profile(
            configuration
        )

        candidate = InstallationCandidate(
            panel_count=15,
            panel_power_wp=540,
            panel_area_m2=2.25666,
        )

        calculator = SolarProductionCalculator(
            base_profile=profile
        )

        result = calculator.calculate(candidate)

        assert len(result.hourly_production) == 8760
        assert result.installed_power_kwp == pytest.approx(8.1)

        assert result.annual_production == pytest.approx(
            8760.0 * 8.1
        )