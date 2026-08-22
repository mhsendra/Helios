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

from helios.solar.installation_layout import (
    InstallationLayout,
)


class TestInstallationEvaluator:

    # ==================================================
    # Helpers
    # ==================================================

    def _constraints(
        self,
        available_area_m2=50.0,
        panel_width_m=1.134,
        panel_height_m=2.273,
        panel_power_wp=540.0,
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

    def _candidate(
        self,
        panel_count=10,
        panel_power_wp=540.0,
        panel_area_m2=2.5764,
    ):

        return InstallationCandidate(
            panel_count=panel_count,
            panel_power_wp=panel_power_wp,
            panel_area_m2=panel_area_m2,
        )

    def _evaluator(
        self,
        **kwargs,
    ):

        return InstallationEvaluator(
            self._constraints(**kwargs)
        )

    def _layout(
        self,
        rows,
        columns,
        orientation="vertical",
        walkway_width_m=0.0,
        walkway_position=None,
    ):

        return InstallationLayout(
            rows=rows,
            columns=columns,
            panel_width_m=1.134,
            panel_height_m=2.273,
            orientation=orientation,
            walkway_width_m=walkway_width_m,
            walkway_position=walkway_position,
        )

    # ==================================================
    # Construction
    # ==================================================

    def test_creates_evaluator(self):

        evaluator = self._evaluator()

        assert isinstance(
            evaluator,
            InstallationEvaluator,
        )

    def test_rejects_invalid_constraints_type(self):

        with pytest.raises(
            TypeError,
            match="constraints must be an InstallationConstraints.",
        ):

            InstallationEvaluator(
                None
            )

    # ==================================================
    # Basic evaluation
    # ==================================================

    def test_evaluate_returns_installation_evaluation(self):

        evaluator = self._evaluator()

        candidate = self._candidate(
            panel_count=10
        )

        result = evaluator.evaluate(
            candidate
        )

        assert isinstance(
            result,
            InstallationEvaluation,
        )

    def test_evaluate_preserves_candidate_reference(self):

        evaluator = self._evaluator()

        candidate = self._candidate(
            panel_count=10
        )

        result = evaluator.evaluate(
            candidate
        )

        assert result.candidate is candidate

    def test_evaluate_preserves_available_area(self):

        evaluator = self._evaluator(
            available_area_m2=75.0
        )

        result = evaluator.evaluate(
            self._candidate()
        )

        assert result.available_area_m2 == pytest.approx(
            75.0
        )

    def test_evaluate_layout_is_none_by_default(self):

        evaluator = self._evaluator()

        result = evaluator.evaluate(
            self._candidate()
        )

        assert result.layout is None

    # ==================================================
    # Candidate validation
    # ==================================================

    def test_rejects_invalid_candidate_type(self):

        evaluator = self._evaluator()

        with pytest.raises(
            TypeError,
            match="candidate must be an InstallationCandidate.",
        ):

            evaluator.evaluate(
                None
            )

    def test_rejects_candidate_below_minimum_panels(self):

        evaluator = self._evaluator(
            min_panels=10,
            max_panels=20,
        )

        candidate = self._candidate(
            panel_count=9
        )

        with pytest.raises(
            ValueError,
            match="Candidate exceeds installation constraints.",
        ):

            evaluator.evaluate(
                candidate
            )

    def test_accepts_candidate_at_minimum_panels(self):

        evaluator = self._evaluator(
            min_panels=10,
            max_panels=20,
        )

        candidate = self._candidate(
            panel_count=10
        )

        result = evaluator.evaluate(
            candidate
        )

        assert result.panel_count == 10

    def test_rejects_candidate_above_maximum_panels(self):

        evaluator = self._evaluator(
            min_panels=1,
            max_panels=10,
        )

        candidate = self._candidate(
            panel_count=11
        )

        with pytest.raises(
            ValueError,
            match="Candidate exceeds installation constraints.",
        ):

            evaluator.evaluate(
                candidate
            )

    def test_accepts_candidate_at_maximum_panels(self):

        evaluator = self._evaluator(
            min_panels=1,
            max_panels=10,
        )

        candidate = self._candidate(
            panel_count=10
        )

        result = evaluator.evaluate(
            candidate
        )

        assert result.panel_count == 10

    def test_accepts_candidate_when_max_panels_is_none(self):

        evaluator = self._evaluator(
            available_area_m2=300.0,
            min_panels=1,
            max_panels=None,
        )

        candidate = self._candidate(
            panel_count=100
        )

        result = evaluator.evaluate(
            candidate
        )

        assert isinstance(
            result,
            InstallationEvaluation,
        )

        assert result.panel_count == 100

    def test_rejects_candidate_exceeding_available_area(self):

        evaluator = self._evaluator(
            available_area_m2=20.0
        )

        candidate = self._candidate(
            panel_count=10
        )

        with pytest.raises(
            ValueError,
            match="Candidate exceeds installation constraints.",
        ):

            evaluator.evaluate(
                candidate
            )

    def test_accepts_candidate_exactly_filling_available_area(
        self,
    ):

        panel_area = 2.0
        panel_count = 10

        evaluator = self._evaluator(
            available_area_m2=20.0
        )

        candidate = self._candidate(
            panel_count=panel_count,
            panel_area_m2=panel_area,
        )

        result = evaluator.evaluate(
            candidate
        )

        assert result.is_within_area is True
        assert result.remaining_area_m2 == pytest.approx(
            0.0
        )

    # ==================================================
    # Evaluation properties
    # ==================================================

    def test_installed_power_kwp(self):

        result = self._evaluator().evaluate(
            self._candidate(
                panel_count=15,
                panel_power_wp=540.0,
            )
        )

        assert result.installed_power_kwp == pytest.approx(
            8.1
        )

    def test_occupied_area(self):

        result = self._evaluator().evaluate(
            self._candidate(
                panel_count=15,
                panel_area_m2=2.5764,
            )
        )

        assert result.occupied_area_m2 == pytest.approx(
            38.646
        )

    def test_panel_count(self):

        result = self._evaluator().evaluate(
            self._candidate(
                panel_count=15
            )
        )

        assert result.panel_count == 15

    def test_remaining_area(self):

        evaluator = self._evaluator(
            available_area_m2=50.0
        )

        result = evaluator.evaluate(
            self._candidate(
                panel_count=15,
                panel_area_m2=2.5764,
            )
        )

        assert result.remaining_area_m2 == pytest.approx(
            11.354
        )

    def test_area_utilization_percent(self):

        evaluator = self._evaluator(
            available_area_m2=50.0
        )

        result = evaluator.evaluate(
            self._candidate(
                panel_count=10,
                panel_area_m2=2.0,
            )
        )

        assert result.area_utilization_percent == pytest.approx(
            40.0
        )

    def test_area_utilization_is_100_when_area_is_fully_used(
        self,
    ):

        evaluator = self._evaluator(
            available_area_m2=20.0
        )

        result = evaluator.evaluate(
            self._candidate(
                panel_count=10,
                panel_area_m2=2.0,
            )
        )

        assert result.area_utilization_percent == pytest.approx(
            100.0
        )

    def test_is_within_area_true_when_under_limit(self):

        evaluator = self._evaluator(
            available_area_m2=50.0
        )

        result = evaluator.evaluate(
            self._candidate(
                panel_count=10,
                panel_area_m2=2.0,
            )
        )

        assert result.is_within_area is True

    def test_is_within_area_true_at_exact_boundary(self):

        evaluator = self._evaluator(
            available_area_m2=20.0
        )

        result = evaluator.evaluate(
            self._candidate(
                panel_count=10,
                panel_area_m2=2.0,
            )
        )

        assert result.is_within_area is True

    # ==================================================
    # Layout evaluation
    # ==================================================

    def test_evaluate_layout_returns_evaluation(self):

        evaluator = self._evaluator()

        candidate = self._candidate(
            panel_count=6
        )

        layout = self._layout(
            rows=2,
            columns=3,
        )

        result = evaluator.evaluate_layout(
            candidate,
            layout,
        )

        assert isinstance(
            result,
            InstallationEvaluation,
        )

    def test_evaluate_layout_preserves_candidate_reference(
        self,
    ):

        evaluator = self._evaluator()

        candidate = self._candidate(
            panel_count=6
        )

        layout = self._layout(
            rows=2,
            columns=3,
        )

        result = evaluator.evaluate_layout(
            candidate,
            layout,
        )

        assert result.candidate is candidate

    def test_evaluate_layout_preserves_layout_reference(
        self,
    ):

        evaluator = self._evaluator()

        candidate = self._candidate(
            panel_count=6
        )

        layout = self._layout(
            rows=2,
            columns=3,
        )

        result = evaluator.evaluate_layout(
            candidate,
            layout,
        )

        assert result.layout is layout

    def test_evaluate_layout_rejects_invalid_candidate_type(
        self,
    ):

        evaluator = self._evaluator()

        layout = self._layout(
            rows=2,
            columns=3,
        )

        with pytest.raises(
            TypeError,
            match="Candidate must be an InstallationCandidate.",
        ):

            evaluator.evaluate_layout(
                None,
                layout,
            )

    def test_evaluate_layout_rejects_invalid_layout_type(
        self,
    ):

        evaluator = self._evaluator()

        candidate = self._candidate(
            panel_count=6
        )

        with pytest.raises(
            TypeError,
            match="Layout must be an InstallationLayout.",
        ):

            evaluator.evaluate_layout(
                candidate,
                None,
            )

    def test_evaluate_layout_requires_matching_panel_count(
        self,
    ):

        evaluator = self._evaluator()

        candidate = self._candidate(
            panel_count=6
        )

        layout = self._layout(
            rows=2,
            columns=2,
        )

        with pytest.raises(
            ValueError,
            match=(
                "Layout panel count must match "
                "candidate panel count."
            ),
        ):

            evaluator.evaluate_layout(
                candidate,
                layout,
            )

    def test_evaluate_layout_accepts_matching_panel_count(
        self,
    ):

        evaluator = self._evaluator()

        candidate = self._candidate(
            panel_count=6
        )

        layout = self._layout(
            rows=2,
            columns=3,
        )

        result = evaluator.evaluate_layout(
            candidate,
            layout,
        )

        assert result.panel_count == 6
        assert result.layout is layout

    def test_evaluate_layout_applies_candidate_constraints(
        self,
    ):

        evaluator = self._evaluator(
            min_panels=10,
            max_panels=20,
        )

        candidate = self._candidate(
            panel_count=6
        )

        layout = self._layout(
            rows=2,
            columns=3,
        )

        with pytest.raises(
            ValueError,
            match="Candidate exceeds installation constraints.",
        ):

            evaluator.evaluate_layout(
                candidate,
                layout,
            )

    def test_evaluate_layout_rejects_candidate_over_area(
        self,
    ):

        evaluator = self._evaluator(
            available_area_m2=10.0
        )

        candidate = self._candidate(
            panel_count=6,
            panel_area_m2=2.0,
        )

        layout = self._layout(
            rows=2,
            columns=3,
        )

        with pytest.raises(
            ValueError,
            match="Candidate exceeds installation constraints.",
        ):

            evaluator.evaluate_layout(
                candidate,
                layout,
            )

    # ==================================================
    # Layout geometry
    # ==================================================

    def test_vertical_layout_keeps_expected_dimensions(self):

        evaluator = self._evaluator()

        candidate = self._candidate(
            panel_count=6
        )

        layout = self._layout(
            rows=2,
            columns=3,
            orientation="vertical",
        )

        result = evaluator.evaluate_layout(
            candidate,
            layout,
        )

        assert result.layout.oriented_panel_width_m == pytest.approx(
            1.134
        )

        assert result.layout.oriented_panel_height_m == pytest.approx(
            2.273
        )

    def test_horizontal_layout_swaps_expected_dimensions(self):

        evaluator = self._evaluator()

        candidate = self._candidate(
            panel_count=6
        )

        layout = self._layout(
            rows=2,
            columns=3,
            orientation="horizontal",
        )

        result = evaluator.evaluate_layout(
            candidate,
            layout,
        )

        assert result.layout.oriented_panel_width_m == pytest.approx(
            2.273
        )

        assert result.layout.oriented_panel_height_m == pytest.approx(
            1.134
        )

    def test_layout_with_vertical_walkway_is_preserved(self):

        evaluator = self._evaluator()

        candidate = self._candidate(
            panel_count=6
        )

        layout = self._layout(
            rows=2,
            columns=3,
            walkway_width_m=1.0,
            walkway_position="vertical",
        )

        result = evaluator.evaluate_layout(
            candidate,
            layout,
        )

        assert result.layout is layout
        assert result.layout.walkway_position == "vertical"
        assert result.layout.walkway_width_m == pytest.approx(
            1.0
        )

    def test_layout_with_horizontal_walkway_is_preserved(self):

        evaluator = self._evaluator()

        candidate = self._candidate(
            panel_count=6
        )

        layout = self._layout(
            rows=2,
            columns=3,
            walkway_width_m=1.0,
            walkway_position="horizontal",
        )

        result = evaluator.evaluate_layout(
            candidate,
            layout,
        )

        assert result.layout is layout
        assert result.layout.walkway_position == "horizontal"
        assert result.layout.walkway_width_m == pytest.approx(
            1.0
        )

    # ==================================================
    # Immutability / input preservation
    # ==================================================

    def test_evaluation_is_immutable(self):

        result = self._evaluator().evaluate(
            self._candidate()
        )

        with pytest.raises(
            AttributeError
        ):

            result.available_area_m2 = 100.0

    def test_evaluation_does_not_modify_candidate(self):

        candidate = self._candidate(
            panel_count=10,
            panel_area_m2=2.0,
        )

        original_values = (
            candidate.panel_count,
            candidate.panel_power_wp,
            candidate.panel_area_m2,
            candidate.installed_power_kwp,
            candidate.occupied_area_m2,
        )

        self._evaluator().evaluate(
            candidate
        )

        assert (
            candidate.panel_count,
            candidate.panel_power_wp,
            candidate.panel_area_m2,
            candidate.installed_power_kwp,
            candidate.occupied_area_m2,
        ) == original_values

    def test_evaluate_layout_does_not_modify_inputs(self):

        candidate = self._candidate(
            panel_count=6
        )

        layout = self._layout(
            rows=2,
            columns=3,
        )

        original_candidate = candidate
        original_layout = layout

        result = self._evaluator().evaluate_layout(
            candidate,
            layout,
        )

        assert result.candidate is original_candidate
        assert result.layout is original_layout

    # ==================================================
    # Consistency invariants
    # ==================================================

    def test_remaining_area_plus_occupied_area_equals_available_area(
        self,
    ):

        evaluator = self._evaluator(
            available_area_m2=50.0
        )

        result = evaluator.evaluate(
            self._candidate(
                panel_count=10,
                panel_area_m2=2.0,
            )
        )

        assert (
            result.remaining_area_m2
            + result.occupied_area_m2
        ) == pytest.approx(
            result.available_area_m2
        )

    def test_area_utilization_matches_occupied_area_ratio(
        self,
    ):

        evaluator = self._evaluator(
            available_area_m2=50.0
        )

        result = evaluator.evaluate(
            self._candidate(
                panel_count=10,
                panel_area_m2=2.0,
            )
        )

        expected = (
            result.occupied_area_m2
            / result.available_area_m2
            * 100
        )

        assert result.area_utilization_percent == pytest.approx(
            expected
        )

    def test_is_within_area_matches_boundary_condition(self):

        evaluator = self._evaluator(
            available_area_m2=50.0
        )

        result = evaluator.evaluate(
            self._candidate(
                panel_count=10,
                panel_area_m2=2.0,
            )
        )

        assert result.is_within_area is (
            result.occupied_area_m2
            <= result.available_area_m2
        )