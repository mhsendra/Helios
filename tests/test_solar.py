from unittest.mock import MagicMock

from helios.core.solar import SolarEngine


class TestSolarEngine:

    def setup_method(self):

        self.engine = SolarEngine()

        self.engine.manager = MagicMock()

    def test_configuration_property(self):

        configuration = MagicMock()

        self.engine.manager.configuration = configuration

        assert self.engine.configuration is configuration

    def test_calculate_hourly_production(self):

        configuration = MagicMock()

        self.engine.calculate_hourly_production(
            configuration
        )

        self.engine.manager.calculate_hourly_production.assert_called_once_with(
            configuration
        )

    def test_calculate_daily_production(self):

        self.engine.calculate_daily_production()

        self.engine.manager.calculate_daily_production.assert_called_once_with()

    def test_calculate_statistics(self):

        self.engine.calculate_statistics()

        self.engine.manager.calculate_statistics.assert_called_once_with()

    def test_calculate_monthly_production(self):

        self.engine.calculate_monthly_production()

        self.engine.manager.calculate_monthly_production.assert_called_once_with()

    def test_calculate_yearly_production(self):

        self.engine.calculate_yearly_production()

        self.engine.manager.calculate_yearly_production.assert_called_once_with()

    def test_calculate_energy_balance(self):

        consumption = MagicMock()

        self.engine.calculate_energy_balance(
            consumption
        )

        self.engine.manager.calculate_energy_balance.assert_called_once_with(
            consumption
        )

    def test_hourly_production_property(self):

        value = MagicMock()

        self.engine.manager.hourly_production = value

        assert self.engine.hourly_production is value

    def test_daily_production_property(self):

        value = MagicMock()

        self.engine.manager.daily_production = value

        assert self.engine.daily_production is value

    def test_monthly_production_property(self):

        value = MagicMock()

        self.engine.manager.monthly_production = value

        assert self.engine.monthly_production is value

    def test_yearly_production_property(self):

        value = MagicMock()

        self.engine.manager.yearly_production = value

        assert self.engine.yearly_production is value

    def test_statistics_property(self):

        value = MagicMock()

        self.engine.manager.statistics = value

        assert self.engine.statistics is value

    def test_energy_balance_property(self):

        value = MagicMock()

        self.engine.manager.energy_balance = value

        assert self.engine.energy_balance is value

    def test_get_configuration(self):

        configuration = MagicMock()

        self.engine.manager.configuration = configuration

        result = self.engine.get_configuration()

        assert result is configuration