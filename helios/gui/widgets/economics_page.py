from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QFormLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QScrollArea,
)

from helios.core.economic_scenarios import default_economic_scenarios

class EconomicsPage(QWidget):

    def __init__(self, project):

        super().__init__()

        self.project = project
        self.controller = self.project.economics

        outer_layout = QVBoxLayout(self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        content = QWidget()

        layout = QVBoxLayout(content)

        # ==================================================
        # Resumen económico
        # ==================================================

        title = QLabel("<h2>Economía</h2>")
        layout.addWidget(title)
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
        # Análisis económico del almacenamiento
        # ==================================================

        battery_group = QGroupBox(
            "Análisis económico del almacenamiento"
        )

        battery_layout = QVBoxLayout(
            battery_group
        )

        self.battery_table = QTableWidget()

        self.battery_table.setMinimumHeight(220)

        battery_layout.addWidget(
            self.battery_table
        )

        layout.addWidget(
            battery_group
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

        self.cash_flow_table.setMinimumHeight(220)

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

        self.scroll_area.setWidget(content)

        outer_layout.addWidget(
            self.scroll_area
        )

    def calculate(self):

        self.controller.calculate()

        scenarios = default_economic_scenarios()

        self.controller.calculate_scenarios(
            scenarios
        )

        self.update_summary()
        self.update_profitability()
        self.update_battery_analysis()
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

        economics = (
            self.project
            .analyzer
            .economics_engine
        )

        if economics.payback_years is not None:

            self.payback_label.setText(
                f"{economics.payback_years:.2f} años"
            )

        else:

            self.payback_label.setText(
                "No recuperable en 25 años"
            )

        if economics.npv is not None:

            self.npv_label.setText(
                f"{economics.npv:,.2f} €"
            )

        else:

            self.npv_label.setText(
                "N/D"
            )

        if economics.irr is not None:

            self.irr_label.setText(
                f"{economics.irr * 100:.2f} %"
            )

        else:

            self.irr_label.setText(
                "N/D"
            )

        self.discount_rate_label.setText(
            f"{self.project.economics.configuration.discount_rate * 100:.2f} %"
        )

    def update_battery_analysis(self):

        solar = getattr(
            self.project,
            "solar",
            None,
        )

        recommendations = getattr(
            solar,
            "battery_recommendations",
            [],
        )

        headers = [
            "Capacidad",
            "Coste anual",
            "Ahorro adicional",
            "Coste incremental",
            "Ahorro incremental",
            "Ahorro marginal",
            "PB marginal",
            "VAN",
            "TIR",
            "PB",
        ]

        self.battery_table.clear()
        self.battery_table.setColumnCount(
            len(headers)
        )
        self.battery_table.setHorizontalHeaderLabels(
            headers
        )

        if not recommendations:

            self.battery_table.setRowCount(0)
            self.battery_table.resizeColumnsToContents()
            
            return

        self.battery_table.setRowCount(
            len(recommendations)
        )

        for row, recommendation in enumerate(
            recommendations
        ):

            marginal_payback = (
                "N/D"
                if recommendation.marginal_payback_years
                == float("inf")
                else (
                    f"{recommendation.marginal_payback_years:.2f} años"
                )
            )

            values = [
                f"{recommendation.capacity_kwh:.1f} kWh",
                f"{recommendation.annual_cost_with_battery_eur:,.2f} €",
                f"{recommendation.annual_additional_savings_eur:,.2f} €",
                f"{recommendation.incremental_battery_cost_eur:,.2f} €",
                f"{recommendation.incremental_savings_eur:,.2f} €",
                f"{recommendation.marginal_savings_per_kwh:,.2f} €/kWh",
                marginal_payback,
                f"{recommendation.economic_npv_eur:,.2f} €",
                f"{recommendation.economic_irr_percent:.2f} %",
                f"{recommendation.economic_payback_years:.2f} años",
            ]

            for column, value in enumerate(values):

                self.battery_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(value),
                )

        self.battery_table.resizeColumnsToContents()
        self.battery_table.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

    def refresh_battery_analysis(self):
        """Actualiza la tabla económica del almacenamiento."""

        self.update_battery_analysis()
        
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