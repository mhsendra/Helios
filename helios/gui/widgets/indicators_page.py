from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QGroupBox,
    QFormLayout
)


class IndicatorsPage(QWidget):

    def __init__(self, project):

        super().__init__()

        self.project = project
        self.analyzer = project.analyzer

        layout = QVBoxLayout(self)

        title = QLabel("<h2>Indicadores</h2>")
        layout.addWidget(title)

        # ==========================================================
        # KPI: Consumo
        # ==========================================================

        consumption_group = QGroupBox("Indicadores de consumo")
        consumption_layout = QFormLayout(consumption_group)

        self.kpi_total_year_label = QLabel("-")
        self.kpi_avg_month_label = QLabel("-")
        self.kpi_avg_day_label = QLabel("-")
        self.kpi_max_day_label = QLabel("-")
        self.kpi_min_day_label = QLabel("-")

        consumption_layout.addRow("Consumo total anual", self.kpi_total_year_label)
        consumption_layout.addRow("Consumo medio mensual", self.kpi_avg_month_label)
        consumption_layout.addRow("Consumo medio diario", self.kpi_avg_day_label)
        consumption_layout.addRow("Día de mayor consumo", self.kpi_max_day_label)
        consumption_layout.addRow("Día de menor consumo", self.kpi_min_day_label)

        layout.addWidget(consumption_group)

        # ==========================================================
        # KPI: Estabilidad
        # ==========================================================

        stability_group = QGroupBox("Indicadores de estabilidad")
        stability_layout = QFormLayout(stability_group)

        self.kpi_stable_month_label = QLabel("-")
        self.kpi_volatile_month_label = QLabel("-")
        self.kpi_stable_week_label = QLabel("-")
        self.kpi_volatile_week_label = QLabel("-")

        stability_layout.addRow("Mes más estable", self.kpi_stable_month_label)
        stability_layout.addRow("Mes más volátil", self.kpi_volatile_month_label)
        stability_layout.addRow("Semana más estable", self.kpi_stable_week_label)
        stability_layout.addRow("Semana más volátil", self.kpi_volatile_week_label)

        layout.addWidget(stability_group)

        # ==========================================================
        # KPI: Anomalías
        # ==========================================================

        anomalies_group = QGroupBox("Indicadores de anomalías")
        anomalies_layout = QFormLayout(anomalies_group)

        self.kpi_anomaly_count_label = QLabel("-")
        self.kpi_worst_anomaly_label = QLabel("-")
        self.kpi_max_anomaly_pct_label = QLabel("-")

        anomalies_layout.addRow("Número de anomalías detectadas", self.kpi_anomaly_count_label)
        anomalies_layout.addRow("Anomalía más severa", self.kpi_worst_anomaly_label)
        anomalies_layout.addRow("Máxima desviación mensual (%)", self.kpi_max_anomaly_pct_label)

        layout.addWidget(anomalies_group)

        # ==========================================================
        # KPI: Tendencias
        # ==========================================================

        trends_group = QGroupBox("Indicadores de tendencia")
        trends_layout = QFormLayout(trends_group)

        self.kpi_year_trend_label = QLabel("-")
        self.kpi_max_increase_label = QLabel("-")
        self.kpi_max_decrease_label = QLabel("-")

        trends_layout.addRow("Tendencia anual", self.kpi_year_trend_label)
        trends_layout.addRow("Máximo incremento mensual", self.kpi_max_increase_label)
        trends_layout.addRow("Máxima caída mensual", self.kpi_max_decrease_label)

        layout.addWidget(trends_group)

        layout.addStretch()

    # ==========================================================
    # UPDATE DATA
    # ==========================================================

    def update_data(self):
        """
        Actualiza todos los KPI de la página Indicadores.
        """

        analyzer = self.analyzer
        comparisons = analyzer.comparisons

        # Consumo diario: viene de ConsumptionStatistics
        if not hasattr(analyzer.statistics_engine, "daily_consumption"):
            return

        daily = analyzer.statistics_engine.daily_consumption

        if daily is None or len(daily) == 0:
            return

        # Comparativas necesarias
        if (
            comparisons.get_weekly_comparison() is None or
            comparisons.get_monthly_comparison() is None or
            comparisons.get_yearly_comparison() is None
        ):
            return

        # ==========================================================
        # KPI: Consumo
        # ==========================================================

        total_year = daily.sum()
        avg_month = daily.resample("ME").sum().mean()
        avg_day = daily.mean()

        max_day = daily.idxmax()
        min_day = daily.idxmin()

        self.kpi_total_year_label.setText(f"{total_year:.2f} kWh")
        self.kpi_avg_month_label.setText(f"{avg_month:.2f} kWh")
        self.kpi_avg_day_label.setText(f"{avg_day:.2f} kWh")

        self.kpi_max_day_label.setText(
            f"{max_day.date()} — {daily[max_day]:.2f} kWh"
        )

        self.kpi_min_day_label.setText(
            f"{min_day.date()} — {daily[min_day]:.2f} kWh"
        )

        # ==========================================================
        # KPI: Estabilidad (usa ComparisonsEngine)
        # ==========================================================

        month_extremes = comparisons.monthly_stability_extremes()
        week_extremes = comparisons.weekly_stability_extremes()

        if month_extremes:
            stable_m = month_extremes["stable"]
            volatile_m = month_extremes["volatile"]

            self.kpi_stable_month_label.setText(
                f"{stable_m['month']} — CV {stable_m['cv']:.2f}"
            )
            self.kpi_volatile_month_label.setText(
                f"{volatile_m['month']} — CV {volatile_m['cv']:.2f}"
            )

        if week_extremes:
            stable_w = week_extremes["stable"]
            volatile_w = week_extremes["volatile"]

            self.kpi_stable_week_label.setText(
                f"{stable_w['week']} — CV {stable_w['cv']:.2f}"
            )
            self.kpi_volatile_week_label.setText(
                f"{volatile_w['week']} — CV {volatile_w['cv']:.2f}"
            )

        # ==========================================================
        # KPI: Anomalías
        # ==========================================================

        anomalies = comparisons.detect_monthly_anomalies()

        self.kpi_anomaly_count_label.setText(str(len(anomalies)))

        if anomalies:
            worst = max(
                anomalies,
                key=lambda a: abs(a.get("value", 0))
            )

            self.kpi_worst_anomaly_label.setText(
                f"{worst['month']} {worst['year']} — {worst['detail']}"
            )

            if "value" in worst:
                self.kpi_max_anomaly_pct_label.setText(
                    f"{worst['value']:.2f}%"
                )
            else:
                self.kpi_max_anomaly_pct_label.setText("N/A")
        else:
            self.kpi_worst_anomaly_label.setText("Ninguna")
            self.kpi_max_anomaly_pct_label.setText("0%")

        # ==========================================================
        # KPI: Tendencias
        # ==========================================================

        yearly_trend = comparisons.yearly_trend()

        self.kpi_year_trend_label.setText(
            f"{yearly_trend['classification']} "
            f"(+{yearly_trend['positive_steps']} / "
            f"-{yearly_trend['negative_steps']})"
        )

        self.kpi_max_increase_label.setText(
            f"{yearly_trend['max_increase']:.2f}%"
        )

        self.kpi_max_decrease_label.setText(
            f"{yearly_trend['max_decrease']:.2f}%"
        )