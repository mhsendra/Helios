from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QGroupBox,
)


class GraphicsPage(QWidget):

    def __init__(self, project):

        super().__init__()

        self.project = project

        layout = QVBoxLayout(self)

        # ==================================================
        # Título
        # ==================================================

        title = QLabel("<h2>Gráficas</h2>")

        layout.addWidget(title)

        # ==================================================
        # Perfiles
        # ==================================================

        profiles_group = QGroupBox("Perfiles de consumo")

        profiles_layout = QGridLayout()

        self.hourly_button = QPushButton(
            "Perfil horario"
        )

        self.weekday_button = QPushButton(
            "Perfil semanal"
        )

        self.workday_weekend_button = QPushButton(
            "Laborables vs. fin de semana"
        )

        self.monthly_profile_button = QPushButton(
            "Perfil mensual"
        )

        self.seasonal_button = QPushButton(
            "Perfil estacional"
        )

        profiles_layout.addWidget(
            self.hourly_button,
            0,
            0
        )

        profiles_layout.addWidget(
            self.weekday_button,
            0,
            1
        )

        profiles_layout.addWidget(
            self.workday_weekend_button,
            1,
            0
        )

        profiles_layout.addWidget(
            self.monthly_profile_button,
            1,
            1
        )

        profiles_layout.addWidget(
            self.seasonal_button,
            2,
            0
        )

        profiles_group.setLayout(
            profiles_layout
        )

        layout.addWidget(profiles_group)

        # ==================================================
        # Comparativas
        # ==================================================

        comparisons_group = QGroupBox("Comparativas")

        comparisons_layout = QGridLayout()

        self.monthly_comparison_button = QPushButton(
            "Comparativa mensual"
        )

        self.weekly_comparison_button = QPushButton(
            "Comparativa semanal"
        )

        self.yearly_comparison_button = QPushButton(
            "Comparativa anual"
        )

        comparisons_layout.addWidget(
            self.monthly_comparison_button,
            0,
            0
        )

        comparisons_layout.addWidget(
            self.weekly_comparison_button,
            0,
            1
        )

        comparisons_layout.addWidget(
            self.yearly_comparison_button,
            1,
            0
        )

        comparisons_group.setLayout(
            comparisons_layout
        )

        layout.addWidget(
            comparisons_group
        )

        # ==================================================
        # Variaciones
        # ==================================================

        variations_group = QGroupBox("Variaciones")

        variations_layout = QGridLayout()

        self.monthly_variation_button = QPushButton(
            "Variación mensual"
        )

        self.weekly_variation_button = QPushButton(
            "Variación semanal"
        )

        variations_layout.addWidget(
            self.monthly_variation_button,
            0,
            0
        )

        variations_layout.addWidget(
            self.weekly_variation_button,
            0,
            1
        )

        variations_group.setLayout(
            variations_layout
        )

        layout.addWidget(
            variations_group
        )

        layout.addStretch()

# ==================================================
# Conexiones
# ==================================================

        self.hourly_button.clicked.connect(
            self.show_hourly_profile
        )

        self.weekday_button.clicked.connect(
            self.show_weekday_profile
        )

        self.workday_weekend_button.clicked.connect(
            self.show_workday_vs_weekend_profile
        )

        self.monthly_profile_button.clicked.connect(
            self.show_monthly_profile
        )

        self.seasonal_button.clicked.connect(
            self.show_seasonal_profile
        )

        self.monthly_comparison_button.clicked.connect(
            self.show_monthly_comparison
        )

        self.weekly_comparison_button.clicked.connect(
            self.show_weekly_comparison
        )

        self.yearly_comparison_button.clicked.connect(
            self.show_yearly_comparison
        )

        self.monthly_variation_button.clicked.connect(
            self.show_monthly_variation
        )

        self.weekly_variation_button.clicked.connect(
            self.show_weekly_variation
        )

# ==================================================
# Gráficas
# ==================================================

    def show_hourly_profile(self):
        self.project.profiles.plot_hourly_profile()
        self.project.analyzer.show_plots()


    def show_weekday_profile(self):
        self.project.profiles.plot_weekday_profile()
        self.project.analyzer.show_plots()


    def show_workday_vs_weekend_profile(self):
        self.project.profiles.plot_workday_vs_weekend_profile()
        self.project.analyzer.show_plots()


    def show_monthly_profile(self):
        self.project.profiles.plot_monthly_profile()
        self.project.analyzer.show_plots()


    def show_seasonal_profile(self):
        self.project.profiles.plot_seasonal_profile()
        self.project.analyzer.show_plots()


    def show_monthly_comparison(self):
        self.project.comparisons.plot_monthly_comparison()
        self.project.analyzer.show_plots()


    def show_weekly_comparison(self):
        self.project.comparisons.plot_weekly_comparison()
        self.project.analyzer.show_plots()


    def show_yearly_comparison(self):
        self.project.comparisons.plot_yearly_comparison()
        self.project.analyzer.show_plots()


    def show_monthly_variation(self):
        self.project.comparisons.plot_monthly_variation()
        self.project.analyzer.show_plots()


    def show_weekly_variation(self):
        self.project.comparisons.plot_weekly_variation()
        self.project.analyzer.show_plots()