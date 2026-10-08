from helios.solar.configuration import SolarConfiguration

from helios.solar.installation_configuration import (
    InstallationConfiguration,
)

from helios.solar.installation_coordinator import (
    InstallationCoordinator,
)

from helios.solar.installation_evaluation import (
    InstallationEvaluator,
    InstallationEvaluation, 
    )

from helios.solar.installation_optimizer import (
    InstallationOptimizer,
)

from helios.solar.installation_recommendation import (
    InstallationRecommendation,
    InstallationRecommender,
)

from helios.core.consumption_scenario import (
    ConsumptionScenario,
)

from helios.core.energy_recommendation import (
    EnergyRecommendation,
)

from helios.solar.production_calculator import (
    SolarProductionCalculator,
)

from helios.solar.pvgis_production_profile import (
    PVGISProductionProfileService,
)

from helios.solar.production_profile import (
    SolarProductionProfile,
)

from helios.solar.balance import (
    SolarBalanceEngine,
)

from helios.solar.battery_configuration import BatteryConfiguration

from helios.solar.battery_optimizer import BatteryOptimizer

from helios.solar.battery_economic_model import (
    BatteryEconomicConfiguration,
    CombinedEconomicConfiguration,
)

from helios.solar.battery_recommendation import (
    BatteryRecommendation,
)

from helios.solar.battery_economic_configuration import BatteryEconomicParameters

from helios.core.diagnostics.energy import EnergyDiagnostics
from helios.core.diagnostics import (
    DiagnosticResult,
    EnergyRecommendations,
    RecommendationResult,
)

from helios.core.diagnostics.battery_economics import (
    BatteryEconomicAnalyzer,
    BatteryEconomicRecommendation,)

from helios.ev.scenario import (
    EVScenario,
)

from helios.solar.installation_costs import InstallationCostConfiguration

