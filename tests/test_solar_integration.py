import pandas as pd
import pytest

from helios.core.controllers.solar_controller import SolarController
from helios.core.solar import SolarEngine
from helios.solar.configuration import SolarConfiguration


class TestSolarIntegration:

    def test_complete_solar_flow(self):

        # ==========================================
        # Engine
        # ==========================================

        engine = SolarEngine()

        manager = engine.manager

        # ==========================================
        # Configuration
        # ==========================================

        configuration = SolarConfiguration(
            latitude=41.0,
            longitude=2.0,
            tilt=30,
            azimuth=0,
            reference_year=2025,
            losses=14,
            pv_technology="crystSi",
            mounting_place="building",
        )

        # ==========================================
        # Mock PVGIS response
        # ==========================================

        manager.client.fetch = lambda configuration: {
            "outputs": {
                "hourly": [
                    {
                        "time": "20250101:0100",
                        "P": 2000,
                        "G(i)": 500,
                        "T2m": 15,
                        "WS10m": 2,
                        "Int": 0,
                    },
                    {
                        "time": "20250101:0200",
                        "P": 3000,
                        "G(i)": 700,
                        "T2m": 16,
                        "WS10m": 2,
                        "Int": 0,
                    },
                    {
                        "time": "20250102:0100",
                        "P": 1000,
                        "G(i)": 300,
                        "T2m": 14,
                        "WS10m": 1,
                        "Int": 0,
                    },
                ]
            }
        }

        # ==========================================
        # Mock Analyzer
        # ==========================================

        analyzer = type(
            "Analyzer",
            (),
            {
                "solar_engine": engine,
                "valid_dataset": lambda self: pd.DataFrame(
                    {
                        "AE_kWh": [
                            1.0,
                            2.0,
                            3.0,
                        ]
                    },
                    index=pd.to_datetime(
                        [
                            "2025-01-01 01:00",
                            "2025-01-01 02:00",
                            "2025-01-02 01:00",
                        ]
                    )
                )
            }
        )()

        controller = SolarController(
            analyzer
        )

        # ==========================================
        # Complete calculation
        # ==========================================

        controller.calculate(
            configuration
        )

        # ==========================================
        # Results
        # ==========================================

        assert controller.hourly_production is not None
        assert controller.daily_production is not None
        assert controller.monthly_production is not None
        assert controller.yearly_production is not None
        assert controller.energy_balance is not None
        assert controller.statistics is not None

        # ------------------------------------------
        # Production
        # ------------------------------------------

        assert controller.hourly_production[
            "production_kwh"
        ].sum() == pytest.approx(6.0)

        assert controller.daily_production.loc[
            pd.Timestamp("2025-01-01")
        ] == pytest.approx(5.0)

        assert controller.daily_production.loc[
            pd.Timestamp("2025-01-02")
        ] == pytest.approx(1.0)

        # ------------------------------------------
        # Energy balance
        # ------------------------------------------

        assert controller.energy_balance[
            "consumption_kwh"
        ].sum() == pytest.approx(6.0)

        assert controller.energy_balance[
            "production_kwh"
        ].sum() == pytest.approx(6.0)

        assert controller.energy_balance[
            "self_consumption_kwh"
        ].sum() == pytest.approx(4.0)

        assert controller.energy_balance[
            "grid_import_kwh"
        ].sum() == pytest.approx(2.0)

        assert controller.energy_balance[
            "grid_export_kwh"
        ].sum() == pytest.approx(2.0)

        # ------------------------------------------
        # Statistics
        # ------------------------------------------

        assert controller.statistics[
            "period_production"
        ] == pytest.approx(6.0)

        assert controller.statistics[
            "consumption"
        ] == pytest.approx(6.0)

        assert controller.statistics[
            "self_consumption"
        ] == pytest.approx(4.0)

        assert controller.statistics[
            "grid_import"
        ] == pytest.approx(2.0)

        assert controller.statistics[
            "grid_export"
        ] == pytest.approx(2.0)