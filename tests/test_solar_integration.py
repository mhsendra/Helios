import pandas as pd

from helios.core.controllers.solar_controller import SolarController
from helios.core.solar import SolarEngine


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

        configuration = type(
            "Configuration",
            (),
            {
                "installed_power_kwp": 5.0,
                "latitude": 41.0,
                "longitude": 2.0,
                "tilt": 30,
                "azimuth": 0,
                "reference_year": 2025,
                "losses": 14,
                "pv_technology": "crystSi",
                "mounting_place": "building",
            }
        )()

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