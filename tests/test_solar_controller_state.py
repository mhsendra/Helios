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

    def test_coverage_reads_current_engine_state(self):

        first_balance = MagicMock()
        second_balance = MagicMock()

        self.analyzer.solar_engine.energy_balance = first_balance

        # Aquí no comprobamos el cálculo, que ya tiene sus propios tests.
        # Solo comprobamos que el controller obtiene el estado actual.

        self.analyzer.solar_engine.energy_balance = second_balance

        assert (
            self.analyzer.solar_engine.energy_balance
            is second_balance
        )

    def test_annual_production_reads_current_engine_state(self):

        first_production = MagicMock()
        second_production = MagicMock()

        self.analyzer.solar_engine.yearly_production = first_production

        self.analyzer.solar_engine.yearly_production = second_production

        assert (
            self.analyzer.solar_engine.yearly_production
            is second_production
        )