class SolarController:

    def __init__(self, analyzer):

        self.analyzer = analyzer

        # Resultado del último dimensionamiento.
        self.sizing_result: InstallationRecommendation | None = None

        # Configuración física utilizada para el último
        # dimensionamiento.
        self.installation_configuration = None

        # Resultados de la evaluación técnica y económica
        # de las capacidades de batería candidatas.
        self._battery_recommendations: list[
            BatteryRecommendation
        ] = []

        # Recomendación energética integral FV + batería + EV.
        self.energy_recommendation: EnergyRecommendation | None = None

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
    # Resultados de diagnóstico
    # ==================================================

    @property
    def diagnostics(self) -> list[DiagnosticResult]:
        balance = self.energy_balance

        if balance is None or balance.empty:
            return []

        return EnergyDiagnostics.diagnose(balance)

    @property
    def recommendations(self) -> list[RecommendationResult]:
        """
        Recomendaciones derivadas de los diagnósticos energéticos actuales.

        Las recomendaciones se calculan siempre a partir del balance vigente,
        a través de EnergyDiagnostics, y no mantienen estado propio.
        """
        diagnostics = self.diagnostics

        if not diagnostics:
            return []

        return EnergyRecommendations.recommend(
            diagnostics,
            self.battery_economic_recommendations,
        )

    @property
    def battery_economic_recommendations(
        self,
    ) -> list[BatteryEconomicRecommendation]:
        return BatteryEconomicAnalyzer.analyze(
            self.battery_recommendations
        )

    # ==================================================
    # Configuración solar
    # ==================================================

    def set_configuration(
        self,
        configuration: SolarConfiguration,
    ):
        """
        Sincroniza la configuración solar con el motor.

        Cambiar la configuración invalida todos los resultados
        derivados de la configuración anterior.

        Reaplicar exactamente la misma configuración no invalida
        resultados ya calculados.

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

        current_configuration = self.configuration

        configuration_changed = (
            current_configuration != configuration
        )

        self.analyzer.solar_engine.set_configuration(
            configuration
        )

        if configuration_changed:
            self.sizing_result = None
            self.installation_configuration = None
            self._battery_recommendations = []
            self.energy_recommendation = None
            
    def invalidate_energy_balance(self) -> None:
        """
        Invalida los resultados que dependen de la configuración
        energética actual, manteniendo intacta la producción solar.

        Se utiliza cuando cambia la configuración de batería.
        """

        self.analyzer.solar_engine.invalidate_energy_balance()

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

        consumption_scenario = (
            self.analyzer
            .calculate_representative_consumption_scenario()
        )

        if consumption_scenario is None:
            raise ValueError(
                "A representative consumption scenario is required "
                "to calculate the energy balance."
            )

        solar_engine = self.analyzer.solar_engine

        hourly_production = solar_engine.hourly_production

        if hourly_production is None:
            raise RuntimeError(
                "Hourly solar production has not been calculated."
            )

        production_profile = SolarProductionProfile(
            hourly_production=(
                hourly_production["production_kwh"]
            ),
            reference_year=(
                solar_engine
                .configuration
                .reference_year
            ),
            installed_power_kwp=(
                solar_engine
                .installed_power_kwp
            ),
        )

        project = self.analyzer.project

        battery_configuration = getattr(
            project,
            "battery_configuration",
            None,
        )

        if battery_configuration is not None and not isinstance(
            battery_configuration,
            BatteryConfiguration,
        ):
            raise TypeError(
                "battery_configuration must be a "
                "BatteryConfiguration."
            )

        ev_scenario = None

        if getattr(project, "ev_configuration", None) is not None:
            ev_scenario = project.build_ev_scenario()

        solar_engine.set_energy_balance(
            SolarBalanceEngine.calculate(
                consumption_scenario,
                production_profile,
                battery_configuration,
                ev_scenario,
            )
        )

    def _build_combined_economic_configuration(
        self,
        *,
        evaluation: InstallationEvaluation,
        production_profile: SolarProductionProfile,
        consumption_scenario: ConsumptionScenario,
        installation_cost_configuration: InstallationCostConfiguration,
        ev_scenario: EVScenario | None,
        battery_economic_parameters: BatteryEconomicParameters,
    ) -> CombinedEconomicConfiguration:
        """
        Construye la configuración económica combinada
        FV + batería para una instalación candidata.

        Centraliza la lógica económica utilizada por la evaluación
        de baterías y por la recomendación energética integral.

        No modifica ninguna hipótesis económica: únicamente
        concentra su construcción en un único punto.
        """

        economics_controller = self.analyzer.economics
        economics_configuration = (
            economics_controller.configuration
        )

        baseline_balance = SolarBalanceEngine.calculate(
            consumption_scenario,
            production_profile,
            None,
            ev_scenario,
        )

        annual_cost_with_pv = (
            economics_controller
            .calculate_cost_with_balance(
                baseline_balance
            )
        )

        annual_cost_without_pv = (
            economics_controller
            .calculate_cost_without_pv()
        )

        annual_pv_savings = (
            annual_cost_without_pv
            - annual_cost_with_pv
        )

        gross_installation_cost = (
            installation_cost_configuration
            .calculate_installation_cost(
                evaluation
            )
            + installation_cost_configuration
            .calculate_legalization_cost(
                evaluation
            )
        )

        net_installation_cost = (
            gross_installation_cost
            - economics_configuration.subsidies
            - economics_configuration.tax_deductions
        )

        return CombinedEconomicConfiguration(
            installation_cost_eur=(
                net_installation_cost
            ),
            battery_cost_eur=0.0,
            annual_pv_savings_eur=(
                annual_pv_savings
            ),
            annual_battery_additional_savings_eur=0.0,
            years=(
                battery_economic_parameters
                .lifetime_years
            ),
            electricity_price_growth=(
                economics_configuration
                .annual_electricity_price_growth
            ),
            pv_initial_degradation=(
                economics_configuration
                .first_year_degradation
            ),
            pv_degradation=(
                economics_configuration
                .annual_degradation
            ),
            battery_degradation=(
                battery_economic_parameters
                .annual_degradation
            ),
            annual_pv_maintenance_eur=(
                economics_configuration
                .annual_maintenance_cost
            ),
            annual_battery_maintenance_eur=(
                battery_economic_parameters
                .annual_maintenance_eur
            ),
            maintenance_growth=(
                economics_configuration
                .annual_maintenance_growth
            ),
            discount_rate=(
                economics_configuration
                .discount_rate
            ),
        )

    def evaluate_batteries(
        self,
        candidate_capacities_kwh: list[float],
        *,
        max_charge_power_kw: float,
        max_discharge_power_kw: float,
        charge_efficiency: float = 0.95,
        discharge_efficiency: float = 0.95,
        min_soc: float = 0.10,
        max_soc: float = 0.90,
        initial_soc: float = 0.10,
        battery_economic_parameters: (
            BatteryEconomicParameters | None
        ) = None,
    ) -> list[BatteryRecommendation]:

        if battery_economic_parameters is None:
            battery_economic_parameters = (
                BatteryEconomicParameters()
            )

        consumption_scenario = (
            self.analyzer
            .calculate_representative_consumption_scenario()
        )

        if consumption_scenario is None:
            raise ValueError(
                "A representative consumption scenario is required "
                "for battery evaluation."
            )

        solar_engine = self.analyzer.solar_engine

        hourly_production = (
            solar_engine.hourly_production
        )

        if hourly_production is None:
            raise RuntimeError(
                "Hourly solar production has not been calculated."
            )

        configuration = solar_engine.configuration

        if configuration is None:
            raise ValueError(
                "A solar configuration is required "
                "for battery evaluation."
            )

        production_profile = SolarProductionProfile(
            hourly_production=(
                hourly_production["production_kwh"]
            ),
            reference_year=configuration.reference_year,
            installed_power_kwp=(
                solar_engine.installed_power_kwp
            ),
        )

        economics_controller = self.analyzer.economics
        economics_configuration = (
            self.analyzer.economics.configuration
        )

        # ---------------------------------------------------------
        # Baseline FV without battery
        # ---------------------------------------------------------

        baseline_balance = SolarBalanceEngine.calculate(
            consumption_scenario,
            production_profile,
            None,
        )

        annual_cost_with_pv = (
            economics_controller
            .calculate_cost_with_balance(
                baseline_balance
            )
        )

        annual_cost_without_pv = (
            economics_controller
            .calculate_cost_without_pv()
        )

        annual_pv_savings = (
            annual_cost_without_pv
            - annual_cost_with_pv
        )

        cost_calculator = (
            economics_controller
            .calculate_cost_with_balance
        )

        # ---------------------------------------------------------
        # Incremental battery economics
        # ---------------------------------------------------------

        battery_economic_configuration = (
            BatteryEconomicConfiguration(
                battery_cost_eur=0.0,
                annual_savings_eur=0.0,
                years=(
                    battery_economic_parameters
                    .lifetime_years
                ),
                electricity_price_growth=(
                    economics_configuration
                    .annual_electricity_price_growth
                ),
                pv_initial_degradation=(
                    economics_configuration
                    .first_year_degradation
                ),
                pv_degradation=(
                    economics_configuration
                    .annual_degradation
                ),
                battery_degradation=(
                    battery_economic_parameters
                    .annual_degradation
                ),
                annual_maintenance_eur=(
                    battery_economic_parameters
                    .annual_maintenance_eur
                ),
                maintenance_growth=(
                    economics_configuration
                    .annual_maintenance_growth
                ),
                discount_rate=(
                    economics_configuration
                    .discount_rate
                ),
            )
        )

        # ---------------------------------------------------------
        # Combined PV + battery economics
        # ---------------------------------------------------------

        combined_economic_configuration = None

        installation_cost_configuration = getattr(
            self.analyzer.project,
            "installation_cost_configuration",
            None,
        )

        if (
            installation_cost_configuration is not None
            and self.sizing_result is not None
        ):
            combined_economic_configuration = (
                self._build_combined_economic_configuration(
                    evaluation=self.sizing_result.evaluation,
                    production_profile=production_profile,
                    consumption_scenario=consumption_scenario,
                    installation_cost_configuration=(
                        installation_cost_configuration
                    ),
                    ev_scenario=None,
                    battery_economic_parameters=(
                        battery_economic_parameters
                    ),
                )
            )

        # ---------------------------------------------------------
        # Battery evaluation
        # ---------------------------------------------------------

        self._battery_recommendations = (
            BatteryOptimizer().evaluate(
                consumption_scenario,
                production_profile,
                candidate_capacities_kwh,
                max_charge_power_kw=(
                    max_charge_power_kw
                ),
                max_discharge_power_kw=(
                    max_discharge_power_kw
                ),
                charge_efficiency=(
                    charge_efficiency
                ),
                discharge_efficiency=(
                    discharge_efficiency
                ),
                min_soc=min_soc,
                max_soc=max_soc,
                initial_soc=initial_soc,
                battery_cost_per_kwh_eur=(
                    battery_economic_parameters
                    .cost_per_kwh_eur
                ),
                annual_cost_without_battery_eur=(
                    annual_cost_with_pv
                ),
                cost_calculator=cost_calculator,
                economic_configuration=(
                    battery_economic_configuration
                ),
                combined_economic_configuration=(
                    combined_economic_configuration
                ),
            )
        )

        return self._battery_recommendations

    @property
    def battery_recommendations(
        self,
    ) -> list[BatteryRecommendation]:
        return getattr(self, "_battery_recommendations", [])

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
        configuration,
        consumption_scenario,
    ):
        if not isinstance(
            configuration,
            InstallationConfiguration,
        ):
            raise TypeError(
                "configuration must be an InstallationConfiguration."
            )

        if not isinstance(
            consumption_scenario,
            ConsumptionScenario,
        ):
            raise TypeError(
                "consumption_scenario must be a ConsumptionScenario."
            )

        # --------------------------------------------------
        # La ruta automática necesita una configuración
        # solar, pero NO necesita una simulación manual previa.
        # --------------------------------------------------

        solar_configuration = self.configuration

        if solar_configuration is None:
            raise ValueError(
                "A solar configuration is required "
                "before recommending an installation."
            )

        # --------------------------------------------------
        # Obtener el perfil solar base de 1 kWp mediante PVGIS.
        # --------------------------------------------------

        production_service = PVGISProductionProfileService()

        base_profile = production_service.get_production_profile(
            solar_configuration
        )

        # --------------------------------------------------
        # Escalar el perfil base para cada candidato.
        # El InstallationCoordinator espera una función que
        # devuelva SolarProductionProfile.
        # --------------------------------------------------

        production_calculator = SolarProductionCalculator(
            base_profile
        )

        # --------------------------------------------------
        # Dimensionamiento automático.
        # --------------------------------------------------

        constraints = configuration.to_constraints()

        coordinator = InstallationCoordinator(
            optimizer=InstallationOptimizer(constraints),
            evaluator=InstallationEvaluator(constraints),
            recommender=InstallationRecommender(),
            production_calculator=production_calculator.calculate,
        )

        result = coordinator.recommend(
            configuration=configuration,
            annual_consumption_kwh=consumption_scenario.annual_consumption,
            consumption_scenario=consumption_scenario,
        )

        self.sizing_result = result
        self.installation_configuration = configuration

        return result

    def recommend_energy(
        self,
        configuration,
        consumption_scenario,
        candidate_capacities_kwh: list[float],
        *,
        max_charge_power_kw: float,
        max_discharge_power_kw: float,
        battery_cost_per_kwh_eur: float = 249.70,
        installation_cost_configuration: InstallationCostConfiguration | None = None,
        ev_scenario: EVScenario | None = None,
        optimization_criterion: str = "combined_npv",
        charge_efficiency: float = 0.95,
        discharge_efficiency: float = 0.95,
        min_soc: float = 0.10,
        max_soc: float = 0.90,
        initial_soc: float = 0.10,
    ) -> EnergyRecommendation:
        """
        Ejecuta la recomendación energética integral
        FV + batería + EV.

        Reutiliza el mismo flujo de candidatos, evaluaciones
        geométricas y perfiles de producción empleado por
        recommend_installation().

        La decisión integral se delega en
        InstallationCoordinator.recommend_energy().
        """

        if not isinstance(
            configuration,
            InstallationConfiguration,
        ):
            raise TypeError(
                "configuration must be an "
                "InstallationConfiguration."
            )

        if not isinstance(
            consumption_scenario,
            ConsumptionScenario,
        ):
            raise TypeError(
                "consumption_scenario must be a "
                "ConsumptionScenario."
            )

        # --------------------------------------------------
        # Configuración económica de la instalación.
        #
        # Si no se proporciona explícitamente, se utiliza
        # la configuración almacenada en el proyecto.
        # --------------------------------------------------

        if installation_cost_configuration is None:
            project = self.analyzer.project

            installation_cost_configuration = getattr(
                project,
                "installation_cost_configuration",
                None,
            )

        if installation_cost_configuration is None:
            raise ValueError(
                "An installation cost configuration is required "
                "before recommending an energy system."
            )

        if not isinstance(
            installation_cost_configuration,
            InstallationCostConfiguration,
        ):
            raise TypeError(
                "installation_cost_configuration must be an "
                "InstallationCostConfiguration."
            )

        solar_configuration = self.configuration

        if solar_configuration is None:
            raise ValueError(
                "A solar configuration is required "
                "before recommending an energy system."
            )

        # --------------------------------------------------
        # Perfil solar base de 1 kWp.
        # --------------------------------------------------

        production_service = PVGISProductionProfileService()

        base_profile = (
            production_service.get_production_profile(
                solar_configuration
            )
        )

        production_calculator = SolarProductionCalculator(
            base_profile
        )

        # --------------------------------------------------
        # EV
        # --------------------------------------------------

        if ev_scenario is None:
            project = self.analyzer.project

            if getattr(
                project,
                "ev_configuration",
                None,
            ) is not None:
                ev_scenario = project.build_ev_scenario()

        # --------------------------------------------------
        # Factory económica específica para cada instalación.
        # --------------------------------------------------

        battery_economic_parameters = (
            BatteryEconomicParameters()
        )

        def economic_configuration_factory(
            evaluation: InstallationEvaluation,
            production_profile: SolarProductionProfile,
        ) -> CombinedEconomicConfiguration:
            return (
                self._build_combined_economic_configuration(
                    evaluation=evaluation,
                    production_profile=production_profile,
                    consumption_scenario=consumption_scenario,
                    installation_cost_configuration=(
                        installation_cost_configuration
                    ),
                    ev_scenario=ev_scenario,
                    battery_economic_parameters=(
                        battery_economic_parameters
                    ),
                )
            )

        # --------------------------------------------------
        # Coordinador de instalación.
        # --------------------------------------------------

        constraints = configuration.to_constraints()

        coordinator = InstallationCoordinator(
            optimizer=InstallationOptimizer(
                constraints
            ),
            evaluator=InstallationEvaluator(
                constraints
            ),
            recommender=InstallationRecommender(),
            production_calculator=(
                production_calculator.calculate
            ),
        )

        result = coordinator.recommend_energy(
            configuration=configuration,
            annual_consumption_kwh=(
                consumption_scenario.annual_consumption
            ),
            consumption_scenario=consumption_scenario,
            candidate_capacities_kwh=(
                candidate_capacities_kwh
            ),
            max_charge_power_kw=(
                max_charge_power_kw
            ),
            max_discharge_power_kw=(
                max_discharge_power_kw
            ),
            battery_cost_per_kwh_eur=(
                battery_cost_per_kwh_eur
            ),
            economic_configuration_factory=(
                economic_configuration_factory
            ),
            ev_scenario=ev_scenario,
            optimization_criterion=(
                optimization_criterion
            ),
            charge_efficiency=(
                charge_efficiency
            ),
            discharge_efficiency=(
                discharge_efficiency
            ),
            min_soc=min_soc,
            max_soc=max_soc,
            initial_soc=initial_soc,
        )

        self.energy_recommendation = result
        self.installation_configuration = configuration

        return result

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

        return (
            self.analyzer.solar_engine
            .installation_simulation_report(
                configuration=(
                    self.installation_configuration
                ),
                recommendation=self.sizing_result,
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
        self.analyzer.solar_engine.reset()

        self.sizing_result = None
        self.installation_configuration = None
        self._battery_recommendations = []
        self.energy_recommendation = None
