# helios/core/controllers/indicators_controller.py

class IndicatorsController:

    def __init__(self, analyzer):
        """
        Controlador de indicadores energéticos.
        Encapsula cálculos, reportes y gráficas relacionadas
        con indicadores de consumo.
        """
        self.analyzer = analyzer

    # ==================================================
    # Cálculos de indicadores
    # ==================================================

    def calculate_mean_consumption(self):
        self.analyzer.indicators_engine.calculate_mean_consumption(
            self.analyzer.valid_dataset()
        )

    def calculate_extremes(self):
        self.analyzer.indicators_engine.calculate_extremes(
            dataset=self.analyzer.valid_dataset(),
            daily=self.analyzer.statistics_engine.daily_consumption,
            monthly=self.analyzer.statistics_engine.monthly_consumption,
            weekly=self.analyzer.comparisons.get_weekly_comparison()
        )

    def calculate_base_load(self):
        self.analyzer.indicators_engine.calculate_base_load(
            self.analyzer.valid_dataset()
        )

    def calculate(self):
        """
        Ejecuta todos los cálculos de indicadores.
        """
        self.calculate_mean_consumption()
        self.calculate_extremes()
        self.calculate_base_load()

    # ==================================================
    # Reportes de indicadores
    # ==================================================

    def mean_consumption_report(self):
        self.analyzer.indicator_reporter.mean_consumption(
            self.analyzer.indicators_engine.mean_consumption
        )

    def extremes_report(self):
        self.analyzer.indicator_reporter.extremes(
            self.analyzer.indicators_engine.extremes
        )

    def base_load_report(self):
        self.analyzer.indicator_reporter.base_load(
            self.analyzer.indicators_engine.base_load
        )

    def reports(self):
        """
        Genera todos los informes de indicadores.
        """
        self.mean_consumption_report()
        self.extremes_report()
        self.base_load_report()
