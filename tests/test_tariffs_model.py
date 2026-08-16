from helios.core.tariffs_model import TariffPrices


class TestTariffPrices:

    def test_default_values(self):

        tariff = TariffPrices()

        assert tariff.buy_p1 == 0.25
        assert tariff.buy_p2 == 0.18
        assert tariff.buy_p3 == 0.12
        assert tariff.sell_price == 0.06

    def test_custom_values(self):

        tariff = TariffPrices(
            buy_p1=0.30,
            buy_p2=0.20,
            buy_p3=0.15,
            sell_price=0.08,
        )

        assert tariff.buy_p1 == 0.30
        assert tariff.buy_p2 == 0.20
        assert tariff.buy_p3 == 0.15
        assert tariff.sell_price == 0.08

    def test_values_are_independent_between_instances(self):

        tariff_1 = TariffPrices()
        tariff_2 = TariffPrices(
            buy_p1=0.30
        )

        assert tariff_1.buy_p1 == 0.25
        assert tariff_2.buy_p1 == 0.30

        assert tariff_1.buy_p2 == tariff_2.buy_p2
        assert tariff_1.buy_p3 == tariff_2.buy_p3
        assert tariff_1.sell_price == tariff_2.sell_price