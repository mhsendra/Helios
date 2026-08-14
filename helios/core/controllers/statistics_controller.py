# helios/core/controllers/statistics_controller.py


class StatisticsController:

    def __init__(self, analyzer):
        """
        Controlador de estadísticas de consumo.
        Encapsula los cálculos y reportes relacionados
        con estadísticas generales, diarias, mensuales y anuales.
        """
        self.analyzer = analyzer

    # ==================================================
    # Cálculos de estadísticas
    # ==================================================

    def calculate_statistics(self):

        dataset = self.analyzer.valid_dataset()

        self.analyzer.statistics_engine.calculate(
            dataset
        )

    def calculate_daily_consumption(self):

        dataset = self.analyzer.valid_dataset()

        self.analyzer.statistics_engine.calculate_daily_consumption(
            dataset
        )

    def calculate_monthly_consumption(self):

        dataset = self.analyzer.valid_dataset()

        self.analyzer.statistics_engine.calculate_monthly_consumption(
            dataset
        )

    def calculate_yearly_consumption(self):

        dataset = self.analyzer.valid_dataset()

        self.analyzer.statistics_engine.calculate_yearly_consumption(
            dataset
        )

    def calculate(self):
        """
        Ejecuta todos los cálculos de estadísticas.
        """

        self.calculate_statistics()
        self.calculate_daily_consumption()
        self.calculate_monthly_consumption()
        self.calculate_yearly_consumption()

    # ==================================================
    # Reportes de estadísticas
    # ==================================================

    def statistics_report(self):

        self.analyzer.statistics_reporter.statistics(
            self.analyzer.statistics_engine.statistics
        )

    def daily_report(self):

        self.analyzer.statistics_reporter.daily(
            self.analyzer.statistics_engine.daily_consumption
        )

    def monthly_report(self):

        self.analyzer.statistics_reporter.monthly(
            self.analyzer.statistics_engine.monthly_consumption
        )

    def yearly_report(self):

        self.analyzer.statistics_reporter.yearly(
            self.analyzer.statistics_engine.yearly_consumption
        )

    def reports(self):
        """
        Genera todos los informes de estadísticas.
        """

        self.statistics_report()
        self.daily_report()
        self.monthly_report()
        self.yearly_report()