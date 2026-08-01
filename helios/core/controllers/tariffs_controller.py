# helios/core/controllers/tariffs_controller.py

class TariffsController:

    def __init__(self, analyzer):
        """
        Controlador de tarifas eléctricas.
        Encapsula cálculos y reportes relacionados con periodos tarifarios.
        """
        self.analyzer = analyzer

    # ==================================================
    # Cálculos de tarifas
    # ==================================================

    def calculate_tariff_periods(self):
        self.analyzer.tariff_engine.calculate_period_consumption(
            self.analyzer.valid_dataset()
        )
        self.analyzer.tariff_engine.calculate_period_percentage()

    def calculate(self):
        """
        Ejecuta todos los cálculos de tarifas.
        """
        self.calculate_tariff_periods()

    # ==================================================
    # Reportes de tarifas
    # ==================================================

    def tariff_periods_report(self):
        self.analyzer.tariff_reporter.tariff_periods(
            self.analyzer.tariff_engine.period_consumption,
            self.analyzer.tariff_engine.period_percentage,
            self.analyzer.tariff_engine.PERIODS
        )

    def reports(self):
        """
        Genera todos los informes de tarifas.
        """
        self.tariff_periods_report()
