import pytest

from helios.solar.installation_candidate import (
    InstallationCandidate
)

from helios.solar.installation_constraints import (
    InstallationConstraints
)

from helios.solar.installation_evaluation import (
    InstallationEvaluation
)

from helios.solar.installation_recommendation import (
    InstallationRecommendation,
    InstallationRecommender,
)


class TestInstallationRecommendation:

    # ==================================================
    # Helpers
    # ==================================================

    def _constraints(
        self,
        available_area_m2=100.0,
        panel_width_m=1.134,
        panel_height_m=2.273,
        panel_power_wp=540,
        min_panels=1,
        max_panels=None,
    ):

        return InstallationConstraints(
            available_area_m2=available_area_m2,
            panel_width_m=panel_width_m,
            panel_height_m=panel_height_m,
            panel_power_wp=panel_power_wp,
            min_panels=min_panels,
            max_panels=max_panels,
        )

    def _evaluation(
        self,
        panel_count=10,
        panel_power_wp=540,
        panel_area_m2=2.5764,
        available_area_m2=100.0,
    ):

        candidate = InstallationCandidate(
            panel_count=panel_count,
            panel_power_wp=panel_power_wp,
            panel_area_m2=panel_area_m2,
        )

        return InstallationEvaluation(
            candidate=candidate,
            available_area_m2=available_area_m2,
        )

    def _recommendation(
        self,
        evaluation,
        annual_consumption_kwh=6000.0,
        annual_production_kwh=6500.0,
    ):

        return InstallationRecommendation(
            evaluation=evaluation,
            annual_consumption_kwh=annual_consumption_kwh,
            annual_production_kwh=annual_production_kwh,
        )

    def _recommend(
        self,
        evaluations,
        annual_consumption_kwh=6000.0,
        productions=None,
    ):

        if productions is None:

            productions = {
                evaluation.panel_count: (
                    evaluation.installed_power_kwp
                    * 1000
                )
                for evaluation in evaluations
            }

        return InstallationRecommender().recommend(
            evaluations=evaluations,
            annual_consumption_kwh=annual_consumption_kwh,
            annual_productions_kwh=productions,
        )

    # ==================================================
    # Recommendation construction
    # ==================================================

    def test_creates_recommendation(self):

        evaluation = self._evaluation(
            panel_count=10
        )

        recommendation = self._recommendation(
            evaluation
        )

        assert isinstance(
            recommendation,
            InstallationRecommendation
        )

        assert recommendation.evaluation is evaluation

    def test_recommendation_is_immutable(self):

        evaluation = self._evaluation()

        recommendation = self._recommendation(
            evaluation
        )

        with pytest.raises(AttributeError):

            recommendation.evaluation = None

    # ==================================================
    # Exposed installation properties
    # ==================================================

    def test_exposes_panel_count(self):

        evaluation = self._evaluation(
            panel_count=15
        )

        recommendation = self._recommendation(
            evaluation
        )

        assert recommendation.panel_count == 15

    def test_exposes_installed_power(self):

        evaluation = self._evaluation(
            panel_count=15,
            panel_power_wp=540,
        )

        recommendation = self._recommendation(
            evaluation
        )

        assert recommendation.installed_power_kwp == pytest.approx(
            8.1
        )

    def test_exposes_occupied_area(self):

        evaluation = self._evaluation(
            panel_count=15
        )

        recommendation = self._recommendation(
            evaluation
        )

        assert recommendation.occupied_area_m2 == pytest.approx(
            38.646
        )

    def test_exposes_remaining_area(self):

        evaluation = self._evaluation(
            panel_count=15,
            available_area_m2=42.0,
        )

        recommendation = self._recommendation(
            evaluation
        )

        assert recommendation.remaining_area_m2 == pytest.approx(
            3.354
        )

    def test_exposes_area_utilization(self):

        evaluation = self._evaluation(
            panel_count=15,
            available_area_m2=42.0,
        )

        recommendation = self._recommendation(
            evaluation
        )

        expected = (
            38.646
            / 42.0
            * 100
        )

        assert recommendation.area_utilization_percent == pytest.approx(
            expected
        )

    # ==================================================
    # Exposed energy properties
    # ==================================================

    def test_exposes_annual_consumption(self):

        evaluation = self._evaluation(
            panel_count=15
        )

        recommendation = self._recommendation(
            evaluation,
            annual_consumption_kwh=6000.0,
            annual_production_kwh=7500.0,
        )

        assert recommendation.annual_consumption_kwh == pytest.approx(
            6000.0
        )

    def test_exposes_annual_production(self):

        evaluation = self._evaluation(
            panel_count=15
        )

        recommendation = self._recommendation(
            evaluation,
            annual_consumption_kwh=6000.0,
            annual_production_kwh=7500.0,
        )

        assert recommendation.annual_production_kwh == pytest.approx(
            7500.0
        )

    def test_exposes_self_consumption(self):

        evaluation = self._evaluation(
            panel_count=15
        )

        recommendation = self._recommendation(
            evaluation,
            annual_consumption_kwh=6000.0,
            annual_production_kwh=7500.0,
        )

        assert recommendation.self_consumption_kwh == pytest.approx(
            6000.0
        )

    def test_exposes_energy_surplus(self):

        evaluation = self._evaluation(
            panel_count=15
        )

        recommendation = self._recommendation(
            evaluation,
            annual_consumption_kwh=6000.0,
            annual_production_kwh=7500.0,
        )

        assert recommendation.energy_surplus_kwh == pytest.approx(
            1500.0
        )

    def test_exposes_energy_deficit(self):

        evaluation = self._evaluation(
            panel_count=15
        )

        recommendation = self._recommendation(
            evaluation,
            annual_consumption_kwh=7500.0,
            annual_production_kwh=6000.0,
        )

        assert recommendation.energy_deficit_kwh == pytest.approx(
            1500.0
        )

    def test_energy_information_matches_recommendation_input(self):

        evaluation = self._evaluation(
            panel_count=15
        )

        recommendation = self._recommendation(
            evaluation,
            annual_consumption_kwh=6000.0,
            annual_production_kwh=7500.0,
        )

        assert recommendation.annual_consumption_kwh == pytest.approx(
            6000.0
        )

        assert recommendation.annual_production_kwh == pytest.approx(
            7500.0
        )

        assert recommendation.self_consumption_kwh == pytest.approx(
            6000.0
        )

        assert recommendation.energy_surplus_kwh == pytest.approx(
            1500.0
        )

        assert recommendation.energy_deficit_kwh == pytest.approx(
            0.0
        )

    # ==================================================
    # Recommender validation
    # ==================================================

    def test_recommender_accepts_valid_evaluations(self):

        evaluations = [
            self._evaluation(panel_count=5),
            self._evaluation(panel_count=10),
        ]

        result = self._recommend(
            evaluations
        )

        assert isinstance(
            result,
            InstallationRecommendation
        )

    def test_rejects_empty_evaluation_list(self):

        with pytest.raises(
            ValueError,
            match=(
                "At least one installation evaluation "
                "is required."
            )
        ):

            self._recommend([])

    def test_rejects_invalid_evaluation_type(self):

        with pytest.raises(
            TypeError,
            match=(
                "evaluations must contain only "
                "InstallationEvaluation instances."
            )
        ):

            self._recommend(
                [None],
                productions={
                    0: 0.0,
                },
            )

    def test_rejects_mixed_evaluation_types(self):

        evaluations = [
            self._evaluation(panel_count=5),
            None,
        ]

        with pytest.raises(
            TypeError,
            match=(
                "evaluations must contain only "
                "InstallationEvaluation instances."
            )
        ):

            self._recommend(
                evaluations,
                productions={
                    5: 3000.0,
                    0: 0.0,
                },
            )

    # ==================================================
    # Selection by energy coverage
    # ==================================================

    def test_selects_smallest_configuration_covering_consumption(
        self,
    ):

        evaluations = [
            self._evaluation(panel_count=10),
            self._evaluation(panel_count=12),
            self._evaluation(panel_count=15),
        ]

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=6000.0,
            productions={
                10: 5000.0,
                12: 6000.0,
                15: 7500.0,
            },
        )

        assert result.panel_count == 12

    def test_does_not_select_larger_configuration_when_smaller_covers(
        self,
    ):

        evaluations = [
            self._evaluation(panel_count=10),
            self._evaluation(panel_count=12),
            self._evaluation(panel_count=15),
            self._evaluation(panel_count=18),
        ]

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=6000.0,
            productions={
                10: 5000.0,
                12: 6500.0,
                15: 8000.0,
                18: 9500.0,
            },
        )

        assert result.panel_count == 12

    def test_exact_production_boundary_is_considered_covering(
        self,
    ):

        evaluations = [
            self._evaluation(panel_count=10),
            self._evaluation(panel_count=12),
        ]

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=6000.0,
            productions={
                10: 5000.0,
                12: 6000.0,
            },
        )

        assert result.panel_count == 12

    def test_selects_highest_production_when_none_covers(
        self,
    ):

        evaluations = [
            self._evaluation(panel_count=10),
            self._evaluation(panel_count=12),
            self._evaluation(panel_count=15),
        ]

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=7000.0,
            productions={
                10: 4000.0,
                12: 5000.0,
                15: 5500.0,
            },
        )

        assert result.panel_count == 15

    def test_selects_highest_production_not_highest_panel_count(
        self,
    ):

        evaluations = [
            self._evaluation(panel_count=10),
            self._evaluation(panel_count=12),
            self._evaluation(panel_count=15),
        ]

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=7000.0,
            productions={
                10: 5000.0,
                12: 6000.0,
                15: 5500.0,
            },
        )

        assert result.panel_count == 12

    # ==================================================
    # Selection order independence
    # ==================================================

    def test_selection_is_independent_of_input_order(self):

        evaluations = [
            self._evaluation(panel_count=15),
            self._evaluation(panel_count=5),
            self._evaluation(panel_count=10),
        ]

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=6000.0,
            productions={
                5: 3000.0,
                10: 5000.0,
                15: 7500.0,
            },
        )

        assert result.panel_count == 15

    def test_single_evaluation_is_selected(self):

        evaluation = self._evaluation(
            panel_count=12
        )

        result = self._recommend(
            [evaluation],
            annual_consumption_kwh=6000.0,
            productions={
                12: 6500.0,
            },
        )

        assert result.evaluation is evaluation

    # ==================================================
    # Tie-breaking
    # ==================================================

    def test_tie_between_covering_candidates_prefers_fewer_panels(
        self,
    ):

        evaluation_a = self._evaluation(
            panel_count=10,
        )

        evaluation_b = self._evaluation(
            panel_count=12,
        )

        result = self._recommend(
            [
                evaluation_a,
                evaluation_b,
            ],
            annual_consumption_kwh=5000.0,
            productions={
                10: 6000.0,
                12: 6000.0,
            },
        )

        assert result.panel_count == 10

    def test_tie_between_non_covering_candidates_prefers_smaller_area(
        self,
    ):

        evaluation_a = self._evaluation(
            panel_count=10,
            panel_area_m2=2.0,
        )

        evaluation_b = self._evaluation(
            panel_count=12,
            panel_area_m2=3.0,
        )

        result = self._recommend(
            [
                evaluation_a,
                evaluation_b,
            ],
            annual_consumption_kwh=10000.0,
            productions={
                10: 6000.0,
                12: 6000.0,
            },
        )

        assert result.panel_count == 10

    # ==================================================
    # Boundary cases
    # ==================================================

    def test_selects_candidate_at_100_percent_utilization(self):

        evaluation = self._evaluation(
            panel_count=5,
            panel_area_m2=4.0,
            available_area_m2=20.0,
        )

        result = self._recommend(
            [evaluation],
            annual_consumption_kwh=5000.0,
            productions={
                5: 6000.0,
            },
        )

        assert result.panel_count == 5

        assert result.area_utilization_percent == pytest.approx(
            100.0
        )

        assert result.remaining_area_m2 == pytest.approx(
            0.0
        )

    # ==================================================
    # Energy boundaries
    # ==================================================

    def test_production_above_consumption_creates_surplus(
        self,
    ):

        evaluation = self._evaluation(
            panel_count=15
        )

        result = self._recommend(
            [evaluation],
            annual_consumption_kwh=6000.0,
            productions={
                15: 7500.0,
            },
        )

        assert result.self_consumption_kwh == pytest.approx(
            6000.0
        )

        assert result.energy_surplus_kwh == pytest.approx(
            1500.0
        )

        assert result.energy_deficit_kwh == pytest.approx(
            0.0
        )

    def test_production_below_consumption_creates_deficit(
        self,
    ):

        evaluation = self._evaluation(
            panel_count=15
        )

        result = self._recommend(
            [evaluation],
            annual_consumption_kwh=7500.0,
            productions={
                15: 6000.0,
            },
        )

        assert result.self_consumption_kwh == pytest.approx(
            6000.0
        )

        assert result.energy_surplus_kwh == pytest.approx(
            0.0
        )

        assert result.energy_deficit_kwh == pytest.approx(
            1500.0
        )

    def test_exact_production_equals_consumption_has_no_surplus_or_deficit(
        self,
    ):

        evaluation = self._evaluation(
            panel_count=12
        )

        result = self._recommend(
            [evaluation],
            annual_consumption_kwh=6000.0,
            productions={
                12: 6000.0,
            },
        )

        assert result.self_consumption_kwh == pytest.approx(
            6000.0
        )

        assert result.energy_surplus_kwh == pytest.approx(
            0.0
        )

        assert result.energy_deficit_kwh == pytest.approx(
            0.0
        )

    # ==================================================
    # Realistic installation
    # ==================================================

    def test_recommends_15_panel_540wp_installation(self):

        evaluations = [
            self._evaluation(
                panel_count=10,
                panel_power_wp=540,
                available_area_m2=42.0,
            ),
            self._evaluation(
                panel_count=12,
                panel_power_wp=540,
                available_area_m2=42.0,
            ),
            self._evaluation(
                panel_count=15,
                panel_power_wp=540,
                available_area_m2=42.0,
            ),
        ]

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=7500.0,
            productions={
                10: 5200.0,
                12: 6240.0,
                15: 7800.0,
            },
        )

        assert result.panel_count == 15

        assert result.installed_power_kwp == pytest.approx(
            8.1
        )

        assert result.occupied_area_m2 == pytest.approx(
            38.646
        )

        assert result.remaining_area_m2 == pytest.approx(
            3.354
        )

        assert result.area_utilization_percent == pytest.approx(
            38.646 / 42.0 * 100
        )

        assert result.annual_consumption_kwh == pytest.approx(
            7500.0
        )

        assert result.annual_production_kwh == pytest.approx(
            7800.0
        )

        assert result.self_consumption_kwh == pytest.approx(
            7500.0
        )

        assert result.energy_surplus_kwh == pytest.approx(
            300.0
        )

        assert result.energy_deficit_kwh == pytest.approx(
            0.0
        )

    def test_realistic_installation_does_not_overdimension(
        self,
    ):

        evaluations = [
            self._evaluation(
                panel_count=10,
                panel_power_wp=540,
                available_area_m2=42.0,
            ),
            self._evaluation(
                panel_count=12,
                panel_power_wp=540,
                available_area_m2=42.0,
            ),
            self._evaluation(
                panel_count=14,
                panel_power_wp=540,
                available_area_m2=42.0,
            ),
            self._evaluation(
                panel_count=15,
                panel_power_wp=540,
                available_area_m2=42.0,
            ),
            self._evaluation(
                panel_count=16,
                panel_power_wp=540,
                available_area_m2=42.0,
            ),
        ]

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=7000.0,
            productions={
                10: 5200.0,
                12: 6240.0,
                14: 7280.0,
                15: 7800.0,
                16: 8320.0,
            },
        )

        assert result.panel_count == 14

        assert result.installed_power_kwp == pytest.approx(
            7.56
        )

        assert result.annual_consumption_kwh == pytest.approx(
            7000.0
        )

        assert result.annual_production_kwh == pytest.approx(
            7280.0
        )

        assert result.energy_surplus_kwh == pytest.approx(
            280.0
        )

    # ==================================================
    # Input preservation
    # ==================================================

    def test_recommendation_does_not_modify_evaluations(
        self,
    ):

        evaluations = [
            self._evaluation(panel_count=5),
            self._evaluation(panel_count=10),
            self._evaluation(panel_count=15),
        ]

        original = list(evaluations)

        self._recommend(
            evaluations,
            annual_consumption_kwh=6000.0,
            productions={
                5: 3000.0,
                10: 5000.0,
                15: 7500.0,
            },
        )

        assert evaluations == original

    def test_repeated_recommendation_is_deterministic(
        self,
    ):

        evaluations = [
            self._evaluation(panel_count=5),
            self._evaluation(panel_count=10),
            self._evaluation(panel_count=15),
        ]

        recommender = InstallationRecommender()

        productions = {
            5: 3000.0,
            10: 5000.0,
            15: 7500.0,
        }

        first = recommender.recommend(
            evaluations=evaluations,
            annual_consumption_kwh=6000.0,
            annual_productions_kwh=productions,
        )

        second = recommender.recommend(
            evaluations=evaluations,
            annual_consumption_kwh=6000.0,
            annual_productions_kwh=productions,
        )

        assert first == second

        assert first.panel_count == 15

        assert first.annual_consumption_kwh == pytest.approx(
            6000.0
        )

        assert first.annual_production_kwh == pytest.approx(
            7500.0
        )
    def test_rejects_negative_annual_production(self):

        evaluation = self._evaluation(
            panel_count=10
        )

        with pytest.raises(
            ValueError,
            match="Annual production must be greater than or equal to zero."
        ):

            self._recommend(
                [evaluation],
                productions={
                    10: -1.0,
                },
            )

    @pytest.mark.parametrize(
        "production",
        [None, "5000", object()],
    )
    def test_rejects_invalid_annual_production_type(
        self,
        production,
    ):

        evaluation = self._evaluation(
            panel_count=10
        )

        with pytest.raises(
            TypeError,
            match="Annual production must be a number."
        ):

            self._recommend(
                [evaluation],
                productions={
                    10: production,
                },
            )

    def test_zero_consumption_selects_smallest_configuration(
        self,
    ):

        evaluations = [
            self._evaluation(panel_count=5),
            self._evaluation(panel_count=10),
            self._evaluation(panel_count=15),
        ]

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=0.0,
            productions={
                5: 0.0,
                10: 1000.0,
                15: 2000.0,
            },
        )

        assert result.panel_count == 5

    def test_zero_production_is_valid(self):

        evaluation = self._evaluation(
            panel_count=10
        )

        result = self._recommend(
            [evaluation],
            annual_consumption_kwh=5000.0,
            productions={
                10: 0.0,
            },
        )

        assert result.panel_count == 10
        assert result.annual_production_kwh == pytest.approx(0.0)
        assert result.self_consumption_kwh == pytest.approx(0.0)
        assert result.energy_surplus_kwh == pytest.approx(0.0)
        assert result.energy_deficit_kwh == pytest.approx(5000.0)

    def test_rejects_missing_production_for_any_evaluation(
        self,
    ):

        evaluations = [
            self._evaluation(panel_count=10),
            self._evaluation(panel_count=15),
        ]

        with pytest.raises(
            ValueError,
            match="Missing annual production for 15 panels."
        ):

            self._recommend(
                evaluations,
                productions={
                    10: 5000.0,
                },
            )

    def test_rejects_empty_production_dictionary(self):

        evaluation = self._evaluation(
            panel_count=10
        )

        with pytest.raises(
            ValueError,
            match="Missing annual production for 10 panels."
        ):

            self._recommend(
                [evaluation],
                productions={},
            )

    def test_rejects_duplicate_panel_counts(self):

        evaluations = [
            self._evaluation(panel_count=15),
            self._evaluation(panel_count=15),
        ]

        with pytest.raises(
            ValueError,
            match="Duplicate panel count"
        ):

            self._recommend(
                evaluations,
                productions={
                    15: 7500.0,
                },
            )

    def test_equal_production_and_area_has_deterministic_tie_break(
        self,
    ):

        evaluation_a = self._evaluation(
            panel_count=10,
            panel_area_m2=2.5,
        )

        evaluation_b = self._evaluation(
            panel_count=12,
            panel_area_m2=2.5,
        )

        result = self._recommend(
            [
                evaluation_b,
                evaluation_a,
            ],
            annual_consumption_kwh=10000.0,
            productions={
                10: 5000.0,
                12: 5000.0,
            },
        )

        assert result.panel_count == 10

    @pytest.mark.parametrize(
        "consumption",
        [None, "6000", object()],
    )
    def test_rejects_invalid_consumption_type(
        self,
        consumption,
    ):

        evaluation = self._evaluation(
            panel_count=10
        )

        with pytest.raises(
            TypeError,
            match="annual_consumption_kwh must be a number."
        ):

            self._recommend(
                [evaluation],
                annual_consumption_kwh=consumption,
                productions={
                    10: 5000.0,
                },
            )