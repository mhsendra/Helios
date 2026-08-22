import pytest

from helios.solar.installation_candidate import (
    InstallationCandidate,
)

from helios.solar.installation_constraints import (
    InstallationConstraints,
)

from helios.solar.installation_evaluation import (
    InstallationEvaluation,
    InstallationEvaluator,
)

from helios.solar.solar_installation_sizing import (
    SolarInstallationSizing,
    SolarSizingResult,
)


class TestSolarInstallationSizing:

    # ==================================================
    # Helpers
    # ==================================================

    def _constraints(
        self,
        available_area_m2=50.0,
        panel_width_m=1.134,
        panel_height_m=2.273,
        panel_power_wp=540,
        min_panels=1,
        max_panels=20,
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
        panel_count,
        available_area_m2=50.0,
        panel_power_wp=540,
        panel_area_m2=2.5764,
    ):

        constraints = self._constraints(
            available_area_m2=available_area_m2,
            max_panels=20,
        )

        candidate = InstallationCandidate(
            panel_count=panel_count,
            panel_power_wp=panel_power_wp,
            panel_area_m2=panel_area_m2,
        )

        return InstallationEvaluator(
            constraints
        ).evaluate(candidate)

    def _evaluations(self, counts):

        return [
            self._evaluation(count)
            for count in counts
        ]

    def _sizing(self):

        return SolarInstallationSizing()

    def _recommend(
        self,
        evaluations,
        annual_consumption_kwh,
        productions,
    ):

        return self._sizing().recommend(
            evaluations=evaluations,
            annual_consumption_kwh=annual_consumption_kwh,
            annual_productions_kwh=productions,
        )

    # ==================================================
    # Construction / basic operation
    # ==================================================

    def test_creates_sizing_engine(self):

        sizing = self._sizing()

        assert isinstance(
            sizing,
            SolarInstallationSizing,
        )

    def test_returns_solar_sizing_result(self):

        evaluations = self._evaluations(
            [10, 12, 15]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=6000.0,
            productions={
                10: 5000.0,
                12: 6000.0,
                15: 7500.0,
            },
        )

        assert isinstance(
            result,
            SolarSizingResult,
        )

    # ==================================================
    # Input validation
    # ==================================================

    def test_rejects_zero_consumption(self):

        evaluations = self._evaluations(
            [10]
        )

        with pytest.raises(
            ValueError,
            match="Annual consumption must be greater than zero.",
        ):

            self._recommend(
                evaluations,
                annual_consumption_kwh=0.0,
                productions={
                    10: 5000.0,
                },
            )

    @pytest.mark.parametrize(
        "consumption",
        [
            -1.0,
            -100.0,
            -0.01,
        ],
    )
    def test_rejects_negative_consumption(
        self,
        consumption,
    ):

        evaluations = self._evaluations(
            [10]
        )

        with pytest.raises(
            ValueError,
            match="Annual consumption must be greater than zero.",
        ):

            self._recommend(
                evaluations,
                annual_consumption_kwh=consumption,
                productions={
                    10: 5000.0,
                },
            )

    def test_rejects_empty_evaluations(self):

        with pytest.raises(
            ValueError,
            match="At least one installation evaluation is required.",
        ):

            self._recommend(
                [],
                annual_consumption_kwh=5000.0,
                productions={},
            )

    def test_rejects_invalid_evaluation_type(self):

        with pytest.raises(
            TypeError,
            match=(
                "evaluations must contain only "
                "InstallationEvaluation instances."
            ),
        ):

            self._recommend(
                [None],
                annual_consumption_kwh=5000.0,
                productions={},
            )

    def test_rejects_mixed_evaluation_types(self):

        evaluations = [
            self._evaluation(10),
            None,
        ]

        with pytest.raises(
            TypeError,
            match=(
                "evaluations must contain only "
                "InstallationEvaluation instances."
            ),
        ):

            self._recommend(
                evaluations,
                annual_consumption_kwh=5000.0,
                productions={
                    10: 5000.0,
                },
            )

    # ==================================================
    # Production mapping validation
    # ==================================================

    def test_rejects_missing_production_for_candidate(self):

        evaluations = self._evaluations(
            [10, 12]
        )

        with pytest.raises(
            ValueError,
            match="Missing annual production for 12 panels.",
        ):

            self._recommend(
                evaluations,
                annual_consumption_kwh=5000.0,
                productions={
                    10: 5000.0,
                },
            )

    @pytest.mark.parametrize(
        "evaluations",
        [
            [10, 12],
            [12, 10],
            [10, 15, 12],
        ],
    )
    
    def test_missing_production_is_detected_independently_of_order(
        self,
        evaluations,
    ):

        evaluated = self._evaluations(
            evaluations
        )

        with pytest.raises(
            ValueError,
            match=r"Missing annual production for \d+ panels\.",
        ):

            self._recommend(
                evaluated,
                annual_consumption_kwh=5000.0,
                productions={
                    10: 5000.0,
                },
            )

    def test_extra_production_entries_are_ignored(self):

        evaluations = self._evaluations(
            [10]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=5000.0,
            productions={
                10: 6000.0,
                20: 12000.0,
            },
        )

        assert result.panel_count == 10

    # ==================================================
    # Basic recommendation
    # ==================================================

    def test_selects_smallest_configuration_covering_consumption(
        self,
    ):

        evaluations = self._evaluations(
            [10, 12, 15]
        )

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

        evaluations = self._evaluations(
            [10, 12, 15, 18]
        )

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

    def test_exact_production_boundary_is_covering(self):

        evaluations = self._evaluations(
            [10, 12]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=6000.0,
            productions={
                10: 5000.0,
                12: 6000.0,
            },
        )

        assert result.panel_count == 12

    def test_single_evaluation_is_selected(self):

        evaluation = self._evaluation(
            12
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
    # No configuration covers consumption
    # ==================================================

    def test_selects_highest_production_when_none_covers(
        self,
    ):

        evaluations = self._evaluations(
            [10, 12, 15]
        )

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

        evaluations = self._evaluations(
            [10, 12, 15]
        )

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

    def test_non_covering_result_has_zero_surplus(self):

        evaluations = self._evaluations(
            [10, 12]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=7000.0,
            productions={
                10: 4000.0,
                12: 6000.0,
            },
        )

        assert result.annual_surplus_kwh == pytest.approx(
            0.0
        )

        assert result.annual_deficit_kwh == pytest.approx(
            1000.0
        )

    # ==================================================
    # Result values
    # ==================================================

    def test_result_preserves_selected_evaluation(self):

        evaluations = self._evaluations(
            [10, 12]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=6000.0,
            productions={
                10: 5000.0,
                12: 6500.0,
            },
        )

        assert result.evaluation is evaluations[1]

    def test_result_preserves_consumption(self):

        evaluations = self._evaluations(
            [10]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=5234.5,
            productions={
                10: 6000.0,
            },
        )

        assert result.annual_consumption_kwh == pytest.approx(
            5234.5
        )

    def test_result_preserves_production(self):

        evaluations = self._evaluations(
            [10]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=5000.0,
            productions={
                10: 6123.45,
            },
        )

        assert result.annual_production_kwh == pytest.approx(
            6123.45
        )

    def test_result_exposes_panel_count(self):

        evaluation = self._evaluation(
            15
        )

        result = self._recommend(
            [evaluation],
            annual_consumption_kwh=6000.0,
            productions={
                15: 7500.0,
            },
        )

        assert result.panel_count == 15

    def test_result_exposes_installed_power(self):

        evaluation = self._evaluation(
            15
        )

        result = self._recommend(
            [evaluation],
            annual_consumption_kwh=6000.0,
            productions={
                15: 7500.0,
            },
        )

        assert result.installed_power_kwp == pytest.approx(
            8.1
        )

    def test_result_exposes_occupied_area(self):

        evaluation = self._evaluation(
            15
        )

        result = self._recommend(
            [evaluation],
            annual_consumption_kwh=6000.0,
            productions={
                15: 7500.0,
            },
        )

        assert result.occupied_area_m2 == pytest.approx(
            38.646
        )

    def test_result_exposes_remaining_area(self):

        evaluation = self._evaluation(
            15,
            available_area_m2=42.0,
        )

        result = self._recommend(
            [evaluation],
            annual_consumption_kwh=6000.0,
            productions={
                15: 7500.0,
            },
        )

        assert result.remaining_area_m2 == pytest.approx(
            3.354
        )

    # ==================================================
    # Self sufficiency
    # ==================================================

    def test_calculates_self_sufficiency_percent(self):

        evaluations = self._evaluations(
            [10]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=6000.0,
            productions={
                10: 3000.0,
            },
        )

        assert result.self_sufficiency_percent == pytest.approx(
            50.0
        )

    def test_self_sufficiency_is_capped_at_100_percent(self):

        evaluations = self._evaluations(
            [10]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=5000.0,
            productions={
                10: 8000.0,
            },
        )

        assert result.self_sufficiency_percent == pytest.approx(
            100.0
        )

    def test_self_sufficiency_is_100_at_exact_coverage(self):

        evaluations = self._evaluations(
            [10]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=6000.0,
            productions={
                10: 6000.0,
            },
        )

        assert result.self_sufficiency_percent == pytest.approx(
            100.0
        )

    # ==================================================
    # Production coverage
    # ==================================================

    def test_calculates_production_coverage_percent(self):

        evaluations = self._evaluations(
            [10]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=3000.0,
            productions={
                10: 6000.0,
            },
        )

        assert result.production_coverage_percent == pytest.approx(
            50.0
        )

    def test_production_coverage_is_capped_at_100_percent(self):

        evaluations = self._evaluations(
            [10]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=8000.0,
            productions={
                10: 6000.0,
            },
        )

        assert result.production_coverage_percent == pytest.approx(
            100.0
        )

    def test_production_coverage_is_zero_when_production_is_zero(self):

        evaluations = self._evaluations(
            [10]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=5000.0,
            productions={
                10: 0.0,
            },
        )

        assert result.production_coverage_percent == pytest.approx(
            0.0
        )

    # ==================================================
    # Surplus / deficit
    # ==================================================

    def test_calculates_annual_surplus(self):

        evaluations = self._evaluations(
            [10]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=5000.0,
            productions={
                10: 6500.0,
            },
        )

        assert result.annual_surplus_kwh == pytest.approx(
            1500.0
        )

    def test_surplus_is_zero_when_production_is_lower(self):

        evaluations = self._evaluations(
            [10]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=6500.0,
            productions={
                10: 5000.0,
            },
        )

        assert result.annual_surplus_kwh == pytest.approx(
            0.0
        )

    def test_calculates_annual_deficit(self):

        evaluations = self._evaluations(
            [10]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=6500.0,
            productions={
                10: 5000.0,
            },
        )

        assert result.annual_deficit_kwh == pytest.approx(
            1500.0
        )

    def test_deficit_is_zero_when_production_is_higher(self):

        evaluations = self._evaluations(
            [10]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=5000.0,
            productions={
                10: 6500.0,
            },
        )

        assert result.annual_deficit_kwh == pytest.approx(
            0.0
        )

    def test_exact_balance_has_zero_surplus_and_deficit(self):

        evaluations = self._evaluations(
            [10]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=6000.0,
            productions={
                10: 6000.0,
            },
        )

        assert result.annual_surplus_kwh == pytest.approx(
            0.0
        )

        assert result.annual_deficit_kwh == pytest.approx(
            0.0
        )

    # ==================================================
    # Tie breaking
    # ==================================================

    def test_tie_between_covering_candidates_prefers_fewer_panels(
        self,
    ):

        evaluations = self._evaluations(
            [10, 12]
        )

        result = self._recommend(
            evaluations,
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
            panel_area_m2=3.0,
        )

        evaluation_b = self._evaluation(
            panel_count=12,
            panel_area_m2=2.0,
        )

        result = self._recommend(
            [evaluation_a, evaluation_b],
            annual_consumption_kwh=10000.0,
            productions={
                10: 6000.0,
                12: 6000.0,
            },
        )

        assert result.panel_count == 12

        assert result.occupied_area_m2 == pytest.approx(
            24.0
        )

    def test_equal_production_and_equal_area_preserves_input_order(
        self,
    ):

        first = self._evaluation(
            panel_count=10,
            panel_area_m2=2.0,
        )

        second = self._evaluation(
            panel_count=12,
            panel_area_m2=2.0,
        )

        result = self._recommend(
            [first, second],
            annual_consumption_kwh=10000.0,
            productions={
                10: 6000.0,
                12: 6000.0,
            },
        )

        assert result.evaluation is first

    # ==================================================
    # Determinism
    # ==================================================

    def test_recommendation_is_deterministic(self):

        evaluations = self._evaluations(
            [10, 12, 15]
        )

        productions = {
            10: 5000.0,
            12: 6500.0,
            15: 8000.0,
        }

        sizing = self._sizing()

        first = sizing.recommend(
            evaluations=evaluations,
            annual_consumption_kwh=6000.0,
            annual_productions_kwh=productions,
        )

        second = sizing.recommend(
            evaluations=evaluations,
            annual_consumption_kwh=6000.0,
            annual_productions_kwh=productions,
        )

        assert first == second

    def test_covering_recommendation_is_independent_of_input_order(
        self,
    ):

        evaluations = self._evaluations(
            [15, 10, 12]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=6000.0,
            productions={
                10: 5000.0,
                12: 6500.0,
                15: 8000.0,
            },
        )

        assert result.panel_count == 12

    def test_non_covering_recommendation_is_independent_of_input_order(
        self,
    ):

        evaluations = self._evaluations(
            [15, 10, 12]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=7000.0,
            productions={
                10: 4000.0,
                12: 6000.0,
                15: 5500.0,
            },
        )

        assert result.panel_count == 12

    # ==================================================
    # Input preservation
    # ==================================================

    def test_recommendation_does_not_modify_evaluations(self):

        evaluations = self._evaluations(
            [10, 12, 15]
        )

        original = list(evaluations)

        self._recommend(
            evaluations,
            annual_consumption_kwh=6000.0,
            productions={
                10: 5000.0,
                12: 6500.0,
                15: 8000.0,
            },
        )

        assert evaluations == original

        assert evaluations[0] is original[0]
        assert evaluations[1] is original[1]
        assert evaluations[2] is original[2]

    # ==================================================
    # Realistic installation
    # ==================================================

    def test_realistic_15_panel_installation(self):

        evaluations = self._evaluations(
            [10, 12, 14, 15, 16]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=7500.0,
            productions={
                10: 5200.0,
                12: 6240.0,
                14: 7280.0,
                15: 7800.0,
                16: 8320.0,
            },
        )

        assert result.panel_count == 15

        assert result.installed_power_kwp == pytest.approx(
            8.1
        )

        assert result.occupied_area_m2 == pytest.approx(
            38.646
        )

        assert result.annual_consumption_kwh == pytest.approx(
            7500.0
        )

        assert result.annual_production_kwh == pytest.approx(
            7800.0
        )

        assert result.annual_surplus_kwh == pytest.approx(
            300.0
        )

        assert result.annual_deficit_kwh == pytest.approx(
            0.0
        )

        assert result.self_sufficiency_percent == pytest.approx(
            100.0
        )

    def test_realistic_installation_does_not_overdimension(self):

        evaluations = self._evaluations(
            [10, 12, 14, 15, 16]
        )

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

        assert result.panel_count < 15

        assert result.installed_power_kwp == pytest.approx(
            7.56
        )

        assert result.annual_production_kwh == pytest.approx(
            7280.0
        )

        assert result.annual_surplus_kwh == pytest.approx(
            280.0
        )

        assert result.annual_deficit_kwh == pytest.approx(
            0.0
        )

    # ==================================================
    # Immutability
    # ==================================================

    def test_sizing_result_is_immutable(self):

        evaluations = self._evaluations(
            [10]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=5000.0,
            productions={
                10: 6000.0,
            },
        )

        with pytest.raises(
            AttributeError
        ):

            result.annual_consumption_kwh = 7000.0

    def test_sizing_result_evaluation_is_immutable_reference(self):

        evaluation = self._evaluation(
            10
        )

        result = self._recommend(
            [evaluation],
            annual_consumption_kwh=5000.0,
            productions={
                10: 6000.0,
            },
        )

        assert result.evaluation is evaluation

    @pytest.mark.parametrize(
        "consumption",
        [
            None,
            "6000",
            object(),
            True,
            False,
        ],
    )
    def test_rejects_invalid_consumption_type(
        self,
        consumption,
    ):

        evaluations = self._evaluations(
            [10]
        )

        with pytest.raises(
            TypeError,
            match="Annual consumption must be a number.",
        ):

            self._recommend(
                evaluations,
                annual_consumption_kwh=consumption,
                productions={
                    10: 5000.0,
                },
            )

    @pytest.mark.parametrize(
        "production",
        [
            -1.0,
            -100.0,
            -0.01,
        ],
    )
    def test_rejects_negative_annual_production(
        self,
        production,
    ):

        evaluations = self._evaluations(
            [10]
        )

        with pytest.raises(
            ValueError,
            match=(
                "Annual production must be greater "
                "than or equal to zero."
            ),
        ):

            self._recommend(
                evaluations,
                annual_consumption_kwh=5000.0,
                productions={
                    10: production,
                },
            )

    @pytest.mark.parametrize(
        "production",
        [
            None,
            "5000",
            object(),
            True,
            False,
        ],
    )
    def test_rejects_invalid_annual_production_type(
        self,
        production,
    ):

        evaluations = self._evaluations(
            [10]
        )

        with pytest.raises(
            TypeError,
            match="Annual production must be a number.",
        ):

            self._recommend(
                evaluations,
                annual_consumption_kwh=5000.0,
                productions={
                    10: production,
                },
            )

    def test_accepts_zero_annual_production(self):

        evaluations = self._evaluations(
            [10]
        )

        result = self._recommend(
            evaluations,
            annual_consumption_kwh=5000.0,
            productions={
                10: 0.0,
            },
        )

        assert result.panel_count == 10
        assert result.annual_production_kwh == pytest.approx(0.0)
        assert result.self_sufficiency_percent == pytest.approx(0.0)
        assert result.production_coverage_percent == pytest.approx(0.0)
        assert result.annual_surplus_kwh == pytest.approx(0.0)
        assert result.annual_deficit_kwh == pytest.approx(5000.0)

    def test_rejects_duplicate_panel_counts(self):

        evaluations = [
            self._evaluation(10),
            self._evaluation(10),
        ]

        with pytest.raises(
            ValueError,
            match="Duplicate panel count found in evaluations.",
        ):

            self._recommend(
                evaluations,
                annual_consumption_kwh=5000.0,
                productions={
                    10: 6000.0,
                },
            )

    def test_rejects_duplicate_panel_counts_independent_of_object_identity(
        self,
    ):

        first = self._evaluation(10)
        second = self._evaluation(
            10,
            panel_area_m2=2.0,
        )

        with pytest.raises(
            ValueError,
            match="Duplicate panel count found in evaluations.",
        ):

            self._recommend(
                [first, second],
                annual_consumption_kwh=5000.0,
                productions={
                    10: 6000.0,
                },
            )