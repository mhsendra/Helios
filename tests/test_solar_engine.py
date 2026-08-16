from unittest.mock import MagicMock, call

from helios.core.solar import SolarEngine


class TestSolarEngine:

    def setup_method(self):

        self.engine = SolarEngine()

        self.manager = MagicMock()

        self.engine.manager = self.manager

    # ==================================================
    # Estado
    # ==================================================

    def test_engine_stores_manager(self):

        assert self.engine.manager is self.manager

    def test_engine_does_not_store_solar_state(self):

        assert "hourly_production" not in self.engine.__dict__
        assert "daily_production" not in self.engine.__dict__
        assert "monthly_production" not in self.engine.__dict__
        assert "yearly_production" not in self.engine.__dict__
        assert "statistics" not in self.engine.__dict__
        assert "energy_balance" not in self.engine.__dict__

    # ==================================================
    # Propiedades
    # ==================================================

    def test_configuration_property(self):

        value = MagicMock()

        self.manager.configuration = value

        assert self.engine.configuration is value

    def test_hourly_production_property(self):

        value = MagicMock()

        self.manager.hourly_production = value

        assert self.engine.hourly_production is value

    def test_daily_production_property(self):

        value = MagicMock()

        self.manager.daily_production = value

        assert self.engine.daily_production is value

    def test_monthly_production_property(self):

        value = MagicMock()

        self.manager.monthly_production = value

        assert self.engine.monthly_production is value

    def test_yearly_production_property(self):

        value = MagicMock()

        self.manager.yearly_production = value

        assert self.engine.yearly_production is value

    def test_statistics_property(self):

        value = MagicMock()

        self.manager.statistics = value

        assert self.engine.statistics is value

    def test_energy_balance_property(self):

        value = MagicMock()

        self.manager.energy_balance = value

        assert self.engine.energy_balance is value

    # ==================================================
    # Cálculos
    # ==================================================

    def test_calculate_hourly_production(self):

        configuration = MagicMock()

        self.engine.calculate_hourly_production(
            configuration
        )

        self.manager.calculate_hourly_production.assert_called_once_with(
            configuration
        )

    def test_calculate_daily_production(self):

        self.engine.calculate_daily_production()

        self.manager.calculate_daily_production.assert_called_once_with()

    def test_calculate_statistics(self):

        self.engine.calculate_statistics()

        self.manager.calculate_statistics.assert_called_once_with()

    def test_calculate_monthly_production(self):

        self.engine.calculate_monthly_production()

        self.manager.calculate_monthly_production.assert_called_once_with()

    def test_calculate_yearly_production(self):

        self.engine.calculate_yearly_production()

        self.manager.calculate_yearly_production.assert_called_once_with()

    def test_calculate_energy_balance(self):

        consumption = MagicMock()

        self.engine.calculate_energy_balance(
            consumption
        )

        self.manager.calculate_energy_balance.assert_called_once_with(
            consumption
        )

    # ==================================================
    # Informes
    # ==================================================

    def test_monthly_production_report(self):

        self.manager.monthly_production_report.return_value = "result"

        result = self.engine.monthly_production_report()

        self.manager.monthly_production_report.assert_called_once_with()

        assert result == "result"

    def test_production_statistics_report(self):

        self.manager.production_statistics_report.return_value = "result"

        result = self.engine.production_statistics_report()

        self.manager.production_statistics_report.assert_called_once_with()

        assert result == "result"

    def test_energy_balance_report(self):

        self.manager.energy_balance_report.return_value = "result"

        result = self.engine.energy_balance_report()

        self.manager.energy_balance_report.assert_called_once_with()

        assert result == "result"