# helios/core/controllers/profiles_controller.py

class ProfilesController:

    def __init__(self, analyzer):
        """
        Controlador de perfiles de consumo.
        Encapsula todos los cálculos y reportes relacionados
        con perfiles horarios, diarios, mensuales y estacionales.
        """
        self.analyzer = analyzer

    # ==================================================
    # Cálculos de perfiles
    # ==================================================

    def calculate_hourly_profile(self):
        self.analyzer.statistics_engine.calculate_hourly_profile(
            self.analyzer.valid_dataset()
        )

    def calculate_weekday_profile(self):
        self.analyzer.statistics_engine.calculate_weekday_profile(
            self.analyzer.valid_dataset()
        )

    def calculate_monthly_profile(self):
        self.analyzer.statistics_engine.calculate_monthly_profile(
            self.analyzer.valid_dataset()
        )

    def calculate_seasonal_profile(self):
        self.analyzer.statistics_engine.calculate_seasonal_profile()

    def calculate(self):
        """
        Ejecuta todos los cálculos de perfiles.
        """
        self.calculate_hourly_profile()
        self.calculate_weekday_profile()
        self.calculate_monthly_profile()
        self.calculate_seasonal_profile()
        self.calculate_workday_vs_weekend_profile()

    # ==================================================
    # Reportes de perfiles
    # ==================================================

    def hourly_profile_report(self):
        self.analyzer.profile_reporter.hourly_profile(
            self.analyzer.statistics_engine.hourly_profile
        )

    def weekday_profile_report(self):
        self.analyzer.profile_reporter.weekday_profile(
            self.analyzer.statistics_engine.weekday_profile
        )

    def monthly_profile_report(self):
        self.analyzer.profile_reporter.monthly_profile(
            self.analyzer.statistics_engine.monthly_profile
        )

    def seasonal_profile_report(self):
        self.analyzer.profile_reporter.seasonal_profile(
            self.analyzer.statistics_engine.seasonal_profile
        )

    def reports(self):
        """
        Genera todos los informes de perfiles.
        """
        self.hourly_profile_report()
        self.weekday_profile_report()
        self.monthly_profile_report()
        self.seasonal_profile_report()

    # ==================================================
    # Gráficas de perfiles
    # ==================================================

    def plot_hourly_profile(self):
        self.analyzer.plotter.profiles.plot_hourly_profile(
            self.analyzer.statistics_engine.hourly_profile
        )

    def plot_weekday_profile(self):
        self.analyzer.plotter.profiles.plot_weekday_profile(
            self.analyzer.statistics_engine.weekday_profile
        )

    def plot_monthly_profile(self):
        self.analyzer.plotter.profiles.plot_monthly_profile(
            self.analyzer.statistics_engine.monthly_profile
        )

    def plot_seasonal_profile(self):
        self.analyzer.plotter.profiles.plot_seasonal_profile(
            self.analyzer.statistics_engine.seasonal_profile
        )

    def calculate_workday_vs_weekend_profile(self):
        self.analyzer.statistics_engine.calculate_workday_vs_weekend_profile(
            self.analyzer.valid_dataset()
        )

    def plot_workday_vs_weekend_profile(self):
        self.analyzer.plotter.profiles.plot_workday_vs_weekend_profile(
            self.analyzer.statistics_engine.workday_vs_weekend_profile
        )

    def plots(self):
        """
        Genera todas las gráficas de perfiles.
        """
        self.plot_hourly_profile()
        self.plot_workday_vs_weekend_profile()
        self.plot_weekday_profile()
        self.plot_monthly_profile()
        self.plot_seasonal_profile()