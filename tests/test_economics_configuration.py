from helios.core.economics_configuration import EconomicsConfiguration


class TestEconomicsConfiguration:

    def test_required_installation_cost(self):

        configuration = EconomicsConfiguration(
            installation_cost=12000.0
        )

        assert configuration.installation_cost == 12000.0

    def test_default_values(self):

        configuration = EconomicsConfiguration(
            installation_cost=12000.0
        )

        assert configuration.subsidies == 0.0
        assert configuration.tax_deductions == 0.0

        assert configuration.first_year_degradation == 0.01
        assert configuration.annual_degradation == 0.0035

        assert configuration.annual_electricity_price_growth == 0.02
        assert configuration.annual_export_price_growth == 0.0

        assert configuration.annual_maintenance_cost == 150.0
        assert configuration.annual_maintenance_growth == 0.02

        assert configuration.discount_rate == 0.05

    def test_custom_values(self):

        configuration = EconomicsConfiguration(
            installation_cost=15000.0,
            subsidies=2000.0,
            tax_deductions=3000.0,
            first_year_degradation=0.02,
            annual_degradation=0.005,
            annual_electricity_price_growth=0.03,
            annual_export_price_growth=0.01,
            annual_maintenance_cost=200.0,
            annual_maintenance_growth=0.025,
            discount_rate=0.06,
        )

        assert configuration.installation_cost == 15000.0
        assert configuration.subsidies == 2000.0
        assert configuration.tax_deductions == 3000.0

        assert configuration.first_year_degradation == 0.02
        assert configuration.annual_degradation == 0.005

        assert configuration.annual_electricity_price_growth == 0.03
        assert configuration.annual_export_price_growth == 0.01

        assert configuration.annual_maintenance_cost == 200.0
        assert configuration.annual_maintenance_growth == 0.025

        assert configuration.discount_rate == 0.06