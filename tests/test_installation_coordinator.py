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

    # ==================================================
    # Constraints completos
    # ==================================================

    def test_build_constraints_translates_all_configuration_fields(
        self,
    ):

        configuration = InstallationConfiguration(
            available_area_m2=42.25,
            panel_width_m=1.134,
            panel_height_m=1.762,
            panel_power_wp=540,
            min_panels=5,
            max_panels=15,
            maintenance_passage_required=True,
            maintenance_passage_width_m=0.45,
            maintenance_passage_orientation="vertical",
            roof_width_m=10.0,
            roof_height_m=8.0,
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
            lambda candidate: 1000.0,
        )

        constraints = coordinator._build_constraints(
            configuration
        )

        assert constraints.available_area_m2 == 42.25
        assert constraints.panel_width_m == 1.134
        assert constraints.panel_height_m == 1.762
        assert constraints.panel_power_wp == 540
        assert constraints.min_panels == 5
        assert constraints.max_panels == 15

        assert (
            constraints.maintenance_passage_required
            is True
        )

        assert (
            constraints.maintenance_passage_width_m
            == 0.45
        )

        assert (
            constraints.maintenance_passage_orientation
            == "vertical"
        )

        assert constraints.roof_width_m == 10.0
        assert constraints.roof_height_m == 8.0


    # ==================================================
    # Generación de layouts
    # ==================================================

    def test_generate_candidate_layouts_without_maintenance_passage(
        self,
        monkeypatch,
    ):

        configuration = self.configuration()

        optimizer = InstallationOptimizer(
            configuration.to_constraints()
        )

        evaluator = InstallationEvaluator(
            configuration.to_constraints()
        )

        coordinator = self.coordinator(
            optimizer,
            evaluator,
            InstallationRecommender(),
            lambda candidate: 1000.0,
        )

        candidate = self.candidate(5)

        calls = []

        def generate_layouts(
            panel_count,
            walkway_width_m,
            walkway_position,
        ):

            calls.append(
                (
                    panel_count,
                    walkway_width_m,
                    walkway_position,
                )
            )

            return ["layout"]

        monkeypatch.setattr(
            optimizer,
            "generate_layouts",
            generate_layouts,
        )

        layouts = coordinator._generate_candidate_layouts(
            candidate
        )

        assert layouts == ["layout"]

        assert calls == [
            (
                5,
                0.0,
                None,
            )
        ]


    def test_generate_candidate_layouts_with_maintenance_passage_tries_all_orientations(
        self,
        monkeypatch,
    ):

        configuration = InstallationConfiguration(
            available_area_m2=42.25,
            panel_width_m=1.134,
            panel_height_m=1.762,
            panel_power_wp=540,
            min_panels=5,
            max_panels=15,
            maintenance_passage_required=True,
            maintenance_passage_width_m=0.45,
            maintenance_passage_orientation="auto",
            roof_width_m=10.0,
            roof_height_m=8.0,
        )

        optimizer = InstallationOptimizer(
            configuration.to_constraints()
        )

        evaluator = InstallationEvaluator(
            configuration.to_constraints()
        )

        coordinator = self.coordinator(
            optimizer,
            evaluator,
            InstallationRecommender(),
            lambda candidate: 1000.0,
        )

        candidate = self.candidate(5)

        calls = []

        def generate_layouts(
            panel_count,
            walkway_width_m,
            walkway_position,
        ):

            calls.append(
                (
                    panel_count,
                    walkway_width_m,
                    walkway_position,
                )
            )

            return [
                f"layout-{walkway_position}"
            ]

        monkeypatch.setattr(
            optimizer,
            "generate_layouts",
            generate_layouts,
        )

        layouts = coordinator._generate_candidate_layouts(
            candidate
        )

        expected_positions = (
            optimizer.constraints.maintenance_passage_orientations
        )

        assert len(calls) == len(
            expected_positions
        )

        assert calls == [
            (
                5,
                0.45,
                position,
            )
            for position in expected_positions
        ]

        assert layouts == [
            f"layout-{position}"
            for position in expected_positions
        ]


    # ==================================================
    # Evaluaciones
    # ==================================================

    def test_generate_evaluations_uses_layout_with_smallest_occupied_area(
        self,
        monkeypatch,
    ):

        configuration = InstallationConfiguration(
            available_area_m2=42.25,
            panel_width_m=1.134,
            panel_height_m=1.762,
            panel_power_wp=540,
            min_panels=5,
            max_panels=5,
            maintenance_passage_required=False,
            maintenance_passage_width_m=0.45,
            maintenance_passage_orientation="auto",
            roof_width_m=10.0,
            roof_height_m=8.0,
        )

        optimizer = InstallationOptimizer(
            configuration.to_constraints()
        )

        evaluator = InstallationEvaluator(
            configuration.to_constraints()
        )

        coordinator = self.coordinator(
            optimizer,
            evaluator,
            InstallationRecommender(),
            lambda candidate: 1000.0,
        )

        candidate = self.candidate(5)

        class Layout:

            def __init__(
                self,
                area,
                width,
                height,
            ):

                self.occupied_area_m2 = area
                self.occupied_width_m = width
                self.occupied_height_m = height

        layouts = [
            Layout(
                area=20.0,
                width=5.0,
                height=4.0,
            ),
            Layout(
                area=15.0,
                width=6.0,
                height=2.5,
            ),
            Layout(
                area=18.0,
                width=4.0,
                height=4.5,
            ),
        ]

        monkeypatch.setattr(
            optimizer,
            "generate_candidates",
            lambda: [candidate],
        )

        monkeypatch.setattr(
            coordinator,
            "_generate_candidate_layouts",
            lambda candidate: layouts,
        )

        selected = []

        def evaluate_layout(
            candidate,
            layout,
        ):

            selected.append(layout)

            return InstallationEvaluation(
                candidate=candidate,
                available_area_m2=42.25,
                layout=layout,
            )

        monkeypatch.setattr(
            evaluator,
            "evaluate_layout",
            evaluate_layout,
        )

        result = coordinator._generate_evaluations()

        assert len(result) == 1

        assert selected == [layouts[1]]


    def test_generate_evaluations_uses_width_as_second_layout_sort_key(
        self,
        monkeypatch,
    ):

        configuration = InstallationConfiguration(
            available_area_m2=42.25,
            panel_width_m=1.134,
            panel_height_m=1.762,
            panel_power_wp=540,
            min_panels=5,
            max_panels=5,
            maintenance_passage_required=False,
            maintenance_passage_width_m=0.45,
            maintenance_passage_orientation="auto",
            roof_width_m=10.0,
            roof_height_m=8.0,
        )

        optimizer = InstallationOptimizer(
            configuration.to_constraints()
        )

        evaluator = InstallationEvaluator(
            configuration.to_constraints()
        )

        coordinator = self.coordinator(
            optimizer,
            evaluator,
            InstallationRecommender(),
            lambda candidate: 1000.0,
        )

        candidate = self.candidate(5)

        class Layout:

            def __init__(
                self,
                area,
                width,
                height,
            ):

                self.occupied_area_m2 = area
                self.occupied_width_m = width
                self.occupied_height_m = height

        first = Layout(
            area=20.0,
            width=6.0,
            height=3.0,
        )

        second = Layout(
            area=20.0,
            width=5.0,
            height=4.0,
        )

        monkeypatch.setattr(
            optimizer,
            "generate_candidates",
            lambda: [candidate],
        )

        monkeypatch.setattr(
            coordinator,
            "_generate_candidate_layouts",
            lambda candidate: [
                first,
                second,
            ],
        )

        selected = []

        def evaluate_layout(
            candidate,
            layout,
        ):

            selected.append(layout)

            return InstallationEvaluation(
                candidate=candidate,
                available_area_m2=42.25,
                layout=layout,
            )

        monkeypatch.setattr(
            evaluator,
            "evaluate_layout",
            evaluate_layout,
        )

        coordinator._generate_evaluations()

        assert selected == [second]


    def test_generate_evaluations_uses_height_as_third_layout_sort_key(
        self,
        monkeypatch,
    ):

        configuration = InstallationConfiguration(
            available_area_m2=42.25,
            panel_width_m=1.134,
            panel_height_m=1.762,
            panel_power_wp=540,
            min_panels=5,
            max_panels=5,
            maintenance_passage_required=False,
            maintenance_passage_width_m=0.45,
            maintenance_passage_orientation="auto",
            roof_width_m=10.0,
            roof_height_m=8.0,
        )

        optimizer = InstallationOptimizer(
            configuration.to_constraints()
        )

        evaluator = InstallationEvaluator(
            configuration.to_constraints()
        )

        coordinator = self.coordinator(
            optimizer,
            evaluator,
            InstallationRecommender(),
            lambda candidate: 1000.0,
        )

        candidate = self.candidate(5)

        class Layout:

            def __init__(
                self,
                area,
                width,
                height,
            ):

                self.occupied_area_m2 = area
                self.occupied_width_m = width
                self.occupied_height_m = height

        first = Layout(
            area=20.0,
            width=5.0,
            height=4.0,
        )

        second = Layout(
            area=20.0,
            width=5.0,
            height=3.0,
        )

        monkeypatch.setattr(
            optimizer,
            "generate_candidates",
            lambda: [candidate],
        )

        monkeypatch.setattr(
            coordinator,
            "_generate_candidate_layouts",
            lambda candidate: [
                first,
                second,
            ],
        )

        selected = []

        def evaluate_layout(
            candidate,
            layout,
        ):

            selected.append(layout)

            return InstallationEvaluation(
                candidate=candidate,
                available_area_m2=42.25,
                layout=layout,
            )

        monkeypatch.setattr(
            evaluator,
            "evaluate_layout",
            evaluate_layout,
        )

        coordinator._generate_evaluations()

        assert selected == [second]


    # ==================================================
    # Evaluación sin tejado
    # ==================================================

    def test_generate_evaluations_uses_area_only_evaluation_without_roof(
        self,
        monkeypatch,
    ):

        configuration = self.configuration()

        optimizer = InstallationOptimizer(
            configuration.to_constraints()
        )

        evaluator = InstallationEvaluator(
            configuration.to_constraints()
        )

        coordinator = self.coordinator(
            optimizer,
            evaluator,
            InstallationRecommender(),
            lambda candidate: 1000.0,
        )

        candidate = self.candidate(5)

        monkeypatch.setattr(
            optimizer,
            "generate_candidates",
            lambda: [candidate],
        )

        monkeypatch.setattr(
            coordinator,
            "_generate_candidate_layouts",
            lambda candidate: [],
        )

        calls = []

        def evaluate(candidate):

            calls.append(candidate)

            return InstallationEvaluation(
                candidate=candidate,
                available_area_m2=42.25,
            )

        monkeypatch.setattr(
            evaluator,
            "evaluate",
            evaluate,
        )

        result = coordinator._generate_evaluations()

        assert len(result) == 1

        assert calls == [candidate]


    # ==================================================
    # Candidatos incompatibles con tejado
    # ==================================================

    def test_generate_evaluations_raises_when_candidate_has_no_layout_and_roof_exists(
        self,
        monkeypatch,
    ):

        configuration = InstallationConfiguration(
            available_area_m2=42.25,
            panel_width_m=1.134,
            panel_height_m=1.762,
            panel_power_wp=540,
            min_panels=5,
            max_panels=5,
            maintenance_passage_required=False,
            maintenance_passage_width_m=0.45,
            maintenance_passage_orientation="auto",
            roof_width_m=10.0,
            roof_height_m=8.0,
        )

        optimizer = InstallationOptimizer(
            configuration.to_constraints()
        )

        evaluator = InstallationEvaluator(
            configuration.to_constraints()
        )

        coordinator = self.coordinator(
            optimizer,
            evaluator,
            InstallationRecommender(),
            lambda candidate: 1000.0,
        )

        candidate = self.candidate(5)

        monkeypatch.setattr(
            optimizer,
            "generate_candidates",
            lambda: [candidate],
        )

        monkeypatch.setattr(
            coordinator,
            "_generate_candidate_layouts",
            lambda candidate: [],
        )

        evaluator.evaluate = lambda candidate: pytest.fail(
            "evaluate() must not be called when roof geometry exists"
        )

        with pytest.raises(
            ValueError,
            match=(
                "No valid installation candidates "
                "fit the available installation geometry."
            ),
        ):
            coordinator._generate_evaluations()


    def test_generate_evaluations_raises_when_no_candidates_fit(
        self,
        monkeypatch,
    ):

        configuration = InstallationConfiguration(
            available_area_m2=1.0,
            panel_width_m=1.134,
            panel_height_m=1.762,
            panel_power_wp=540,
            min_panels=5,
            max_panels=5,
            maintenance_passage_required=False,
            maintenance_passage_width_m=0.45,
            maintenance_passage_orientation="auto",
            roof_width_m=2.0,
            roof_height_m=2.0,
        )

        optimizer = InstallationOptimizer(
            configuration.to_constraints()
        )

        evaluator = InstallationEvaluator(
            configuration.to_constraints()
        )

        coordinator = self.coordinator(
            optimizer,
            evaluator,
            InstallationRecommender(),
            lambda candidate: 1000.0,
        )

        candidate = self.candidate(5)

        monkeypatch.setattr(
            optimizer,
            "generate_candidates",
            lambda: [candidate],
        )

        monkeypatch.setattr(
            coordinator,
            "_generate_candidate_layouts",
            lambda candidate: [],
        )

        with pytest.raises(
            ValueError,
            match=(
                "No valid installation candidates "
                "fit the available installation geometry."
            ),
        ):
            coordinator._generate_evaluations()

    def test_generate_evaluations_raises_when_all_candidates_are_discarded(
        self,
        monkeypatch,
    ):

        configuration = InstallationConfiguration(
            available_area_m2=42.25,
            panel_width_m=1.134,
            panel_height_m=1.762,
            panel_power_wp=540,
            min_panels=5,
            max_panels=5,
            maintenance_passage_required=False,
            maintenance_passage_width_m=0.45,
            maintenance_passage_orientation="auto",
            roof_width_m=10.0,
            roof_height_m=8.0,
        )

        optimizer = InstallationOptimizer(
            configuration.to_constraints()
        )

        evaluator = InstallationEvaluator(
            configuration.to_constraints()
        )

        coordinator = self.coordinator(
            optimizer,
            evaluator,
            InstallationRecommender(),
            lambda candidate: 1000.0,
        )

        candidate = self.candidate(5)

        monkeypatch.setattr(
            optimizer,
            "generate_candidates",
            lambda: [candidate],
        )

        monkeypatch.setattr(
            coordinator,
            "_generate_candidate_layouts",
            lambda candidate: [],
        )

        with pytest.raises(
            ValueError,
            match=(
                "No valid installation candidates "
                "fit the available installation geometry."
            ),
        ):

            coordinator._generate_evaluations()

    def test_generate_evaluations_uses_smallest_occupied_layout(
        self,
        monkeypatch,
    ):

        configuration = InstallationConfiguration(
            available_area_m2=42.25,
            panel_width_m=1.134,
            panel_height_m=1.762,
            panel_power_wp=540,
            min_panels=5,
            max_panels=5,
            maintenance_passage_required=False,
            maintenance_passage_width_m=0.45,
            maintenance_passage_orientation="auto",
            roof_width_m=10.0,
            roof_height_m=8.0,
        )

        optimizer = InstallationOptimizer(
            configuration.to_constraints()
        )

        evaluator = InstallationEvaluator(
            configuration.to_constraints()
        )

        coordinator = self.coordinator(
            optimizer,
            evaluator,
            InstallationRecommender(),
            lambda candidate: 1000.0,
        )

        candidate = self.candidate(5)

        layout_large = type(
            "Layout",
            (),
            {
                "occupied_area_m2": 20.0,
                "occupied_width_m": 5.0,
                "occupied_height_m": 4.0,
            },
        )()

        layout_small = type(
            "Layout",
            (),
            {
                "occupied_area_m2": 18.0,
                "occupied_width_m": 6.0,
                "occupied_height_m": 3.0,
            },
        )()

        monkeypatch.setattr(
            optimizer,
            "generate_candidates",
            lambda: [candidate],
        )

        monkeypatch.setattr(
            coordinator,
            "_generate_candidate_layouts",
            lambda candidate: [
                layout_large,
                layout_small,
            ],
        )

        calls = []

        def evaluate_layout(candidate, layout):

            calls.append(layout)

            return InstallationEvaluation(
                candidate=candidate,
                available_area_m2=42.25,
                layout=layout,
            )

        monkeypatch.setattr(
            evaluator,
            "evaluate_layout",
            evaluate_layout,
        )

        result = coordinator._generate_evaluations()

        assert len(result) == 1

        assert calls == [
            layout_small,
        ]

        assert result[0].layout is layout_small