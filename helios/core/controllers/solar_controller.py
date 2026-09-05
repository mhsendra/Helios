from helios.solar.configuration import SolarConfiguration

from helios.solar.installation_configuration import (
    InstallationConfiguration,
)

from helios.solar.installation_coordinator import (
    InstallationCoordinator,
)

from helios.solar.installation_evaluation import (
    InstallationEvaluator,
)

from helios.solar.installation_optimizer import (
    InstallationOptimizer,
)

from helios.solar.installation_recommendation import (
    InstallationRecommender,
)

from helios.solar.solar_installation_sizing import (
    SolarSizingResult,
)


class SolarController:

    def __init__(self, analyzer):

        self.analyzer = analyzer

        # Resultado del último dimensionamiento.
        self.sizing_result: SolarSizingResult | None = None

        # Configuración física utilizada para el último
        # dimensionamiento.
        self.installation_configuration = None

        # Producción específica utilizada para evaluar
        # el dimensionamiento.
        self.installation_specific_production = None

    # ==================================================
    # Propiedades de producción
    # ==================================================

    @property
    def hourly_production(self):

        return (
            self.analyzer
            .solar_engine
            .hourly_production
        )

    @property
    def daily_production(self):

        return (
            self.analyzer
            .solar_engine
            .daily_production
        )

    @property
    def monthly_production(self):

        return (
            self.analyzer
            .solar_engine
            .monthly_production
        )

    @property
    def yearly_production(self):

        return (
            self.analyzer
            .solar_engine
            .yearly_production
        )

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

        return (
            self.analyzer
            .solar_engine
            .statistics
        )

    @property
    def energy_balance(self):

        return (
            self.analyzer
            .solar_engine
            .energy_balance
        )

    @property
    def configuration(self) -> SolarConfiguration | None:

        return (
            self.analyzer
            .solar_engine
            .configuration
        )

    # ==================================================
    # Propiedades derivadas
    # ==================================================

    @property
    def installed_power_kwp(self) -> float | None:
        """
        Potencia instalada de la recomendación actual.

        No representa la potencia utilizada por una
        simulación solar normalizada.
        """

        if self.sizing_result is None:
            return None

        return self.sizing_result.installed_power_kwp

    @property
    def simulation_installed_power_kwp(self) -> float | None:
        """
        Potencia instalada utilizada por la simulación solar actual.

        Esta propiedad es independiente del resultado de
        dimensionamiento automático.
        """

        solar_engine = self.analyzer.solar_engine

        return getattr(
            solar_engine.manager,
            "installed_power_kwp",
            None,
        )

    @property
    def coverage(self) -> float | None:

        balance = (
            self.analyzer
            .solar_engine
            .energy_balance
        )

        if balance is None or balance.empty:
            return None

        consumption = balance[
            "consumption_kwh"
        ].sum()

        if consumption == 0:
            return None

        self_consumption = balance[
            "self_consumption_kwh"
        ].sum()

        return (
            100
            * self_consumption
            / consumption
        )

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

        balance = (
            self.analyzer
            .solar_engine
            .energy_balance
        )

        if balance is None:
            return None

        return float(
            balance[
                "self_consumption_kwh"
            ].sum()
        )

    @property
    def grid_import(self) -> float | None:

        balance = (
            self.analyzer
            .solar_engine
            .energy_balance
        )

        if balance is None:
            return None

        return float(
            balance[
                "grid_import_kwh"
            ].sum()
        )

    @property
    def grid_export(self) -> float | None:

        balance = (
            self.analyzer
            .solar_engine
            .energy_balance
        )

        if balance is None:
            return None

        return float(
            balance[
                "grid_export_kwh"
            ].sum()
        )

    @property
    def monthly_energy_balance(self):

        balance = (
            self.analyzer
            .solar_engine
            .energy_balance
        )

        if balance is None:
            return None

        return balance.resample(
            "ME"
        ).sum()

    # ==================================================
    # Configuración solar
    # ==================================================

    def set_configuration(
        self,
        configuration: SolarConfiguration,
    ):
        """
        Sincroniza la configuración solar con el motor.

        No ejecuta cálculos ni gestiona la persistencia
        del proyecto.
        """

        if not isinstance(
            configuration,
            SolarConfiguration,
        ):
            raise TypeError(
                "configuration must be a "
                "SolarConfiguration."
            )

        self.analyzer.solar_engine.set_configuration(
            configuration
        )

    # ==================================================
    # Cálculos de producción
    # ==================================================

    def calculate_hourly_production(
        self,
        configuration=None,
        installed_power_kwp: float = 1.0,
    ):
        """
        Calcula la producción horaria.

        La potencia instalada pertenece a la simulación
        que se está ejecutando y no se obtiene del
        resultado del dimensionamiento.
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

        if (
            isinstance(
                installed_power_kwp,
                bool,
            )
            or not isinstance(
                installed_power_kwp,
                (int, float),
            )
        ):
            raise TypeError(
                "installed_power_kwp must be a number."
            )

        if installed_power_kwp <= 0:
            raise ValueError(
                "installed_power_kwp must be "
                "greater than zero."
            )

        self.analyzer.solar_engine.calculate_hourly_production(
            configuration,
            float(installed_power_kwp),
        )

    def calculate_daily_production(self):

        self.analyzer.solar_engine.calculate_daily_production()

    def calculate_monthly_production(self):

        self.analyzer.solar_engine.calculate_monthly_production()

    def calculate_yearly_production(self):

        self.analyzer.solar_engine.calculate_yearly_production()

    def calculate_energy_balance(self):

        dataset = self.analyzer.valid_dataset()

        if dataset is None or dataset.empty:
            raise ValueError(
                "A valid consumption dataset is required "
                "to calculate the energy balance."
            )

        self.analyzer.solar_engine.calculate_energy_balance(
            dataset["AE_kWh"]
        )

    def calculate_statistics(self):

        self.analyzer.solar_engine.calculate_statistics()

    def calculate(
        self,
        configuration=None,
        installed_power_kwp: float | None = None,
    ):
        """
        Ejecuta el flujo completo de cálculo solar.

        La configuración puede proporcionarse explícitamente
        o utilizar la configuración ya establecida en el
        motor.

        Si no se especifica potencia instalada se utiliza
        1 kWp, que corresponde a la simulación normalizada
        utilizada para obtener la producción específica.
        """

        if configuration is None:
            configuration = self.configuration

        if configuration is None:
            raise ValueError(
                "A solar configuration is required "
                "before calculating production."
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
    # Dimensionamiento
    # ==================================================

    def recommend_installation(
        self,
        configuration: InstallationConfiguration,
    ) -> SolarSizingResult:
        """
        Ejecuta el dimensionamiento de la instalación.

        InstallationConfiguration contiene las restricciones
        físicas de la instalación.

        SolarConfiguration y InstallationConfiguration son
        conceptos independientes.
        """

        if not isinstance(
            configuration,
            InstallationConfiguration,
        ):
            raise TypeError(
                "configuration must be an "
                "InstallationConfiguration."
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
                "Annual consumption must be "
                "greater than zero."
            )

        constraints = (
            configuration.to_constraints()
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

        self.installation_configuration = (
            configuration
        )

        self.installation_specific_production = (
            specific_production
        )

        return result

    def _calculate_installation_production(
        self,
        candidate,
    ) -> float:
        """
        Calcula la producción anual de una instalación
        candidata utilizando la producción específica
        previamente calculada.
        """

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

        return float(
            candidate.installed_power_kwp
            * specific_production
        )

    # ==================================================
    # Informes
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

    def installation_simulation_report(self):

        if self.installation_configuration is None:
            raise RuntimeError(
                "Installation configuration is not available."
            )

        if self.sizing_result is None:
            raise RuntimeError(
                "Installation recommendation is not available."
            )

        if self.installation_specific_production is None:
            raise RuntimeError(
                "Specific solar production is not available."
            )

        return (
            self.analyzer.solar_engine
            .installation_simulation_report(
                configuration=(
                    self.installation_configuration
                ),
                recommendation=self.sizing_result,
                specific_production=(
                    self.installation_specific_production
                ),
            )
        )

    def reports(self):

        self.production_statistics_report()

        self.monthly_production_report()

        self.energy_balance_report()

    # ==================================================
    # Reset
    # ==================================================

    def reset(self):

        self.sizing_result = None

        self.installation_configuration = None

        self.installation_specific_production = None

        self.analyzer.solar_engine.reset()