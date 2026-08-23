from collections.abc import Callable

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
    """

    def __init__(
        self,
        optimizer: InstallationOptimizer,
        evaluator: InstallationEvaluator,
        recommender: InstallationRecommender,
        production_calculator: Callable[
            [InstallationCandidate],
            float,
        ],
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

        self.optimizer = optimizer
        self.evaluator = evaluator
        self.recommender = recommender
        self.production_calculator = production_calculator

    # ==================================================
    # Public API
    # ==================================================

    def recommend(
        self,
        configuration: InstallationConfiguration,
        annual_consumption_kwh: float,
    ) -> InstallationRecommendation:
        """
        Ejecuta el proceso completo de dimensionamiento
        y devuelve la instalación recomendada.
        """

        self._validate_configuration(
            configuration
        )

        self._validate_consumption(
            annual_consumption_kwh
        )

        constraints = configuration.to_constraints()

        self._validate_constraints(
            constraints
        )

        self.optimizer = InstallationOptimizer(
            constraints
        )

        evaluations = (
            self._generate_evaluations()
        )

        annual_productions_kwh = (
            self._calculate_productions(
                evaluations
            )
        )

        return self.recommender.recommend(
            evaluations=evaluations,
            annual_consumption_kwh=annual_consumption_kwh,
            annual_productions_kwh=annual_productions_kwh,
        )

    # ==================================================
    # Constraints
    # ==================================================

    def _build_constraints(
        self,
        configuration: InstallationConfiguration,
    ) -> InstallationConstraints:

        return InstallationConstraints(
            available_area_m2=(
                configuration.available_area_m2
            ),
            panel_width_m=(
                configuration.panel_width_m
            ),
            panel_height_m=(
                configuration.panel_height_m
            ),
            panel_power_wp=(
                configuration.panel_power_wp
            ),
            min_panels=(
                configuration.min_panels
            ),
            max_panels=(
                configuration.max_panels
            ),
            maintenance_passage_required=(
                configuration.maintenance_passage_required
            ),
            maintenance_passage_width_m=(
                configuration.maintenance_passage_width_m
            ),
            maintenance_passage_orientation=(
                configuration.maintenance_passage_orientation
            ),
            roof_width_m=(
                configuration.roof_width_m
            ),
            roof_height_m=(
                configuration.roof_height_m
            ),
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
    ) -> dict[int, float]:
        """
        Calcula la producción anual de cada instalación
        candidata.

        El cálculo real de producción se delega al servicio
        proporcionado mediante production_calculator.
        """

        productions = {}

        for evaluation in evaluations:

            production = (
                self.production_calculator(
                    evaluation.candidate
                )
            )

            if (
                isinstance(production, bool)
                or not isinstance(
                    production,
                    (int, float),
                )
            ):
                raise TypeError(
                    "Production calculator must return "
                    "a numeric value."
                )

            if production < 0:
                raise ValueError(
                    "Annual production cannot be negative."
                )

            productions[
                evaluation.panel_count
            ] = float(production)

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