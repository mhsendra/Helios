import pytest

from helios.solar.installation_constraints import (
    InstallationConstraints
)

from helios.solar.installation_candidate import (
    InstallationCandidate
)

from helios.solar.installation_optimizer import (
    InstallationOptimizer
)

from helios.solar.installation_layout import InstallationLayout

class TestInstallationOptimizer:

    # ==================================================
    # Helpers
    # ==================================================

    def _constraints(
        self,
        available_area_m2=42.0,
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

    # ==================================================
    # Construction
    # ==================================================

    def test_creates_optimizer(self):

        constraints = self._constraints()

        optimizer = InstallationOptimizer(
            constraints
        )

        assert optimizer.constraints is constraints

    def test_rejects_invalid_constraints_type(self):

        with pytest.raises(
            TypeError,
            match="constraints must be an InstallationConstraints."
        ):

            InstallationOptimizer(None)

    # ==================================================
    # Candidate generation
    # ==================================================

    def test_generates_candidates(self):

        constraints = self._constraints(
            max_panels=5
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        candidates = optimizer.generate_candidates()

        assert len(candidates) == 5

        assert all(
            isinstance(
                candidate,
                InstallationCandidate
            )
            for candidate in candidates
        )

    def test_generates_panel_counts_in_order(self):

        constraints = self._constraints(
            min_panels=3,
            max_panels=7
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        candidates = optimizer.generate_candidates()

        assert [
            candidate.panel_count
            for candidate in candidates
        ] == [
            3,
            4,
            5,
            6,
            7,
        ]

    def test_respects_minimum_panel_count(self):

        constraints = self._constraints(
            min_panels=5,
            max_panels=8
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        candidates = optimizer.generate_candidates()

        assert candidates[0].panel_count == 5

    def test_respects_maximum_panel_count(self):

        constraints = self._constraints(
            max_panels=8
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        candidates = optimizer.generate_candidates()

        assert candidates[-1].panel_count == 8

    def test_uses_area_limit_when_max_panels_is_none(self):

        constraints = self._constraints(
            available_area_m2=10.0
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        candidates = optimizer.generate_candidates()

        assert candidates[-1].panel_count == (
            constraints.maximum_panels_by_area
        )

    def test_does_not_exceed_area_limit(self):

        constraints = self._constraints(
            available_area_m2=42.0
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        candidates = optimizer.generate_candidates()

        for candidate in candidates:

            assert (
                candidate.occupied_area_m2
                <= constraints.available_area_m2
            )

    def test_respects_both_area_and_max_panel_limit(self):

        constraints = self._constraints(
            available_area_m2=42.0,
            max_panels=5
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        candidates = optimizer.generate_candidates()

        assert len(candidates) == 5

        assert candidates[-1].panel_count == 5

    def test_area_limit_can_be_lower_than_max_panels(self):

        constraints = self._constraints(
            available_area_m2=15.0,
            max_panels=20
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        candidates = optimizer.generate_candidates()

        assert candidates[-1].panel_count == (
            constraints.maximum_panels_by_area
        )

        assert candidates[-1].panel_count < 20

    # ==================================================
    # Candidate properties
    # ==================================================

    def test_candidates_use_configured_panel_power(self):

        constraints = self._constraints(
            panel_power_wp=540,
            max_panels=3
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        candidates = optimizer.generate_candidates()

        assert all(
            candidate.panel_power_wp == 540
            for candidate in candidates
        )

    def test_candidates_use_configured_panel_area(self):

        constraints = self._constraints(
            max_panels=3
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        candidates = optimizer.generate_candidates()

        expected_area = (
            constraints.panel_area_m2
        )

        assert all(
            candidate.panel_area_m2
            == pytest.approx(expected_area)
            for candidate in candidates
        )

    def test_candidate_power_increases_with_panel_count(self):

        constraints = self._constraints(
            max_panels=5
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        candidates = optimizer.generate_candidates()

        powers = [
            candidate.installed_power_kwp
            for candidate in candidates
        ]

        assert powers == sorted(powers)

    def test_candidate_area_increases_with_panel_count(self):

        constraints = self._constraints(
            max_panels=5
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        candidates = optimizer.generate_candidates()

        areas = [
            candidate.occupied_area_m2
            for candidate in candidates
        ]

        assert areas == sorted(areas)

    # ==================================================
    # Exact boundary
    # ==================================================

    def test_allows_exact_area_boundary(self):

        constraints = self._constraints(
            available_area_m2=20.0,
            panel_width_m=2.0,
            panel_height_m=2.0,
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        candidates = optimizer.generate_candidates()

        assert candidates[-1].panel_count == 5

        assert candidates[-1].occupied_area_m2 == pytest.approx(
            20.0
        )

    def test_excludes_first_panel_over_area_limit(self):

        constraints = self._constraints(
            available_area_m2=3.9,
            panel_width_m=2.0,
            panel_height_m=2.0,
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        candidates = optimizer.generate_candidates()

        assert candidates == []

    # ==================================================
    # Minimum panel boundary
    # ==================================================

    def test_returns_empty_when_minimum_exceeds_area(self):

        constraints = self._constraints(
            available_area_m2=3.9,
            panel_width_m=2.0,
            panel_height_m=2.0,
            min_panels=2,
            max_panels=10,
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        candidates = optimizer.generate_candidates()

        assert candidates == []

    def test_returns_single_candidate_when_limits_are_equal(self):

        constraints = self._constraints(
            min_panels=5,
            max_panels=5
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        candidates = optimizer.generate_candidates()

        assert len(candidates) == 1
        assert candidates[0].panel_count == 5

    # ==================================================
    # Repeated calls
    # ==================================================

    def test_generate_candidates_is_deterministic(self):

        constraints = self._constraints(
            max_panels=5
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        first = optimizer.generate_candidates()
        second = optimizer.generate_candidates()

        assert first == second

    def test_generate_candidates_does_not_modify_constraints(self):

        constraints = self._constraints(
            max_panels=5
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        optimizer.generate_candidates()

        assert constraints.min_panels == 1
        assert constraints.max_panels == 5

    # ==================================================
    # Realistic installation
    # ==================================================

    def test_realistic_540wp_installation(self):

        constraints = self._constraints(
            available_area_m2=42.0,
            panel_power_wp=540,
            max_panels=20,
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        candidates = optimizer.generate_candidates()

        assert candidates[0].panel_count == 1
        assert candidates[-1].panel_count == 16

        assert candidates[-1].installed_power_kwp == pytest.approx(
            8.64
        )

    def test_realistic_installation_candidate_values(self):

        constraints = self._constraints(
            available_area_m2=42.0,
            panel_power_wp=540,
            max_panels=20,
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        candidates = optimizer.generate_candidates()

        candidate = candidates[9]

        assert candidate.panel_count == 10
        assert candidate.installed_power_kwp == pytest.approx(
            5.4
        )
        assert candidate.occupied_area_m2 == pytest.approx(
            10 * constraints.panel_area_m2
        )

    # ==================================================
    # Layout generation
    # ==================================================

    def test_generates_layouts_for_valid_panel_count(self):

        constraints = self._constraints(
            max_panels=15
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        layouts = optimizer.generate_layouts(
            panel_count=15
        )

        assert layouts

        assert all(
            isinstance(
                layout,
                InstallationLayout
            )
            for layout in layouts
        )

    def test_generates_all_rectangular_factorizations(self):

        constraints = self._constraints(
            max_panels=15
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        layouts = optimizer.generate_layouts(
            panel_count=15,
            orientation="vertical",
        )

        dimensions = [
            (
                layout.rows,
                layout.columns
            )
            for layout in layouts
        ]

        assert dimensions == [
            (1, 15),
            (3, 5),
            (5, 3),
            (15, 1),
        ]

    def test_every_layout_has_requested_panel_count(self):

        constraints = self._constraints(
            available_area_m2=60.0,
            max_panels=20
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        layouts = optimizer.generate_layouts(
            panel_count=20
        )

        assert layouts

        assert all(
            layout.panel_count == 20
            for layout in layouts
        )

    def test_rejects_zero_panel_count(self):

        constraints = self._constraints()

        optimizer = InstallationOptimizer(
            constraints
        )

        with pytest.raises(
            ValueError,
            match="Panel count must be at least one."
        ):

            optimizer.generate_layouts(
                panel_count=0
            )

    @pytest.mark.parametrize(
        "panel_count",
        [-1, -5, -10]
    )
    def test_rejects_negative_panel_count(
        self,
        panel_count
    ):

        constraints = self._constraints()

        optimizer = InstallationOptimizer(
            constraints
        )

        with pytest.raises(
            ValueError,
            match="Panel count must be at least one."
        ):

            optimizer.generate_layouts(
                panel_count=panel_count
            )

    def test_returns_empty_when_panel_count_exceeds_limit(self):

        constraints = self._constraints(
            max_panels=10
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        layouts = optimizer.generate_layouts(
            panel_count=11
        )

        assert layouts == []

    def test_returns_empty_when_panel_count_exceeds_area_limit(self):

        constraints = self._constraints(
            available_area_m2=10.0,
            max_panels=20
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        layouts = optimizer.generate_layouts(
            panel_count=20
        )

        assert layouts == []

    def test_accepts_vertical_orientation(self):

        constraints = self._constraints(
            max_panels=6
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        layouts = optimizer.generate_layouts(
            panel_count=6,
            orientation="vertical",
        )

        assert layouts

        assert all(
            layout.orientation == "vertical"
            for layout in layouts
        )

    def test_accepts_horizontal_orientation(self):

        constraints = self._constraints(
            max_panels=6
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        layouts = optimizer.generate_layouts(
            panel_count=6,
            orientation="horizontal",
        )

        assert layouts

        assert all(
            layout.orientation == "horizontal"
            for layout in layouts
        )

    def test_generates_both_orientations_by_default(self):

        constraints = self._constraints(
            max_panels=6
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        layouts = optimizer.generate_layouts(
            panel_count=6
        )

        orientations = {
            layout.orientation
            for layout in layouts
        }

        assert orientations == {
            "vertical",
            "horizontal",
        }

    def test_rejects_invalid_orientation(self):

        constraints = self._constraints()

        optimizer = InstallationOptimizer(
            constraints
        )

        with pytest.raises(
            ValueError,
            match=(
                "Orientation must be "
                "'vertical' or 'horizontal'."
            )
        ):

            optimizer.generate_layouts(
                panel_count=6,
                orientation="diagonal",
            )

    def test_accepts_vertical_walkway(self):

        constraints = self._constraints(
            max_panels=15
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        layouts = optimizer.generate_layouts(
            panel_count=15,
            orientation="vertical",
            walkway_width_m=0.45,
            walkway_position="vertical",
        )

        assert layouts

        assert all(
            layout.walkway_width_m == pytest.approx(
                0.45
            )
            for layout in layouts
        )

        assert all(
            layout.walkway_position == "vertical"
            for layout in layouts
        )

    def test_accepts_horizontal_walkway(self):

        constraints = self._constraints(
            max_panels=15
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        layouts = optimizer.generate_layouts(
            panel_count=15,
            orientation="vertical",
            walkway_width_m=0.45,
            walkway_position="horizontal",
        )

        assert layouts

        assert all(
            layout.walkway_width_m == pytest.approx(
                0.45
            )
            for layout in layouts
        )

        assert all(
            layout.walkway_position == "horizontal"
            for layout in layouts
        )

    def test_rejects_negative_walkway_width(self):

        constraints = self._constraints()

        optimizer = InstallationOptimizer(
            constraints
        )

        with pytest.raises(
            ValueError,
            match="Walkway width cannot be negative."
        ):

            optimizer.generate_layouts(
                panel_count=6,
                walkway_width_m=-0.1,
            )

    def test_rejects_invalid_walkway_position(self):

        constraints = self._constraints()

        optimizer = InstallationOptimizer(
            constraints
        )

        with pytest.raises(
            ValueError,
            match=(
                "Walkway position must be "
                "'vertical', 'horizontal' or None."
            )
        ):

            optimizer.generate_layouts(
                panel_count=6,
                walkway_width_m=0.45,
                walkway_position="diagonal",
            )

    def test_realistic_15_panel_vertical_walkway_layouts(self):

        constraints = self._constraints(
            available_area_m2=42.0,
            panel_power_wp=540,
            max_panels=15,
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        layouts = optimizer.generate_layouts(
            panel_count=15,
            orientation="vertical",
            walkway_width_m=0.45,
            walkway_position="vertical",
        )

        assert len(layouts) == 2

        assert {
            (
                layout.rows,
                layout.columns,
            )
            for layout in layouts
        } == {
            (1, 15),
            (3, 5),
        }

        layout = next(
            layout
            for layout in layouts
            if layout.rows == 3
            and layout.columns == 5
        )

        assert layout.panel_count == 15

        assert layout.panels_width_m == pytest.approx(
            5.67
        )

        assert layout.panels_height_m == pytest.approx(
            6.819
        )

        assert layout.occupied_width_m == pytest.approx(
            6.12
        )

        assert layout.occupied_height_m == pytest.approx(
            6.819
        )

    def test_layouts_use_configured_panel_dimensions(self):

        constraints = self._constraints(
            panel_width_m=1.2,
            panel_height_m=2.0,
            max_panels=6,
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        layouts = optimizer.generate_layouts(
            panel_count=6,
            orientation="vertical",
        )

        assert all(
            layout.panel_width_m == pytest.approx(1.2)
            for layout in layouts
        )

        assert all(
            layout.panel_height_m == pytest.approx(2.0)
            for layout in layouts
        )

    def test_generate_layouts_is_deterministic(self):

        constraints = self._constraints(
            max_panels=15
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        first = optimizer.generate_layouts(
            panel_count=15,
            orientation="vertical",
            walkway_width_m=0.45,
            walkway_position="vertical",
        )

        second = optimizer.generate_layouts(
            panel_count=15,
            orientation="vertical",
            walkway_width_m=0.45,
            walkway_position="vertical",
        )

        assert first == second

    def test_generate_layouts_does_not_modify_constraints(self):

        constraints = self._constraints(
            max_panels=15
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        optimizer.generate_layouts(
            panel_count=15,
            orientation="vertical",
            walkway_width_m=0.45,
            walkway_position="vertical",
        )

        assert constraints.min_panels == 1
        assert constraints.max_panels == 15
        assert constraints.panel_width_m == pytest.approx(
            1.134
        )
        assert constraints.panel_height_m == pytest.approx(
            2.273
        )
        assert constraints.panel_power_wp == 540

    def test_single_panel_generates_single_layout_per_orientation(self):

        constraints = self._constraints(
            max_panels=1
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        layouts = optimizer.generate_layouts(
            panel_count=1
        )

        assert len(layouts) == 2

        assert {
            layout.orientation
            for layout in layouts
        } == {
            "vertical",
            "horizontal",
        }

        assert all(
            layout.panel_count == 1
            for layout in layouts
        )

    def test_rejects_walkway_width_without_position(self):

        constraints = self._constraints(
            max_panels=6
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        with pytest.raises(
            ValueError,
            match=(
                "Walkway position is required "
                "when walkway width is greater than zero."
            )
        ):

            optimizer.generate_layouts(
                panel_count=6,
                walkway_width_m=0.45,
            )


    def test_rejects_walkway_position_without_width(self):

        constraints = self._constraints(
            max_panels=6
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        with pytest.raises(
            ValueError,
            match=(
                "Walkway width must be greater than zero "
                "when walkway position is specified."
            )
        ):

            optimizer.generate_layouts(
                panel_count=6,
                walkway_position="vertical",
            )


    def test_panel_count_below_minimum_returns_empty(self):

        constraints = self._constraints(
            min_panels=5,
            max_panels=10,
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        layouts = optimizer.generate_layouts(
            panel_count=4
        )

        assert layouts == []


    def test_prime_panel_count_generates_only_trivial_factorizations(self):

        constraints = self._constraints(
            max_panels=13
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        layouts = optimizer.generate_layouts(
            panel_count=13,
            orientation="vertical",
        )

        assert [
            (
                layout.rows,
                layout.columns,
            )
            for layout in layouts
        ] == [
            (1, 13),
            (13, 1),
        ]

    def test_layout_with_walkway_cannot_exceed_available_area(self):

        constraints = self._constraints(
            available_area_m2=9.0,
            panel_width_m=2.0,
            panel_height_m=2.0,
            max_panels=2,
        )

        optimizer = InstallationOptimizer(
            constraints
        )

        layouts = optimizer.generate_layouts(
            panel_count=2,
            orientation="vertical",
            walkway_width_m=1.0,
            walkway_position="vertical",
        )

        assert layouts == []

    def test_generate_layouts_respects_vertical_orientation(self):

        constraints = InstallationConstraints(
            available_area_m2=100,
            panel_width_m=1.134,
            panel_height_m=1.99,
            panel_power_wp=540,
            panel_orientation="vertical",
        )

        optimizer = InstallationOptimizer(constraints)

        layouts = optimizer.generate_layouts(
            panel_count=6
        )

        assert layouts
        assert all(
            layout.orientation == "vertical"
            for layout in layouts
        )

    def test_generate_layouts_respects_horizontal_orientation(self):

        constraints = InstallationConstraints(
            available_area_m2=100,
            panel_width_m=1.134,
            panel_height_m=1.99,
            panel_power_wp=540,
            panel_orientation="horizontal",
        )

        optimizer = InstallationOptimizer(constraints)

        layouts = optimizer.generate_layouts(
            panel_count=6
        )

        assert layouts
        assert all(
            layout.orientation == "horizontal"
            for layout in layouts
        )

    def test_generate_layouts_auto_evaluates_both_orientations(self):

        constraints = InstallationConstraints(
            available_area_m2=100,
            panel_width_m=1.134,
            panel_height_m=1.99,
            panel_power_wp=540,
            panel_orientation="auto",
        )

        optimizer = InstallationOptimizer(constraints)

        layouts = optimizer.generate_layouts(
            panel_count=6
        )

        orientations = {
            layout.orientation
            for layout in layouts
        }

        assert orientations == {
            "vertical",
            "horizontal",
        }

    def test_invalid_panel_orientation_is_rejected(self):

        with pytest.raises(ValueError):

            InstallationConstraints(
                available_area_m2=100,
                panel_width_m=1.134,
                panel_height_m=1.99,
                panel_power_wp=540,
                panel_orientation="diagonal",
            )