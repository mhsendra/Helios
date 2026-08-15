# helios/core/controllers/comparisons_controller.py

class ComparisonsController:

    def __init__(self, analyzer):
        """
        Controlador de comparativas de consumo.
        Encapsula todos los cálculos, reportes y gráficas
        relacionados con comparaciones mensuales, semanales y anuales.
        """
        self.analyzer = analyzer

    @property
    def monthly_comparison(self):
        return self.analyzer.comparisons_engine.monthly_comparison

    @property
    def monthly_variation(self):
        return self.analyzer.comparisons_engine.monthly_variation

    @property
    def weekly_comparison(self):
        return self.analyzer.comparisons_engine.weekly_comparison

    @property
    def weekly_variation(self):
        return self.analyzer.comparisons_engine.weekly_variation

    @property
    def yearly_comparison(self):
        return self.analyzer.comparisons_engine.yearly_comparison

    # ==================================================
    # Cálculos de comparativas
    # ==================================================

    def compare_months_by_year(self):
        self.analyzer.comparisons_engine.compare_months_by_year(
            self.analyzer.valid_dataset()
        )

    def calculate_monthly_variation(self):
        self.analyzer.comparisons_engine.calculate_monthly_variation()

    def compare_weeks_by_year(self):
        self.analyzer.comparisons_engine.compare_weeks_by_year(
            self.analyzer.valid_dataset()
        )

    def calculate_weekly_variation(self):
        self.analyzer.comparisons_engine.calculate_weekly_variation()

    def compare_years(self):
        self.analyzer.comparisons_engine.compare_years(
            self.analyzer.valid_dataset()
        )

    def calculate(self):
        """
        Ejecuta todas las comparativas.
        """
        self.compare_months_by_year()
        self.calculate_monthly_variation()

        self.compare_weeks_by_year()
        self.calculate_weekly_variation()

        self.compare_years()

    # ==================================================
    # Reportes de comparativas
    # ==================================================

    def monthly_comparison_report(self):
        self.analyzer.comparisons_engine.monthly_comparison_report(
            self.analyzer.comparisons_engine.monthly_comparison
        )

    def monthly_variation_report(self):
        self.analyzer.comparisons_engine.monthly_variation_report(
            self.analyzer.comparisons_engine.monthly_variation
        )

    def weekly_comparison_report(self):
        self.analyzer.comparisons_engine.weekly_comparison_report(
            self.analyzer.comparisons_engine.weekly_comparison
        )

    def weekly_variation_report(self):
        self.analyzer.comparisons_engine.weekly_variation_report(
            self.analyzer.comparisons_engine.weekly_variation
        )

    def yearly_comparison_report(self):
        self.analyzer.comparisons_engine.yearly_comparison_report(
            self.analyzer.comparisons_engine.yearly_comparison
        )

    def reports(self):
        """
        Genera todos los informes de comparativas.
        """
        self.monthly_comparison_report()
        self.monthly_variation_report()

        self.weekly_comparison_report()
        self.weekly_variation_report()

        self.yearly_comparison_report()

    # ==================================================
    # Gráficas de comparativas
    # ==================================================

    def plot_monthly_comparison(self):
        self.analyzer.plotter.comparisons.plot_monthly_comparison(
            self.analyzer.comparisons_engine.monthly_comparison
        )

    def plot_monthly_variation(self):
        self.analyzer.plotter.variations.plot_monthly_variation(
            self.analyzer.comparisons_engine.monthly_variation
        )

    def plot_weekly_comparison(self):
        self.analyzer.plotter.comparisons.plot_weekly_comparison(
            self.analyzer.comparisons_engine.weekly_comparison
        )

    def plot_weekly_variation(self):
        self.analyzer.plotter.variations.plot_weekly_variation(
            self.analyzer.comparisons_engine.weekly_variation
        )

    def plot_yearly_comparison(self):
        self.analyzer.plotter.comparisons.plot_yearly_comparison(
            self.analyzer.comparisons_engine.yearly_comparison
        )

    def plots(self):
        """
        Genera todas las gráficas de comparativas.
        """
        self.plot_monthly_comparison()
        self.plot_monthly_variation()

        self.plot_weekly_comparison()
        self.plot_weekly_variation()

        self.plot_yearly_comparison()

    def detailed_weekly_insights(self):
        return self.analyzer.comparisons_engine.detailed_weekly_insights()

    def weekly_stability_extremes(self):
        return self.analyzer.comparisons_engine.weekly_stability_extremes()

    def detect_monthly_anomalies(self):
        return self.analyzer.comparisons_engine.detect_monthly_anomalies()

    def monthly_stability_extremes(self):
        return self.analyzer.comparisons_engine.monthly_stability_extremes()

    def monthly_trends(self):
        return self.analyzer.comparisons_engine.monthly_trends()

    def yearly_trend(self):
        return self.analyzer.comparisons_engine.yearly_trend()

    def annual_stability(self):
        return self.analyzer.comparisons_engine.annual_stability()

    def get_monthly_comparison(self):
        return self.analyzer.comparisons_engine.monthly_comparison

    def get_monthly_variation(self):
        return self.analyzer.comparisons_engine.monthly_variation

    def get_weekly_comparison(self):
        return self.analyzer.comparisons_engine.weekly_comparison

    def get_weekly_variation(self):
        return self.analyzer.comparisons_engine.weekly_variation

    def get_yearly_comparison(self):
        return self.analyzer.comparisons_engine.yearly_comparison