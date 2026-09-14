import pandas as pd
import pytest

from helios.core.consumption_scenario import (
    ConsumptionScenario,
)
from helios.core.statistics import (
    ConsumptionStatistics,
)

from helios.solar.configuration import (
    SolarConfiguration,
)
from helios.solar.PVGIS_production import (
    PVGISProductionService,
)
from helios.solar.pvgis_production_profile import (
    PVGISProductionProfileService,
)
from helios.solar.production_calculator import (
    SolarProductionCalculator,
)
from helios.solar.production_profile import (
    SolarProductionProfile,
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
    
    @staticmethod
    def make_production_profile(
        value: float = 1.0,
    ) -> SolarProductionProfile:
        index = pd.date_range(
            start="2025-01-01 00:00:00",
            periods=8760,
            freq="h",
        )

        series = pd.Series(
            value,
            index=index,
            name="production_kwh",
        )

        return SolarProductionProfile(
            hourly_production=series,
            reference_year=2025,
            installed_power_kwp=1.0,
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
    # Production
    # ==================================================

    
    def test_calculate_productions_calls_calculator_for_each_evaluation(
        self,
    ):
        """Debe calcular la producción para cada configuración candidata."""

        evaluations = [
            InstallationEvaluation(
                candidate=self.candidate(5),
                available_area_m2=42.25,
            ),
            InstallationEvaluation(
                candidate=self.candidate(10),
                available_area_m2=42.25,
            ),
            InstallationEvaluation(
                candidate=self.candidate(15),
                available_area_m2=42.25,
            ),
        ]

        calls = []

        def calculator(candidate):

            calls.append(candidate)

            annual_production = candidate.panel_count * 100.0

            index = pd.date_range(
                start="2025-01-01 00:00:00",
                periods=8760,
                freq="h",
            )

            hourly_production = pd.Series(
                annual_production / 8760.0,
                index=index,
                name="production_kwh",
            )

            return SolarProductionProfile(
                hourly_production=hourly_production,
                reference_year=2025,
                installed_power_kwp=1.0,
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
            calculator,
        )

        result = coordinator._calculate_productions(
            evaluations
        )

        assert calls == [
            evaluations[0].candidate,
            evaluations[1].candidate,
            evaluations[2].candidate,
        ]

        assert result[5].annual_production == pytest.approx(500.0)
        assert result[10].annual_production == pytest.approx(1000.0)
        assert result[15].annual_production == pytest.approx(1500.0)

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
        monkeypatch,
    ):
        """Una producción anual negativa debe ser rechazada."""

        evaluation = InstallationEvaluation(
            candidate=self.candidate(5),
            available_area_m2=42.25,
        )

        profile = self.make_production_profile(
            value=1.0,
        )

        monkeypatch.setattr(
            SolarProductionProfile,
            "annual_production",
            property(
                lambda self: -1.0
            ),
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
            lambda candidate: profile,
        )

        with pytest.raises(
            ValueError,
            match="Annual solar production cannot be negative",
        ):
            coordinator._calculate_productions(
                [evaluation]
            )

    def test_calculate_productions_extracts_annual_production_from_profile(
        self,
    ):
        evaluation = InstallationEvaluation(
            candidate=self.candidate(15),
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
            lambda candidate: self.make_production_profile(
                value=2.0,
            ),
        )

        result = coordinator._calculate_productions(
            [evaluation]
        )

        assert result[15].annual_production == pytest.approx(17520.0)


    def test_calculate_productions_rejects_non_profile_result(
        self,
    ):
        evaluation = InstallationEvaluation(
            candidate=self.candidate(15),
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
            lambda candidate: 123.0,
        )

        with pytest.raises(
            TypeError,
            match="Production calculator must return "
            "a SolarProductionProfile",
        ):
            coordinator._calculate_productions(
                [evaluation]
            )


    def test_calculate_productions_uses_profile_annual_production(
        self,
    ):
        evaluation = InstallationEvaluation(
            candidate=self.candidate(15),
            available_area_m2=42.25,
        )

        profile = self.make_production_profile(
            value=3.0,
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
            lambda candidate: profile,
        )

        result = coordinator._calculate_productions(
            [evaluation]
        )

        assert result[15].annual_production == pytest.approx(
            profile.annual_production
        )

    # ==================================================
    # End-to-end coordination
    # ==================================================

    def test_recommend_returns_installation_recommendation(
        self,
    ):
        """recommend() debe devolver una InstallationRecommendation válida."""

        evaluations = [
            InstallationEvaluation(
                candidate=self.candidate(5),
                available_area_m2=42.25,
            ),
            InstallationEvaluation(
                candidate=self.candidate(10),
                available_area_m2=42.25,
            ),
            InstallationEvaluation(
                candidate=self.candidate(15),
                available_area_m2=42.25,
            ),
        ]

        recommendation = InstallationRecommender().recommend(
            evaluations=evaluations,
            annual_consumption_kwh=900.0,
            annual_productions_kwh={
                5: 500.0,
                10: 1000.0,
                15: 1500.0,
            },
        )

        assert isinstance(
            recommendation,
            InstallationRecommendation,
        )

        assert recommendation.panel_count == 10
        assert recommendation.annual_consumption_kwh == 900.0
        assert recommendation.annual_production_kwh == 1000.0

    def test_recommend_selects_smallest_configuration_covering_consumption(
        self,
    ):
        """Debe elegir la configuración más pequeña que cubra el consumo."""

        evaluations = [
            InstallationEvaluation(
                candidate=self.candidate(5),
                available_area_m2=42.25,
            ),
            InstallationEvaluation(
                candidate=self.candidate(10),
                available_area_m2=42.25,
            ),
            InstallationEvaluation(
                candidate=self.candidate(15),
                available_area_m2=42.25,
            ),
        ]

        recommendation = InstallationRecommender().recommend(
            evaluations=evaluations,
            annual_consumption_kwh=900.0,
            annual_productions_kwh={
                5: 500.0,
                10: 1000.0,
                15: 1500.0,
            },
        )

        assert recommendation.panel_count == 10
        assert recommendation.evaluation.panel_count == 10
        assert recommendation.annual_production_kwh == 1000.0
        
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

    def test_recommend_uses_maximum_production_when_no_candidate_covers_consumption(
        self,
    ):
        """Si ninguna configuración cubre el consumo,
        debe elegir la de mayor producción.
        """

        evaluations = [
            InstallationEvaluation(
                candidate=self.candidate(5),
                available_area_m2=42.25,
            ),
            InstallationEvaluation(
                candidate=self.candidate(10),
                available_area_m2=42.25,
            ),
            InstallationEvaluation(
                candidate=self.candidate(15),
                available_area_m2=42.25,
            ),
        ]

        recommendation = InstallationRecommender().recommend(
            evaluations=evaluations,
            annual_consumption_kwh=2000.0,
            annual_productions_kwh={
                5: 500.0,
                10: 1000.0,
                15: 1500.0,
            },
        )

        assert recommendation.panel_count == 15
        assert recommendation.evaluation.panel_count == 15
        assert recommendation.annual_production_kwh == 1500.0

    def test_recommend_uses_solar_production_calculator_with_pvgis_profile(
        self,
    ):
        
        class FakePVGISClient:

            def fetch(self, configuration):
                index = pd.date_range(
                    start="2025-01-01 00:00:00",
                    periods=8760,
                    freq="h",
                )

                hourly = [
                    {
                        "time": timestamp.strftime("%Y%m%d:%H%M"),
                        "P": 1000.0,
                        "G(i)": 100.0,
                        "T2m": 20.0,
                        "WS10m": 2.0,
                        "Int": 0,
                    }
                    for timestamp in index
                ]

                return {
                    "outputs": {
                        "hourly": hourly,
                    }
                }

        solar_configuration = SolarConfiguration(
            latitude=41.62,
            longitude=2.09,
            tilt=30,
            azimuth=0,
            losses=14.0,
            pv_technology="crystSi",
            mounting_place="building",
            reference_year=2025,
        )

        profile_service = PVGISProductionProfileService(
            production_service=PVGISProductionService(
                client=FakePVGISClient()
            )
        )

        base_profile = (
            profile_service.get_production_profile(
                solar_configuration
            )
        )

        calculator = SolarProductionCalculator(
            base_profile=base_profile
        )

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
            calculator.calculate,
        )

        recommendation = coordinator.recommend(
            configuration,
            annual_consumption_kwh=45000.0,
        )

        assert isinstance(
            recommendation,
            InstallationRecommendation,
        )

        assert recommendation.panel_count == 10

        assert recommendation.installed_power_kwp == pytest.approx(
            5.4
        )

        assert recommendation.annual_production_kwh == pytest.approx(
            8760.0 * 5.4
        )

    def test_installation_coordinator_uses_representative_consumption_scenario(
        self,
    ):
        """El escenario representativo de consumo alimenta la recomendación automática."""

        # ---------------------------------------------------------------
        # 1. Construimos un histórico sencillo de consumo
        # ---------------------------------------------------------------

        index = pd.date_range(
            start="2023-01-01 00:00:00",
            periods=8760,
            freq="h",
        )

        consumption_data = pd.DataFrame(
            {
                "AE_kWh": 5.0,
            },
            index=index,
        )

        statistics = ConsumptionStatistics()

        statistics.calculate_representative_year_consumption(
            consumption_data,
            reference_year=2025,
        )

        scenario = (
            statistics.representative_consumption_scenario
        )

        assert isinstance(
            scenario,
            ConsumptionScenario,
        )

        assert scenario.reference_year == 2025

        assert scenario.annual_consumption == pytest.approx(
            8760.0 * 5.0
        )

        # ---------------------------------------------------------------
        # 2. Perfil solar base de 1 kWp
        #
        # Cada hora produce 1 kWh.
        # Por tanto:
        #
        #   1 kWp  -> 8760 kWh/año
        #   5.4 kWp -> 47304 kWh/año
        #
        # ---------------------------------------------------------------

        base_profile = self.make_production_profile(
            value=1.0,
        )

        calculator = SolarProductionCalculator(
            base_profile=base_profile,
        )

        # ---------------------------------------------------------------
        # 3. Configuración física de la instalación
        # ---------------------------------------------------------------

        installation_configuration = (
            InstallationConfiguration(
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
        )

        optimizer = InstallationOptimizer(
            installation_configuration.to_constraints()
        )

        evaluator = InstallationEvaluator(
            installation_configuration.to_constraints()
        )

        recommender = InstallationRecommender()

        coordinator = InstallationCoordinator(
            optimizer=optimizer,
            evaluator=evaluator,
            recommender=recommender,
            production_calculator=calculator.calculate,
        )

        # ---------------------------------------------------------------
        # 4. El consumo del escenario entra directamente en el
        #    proceso automático de recomendación
        # ---------------------------------------------------------------

        recommendation = coordinator.recommend(
            installation_configuration,
            annual_consumption_kwh=scenario.annual_consumption,
        )

        # ---------------------------------------------------------------
        # 5. Verificamos la integración completa
        # ---------------------------------------------------------------

        assert isinstance(
            recommendation,
            InstallationRecommendation,
        )

        assert (
            recommendation.annual_consumption_kwh
            == pytest.approx(
                scenario.annual_consumption
            )
        )

        assert (
            recommendation.annual_production_kwh
            >= recommendation.annual_consumption_kwh
        )

        # 9 paneles = 4.86 kWp
        # 4.86 * 8760 = 42573.6 kWh
        # No cubre los 43800 kWh del escenario.

        # 10 paneles = 5.40 kWp
        # 5.40 * 8760 = 47304 kWh
        # Es la primera configuración que cubre el consumo.

        assert recommendation.panel_count == 10

        assert recommendation.installed_power_kwp == pytest.approx(
            5.4
        )

        assert recommendation.annual_production_kwh == pytest.approx(
            8760.0 * 5.4
        )

    def test_recommend_uses_injected_optimizer(
        self,
    ):
        optimizer = InstallationOptimizer(
            self.configuration().to_constraints()
        )

        evaluator = InstallationEvaluator(
            self.configuration().to_constraints()
        )

        coordinator = self.coordinator(
            optimizer,
            evaluator,
            InstallationRecommender(),
            lambda candidate: self.make_production_profile(
                value=1.0,
            ),
        )

        coordinator.recommend(
            self.configuration(),
            5000.0,
        )

        assert coordinator.optimizer is optimizer


    def test_recommend_rejects_optimizer_with_mismatched_constraints(
        self,
    ):
        configuration = self.configuration()

        optimizer_constraints = InstallationConstraints(
            available_area_m2=42.25,
            panel_width_m=1.134,
            panel_height_m=1.762,
            panel_power_wp=540,
            min_panels=5,
            max_panels=14,
        )

        optimizer = InstallationOptimizer(
            optimizer_constraints
        )

        evaluator = InstallationEvaluator(
            configuration.to_constraints()
        )

        coordinator = self.coordinator(
            optimizer,
            evaluator,
            InstallationRecommender(),
            lambda candidate: self.make_production_profile(
                value=1.0,
            ),
        )

        with pytest.raises(
            ValueError,
            match=(
                "Optimizer constraints do not match "
                "installation configuration"
            ),
        ):
            coordinator.recommend(
                configuration,
                5000.0,
            )