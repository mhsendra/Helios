from collections.abc import Callable

from helios.core.consumption_scenario import (
    ConsumptionScenario,
)

from helios.core.energy_recommendation import (
    EnergyRecommendation,
)

from helios.core.energy_recommender import (
    EnergyRecommender,
)

from helios.ev.scenario import (
    EVScenario,
)

from helios.solar.battery_economic_model import (
    CombinedEconomicConfiguration,
)

from helios.solar.installation_candidate import (
    InstallationCandidate,
)

from helios.solar.installation_configuration import (
    InstallationConfiguration,
)

from helios.solar.installation_constraints import (
    InstallationConstraints,
)

from helios.solar.installation_evaluation import (
    InstallationEvaluation,
    InstallationEvaluator,
)

from helios.solar.installation_optimizer import (
    InstallationOptimizer,
)

from helios.solar.installation_recommendation import (
    InstallationRecommendation,
    InstallationRecommender,
)

from helios.solar.installation_costs import (
    InstallationCostConfiguration,
)

from helios.solar.production_profile import (
    SolarProductionProfile,
)


class InstallationCoordinator:
    """
    Orquesta el proceso completo de dimensionamiento de
    una instalación fotovoltaica.

    Esta clase no implementa reglas de optimización propias.
    Coordina los componentes especializados:

        configuration
            ↓
        constraints
            ↓
        candidates / layouts
            ↓
        evaluation
            ↓
        production simulation
            ↓
        recommendation

    Para la recomendación energética integral, reutiliza los
    mismos candidatos, evaluaciones y perfiles de producción
    y delega la decisión FV + batería + EV a EnergyRecommender.
    """

    def __init__(
        self,
        optimizer: InstallationOptimizer,
        evaluator: InstallationEvaluator,
        recommender: InstallationRecommender,
        production_calculator: Callable[
            [InstallationCandidate],
            SolarProductionProfile,
        ],
        energy_recommender: EnergyRecommender | None = None,
    ):

        if not isinstance(
            optimizer,
            InstallationOptimizer,
        ):
            raise TypeError(
                "optimizer must be an InstallationOptimizer."
            )

        if not isinstance(
            evaluator,
            InstallationEvaluator,
        ):
            raise TypeError(
                "evaluator must be an InstallationEvaluator."
            )

        if not isinstance(
            recommender,
            InstallationRecommender,
        ):
            raise TypeError(
                "recommender must be an InstallationRecommender."
            )

        if not callable(production_calculator):
            raise TypeError(
                "production_calculator must be callable."
            )

        if energy_recommender is not None and not isinstance(
            energy_recommender,
            EnergyRecommender,
        ):
            raise TypeError(
                "energy_recommender must be an EnergyRecommender."
            )

        self.optimizer = optimizer
        self.evaluator = evaluator
        self.recommender = recommender
        self.production_calculator = production_calculator

        self.energy_recommender = (
            energy_recommender
            if energy_recommender is not None
            else EnergyRecommender()
        )

    # ==================================================
    # Public API
    # ==================================================

    def recommend(
        self,
        configuration: InstallationConfiguration,
        annual_consumption_kwh: float,
        consumption_scenario: ConsumptionScenario | None = None,
    ) -> InstallationRecommendation:
        """
        Ejecuta el proceso completo de dimensionamiento
        y devuelve la instalación fotovoltaica recomendada.
        """

        self._validate_configuration(
            configuration
        )

        self._validate_consumption(
            annual_consumption_kwh
        )

        if consumption_scenario is not None and not isinstance(
            consumption_scenario,
            ConsumptionScenario,
        ):
            raise TypeError(
                "consumption_scenario must be a ConsumptionScenario."
            )

        constraints = configuration.to_constraints()

        self._validate_constraints(constraints)

        if self.optimizer.constraints != constraints:
            raise ValueError(
                "Optimizer constraints do not match installation configuration."
            )

        evaluations = self._generate_evaluations()

        production_profiles = self._calculate_productions(
            evaluations
        )

        annual_productions_kwh = {
            panel_count: profile.annual_production
            for panel_count, profile in production_profiles.items()
        }

        return self.recommender.recommend(
            evaluations=evaluations,
            annual_consumption_kwh=annual_consumption_kwh,
            annual_productions_kwh=annual_productions_kwh,
            consumption_scenario=consumption_scenario,
            production_profiles=production_profiles,
        )

    def recommend_energy(
        self,
        configuration: InstallationConfiguration,
        annual_consumption_kwh: float,
        consumption_scenario: ConsumptionScenario,
        candidate_capacities_kwh: list[float],
        *,
        max_charge_power_kw: float,
        max_discharge_power_kw: float,
        battery_cost_per_kwh_eur: float = 249.70,
        economic_configuration_factory: (
            Callable[
                [
                    InstallationEvaluation,
                    SolarProductionProfile,
                ],
                CombinedEconomicConfiguration,
            ]
            | None
        ) = None,
        installation_cost_configuration: (
            InstallationCostConfiguration | None
        ) = None,
        ev_scenario: EVScenario | None = None,
        optimization_criterion: str = "combined_npv",
        charge_efficiency: float = 0.95,
        discharge_efficiency: float = 0.95,
        min_soc: float = 0.10,
        max_soc: float = 0.90,
        initial_soc: float = 0.10,
    ) -> EnergyRecommendation:
        """
        Ejecuta la recomendación energética integral.

        El proceso compara globalmente las combinaciones:

            instalación FV × capacidad batería × EV

        La generación FV y las evaluaciones geométricas se obtienen
        exactamente mediante el mismo flujo utilizado por recommend().

        La simulación energética y la optimización de batería se
        delegan completamente a EnergyRecommender.
        """

        self._validate_configuration(
            configuration
        )

        self._validate_consumption(
            annual_consumption_kwh
        )

        if not isinstance(
            consumption_scenario,
            ConsumptionScenario,
        ):
            raise TypeError(
                "consumption_scenario must be a ConsumptionScenario."
            )

        self._validate_energy_parameters(
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
            charge_efficiency=(
                charge_efficiency
            ),
            discharge_efficiency=(
                discharge_efficiency
            ),
            min_soc=min_soc,
            max_soc=max_soc,
            initial_soc=initial_soc,
            optimization_criterion=(
                optimization_criterion
            ),
        )

        if ev_scenario is not None and not isinstance(
            ev_scenario,
            EVScenario,
        ):
            raise TypeError(
                "ev_scenario must be an EVScenario."
            )

        if (
            installation_cost_configuration is not None
            and not isinstance(
                installation_cost_configuration,
                InstallationCostConfiguration,
            )
        ):
            raise TypeError(
                "installation_cost_configuration must be "
                "an InstallationCostConfiguration."
            )

        if (
            installation_cost_configuration is not None
            and economic_configuration_factory is not None
        ):
            raise ValueError(
                "installation_cost_configuration and "
                "economic_configuration_factory are mutually exclusive."
            )

        if installation_cost_configuration is not None:
            economic_configuration_factory = (
                lambda evaluation, production_profile:
                    installation_cost_configuration.build_economic_configuration(
                        evaluation.panel_count
                    )
            )

        constraints = configuration.to_constraints()

        self._validate_constraints(constraints)

        if self.optimizer.constraints != constraints:
            raise ValueError(
                "Optimizer constraints do not match installation configuration."
            )

        evaluations = self._generate_evaluations()

        production_profiles = self._calculate_productions(
            evaluations
        )

        return self.energy_recommender.recommend(
            evaluations=evaluations,
            annual_consumption_kwh=annual_consumption_kwh,
            consumption_scenario=consumption_scenario,
            production_profiles=production_profiles,
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

    # ==================================================
    # Evaluation
    # ==================================================

    def _generate_evaluations(
        self,
    ) -> list[InstallationEvaluation]:

        candidates = (
            self.optimizer.generate_candidates()
        )

        evaluations = []

        for candidate in candidates:

            layouts = self._generate_candidate_layouts(
                candidate
            )

            if layouts:

                # Keep one physical layout per panel count.
                # Prefer the layout with the smallest occupied area,
                # then the smallest occupied width and height.
                best_layout = min(
                    layouts,
                    key=lambda layout: (
                        layout.occupied_area_m2,
                        layout.occupied_width_m,
                        layout.occupied_height_m,
                    ),
                )

                evaluation = self.evaluator.evaluate_layout(
                    candidate,
                    best_layout,
                )

            else:

                # Without roof dimensions there is no geometric
                # constraint to evaluate, so retain the legacy
                # area-only evaluation behaviour.
                if (
                    self.optimizer.constraints.roof_width_m is None
                    and self.optimizer.constraints.roof_height_m is None
                ):
                    evaluation = self.evaluator.evaluate(
                        candidate
                    )
                else:
                    # A rectangular roof was supplied, therefore a
                    # candidate without a valid layout is physically
                    # impossible and must be discarded.
                    continue

            evaluations.append(evaluation)

        if not evaluations:
            raise ValueError(
                "No valid installation candidates "
                "fit the available installation geometry."
            )

        return evaluations

    def _generate_candidate_layouts(
        self,
        candidate: InstallationCandidate,
    ):
        """Generate all physically valid layouts for a candidate."""

        constraints = self.optimizer.constraints

        if not constraints.maintenance_passage_required:
            return self.optimizer.generate_layouts(
                panel_count=candidate.panel_count,
                walkway_width_m=0.0,
                walkway_position=None,
            )

        layouts = []

        for walkway_position in (
            constraints.maintenance_passage_orientations
        ):
            layouts.extend(
                self.optimizer.generate_layouts(
                    panel_count=candidate.panel_count,
                    walkway_width_m=(
                        constraints.maintenance_passage_width_m
                    ),
                    walkway_position=walkway_position,
                )
            )

        return layouts

    # ==================================================
    # Production
    # ==================================================

    def _calculate_productions(
        self,
        evaluations: list[InstallationEvaluation],
    ) -> dict[int, SolarProductionProfile]:
        """
        Calcula la producción anual de cada instalación
        candidata a partir de su perfil horario.

        El cálculo real de producción se delega al servicio
        proporcionado mediante production_calculator.
        """

        productions = {}

        for evaluation in evaluations:

            profile = self.production_calculator(
                evaluation.candidate
            )

            if not isinstance(
                profile,
                SolarProductionProfile,
            ):
                raise TypeError(
                    "Production calculator must return "
                    "a SolarProductionProfile."
                )

            annual_production = profile.annual_production

            if annual_production < 0:
                raise ValueError(
                    "Annual solar production cannot be negative."
                )

            productions[
                evaluation.panel_count
            ] = profile

        return productions

    # ==================================================
    # Validation
    # ==================================================

    @staticmethod
    def _validate_configuration(
        configuration: InstallationConfiguration,
    ):

        if not isinstance(
            configuration,
            InstallationConfiguration,
        ):
            raise TypeError(
                "configuration must be an "
                "InstallationConfiguration."
            )

    @staticmethod
    def _validate_consumption(
        annual_consumption_kwh: float,
    ):

        if (
            isinstance(
                annual_consumption_kwh,
                bool,
            )
            or not isinstance(
                annual_consumption_kwh,
                (int, float),
            )
        ):
            raise TypeError(
                "annual_consumption_kwh must be a number."
            )

        if annual_consumption_kwh <= 0:
            raise ValueError(
                "annual_consumption_kwh must be "
                "greater than zero."
            )

    @staticmethod
    def _validate_constraints(
        constraints: InstallationConstraints,
    ):

        if not isinstance(
            constraints,
            InstallationConstraints,
        ):
            raise TypeError(
                "Generated constraints must be an "
                "InstallationConstraints."
            )

    @staticmethod
    def _validate_energy_parameters(
        candidate_capacities_kwh: list[float],
        max_charge_power_kw: float,
        max_discharge_power_kw: float,
        battery_cost_per_kwh_eur: float,
        charge_efficiency: float,
        discharge_efficiency: float,
        min_soc: float,
        max_soc: float,
        initial_soc: float,
        optimization_criterion: str,
    ) -> None:

        if not isinstance(
            candidate_capacities_kwh,
            list,
        ):
            raise TypeError(
                "candidate_capacities_kwh must be a list."
            )

        if not candidate_capacities_kwh:
            raise ValueError(
                "candidate_capacities_kwh must not be empty."
            )

        for capacity in candidate_capacities_kwh:
            if (
                isinstance(capacity, bool)
                or not isinstance(capacity, (int, float))
            ):
                raise TypeError(
                    "Battery capacities must be numeric."
                )

            if capacity <= 0:
                raise ValueError(
                    "Battery capacities must be greater than zero."
                )

        numeric_parameters = {
            "max_charge_power_kw": max_charge_power_kw,
            "max_discharge_power_kw": max_discharge_power_kw,
            "battery_cost_per_kwh_eur": battery_cost_per_kwh_eur,
            "charge_efficiency": charge_efficiency,
            "discharge_efficiency": discharge_efficiency,
            "min_soc": min_soc,
            "max_soc": max_soc,
            "initial_soc": initial_soc,
        }

        for name, value in numeric_parameters.items():
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
            ):
                raise TypeError(
                    f"{name} must be numeric."
                )

        if max_charge_power_kw <= 0:
            raise ValueError(
                "max_charge_power_kw must be greater than zero."
            )

        if max_discharge_power_kw <= 0:
            raise ValueError(
                "max_discharge_power_kw must be greater than zero."
            )

        if battery_cost_per_kwh_eur < 0:
            raise ValueError(
                "battery_cost_per_kwh_eur cannot be negative."
            )

        if not 0 < charge_efficiency <= 1:
            raise ValueError(
                "charge_efficiency must be in (0, 1]."
            )

        if not 0 < discharge_efficiency <= 1:
            raise ValueError(
                "discharge_efficiency must be in (0, 1]."
            )

        if not 0 <= min_soc < max_soc <= 1:
            raise ValueError(
                "SOC limits must satisfy "
                "0 <= min_soc < max_soc <= 1."
            )

        if not min_soc <= initial_soc <= max_soc:
            raise ValueError(
                "initial_soc must be between min_soc and max_soc."
            )

        if optimization_criterion not in {
            "energy",
            "npv",
            "combined_npv",
            "payback",
            "combined_payback",
        }:
            raise ValueError(
                "optimization_criterion must be one of: "
                "'energy', 'npv', 'combined_npv', "
                "'payback', 'combined_payback'."
            )