import pytest

from PySide6.QtWidgets import QApplication

from helios.gui.widgets.tariffs_page import TariffsPage


@pytest.fixture
def app():
    return QApplication.instance() or QApplication([])


class TestTariffsPage:

    def create_project(self):

        project = type("Project", (), {})()

        project.analyzer = type(
            "Analyzer",
            (),
            {}
        )()

        project.analyzer.tariff_engine = type(
            "TariffEngine",
            (),
            {}
        )()

        tariff = project.analyzer.tariff_engine

        tariff.period_consumption = {
            "Punta": 1200.0,
            "Llano": 1800.0,
            "Valle": 2500.0,
        }

        tariff.period_percentage = {
            "Punta": 21.82,
            "Llano": 32.73,
            "Valle": 45.45,
        }

        tariff.prices = type(
            "TariffPrices",
            (),
            {
                "buy_p1": 0.25,
                "buy_p2": 0.18,
                "buy_p3": 0.12,
                "sell_price": 0.06,
            }
        )()

        return project

    def test_page_initialization(self, app):

        project = self.create_project()

        page = TariffsPage(project)

        assert page.project is project

        assert page.period_table.rowCount() == 4
        assert page.period_table.columnCount() == 5

        assert (
            page.period_table.horizontalHeaderItem(0).text()
            == "Período"
        )

        assert (
            page.period_table.horizontalHeaderItem(1).text()
            == "Consumo"
        )

        assert (
            page.period_table.horizontalHeaderItem(2).text()
            == "Porcentaje"
        )

        assert (
            page.period_table.horizontalHeaderItem(3).text()
            == "Precio de compra"
        )

        assert page.period_table.horizontalHeaderItem(4).text() == "Gasto"

        assert page.sell_price_label.text() == "0.06 €/kWh"

    def test_update_periods(self, app):

        project = self.create_project()

        page = TariffsPage(project)

        page.update_periods()

        table = page.period_table

        assert table.item(0, 0).text() == "Punta"
        assert table.item(0, 1).text() == "1,200.00 kWh"
        assert table.item(0, 2).text() == "21.82 %"
        assert table.item(0, 3).text() == "0.25 €/kWh"

        assert table.item(1, 0).text() == "Llano"
        assert table.item(1, 1).text() == "1,800.00 kWh"
        assert table.item(1, 2).text() == "32.73 %"
        assert table.item(1, 3).text() == "0.18 €/kWh"

        assert table.item(2, 0).text() == "Valle"
        assert table.item(2, 1).text() == "2,500.00 kWh"
        assert table.item(2, 2).text() == "45.45 %"
        assert table.item(2, 3).text() == "0.12 €/kWh"

    def test_update_sell_price(self, app):

        project = self.create_project()

        page = TariffsPage(project)

        page.update_sell_price()

        assert page.sell_price_label.text() == "0.06 €/kWh"

    def test_update(self, app):

        project = self.create_project()

        page = TariffsPage(project)

        page.update_periods = lambda: setattr(
            page,
            "_periods_updated",
            True
        )

        page.update_sell_price = lambda: setattr(
            page,
            "_sell_price_updated",
            True
        )

        page.update()

        assert page._periods_updated is True
        assert page._sell_price_updated is True