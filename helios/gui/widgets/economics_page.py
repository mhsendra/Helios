from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
)

from helios.core.economic_scenarios import default_economic_scenarios

class EconomicsPage(QWidget):

    def __init__(self, project):

        super().__init__()

        self.project = project
        self.controller = self.project.economics

        layout = QVBoxLayout(self)

        title = QLabel("<h2>Economía</h2>")
        layout.addWidget(title)

        # ==================================================
        # Resumen económico
        # ==================================================

        summary_group = QGroupBox(
            "Resumen económico"
        )

        summary_layout = QFormLayout(
            summary_group
        )

        self.cost_without_pv_label = QLabel("-")
        self.cost_with_pv_label = QLabel("-")
        self.annual_savings_label = QLabel("-")
        self.self_consumption_savings_label = QLabel("-")
        self.export_income_label = QLabel("-")
        self.net_investment_label = QLabel("-")

        summary_layout.addRow(
            "Coste sin FV",
            self.cost_without_pv_label
        )

        summary_layout.addRow(
            "Coste con FV",
            self.cost_with_pv_label
        )

        summary_layout.addRow(
            "Ahorro anual",
            self.annual_savings_label
        )

        summary_layout.addRow(
            "Ahorro por autoconsumo",
            self.self_consumption_savings_label
        )

        summary_layout.addRow(
            "Ingresos por excedentes",
            self.export_income_label
        )

        summary_layout.addRow(
            "Inversión neta",
            self.net_investment_label
        )

        layout.addWidget(summary_group)

        # ==================================================
        # Rentabilidad
        # ==================================================

        profitability_group = QGroupBox(
            "Rentabilidad"
        )

        profitability_layout = QFormLayout(
            profitability_group
        )

        self.payback_label = QLabel("-")
        self.npv_label = QLabel("-")
        self.irr_label = QLabel("-")
        self.discount_rate_label = QLabel("-")

        profitability_layout.addRow(
            "Payback",
            self.payback_label
        )

        profitability_layout.addRow(
            "VAN",
            self.npv_label
        )

        profitability_layout.addRow(
            "TIR",
            self.irr_label
        )

        profitability_layout.addRow(
            "Tasa de descuento",
            self.discount_rate_label
        )

        layout.addWidget(
            profitability_group
        )

        # ==================================================
        # Flujo de caja
        # ==================================================

        cash_flow_group = QGroupBox(
            "Flujo de caja"
        )

        cash_flow_layout = QVBoxLayout(
            cash_flow_group
        )

        self.cash_flow_table = QTableWidget()

        cash_flow_layout.addWidget(
            self.cash_flow_table
        )

        layout.addWidget(
            cash_flow_group
        )

        # ==================================================
        # Botón
        # ==================================================

        self.calculate_button = QPushButton(
            "Calcular análisis económico"
        )

        layout.addWidget(
            self.calculate_button
        )

        self.calculate_button.clicked.connect(
            self.calculate
        )

        layout.addStretch()

    def calculate(self):

        self.controller.calculate()

        scenarios = default_economic_scenarios()

        self.controller.calculate_scenarios(
            scenarios
        )

        self.update_summary()
        self.update_profitability()
        self.update_cash_flow()

    def update_summary(self):

        economics = self.project.analyzer.economics_engine

        self.cost_without_pv_label.setText(
            f"{economics.cost_without_pv:,.2f} €"
        )

        self.cost_with_pv_label.setText(
            f"{economics.cost_with_pv:,.2f} €"
        )

        self.annual_savings_label.setText(
            f"{economics.annual_savings:,.2f} €"
        )

        self.self_consumption_savings_label.setText(
            f"{economics.self_consumption_savings:,.2f} €"
        )

        self.export_income_label.setText(
            f"{economics.export_income:,.2f} €"
        )

        self.net_investment_label.setText(
            f"{economics.net_investment:,.2f} €"
        )

    def update_profitability(self):

        economics = self.project.analyzer.economics_engine

        self.payback_label.setText(
            f"{economics.payback_years:.2f} años"
        )

        self.npv_label.setText(
            f"{economics.npv:,.2f} €"
        )

        self.irr_label.setText(
            f"{economics.irr * 100:.2f} %"
        )

        self.discount_rate_label.setText(
            f"{self.project.economics.configuration.discount_rate * 100:.2f} %"
        )

    def update_cash_flow(self):

        cash_flow = (
            self.project.analyzer
            .economics_engine
            .cash_flow
        )

        if cash_flow is None or cash_flow.empty:

            self.cash_flow_table.clear()
            self.cash_flow_table.setRowCount(0)
            self.cash_flow_table.setColumnCount(0)

            return

        self.cash_flow_table.setRowCount(
            len(cash_flow)
        )

        self.cash_flow_table.setColumnCount(
            len(cash_flow.columns)
        )

        headers = {
            "year": "Año",
            "self_consumption_savings": "Ahorro autoconsumo",
            "export_income": "Ingresos excedentes",
            "maintenance_cost": "Mantenimiento",
            "cash_flow": "Flujo de caja",
            "cumulative_cash_flow": "Flujo acumulado",
        }

        self.cash_flow_table.setHorizontalHeaderLabels(
            [
                headers.get(
                    column,
                    str(column)
                )
                for column in cash_flow.columns
            ]
        )

        for row in range(len(cash_flow)):

            for column in range(len(cash_flow.columns)):

                value = cash_flow.iloc[
                    row,
                    column
                ]

                if isinstance(value, float):

                    text = f"{value:,.2f}"

                else:

                    text = str(value)

                self.cash_flow_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(text)
                )

        self.cash_flow_table.resizeColumnsToContents()