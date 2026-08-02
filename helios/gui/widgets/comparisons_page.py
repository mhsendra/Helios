from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QTabWidget
)


class ComparisonsPage(QWidget):

    def __init__(self, project):

        super().__init__()

        self.project = project
        self.analyzer = project.analyzer

        layout = QVBoxLayout(self)

        title = QLabel("<h2>Comparativas</h2>")
        layout.addWidget(title)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.build_summary_tab()
        self.build_weekly_tab()
        self.build_monthly_tab()
        self.build_yearly_tab()
        self.build_insights_tab()

        layout.addStretch()

    # ==========================================================
    # TABS
    # ==========================================================

    def build_summary_tab(self):

        page = QWidget()
        v = QVBoxLayout(page)

        summary_group = QGroupBox("Resumen general")
        summary_layout = QFormLayout(summary_group)

        self.summary_year_max_label = QLabel("-")
        self.summary_year_min_label = QLabel("-")
        self.summary_stable_month_label = QLabel("-")
        self.summary_volatile_month_label = QLabel("-")
        self.summary_stable_week_label = QLabel("-")
        self.summary_volatile_week_label = QLabel("-")
        self.summary_anomalies_label = QLabel("-")
        self.summary_anomalies_label.setWordWrap(True)

        summary_layout.addRow("Año de mayor consumo", self.summary_year_max_label)
        summary_layout.addRow("Año de menor consumo", self.summary_year_min_label)
        summary_layout.addRow("Mes más estable", self.summary_stable_month_label)
        summary_layout.addRow("Mes más volátil", self.summary_volatile_month_label)
        summary_layout.addRow("Semana más tranquila", self.summary_stable_week_label)
        summary_layout.addRow("Semana más crítica", self.summary_volatile_week_label)
        summary_layout.addRow("Anomalías mensuales", self.summary_anomalies_label)

        v.addWidget(summary_group)
        v.addStretch()

        self.tabs.addTab(page, "Resumen")

    def build_weekly_tab(self):

        page = QWidget()
        v = QVBoxLayout(page)

        weekly_group = QGroupBox("Comparativa semanal")
        weekly_layout = QFormLayout(weekly_group)

        self.week_max_label = QLabel("-")
        self.week_min_label = QLabel("-")

        weekly_layout.addRow("Semana de mayor consumo", self.week_max_label)
        weekly_layout.addRow("Semana de menor consumo", self.week_min_label)

        v.addWidget(weekly_group)

        insights_group = QGroupBox("Insights semanales")
        insights_layout = QFormLayout(insights_group)

        self.week_peak_label = QLabel("-")
        self.week_valley_label = QLabel("-")

        insights_layout.addRow("Pico semanal", self.week_peak_label)
        insights_layout.addRow("Valle semanal", self.week_valley_label)

        v.addWidget(insights_group)

        weekstab_group = QGroupBox("Estabilidad semanal")
        weekstab_layout = QFormLayout(weekstab_group)

        self.most_stable_week_label = QLabel("-")
        self.most_volatile_week_label = QLabel("-")

        weekstab_layout.addRow("Semana más tranquila", self.most_stable_week_label)
        weekstab_layout.addRow("Semana más crítica", self.most_volatile_week_label)

        v.addWidget(weekstab_group)

        v.addStretch()

        self.tabs.addTab(page, "Semanal")

    def build_monthly_tab(self):

        page = QWidget()
        v = QVBoxLayout(page)

        monthly_group = QGroupBox("Comparativa mensual")
        monthly_layout = QFormLayout(monthly_group)

        self.month_max_label = QLabel("-")
        self.month_min_label = QLabel("-")

        monthly_layout.addRow("Mes de mayor consumo", self.month_max_label)
        monthly_layout.addRow("Mes de menor consumo", self.month_min_label)

        v.addWidget(monthly_group)

        anomalies_group = QGroupBox("Meses anómalos")
        anomalies_layout = QVBoxLayout(anomalies_group)

        self.anomalies_label = QLabel("-")
        self.anomalies_label.setWordWrap(True)

        anomalies_layout.addWidget(self.anomalies_label)

        v.addWidget(anomalies_group)

        monthstab_group = QGroupBox("Estabilidad mensual")
        monthstab_layout = QFormLayout(monthstab_group)

        self.most_stable_month_label = QLabel("-")
        self.most_volatile_month_label = QLabel("-")

        monthstab_layout.addRow("Mes más estable", self.most_stable_month_label)
        monthstab_layout.addRow("Mes más volátil", self.most_volatile_month_label)

        v.addWidget(monthstab_group)

        v.addStretch()

        self.tabs.addTab(page, "Mensual")

    def build_yearly_tab(self):

        page = QWidget()
        v = QVBoxLayout(page)

        yearly_group = QGroupBox("Comparativa anual")
        yearly_layout = QFormLayout(yearly_group)

        self.year_max_label = QLabel("-")
        self.year_min_label = QLabel("-")

        yearly_layout.addRow("Año de mayor consumo", self.year_max_label)
        yearly_layout.addRow("Año de menor consumo", self.year_min_label)

        v.addWidget(yearly_group)

        trends_group = QGroupBox("Tendencias interanuales")
        trends_layout = QFormLayout(trends_group)

        self.trend_2024_label = QLabel("-")
        self.trend_2025_label = QLabel("-")
        self.trend_2026_label = QLabel("-")

        trends_layout.addRow("Tendencia 2024", self.trend_2024_label)
        trends_layout.addRow("Tendencia 2025", self.trend_2025_label)
        trends_layout.addRow("Tendencia 2026", self.trend_2026_label)

        v.addWidget(trends_group)

        stability_group = QGroupBox("Estabilidad anual")
        stability_layout = QFormLayout(stability_group)

        self.stab_2024_label = QLabel("-")
        self.stab_2025_label = QLabel("-")
        self.stab_2026_label = QLabel("-")

        stability_layout.addRow("Estabilidad 2024", self.stab_2024_label)
        stability_layout.addRow("Estabilidad 2025", self.stab_2025_label)
        stability_layout.addRow("Estabilidad 2026", self.stab_2026_label)

        v.addWidget(stability_group)

        v.addStretch()

        self.tabs.addTab(page, "Anual")

    def build_insights_tab(self):

        page = QWidget()
        v = QVBoxLayout(page)

        insights_group = QGroupBox("Resumen avanzado")
        insights_layout = QFormLayout(insights_group)

        self.insights_text_label = QLabel("-")
        self.insights_text_label.setWordWrap(True)

        insights_layout.addRow("Resumen del análisis comparativo", self.insights_text_label)

        v.addWidget(insights_group)
        v.addStretch()

        self.tabs.addTab(page, "Insights")

    # ==========================================================
    # UPDATE DATA
    # ==========================================================

    def update_data(self):

        comp = self.analyzer.comparisons_engine

        if (
            comp.weekly_comparison is None or
            comp.monthly_comparison is None or
            comp.yearly_comparison is None
        ):
            return

        # ------------------------------------------
        # Semanal
        # ------------------------------------------

        weekly = comp.weekly_comparison

        week_max = weekly.stack().idxmax()
        week_min = weekly.stack().idxmin()

        self.week_max_label.setText(
            f"Semana {week_max[0]} del año {week_max[1]}"
        )

        self.week_min_label.setText(
            f"Semana {week_min[0]} del año {week_min[1]}"
        )

        insights = comp.detailed_weekly_insights()
        peak = insights["max"]
        valley = insights["min"]

        if peak["variation_prev"] is not None:
            prev_text = f"+{peak['variation_prev']:.2f}% vs año anterior"
        else:
            prev_text = "sin año anterior para comparar"

        self.week_peak_label.setText(
            f"Semana {peak['week']} del {peak['year']} — {peak['value']:.2f} kWh "
            f"({prev_text}, "
            f"+{peak['variation_mean']:.2f}% vs media anual)"
        )

        self.week_valley_label.setText(
            f"Semana {valley['week']} del {valley['year']} — {valley['value']:.2f} kWh"
        )

        week_extremes = comp.weekly_stability_extremes()
        if week_extremes:
            stable = week_extremes["stable"]
            volatile = week_extremes["volatile"]

            self.most_stable_week_label.setText(
                f"{stable['week']} — CV {stable['cv']:.2f}, "
                f"Desv. {stable['std']:.2f} ({stable['classification']})"
            )

            self.most_volatile_week_label.setText(
                f"{volatile['week']} — CV {volatile['cv']:.2f}, "
                f"Desv. {volatile['std']:.2f} ({volatile['classification']})"
            )

        # ------------------------------------------
        # Mensual
        # ------------------------------------------

        monthly = comp.monthly_comparison

        month_max = monthly.stack().idxmax()
        month_min = monthly.stack().idxmin()

        self.month_max_label.setText(
            f"Mes {month_max[0]} del año {month_max[1]}"
        )

        self.month_min_label.setText(
            f"Mes {month_min[0]} del año {month_min[1]}"
        )

        anomalies = comp.detect_monthly_anomalies()
        if anomalies:
            text = "<ul>"
            for a in anomalies:
                text += (
                    f"<li><b>{a['month']} {a['year']}</b>: "
                    f"{a['detail']}</li>"
                )
            text += "</ul>"
        else:
            text = "No se han detectado anomalías."

        self.anomalies_label.setText(text)
        self.summary_anomalies_label.setText(text)

        month_extremes = comp.monthly_stability_extremes()
        if month_extremes:
            stable = month_extremes["stable"]
            volatile = month_extremes["volatile"]

            self.most_stable_month_label.setText(
                f"{stable['month']} — CV {stable['cv']:.2f}, "
                f"Desv. {stable['std']:.2f} ({stable['classification']})"
            )

            self.most_volatile_month_label.setText(
                f"{volatile['month']} — CV {volatile['cv']:.2f}, "
                f"Desv. {volatile['std']:.2f} ({volatile['classification']})"
            )

        # ------------------------------------------
        # Anual
        # ------------------------------------------

        yearly = comp.yearly_comparison

        year_max = yearly.idxmax()
        year_min = yearly.idxmin()

        self.year_max_label.setText(str(year_max))
        self.year_min_label.setText(str(year_min))

        monthly_trends = comp.monthly_trends()
        yearly_trend = comp.yearly_trend()

        def format_trend(t):
            return (
                f"{t['classification']} "
                f"(+{t['positive_steps']} / -{t['negative_steps']}) — "
                f"Max ↑ {t['max_increase']:.2f}, Max ↓ {t['max_decrease']:.2f}"
            )

        self.trend_2024_label.setText(format_trend(monthly_trends.get(2024)))
        self.trend_2025_label.setText(format_trend(monthly_trends.get(2025)))
        self.trend_2026_label.setText(format_trend(monthly_trends.get(2026)))

        stability = comp.annual_stability()

        def format_stab(s):
            return (
                f"{s['classification']} — "
                f"Rango {s['range']:.2f} kWh, "
                f"Desv. {s['std']:.2f}, "
                f"CV {s['cv']:.2f}"
            )

        self.stab_2024_label.setText(format_stab(stability.get(2024)))
        self.stab_2025_label.setText(format_stab(stability.get(2025)))
        self.stab_2026_label.setText(format_stab(stability.get(2026)))

        # ------------------------------------------
        # Resumen (tab Resumen)
        # ------------------------------------------

        self.summary_year_max_label.setText(str(year_max))
        self.summary_year_min_label.setText(str(year_min))

        if month_extremes:
            stable_m = month_extremes["stable"]
            volatile_m = month_extremes["volatile"]

            self.summary_stable_month_label.setText(
                f"{stable_m['month']} — CV {stable_m['cv']:.2f}"
            )
            self.summary_volatile_month_label.setText(
                f"{volatile_m['month']} — CV {volatile_m['cv']:.2f}"
            )

        if week_extremes:
            stable_w = week_extremes["stable"]
            volatile_w = week_extremes["volatile"]

            self.summary_stable_week_label.setText(
                f"{stable_w['week']} — CV {stable_w['cv']:.2f}"
            )
            self.summary_volatile_week_label.setText(
                f"{volatile_w['week']} — CV {volatile_w['cv']:.2f}"
            )

        # ------------------------------------------
        # Insights avanzados
        # ------------------------------------------

        insights_text = (
            f"<b>Año de mayor consumo:</b> {year_max}<br>"
            f"<b>Año de menor consumo:</b> {year_min}<br><br>"
            f"<b>Mes más estable:</b> {self.summary_stable_month_label.text()}<br>"
            f"<b>Mes más volátil:</b> {self.summary_volatile_month_label.text()}<br><br>"
            f"<b>Semana más tranquila:</b> {self.summary_stable_week_label.text()}<br>"
            f"<b>Semana más crítica:</b> {self.summary_volatile_week_label.text()}<br><br>"
            f"<b>Tendencia anual:</b> "
            f"{yearly_trend['classification']} "
            f"(+{yearly_trend['positive_steps']} / -{yearly_trend['negative_steps']})"
        )

        self.insights_text_label.setText(insights_text)