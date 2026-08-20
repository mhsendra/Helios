from unittest.mock import MagicMock

import pytest

from helios.solar.manager import SolarManager


class TestSolarManager:

    def setup_method(self):

        self.manager = SolarManager()

        self.manager.client = MagicMock()
        self.manager.parser = MagicMock()
        self.manager.production_engine = MagicMock()
        self.manager.balance_engine = MagicMock()
        self.manager.statistics_engine = MagicMock()
        self.manager.reporter = MagicMock()

    def test_calculate_hourly_production(self):

        configuration = MagicMock()
        response = MagicMock()
        hourly_production = MagicMock()

        self.manager.client.fetch.return_value = response
        self.manager.parser.parse.return_value = hourly_production

        self.manager.calculate_hourly_production(
            configuration
        )

        self.manager.client.fetch.assert_called_once_with(
            configuration
        )

        self.manager.parser.parse.assert_called_once_with(
            response
        )

        assert self.manager.configuration is configuration
        assert self.manager.hourly_production is hourly_production

    def test_calculate_daily_production(self):

        hourly_production = MagicMock()
        daily_production = MagicMock()

        self.manager.hourly_production = hourly_production

        self.manager.production_engine.daily.return_value = (
            daily_production
        )

        self.manager.calculate_daily_production()

        self.manager.production_engine.daily.assert_called_once_with(
            hourly_production
        )

        assert self.manager.daily_production is daily_production

    def test_calculate_daily_production_without_hourly_data(self):

        with pytest.raises(
            RuntimeError,
            match="Hourly production has not been calculated."
        ):

            self.manager.calculate_daily_production()

    def test_calculate_monthly_production(self):

        daily_production = MagicMock()
        monthly_production = MagicMock()

        self.manager.daily_production = daily_production

        self.manager.production_engine.monthly.return_value = (
            monthly_production
        )

        self.manager.calculate_monthly_production()

        self.manager.production_engine.monthly.assert_called_once_with(
            daily_production
        )

        assert self.manager.monthly_production is monthly_production

    def test_calculate_monthly_production_builds_daily_if_needed(self):

        daily_production = MagicMock()
        monthly_production = MagicMock()

        self.manager.hourly_production = MagicMock()

        self.manager.calculate_daily_production = MagicMock()

        self.manager.daily_production = None

        self.manager.production_engine.monthly.return_value = (
            monthly_production
        )

        self.manager.calculate_monthly_production()

        self.manager.calculate_daily_production.assert_called_once_with()

        self.manager.production_engine.monthly.assert_called_once_with(
            self.manager.daily_production
        )

        assert self.manager.monthly_production is monthly_production

    def test_calculate_yearly_production(self):

        monthly_production = MagicMock()
        yearly_production = MagicMock()

        self.manager.monthly_production = monthly_production

        self.manager.production_engine.yearly.return_value = (
            yearly_production
        )

        self.manager.calculate_yearly_production()

        self.manager.production_engine.yearly.assert_called_once_with(
            monthly_production
        )

        assert self.manager.yearly_production is yearly_production

    def test_calculate_yearly_production_builds_monthly_if_needed(self):

        yearly_production = MagicMock()

        self.manager.hourly_production = MagicMock()

        self.manager.monthly_production = None

        self.manager.calculate_monthly_production = MagicMock()

        self.manager.production_engine.yearly.return_value = (
            yearly_production
        )

        self.manager.calculate_yearly_production()

        self.manager.calculate_monthly_production.assert_called_once_with()

        self.manager.production_engine.yearly.assert_called_once_with(
            self.manager.monthly_production
        )

        assert self.manager.yearly_production is yearly_production

    def test_calculate_energy_balance(self):

        consumption = MagicMock()
        hourly_production = MagicMock()
        energy_balance = MagicMock()

        self.manager.hourly_production = hourly_production

        self.manager.balance_engine.calculate.return_value = (
            energy_balance
        )

        self.manager.calculate_energy_balance(
            consumption
        )

        self.manager.balance_engine.calculate.assert_called_once_with(
            consumption,
            hourly_production
        )

        assert self.manager.energy_balance is energy_balance

    def test_calculate_energy_balance_without_hourly_production(self):

        consumption = MagicMock()

        with pytest.raises(
            RuntimeError,
            match="Hourly production has not been calculated."
        ):

            self.manager.calculate_energy_balance(
                consumption
            )

    def test_calculate_statistics(self):

        hourly_production = MagicMock()
        energy_balance = MagicMock()
        configuration = MagicMock()
        statistics = MagicMock()

        self.manager.hourly_production = hourly_production
        self.manager.energy_balance = energy_balance
        self.manager.configuration = configuration

        self.manager.statistics_engine.calculate.return_value = (
            statistics
        )

        self.manager.calculate_statistics()

        self.manager.statistics_engine.calculate.assert_called_once_with(
            hourly_production,
            energy_balance,
            configuration
        )

        assert self.manager.statistics is statistics

    def test_calculate_statistics_without_hourly_production(self):

        self.manager.energy_balance = MagicMock()

        with pytest.raises(
            RuntimeError,
            match="Hourly production has not been calculated."
        ):

            self.manager.calculate_statistics()

    def test_calculate_statistics_without_energy_balance(self):

        self.manager.hourly_production = MagicMock()

        with pytest.raises(
            RuntimeError,
            match="Energy balance has not been calculated."
        ):

            self.manager.calculate_statistics()

    def test_production_statistics_report(self):

        statistics = MagicMock()
        configuration = MagicMock()

        self.manager.statistics = statistics
        self.manager.configuration = configuration

        self.manager.production_statistics_report()

        self.manager.reporter.production_statistics.assert_called_once_with(
            statistics,
            configuration
        )

    def test_production_statistics_report_without_statistics(self):

        with pytest.raises(
            RuntimeError,
            match="Solar statistics have not been calculated."
        ):

            self.manager.production_statistics_report()

    def test_energy_balance_report(self):

        statistics = MagicMock()

        self.manager.statistics = statistics

        self.manager.energy_balance_report()

        self.manager.reporter.energy_balance.assert_called_once_with(
            statistics
        )

    def test_energy_balance_report_without_statistics(self):

        with pytest.raises(
            RuntimeError,
            match="Energy statistics have not been calculated."
        ):

            self.manager.energy_balance_report()

    def test_monthly_production_report(self):

        monthly_production = MagicMock()

        self.manager.monthly_production = monthly_production

        self.manager.monthly_production_report()

        self.manager.reporter.monthly_production.assert_called_once_with(
            monthly_production
        )

    def test_monthly_production_report_without_monthly_production(self):

        with pytest.raises(
            RuntimeError,
            match="Monthly production has not been calculated."
        ):

            self.manager.monthly_production_report()

    def test_second_calculation_invalidates_first_calculation(self):
    
            configuration_1 = MagicMock()
            configuration_2 = MagicMock()
    
            hourly_1 = MagicMock()
            hourly_2 = MagicMock()
    
            self.manager.client.fetch.side_effect = [
                MagicMock(),
                MagicMock(),
            ]
    
            self.manager.parser.parse.side_effect = [
                hourly_1,
                hourly_2,
            ]
    
            self.manager.calculate_hourly_production(
                configuration_1
            )
    
            self.manager.daily_production = MagicMock()
            self.manager.monthly_production = MagicMock()
            self.manager.yearly_production = MagicMock()
            self.manager.energy_balance = MagicMock()
            self.manager.statistics = MagicMock()
    
            self.manager.calculate_hourly_production(
                configuration_2
            )
    
            assert self.manager.configuration is configuration_2
            assert self.manager.hourly_production is hourly_2
    
            assert self.manager.daily_production is None
            assert self.manager.monthly_production is None
            assert self.manager.yearly_production is None
            assert self.manager.energy_balance is None
            assert self.manager.statistics is None