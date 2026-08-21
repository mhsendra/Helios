from unittest.mock import MagicMock

from helios.core.controllers.solar_controller import SolarController


class TestSolarControllerState:

    def setup_method(self):

        self.analyzer = MagicMock()

        self.controller = SolarController(
            self.analyzer
        )

    def test_controller_does_not_store_solar_state(self):

        assert "hourly_production" not in self.controller.__dict__
        assert "daily_production" not in self.controller.__dict__
        assert "monthly_production" not in self.controller.__dict__
        assert "yearly_production" not in self.controller.__dict__
        assert "statistics" not in self.controller.__dict__
        assert "energy_balance" not in self.controller.__dict__

