import pytest

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

from helios.solar.installation_coordinator import (
    InstallationCoordinator,
)


class TestInstallationCoordinator:

    # ==================================================
    # Helpers
    # ==================================================

    @staticmethod
    def configuration():

        return InstallationConfiguration(
            available_area_m2=42.25,
            panel_width_m=1.134,
            panel_height_m=1.762,
            panel_power_wp=540,
            min_panels=5,
            max_panels=15,
            maintenance_passage_required=False,
            maintenance_passage_width_m=0.45,
            maintenance_passage_orientation="auto",
        )

    @staticmethod
    def candidate(panel_count):

        return InstallationCandidate(
            panel_count=panel_count,
            panel_power_wp=540,
            panel_area_m2=1.134 * 1.762,
        )

    @staticmethod
    def coordinator(
        optimizer,
        evaluator,
        recommender,
        production_calculator,
    ):

        return InstallationCoordinator(
            optimizer=optimizer,
            evaluator=evaluator,
            recommender=recommender,
            production_calculator=production_calculator,
        )

    # ==================================================
    # Constructor
    # ==================================================

    def test_constructor_accepts_valid_dependencies(self):

        optimizer = InstallationOptimizer(
            self.configuration().to_constraints()
        )

        evaluator = InstallationEvaluator(
            InstallationConstraints(
                available_area_m2=42.25,
                panel_width_m=1.134,
                panel_height_m=1.762,
                panel_power_wp=540,
                min_panels=5,
                max_panels=15,
            )
        )

        recommender = InstallationRecommender()

        coordinator = self.coordinator(
            optimizer,
            evaluator,
            recommender,
            lambda candidate: 1000.0,
        )

        assert coordinator.optimizer is optimizer
        assert coordinator.evaluator is evaluator
        assert coordinator.recommender is recommender
        assert callable(
            coordinator.production_calculator
        )

    @pytest.mark.parametrize(
        "optimizer",
        [
            None,
            object(),
            "optimizer",
            123,
        ],
    )
    def test_constructor_rejects_invalid_optimizer(
        self,
        optimizer,
    ):

        evaluator = InstallationEvaluator(
            InstallationConstraints(
                available_area_m2=42.25,
                panel_width_m=1.134,
                panel_height_m=1.762,
                panel_power_wp=540,
            )
        )

        with pytest.raises(TypeError):

            self.coordinator(
                optimizer,
                evaluator,
                InstallationRecommender(),
                lambda candidate: 1000.0,
            )

    @pytest.mark.parametrize(
        "evaluator",
        [
            None,
            object(),
            "evaluator",
            123,
        ],
    )
    def test_constructor_rejects_invalid_evaluator(
        self,
        evaluator,
    ):

        optimizer = InstallationOptimizer(
            self.configuration().to_constraints()
        )

        with pytest.raises(TypeError):

            self.coordinator(
                optimizer,
                evaluator,
                InstallationRecommender(),
                lambda candidate: 1000.0,
            )

    @pytest.mark.parametrize(
        "recommender",
        [
            None,
            object(),
            "recommender",
            123,
        ],
    )
    def test_constructor_rejects_invalid_recommender(
        self,
        recommender,
    ):

        optimizer = InstallationOptimizer(
            self.configuration().to_constraints()
        )

        evaluator = InstallationEvaluator(
            InstallationConstraints(
                available_area_m2=42.25,
                panel_width_m=1.134,
                panel_height_m=1.762,
                panel_power_wp=540,
            )
        )

        with pytest.raises(TypeError):

            self.coordinator(
                optimizer,
                evaluator,
                recommender,
                lambda candidate: 1000.0,
            )

    @pytest.mark.parametrize(
        "calculator",
        [
            None,
            object(),
            "calculator",
            123,
        ],
    )
    def test_constructor_rejects_non_callable_production_calculator(
        self,
        calculator,
    ):

        optimizer = InstallationOptimizer(
            self.configuration().to_constraints()
        )

        evaluator = InstallationEvaluator(
            InstallationConstraints(
                available_area_m2=42.25,
                panel_width_m=1.134,
                panel_height_m=1.762,
                panel_power_wp=540,
            )
        )

        with pytest.raises(TypeError):

            self.coordinator(
                optimizer,
                evaluator,
                InstallationRecommender(),
                calculator,
            )

    # ==================================================
    # Configuration validation
    # ==================================================

    @pytest.mark.parametrize(
        "configuration",
        [
            None,
            object(),
            "configuration",
            123,
        ],
    )
    def test_recommend_rejects_invalid_configuration(
        self,
        configuration,
    ):

        optimizer = InstallationOptimizer(
            self.configuration().to_constraints()
        )

        evaluator = InstallationEvaluator(
            InstallationConstraints(
                available_area_m2=42.25,
                panel_width_m=1.134,
                panel_height_m=1.762,
                panel_power_wp=540,
            )
        )

        coordinator = self.coordinator(
            optimizer,
            evaluator,
            InstallationRecommender(),
            lambda candidate: 1000.0,
        )

        with pytest.raises(TypeError):

            coordinator.recommend(
                configuration,
                5000.0,
            )

    # ==================================================
    # Consumption validation
    # ==================================================

    @pytest.mark.parametrize(
        "consumption",
        [
            None,
            "5000",
            object(),
            True,
            False,
        ],
    )
    def test_recommend_rejects_non_numeric_consumption(
        self,
        consumption,
    ):

        optimizer = InstallationOptimizer(
            self.configuration().to_constraints()
        )

        evaluator = InstallationEvaluator(
            InstallationConstraints(
                available_area_m2=42.25,
                panel_width_m=1.134,
                panel_height_m=1.762,
                panel_power_wp=540,
            )
        )

        coordinator = self.coordinator(
            optimizer,
            evaluator,
            InstallationRecommender(),
            lambda candidate: 1000.0,
        )

        with pytest.raises(TypeError):

            coordinator.recommend(
                self.configuration(),
                consumption,
            )

    @pytest.mark.parametrize(
        "consumption",
        [
            0,
            -1,
            -100,
        ],
    )
    def test_recommend_rejects_non_positive_consumption(
        self,
        consumption,
    ):

        optimizer = InstallationOptimizer(
            self.configuration().to_constraints()
        )

        evaluator = InstallationEvaluator(
            InstallationConstraints(
                available_area_m2=42.25,
                panel_width_m=1.134,
                panel_height_m=1.762,
                panel_power_wp=540,
            )
        )

        coordinator = self.coordinator(
            optimizer,
            evaluator,
            InstallationRecommender(),
            lambda candidate: 1000.0,
        )

        with pytest.raises(ValueError):

            coordinator.recommend(
                self.configuration(),
                consumption,
            )

    # ==================================================
    # Constraints
    # ==================================================

    def test_build_constraints_translates_configuration(self):

        optimizer = InstallationOptimizer(
            self.configuration().to_constraints()
        )

        evaluator = InstallationEvaluator(
            InstallationConstraints(
                available_area_m2=42.25,
                panel_width_m=1.134,
                panel_height_m=1.762,
                panel_power_wp=540,
            )
        )

        coordinator = self.coordinator(
            optimizer,
            evaluator,
            InstallationRecommender(),
            lambda candidate: 1000.0,
        )

        configuration = self.configuration()

        constraints = coordinator._build_constraints(
            configuration
        )

        assert isinstance(
            constraints,
            InstallationConstraints,
        )

        assert (
            constraints.available_area_m2
            == configuration.available_area_m2
        )

        assert (
            constraints.panel_width_m
            == configuration.panel_width_m
        )

        assert (
            constraints.panel_height_m
            == configuration.panel_height_m
        )

        assert (
            constraints.panel_power_wp
            == configuration.panel_power_wp
        )

        assert (
            constraints.min_panels
            == configuration.min_panels
        )

        assert (
            constraints.max_panels
            == configuration.max_panels
        )

    # ==================================================
    # Production
    # ==================================================

    def test_calculate_productions_calls_calculator_for_each_evaluation(
        self,
    ):

        candidates = [
            self.candidate(5),
            self.candidate(10),
            self.candidate(15),
        ]

        evaluations = [
            InstallationEvaluation(
                candidate=candidate,
                available_area_m2=42.25,
            )
            for candidate in candidates
        ]

        calls = []

        def calculator(candidate):

            calls.append(candidate.panel_count)

            return candidate.panel_count * 100.0

        coordinator = self.coordinator(
            InstallationOptimizer(
                self.configuration().to_constraints()
            ),
            InstallationEvaluator(
                InstallationConstraints(
                    available_area_m2=42.25,
                    panel_width_m=1.134,
                    panel_height_m=1.762,
                    panel_power_wp=540,
                )
            ),
            InstallationRecommender(),
            calculator,
        )

        result = coordinator._calculate_productions(
            evaluations
        )

        assert calls == [5, 10, 15]

        assert result == {
            5: 500.0,
            10: 1000.0,
            15: 1500.0,
        }

    @pytest.mark.parametrize(
        "production",
        [
            None,
            "1000",
            object(),
            True,
            False,
        ],
    )
    def test_calculate_productions_rejects_invalid_result(
        self,
        production,
    ):

        evaluation = InstallationEvaluation(
            candidate=self.candidate(5),
            available_area_m2=42.25,
        )

        coordinator = self.coordinator(
            InstallationOptimizer(
                self.configuration().to_constraints()
            ),
            InstallationEvaluator(
                InstallationConstraints(
                    available_area_m2=42.25,
                    panel_width_m=1.134,
                    panel_height_m=1.762,
                    panel_power_wp=540,
                )
            ),
            InstallationRecommender(),
            lambda candidate: production,
        )

        with pytest.raises(TypeError):

            coordinator._calculate_productions(
                [evaluation]
            )

    def test_calculate_productions_rejects_negative_result(
        self,
    ):

        evaluation = InstallationEvaluation(
            candidate=self.candidate(5),
            available_area_m2=42.25,
        )

        coordinator = self.coordinator(
            InstallationOptimizer(
                self.configuration().to_constraints()
            ),
            InstallationEvaluator(
                InstallationConstraints(
                    available_area_m2=42.25,
                    panel_width_m=1.134,
                    panel_height_m=1.762,
                    panel_power_wp=540,
                )
            ),
            InstallationRecommender(),
            lambda candidate: -1.0,
        )

        with pytest.raises(ValueError):

            coordinator._calculate_productions(
                [evaluation]
            )

    # ==================================================
    # End-to-end coordination
    # ==================================================

    def test_recommend_returns_installation_recommendation(
        self,
    ):

        configuration = self.configuration()

        optimizer = InstallationOptimizer(
            self.configuration().to_constraints()
        )

        evaluator = InstallationEvaluator(
            InstallationConstraints(
                available_area_m2=42.25,
                panel_width_m=1.134,
                panel_height_m=1.762,
                panel_power_wp=540,
                min_panels=5,
                max_panels=15,
            )
        )

        coordinator = self.coordinator(
            optimizer,
            evaluator,
            InstallationRecommender(),
            lambda candidate: (
                candidate.panel_count * 400.0
            ),
        )

        recommendation = coordinator.recommend(
            configuration=configuration,
            annual_consumption_kwh=5000.0,
        )

        assert isinstance(
            recommendation,
            InstallationRecommendation,
        )

        assert recommendation.panel_count >= 5

        assert recommendation.installed_power_kwp > 0

        assert recommendation.annual_consumption_kwh == 5000.0

        assert recommendation.annual_production_kwh >= 0

    def test_recommend_selects_smallest_configuration_covering_consumption(
        self,
    ):

        configuration = self.configuration()

        optimizer = InstallationOptimizer(
            self.configuration().to_constraints()
        )

        evaluator = InstallationEvaluator(
            InstallationConstraints(
                available_area_m2=42.25,
                panel_width_m=1.134,
                panel_height_m=1.762,
                panel_power_wp=540,
                min_panels=5,
                max_panels=15,
            )
        )

        coordinator = self.coordinator(
            optimizer,
            evaluator,
            InstallationRecommender(),
            lambda candidate: (
                candidate.panel_count * 500.0
            ),
        )

        recommendation = coordinator.recommend(
            configuration,
            annual_consumption_kwh=5000.0,
        )

        assert recommendation.panel_count == 10

        assert recommendation.annual_production_kwh == 5000.0

    def test_recommend_uses_maximum_production_when_no_candidate_covers_consumption(
        self,
    ):

        configuration = self.configuration()

        optimizer = InstallationOptimizer(
            self.configuration().to_constraints()
        )

        evaluator = InstallationEvaluator(
            InstallationConstraints(
                available_area_m2=42.25,
                panel_width_m=1.134,
                panel_height_m=1.762,
                panel_power_wp=540,
                min_panels=5,
                max_panels=15,
            )
        )

        coordinator = self.coordinator(
            optimizer,
            evaluator,
            InstallationRecommender(),
            lambda candidate: (
                candidate.panel_count * 200.0
            ),
        )

        recommendation = coordinator.recommend(
            configuration,
            annual_consumption_kwh=10000.0,
        )

        assert recommendation.panel_count == 15

        assert recommendation.annual_production_kwh == 3000.0