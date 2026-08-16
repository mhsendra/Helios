from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)


class TariffsPage(QWidget):

    def __init__(self, project):

        super().__init__()

        self.project = project

        layout = QVBoxLayout(self)

        # ==================================================
        # Título
        # ==================================================

        title = QLabel("<h2>Tarifas eléctricas</h2>")

        layout.addWidget(title)

        # ==================================================
        # Períodos tarifarios
        # ==================================================

        layout.addWidget(
            QLabel("<h3>Períodos tarifarios</h3>")
        )

        self.period_table = QTableWidget()

        self.period_table.setColumnCount(5)

        self.period_table.setHorizontalHeaderLabels(
            [
                "Período",
                "Consumo",
                "Porcentaje",
                "Precio de compra",
                "Gasto"
            ]
        )

        header = self.period_table.horizontalHeader()

        for column in range(5):
            header.setSectionResizeMode(
                column,
                QHeaderView.Stretch
            )

        self.period_table.setRowCount(4)

        layout.addWidget(self.period_table)

        # ==================================================
        # Compensación de excedentes
        # ==================================================

        layout.addWidget(
            QLabel("<h3>Compensación de excedentes</h3>")
        )

        self.sell_price_label = QLabel("-")

        layout.addWidget(self.sell_price_label)

        layout.addStretch()

        # ==================================================
        # Datos iniciales
        # ==================================================

        self.update()

    # ==================================================
    # Actualización
    # ==================================================

    def update_periods(self):

        tariff_engine = (
            self.project.analyzer.tariff_engine
        )

        consumption = (
            tariff_engine.period_consumption
            or {}
        )

        percentages = (
            tariff_engine.period_percentage
            or {}
        )

        prices = tariff_engine.prices

        periods = [
            ("Punta", prices.buy_p1),
            ("Llano", prices.buy_p2),
            ("Valle", prices.buy_p3),
        ]

        self.period_table.setRowCount(4)

        total_consumption = 0.0
        total_percentage = 0.0
        total_expense = 0.0

        for row, (period, price) in enumerate(periods):

            consumption_value = consumption.get(
                period,
                0.0
            )

            percentage_value = percentages.get(
                period,
                0.0
            )

            expense = (
                consumption_value * price
            )

            total_consumption += consumption_value
            total_percentage += percentage_value
            total_expense += expense

            self.period_table.setItem(
                row,
                0,
                QTableWidgetItem(period)
            )

            self.period_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    f"{consumption_value:,.2f} kWh"
                )
            )

            self.period_table.setItem(
                row,
                2,
                QTableWidgetItem(
                    f"{percentage_value:.2f} %"
                )
            )

            self.period_table.setItem(
                row,
                3,
                QTableWidgetItem(
                    f"{price:.2f} €/kWh"
                )
            )

            self.period_table.setItem(
                row,
                4,
                QTableWidgetItem(
                    f"{expense:,.2f} €"
                )
            )

        # ==================================================
        # Total
        # ==================================================

        self.period_table.setItem(
            3,
            0,
            QTableWidgetItem("Total")
        )

        self.period_table.setItem(
            3,
            1,
            QTableWidgetItem(
                f"{total_consumption:,.2f} kWh"
            )
        )

        self.period_table.setItem(
            3,
            2,
            QTableWidgetItem(
                f"{total_percentage:.2f} %"
            )
        )

        self.period_table.setItem(
            3,
            3,
            QTableWidgetItem("—")
        )

        self.period_table.setItem(
            3,
            4,
            QTableWidgetItem(
                f"{total_expense:,.2f} €"
            )
        )

    def update_sell_price(self):

        tariff_engine = (
            self.project.analyzer.tariff_engine
        )

        price = tariff_engine.prices.sell_price

        self.sell_price_label.setText(
            f"{price:.2f} €/kWh"
        )

    def update(self):

        self.update_periods()
        self.update_sell_price()