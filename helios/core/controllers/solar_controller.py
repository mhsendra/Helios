# helios/core/controllers/solar_controller.py

from helios.solar.installation_constraints import (
    InstallationConstraints,
)

from helios.solar.installation_optimizer import (
    InstallationOptimizer,
)

from helios.solar.installation_evaluation import (
    InstallationEvaluator,
)

from helios.solar.solar_installation_sizing import (
    SolarInstallationSizing,
    SolarSizingResult,
)


class SolarController:

    def __init__(self, analyzer):
        """
        Controlador de producción solar.

        Encapsula cálculos, reportes, gráficas y
        dimensionamiento de instalaciones fotovoltaicas.
        """

        self.analyzer = analyzer

        # Resultado del último dimensionamiento
        self.sizing_result: SolarSizingResult | None = None

    # ==================================================
    # Propiedades
    # ==================================================

    @property
    def hourly_production(self):
        return self.analyzer.solar_engine.hourly_production

    @property
    def daily_production(self):
        return self.analyzer.solar_engine.daily_production

    @property
    def monthly_production(self):
        return self.analyzer.solar_engine.monthly_production

    @property
    def yearly_production(self):
        return self.analyzer.solar_engine.yearly_production

    @property
    def statistics(self):
        return self.analyzer.solar_engine.statistics

    @property
    def energy_balance(self):
        return self.analyzer.solar_engine.energy_balance

    @property
    def coverage(self) -> float | None:

        balance = self.analyzer.solar_engine.energy_balance

        if balance is None or balance.empty:
            return None

        consumption = balance["consumption_kwh"].sum()

        if consumption == 0:
            return None

        self_consumption = (
            balance["self_consumption_kwh"].sum()
        )

        return 100 * self_consumption / consumption

    @property
    def annual_production(self) -> float | None:

        yearly = self.analyzer.solar_engine.yearly_production

        if yearly is None or yearly.empty:
            return None

        return float(yearly.iloc[-1])

    @property
    def self_consumption(self) -> float | None:

        balance = self.analyzer.solar_engine.energy_balance

        if balance is None:
            return None

        return float(
            balance["self_consumption_kwh"].sum()
        )

    @property
    def grid_import(self) -> float | None:

        balance = self.analyzer.solar_engine.energy_balance

        if balance is None:
            return None

        return float(
            balance["grid_import_kwh"].sum()
        )

    @property
    def grid_export(self) -> float | None:

        balance = self.analyzer.solar_engine.energy_balance

        if balance is None:
            return None

        return float(
            balance["grid_export_kwh"].sum()
        )

    @property
    def specific_production(self) -> float | None:

        annual = self.annual_production

        if annual is None:
            return None

        configuration = (
            self.analyzer.solar_engine.configuration
        )

        return (
            annual
            / configuration.installed_power_kwp
        )

    @property
    def monthly_energy_balance(self):

        balance = self.analyzer.solar_engine.energy_balance

        if balance is None:
            return None

        return balance.resample("ME").sum()

    # ==================================================
    # Dimensionamiento de instalación
    # ==================================================

    def recommend_installation(
        self,
        constraints: InstallationConstraints,
    ) -> SolarSizingResult:
        """
        Recomienda la instalación fotovoltaica óptima
        dentro de las restricciones indicadas.

        Utiliza la producción específica obtenida del
        cálculo solar existente para estimar la producción
        de cada número de paneles candidato.
        """

        if not isinstance(
            constraints,
            InstallationConstraints,
        ):
            raise TypeError(
                "constraints must be an "
                "InstallationConstraints."
            )

        # --------------------------------------------------
        # Producción solar de referencia
        # --------------------------------------------------

        configuration = (
            self.analyzer.solar_engine.configuration
        )

        if configuration is None:
            raise ValueError(
                "A solar configuration is required "
                "to recommend an installation."
            )

        specific_production = (
            self.specific_production
        )

        if specific_production is None:
            raise ValueError(
                "Solar production must be calculated "
                "before recommending an installation."
            )

        if specific_production <= 0:
            raise ValueError(
                "Specific solar production must be "
                "greater than zero."
            )

        # --------------------------------------------------
        # Consumo anual
        # --------------------------------------------------

        dataset = self.analyzer.valid_dataset()

        if dataset is None or dataset.empty:
            raise ValueError(
                "A valid consumption dataset is required "
                "to recommend an installation."
            )

        annual_consumption = float(
            dataset["AE_kWh"].sum()
        )

        if annual_consumption <= 0:
            raise ValueError(
                "Annual consumption must be greater than zero."
            )

        # --------------------------------------------------
        # Generación de candidatos
        # --------------------------------------------------

        optimizer = InstallationOptimizer(
            constraints
        )

        candidates = optimizer.generate_candidates()

        if not candidates:
            raise ValueError(
                "No valid installation candidates "
                "are available."
            )

        # --------------------------------------------------
        # Evaluación de candidatos
        # --------------------------------------------------

        evaluator = InstallationEvaluator(
            constraints
        )

        evaluations = [
            evaluator.evaluate(candidate)
            for candidate in candidates
        ]

        # --------------------------------------------------
        # Producción anual de cada candidato
        # --------------------------------------------------

        annual_productions = {}

        for evaluation in evaluations:

            annual_productions[
                evaluation.panel_count
            ] = (
                evaluation.installed_power_kwp
                * specific_production
            )

        # --------------------------------------------------
        # Selección de la instalación recomendada
        # --------------------------------------------------

        sizing = SolarInstallationSizing()

        result = sizing.recommend(
            evaluations=evaluations,
            annual_consumption_kwh=annual_consumption,
            annual_productions_kwh=annual_productions,
        )

        # --------------------------------------------------
        # Guardar resultado en el controller
        # --------------------------------------------------

        self.sizing_result = result

        return result

    # ==================================================
    # Cálculos de producción solar
    # ==================================================

    def calculate_hourly_production(
        self,
        configuration,
    ):

        self.analyzer.solar_engine.calculate_hourly_production(
            configuration
        )

    def calculate_daily_production(self):

        self.analyzer.solar_engine.calculate_daily_production()

    def calculate_monthly_production(self):

        self.analyzer.solar_engine.calculate_monthly_production()

    def calculate_yearly_production(self):

        self.analyzer.solar_engine.calculate_yearly_production()

    def calculate_energy_balance(self):

        consumption = (
            self.analyzer.valid_dataset()["AE_kWh"]
        )

        self.analyzer.solar_engine.calculate_energy_balance(
            consumption
        )

    def calculate_statistics(self):

        self.analyzer.solar_engine.calculate_statistics()

    def calculate(self, configuration):
        """
        Ejecuta todos los cálculos solares.
        """

        self.calculate_hourly_production(
            configuration
        )

        self.calculate_daily_production()

        self.calculate_monthly_production()

        self.calculate_yearly_production()

        self.calculate_energy_balance()

        self.calculate_statistics()

    # ==================================================
    # Reportes solares
    # ==================================================

    def production_statistics_report(self):

        self.analyzer.solar_engine.production_statistics_report()

    def monthly_production_report(self):

        self.analyzer.solar_engine.monthly_production_report()

    def energy_balance_report(self):

        self.analyzer.solar_engine.energy_balance_report()

    def reports(self):
        """
        Genera todos los informes solares.
        """

        self.production_statistics_report()

        self.monthly_production_report()

        self.energy_balance_report()

    # ==================================================
    # Reset
    # ==================================================

    def reset(self):

        self.sizing_result = None

        self.analyzer.solar_engine.reset()