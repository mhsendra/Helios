# helios/core/controllers/solar_controller.py

from helios.solar.configuration import SolarConfiguration

from helios.solar.installation_coordinator import (
    InstallationCoordinator,
)

from helios.solar.installation_recommendation import (
    InstallationRecommender,
)

from helios.solar.installation_optimizer import (
    InstallationOptimizer,
)

from helios.solar.installation_evaluation import (
    InstallationEvaluator,
)

from helios.solar.solar_installation_sizing import (
    SolarSizingResult,
)

from helios.solar.installation_configuration import (
    InstallationConfiguration,
)


class SolarController:

    def __init__(self, analyzer):

        self.analyzer = analyzer

        # Resultado del último dimensionamiento.
        self.sizing_result: SolarSizingResult | None = None

        # Resultado de la instalación recomendada.
        self.installation_result = None

        self.installation_configuration = None

        # Producción específica utilizada en el
        # dimensionamiento de la instalación.
        self.installation_specific_production = None

    # ==================================================
    # Propiedades
    # ==================================================

    @property
    def installed_power_kwp(self) -> float | None:

        if self.sizing_result is None:
            return None

        candidate = (
            self.sizing_result
            .evaluation
            .candidate
        )

        return (
            candidate.panel_count
            * candidate.panel_power_wp
            / 1000
        )

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
    def annual_production(self) -> float | None:

        yearly_production = (
            self.analyzer
            .solar_engine
            .yearly_production
        )

        if yearly_production is None:
            return None

        if hasattr(yearly_production, "sum"):
            return float(
                yearly_production.sum()
            )

        return float(yearly_production)

    @property
    def statistics(self):
        return self.analyzer.solar_engine.statistics

    @property
    def energy_balance(self):
        return self.analyzer.solar_engine.energy_balance

    @property
    def configuration(self) -> SolarConfiguration | None:
        return self.analyzer.solar_engine.configuration

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
    def specific_production(self) -> float | None:

        statistics = (
            self.analyzer
            .solar_engine
            .statistics
        )

        if statistics is None:
            return None

        return statistics.get(
            "specific_production"
        )

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
    def monthly_energy_balance(self):

        balance = self.analyzer.solar_engine.energy_balance

        if balance is None:
            return None

        return balance.resample("ME").sum()

    # ==================================================
    # Configuración solar
    # ==================================================

    def set_configuration(
        self,
        configuration: SolarConfiguration,
    ):
        """
        Sincroniza una configuración solar con el motor.

        La persistencia de la configuración pertenece a
        HeliosProject.set_solar_configuration().

        Este método no ejecuta ninguna simulación.
        """

        self.analyzer.solar_engine.set_configuration(
            configuration
        )

    # ==================================================
    # Dimensionamiento de instalación
    # ==================================================

    def recommend_installation(
        self,
        configuration: InstallationConfiguration,
    ):
        """
        Recomienda la instalación fotovoltaica óptima.

        InstallationConfiguration representa las
        restricciones físicas utilizadas por el
        optimizador.

        Esta configuración es independiente de
        SolarConfiguration.
        """

        if not isinstance(
            configuration,
            InstallationConfiguration,
        ):
            raise TypeError(
                "configuration must be an "
                "InstallationConfiguration."
            )

        constraints = configuration.to_constraints()

        specific_production = self.specific_production

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

        coordinator = InstallationCoordinator(
            optimizer=InstallationOptimizer(
                constraints
            ),
            evaluator=InstallationEvaluator(
                constraints
            ),
            recommender=InstallationRecommender(),
            production_calculator=(
                self._calculate_installation_production
            ),
        )

        result = coordinator.recommend(
            configuration=configuration,
            annual_consumption_kwh=annual_consumption,
        )

        self.sizing_result = result

        return result

    # ==================================================
    # Cálculos de producción solar
    # ==================================================

    def calculate_hourly_production(
        self,
        configuration=None,
        installed_power_kwp: float = 1.0,
    ):
        """
        Calcula la producción solar horaria.

        Si se proporciona una configuración explícita,
        se sincroniza con el motor y se utiliza directamente.

        Si no se proporciona, utiliza la configuración
        persistente del proyecto.
        """

        if configuration is not None:

            self.set_configuration(
                configuration
            )

        else:

            configuration = self.configuration

        if configuration is None:
            raise ValueError(
                "A solar configuration is required "
                "before calculating production."
            )

        self.analyzer.solar_engine.calculate_hourly_production(
            configuration,
            installed_power_kwp,
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

    def calculate(
        self,
        configuration=None,
        installed_power_kwp: float | None = None,
    ):
        """
        Ejecuta los cálculos solares.

        Si se proporciona una configuración, se utiliza
        directamente para el cálculo horario, manteniendo
        compatibilidad con la API anterior.

        La configuración persistente se establece mediante
        HeliosProject.set_solar_configuration().
        """

        if configuration is None:
            configuration = self.configuration

        if configuration is None:
            raise ValueError(
                "A solar configuration is required "
                "before calculating production."
            )

        if installed_power_kwp is None:

            installed_power_kwp = (
                self.installed_power_kwp
            )

        if installed_power_kwp is None:

            installed_power_kwp = 1.0

        self.calculate_hourly_production(
            configuration,
            installed_power_kwp,
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

        return (
            self.analyzer.solar_engine
            .production_statistics_report()
        )

    def monthly_production_report(self):

        return (
            self.analyzer.solar_engine
            .monthly_production_report()
        )

    def energy_balance_report(self):

        return (
            self.analyzer.solar_engine
            .energy_balance_report()
        )

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
        self.installation_result = None
        self.installation_configuration = None
        self.installation_specific_production = None

        self.analyzer.solar_engine.reset()

    # ==================================================
    # Utilidades de dimensionamiento
    # ==================================================

    def _calculate_installation_production(
        self,
        candidate,
    ) -> float:
        """
        Calcula la producción anual estimada de una
        instalación candidata a partir de la producción
        específica solar ya calculada.
        """

        specific_production = self.specific_production

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

        return (
            candidate.installed_power_kwp
            * specific_production
        )

    def installation_simulation_report(self):
        """
        Genera el informe de simulación de la instalación
        recomendada.
        """

        specific_production = (
            self.installation_specific_production
        )

        if specific_production is None:
            raise RuntimeError(
                "Specific solar production is not available."
            )

        return self.analyzer.solar_engine.installation_simulation_report(
            configuration=self.installation_configuration,
            recommendation=self.sizing_result,
            specific_production=specific_production,
        )