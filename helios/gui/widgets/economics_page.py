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
    QHBoxLayout,
    QTabWidget,
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

        overview_widget = QWidget()

        overview_layout = QHBoxLayout(overview_widget)
        overview_layout.setContentsMargins(0, 0, 0, 0)
        overview_layout.setSpacing(10)

        overview_layout.addWidget(
            summary_group,
            1,
        )

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

        overview_layout.addWidget(
            profitability_group,
            1,
        )

        # ==================================================
        # Botón
        # ==================================================

        self.calculate_button = QPushButton(
            "Calcular\nanálisis económico"
        )
        self.calculate_button.clicked.connect(
            self.calculate
        )

        overview_layout.addWidget(
            self.calculate_button,
            0,
            Qt.AlignmentFlag.AlignCenter,
        )

        layout.addWidget(overview_widget)

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

        self.cash_flow_tabs = QTabWidget()
        cash_flow_layout.addWidget(self.cash_flow_tabs)

        layout.addWidget(
            cash_flow_group
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
        """Actualiza la rentabilidad de la solución recomendada."""

        solar = getattr(
            self.project,
            "solar",
            None,
        )

        energy_recommendation = getattr(
            solar,
            "energy_recommendation",
            None,
        )

        battery_recommendation = None

        if energy_recommendation is not None:
            candidate = getattr(
                energy_recommendation,
                "battery_recommendation",
                None,
            )

            if (
                candidate is not None
                and getattr(
                    candidate,
                    "combined_economic_analysis_calculated",
                    False,
                )
            ):
                battery_recommendation = candidate

        if battery_recommendation is not None:
            payback = (
                battery_recommendation
                .combined_economic_payback_years
            )
            npv = (
                battery_recommendation
                .combined_economic_npv_eur
            )
            irr = (
                battery_recommendation
                .combined_economic_irr_percent
            )

            self.payback_label.setText(
                f"{payback:.2f} años"
                if payback == payback
                and abs(payback) != float("inf")
                else "No recuperable en 25 años"
            )

            self.npv_label.setText(
                f"{npv:,.2f} €"
                if npv == npv
                and abs(npv) != float("inf")
                else "N/D"
            )

            self.irr_label.setText(
                f"{irr:.2f} %"
                if irr == irr
                and abs(irr) != float("inf")
                else "N/D"
            )

        else:
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
                self.npv_label.setText("N/D")

            if economics.irr is not None:
                self.irr_label.setText(
                    f"{economics.irr * 100:.2f} %"
                )
            else:
                self.irr_label.setText("N/D")

        self.discount_rate_label.setText(
            f"{self.project.economics.configuration.discount_rate * 100:.2f} %"
        )

    def update_battery_analysis(self):

        solar = getattr(
            self.project,
            "solar",
            None,
        )

        energy_recommendation = getattr(
            solar,
            "energy_recommendation",
            None,
        )

        if energy_recommendation is not None:
            selected_panel_count = (
                energy_recommendation.panel_count
            )

            recommendations = [
                alternative.battery_recommendation
                for alternative in energy_recommendation.alternatives
                if (
                    alternative.panel_count
                    == selected_panel_count
                )
            ]
        else:
            # Compatibilidad con el flujo de evaluación
            # de baterías de la página Solar.
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
        """Muestra los flujos de caja de las alternativas FV+batería."""

        self.cash_flow_tabs.clear()

        solar = getattr(
            self.project,
            "solar",
            None,
        )

        energy_recommendation = getattr(
            solar,
            "energy_recommendation",
            None,
        )

        if energy_recommendation is not None:
            selected_panel_count = (
                energy_recommendation.panel_count
            )

            recommendations = [
                alternative.battery_recommendation
                for alternative in energy_recommendation.alternatives
                if (
                    alternative.panel_count
                    == selected_panel_count
                )
            ]
        else:
            # Compatibilidad con el flujo anterior de evaluación.
            recommendations = getattr(
                solar,
                "battery_recommendations",
                [],
            ) or []

        viable_recommendations = [
            recommendation
            for recommendation in recommendations
            if (
                recommendation.combined_economic_analysis_calculated
                and recommendation.combined_economic_npv_eur > 0
                and recommendation.combined_economic_cash_flows
                and recommendation.combined_economic_cumulative_cash_flow
            )
        ]

        if not viable_recommendations:
            empty_label = QLabel(
                "No hay alternativas con VAN combinado positivo "
                "y flujo de caja disponible."
            )
            empty_label.setWordWrap(True)

            self.cash_flow_tabs.addTab(
                empty_label,
                "Sin alternativas viables",
            )
            return

        viable_recommendations.sort(
            key=lambda recommendation: (
                recommendation.combined_economic_npv_eur,
                -recommendation.capacity_kwh,
            ),
            reverse=True,
        )

        for recommendation in viable_recommendations:
            cash_flows = (
                recommendation.combined_economic_cash_flows
            )
            cumulative_flows = (
                recommendation.combined_economic_cumulative_cash_flow
            )

            if len(cash_flows) != len(cumulative_flows):
                continue

            table = QTableWidget(
                len(cash_flows),
                3,
            )
            table.setMinimumHeight(220)
            table.setHorizontalHeaderLabels(
                [
                    "Año",
                    "Flujo de caja (€)",
                    "Flujo acumulado (€)",
                ]
            )

            for year, (cash_flow, cumulative_flow) in enumerate(
                zip(cash_flows, cumulative_flows)
            ):
                table.setItem(
                    year,
                    0,
                    QTableWidgetItem(str(year)),
                )
                table.setItem(
                    year,
                    1,
                    QTableWidgetItem(f"{cash_flow:,.2f}"),
                )
                table.setItem(
                    year,
                    2,
                    QTableWidgetItem(f"{cumulative_flow:,.2f}"),
                )

            table.resizeColumnsToContents()

            capacity = recommendation.capacity_kwh
            npv = recommendation.combined_economic_npv_eur
            irr = recommendation.combined_economic_irr_percent
            payback = recommendation.combined_economic_payback_years

            irr_text = (
                f"{irr:.2f} %"
                if irr == irr and abs(irr) != float("inf")
                else "N/D"
            )
            payback_text = (
                f"{payback:.2f} años"
                if payback == payback
                and abs(payback) != float("inf")
                else "N/D"
            )

            details = QWidget()
            details_layout = QVBoxLayout(details)

            details_layout.addWidget(
                QLabel(
                    f"VAN combinado: {npv:,.2f} €    |    "
                    f"TIR: {irr_text}    |    "
                    f"Recuperación: {payback_text}"
                )
            )
            details_layout.addWidget(table)

            self.cash_flow_tabs.addTab(
                details,
                f"{capacity:g} kWh",
            )