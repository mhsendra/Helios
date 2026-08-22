import pytest

from helios.solar.installation_constraints import (
    InstallationConstraints
)


class TestInstallationConstraints:

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
        maintenance_passage_required=False,
        maintenance_passage_width_m=0.45,
        maintenance_passage_orientation="auto",
        roof_width_m=None,
        roof_height_m=None,
    ):

        return InstallationConstraints(
            available_area_m2=available_area_m2,
            panel_width_m=panel_width_m,
            panel_height_m=panel_height_m,
            panel_power_wp=panel_power_wp,
            min_panels=min_panels,
            max_panels=max_panels,
            maintenance_passage_required=(
                maintenance_passage_required
            ),
            maintenance_passage_width_m=(
                maintenance_passage_width_m
            ),
            maintenance_passage_orientation=(
                maintenance_passage_orientation
            ),
            roof_width_m=roof_width_m,
            roof_height_m=roof_height_m,
        )

    # ==================================================
    # Valid construction
    # ==================================================

    def test_creates_valid_constraints(self):

        constraints = InstallationConstraints(
            available_area_m2=42.25,
            panel_width_m=1.13,
            panel_height_m=2.28,
            panel_power_wp=540,
        )

        assert constraints.available_area_m2 == 42.25
        assert constraints.panel_width_m == 1.13
        assert constraints.panel_height_m == 2.28
        assert constraints.panel_power_wp == 540

        assert constraints.min_panels == 1
        assert constraints.max_panels is None

    def test_creates_constraints_with_custom_limits(self):

        constraints = InstallationConstraints(
            available_area_m2=50.0,
            panel_width_m=1.0,
            panel_height_m=2.0,
            panel_power_wp=500,
            min_panels=3,
            max_panels=20,
        )

        assert constraints.min_panels == 3
        assert constraints.max_panels == 20

    # ==================================================
    # available_area_m2 validation
    # ==================================================

    @pytest.mark.parametrize(
        "value",
        [
            0,
            -1,
            -0.01,
        ]
    )
    def test_rejects_invalid_available_area(
        self,
        value
    ):

        with pytest.raises(
            ValueError,
            match="Available area must be greater than zero."
        ):

            InstallationConstraints(
                available_area_m2=value,
                panel_width_m=1.13,
                panel_height_m=2.28,
                panel_power_wp=540,
            )

    # ==================================================
    # panel_width_m validation
    # ==================================================

    @pytest.mark.parametrize(
        "value",
        [
            0,
            -1,
            -0.01,
        ]
    )
    def test_rejects_invalid_panel_width(
        self,
        value
    ):

        with pytest.raises(
            ValueError,
            match="Panel width must be greater than zero."
        ):

            InstallationConstraints(
                available_area_m2=42.25,
                panel_width_m=value,
                panel_height_m=2.28,
                panel_power_wp=540,
            )

    # ==================================================
    # panel_height_m validation
    # ==================================================

    @pytest.mark.parametrize(
        "value",
        [
            0,
            -1,
            -0.01,
        ]
    )
    def test_rejects_invalid_panel_height(
        self,
        value
    ):

        with pytest.raises(
            ValueError,
            match="Panel height must be greater than zero."
        ):

            InstallationConstraints(
                available_area_m2=42.25,
                panel_width_m=1.13,
                panel_height_m=value,
                panel_power_wp=540,
            )

    # ==================================================
    # panel_power_wp validation
    # ==================================================

    @pytest.mark.parametrize(
        "value",
        [
            0,
            -1,
            -0.01,
        ]
    )
    def test_rejects_invalid_panel_power(
        self,
        value
    ):

        with pytest.raises(
            ValueError,
            match="Panel power must be greater than zero."
        ):

            InstallationConstraints(
                available_area_m2=42.25,
                panel_width_m=1.13,
                panel_height_m=2.28,
                panel_power_wp=value,
            )

    # ==================================================
    # min_panels validation
    # ==================================================

    @pytest.mark.parametrize(
        "value",
        [
            0,
            -1,
            -10,
        ]
    )
    def test_rejects_invalid_minimum_panels(
        self,
        value
    ):

        with pytest.raises(
            ValueError,
            match=(
                "Minimum number of panels "
                "must be at least one."
            )
        ):

            InstallationConstraints(
                available_area_m2=42.25,
                panel_width_m=1.13,
                panel_height_m=2.28,
                panel_power_wp=540,
                min_panels=value,
            )

    # ==================================================
    # max_panels validation
    # ==================================================

    def test_accepts_maximum_equal_to_minimum(self):

        constraints = InstallationConstraints(
            available_area_m2=42.25,
            panel_width_m=1.13,
            panel_height_m=2.28,
            panel_power_wp=540,
            min_panels=5,
            max_panels=5,
        )

        assert constraints.min_panels == 5
        assert constraints.max_panels == 5

    def test_rejects_maximum_less_than_minimum(self):

        with pytest.raises(
            ValueError,
            match=(
                "Maximum number of panels cannot be less "
                "than minimum number of panels."
            )
        ):

            InstallationConstraints(
                available_area_m2=42.25,
                panel_width_m=1.13,
                panel_height_m=2.28,
                panel_power_wp=540,
                min_panels=10,
                max_panels=5,
            )

    def test_accepts_no_maximum_panels_limit(self):

        constraints = InstallationConstraints(
            available_area_m2=42.25,
            panel_width_m=1.13,
            panel_height_m=2.28,
            panel_power_wp=540,
            max_panels=None,
        )

        assert constraints.max_panels is None

    # ==================================================
    # panel_area_m2
    # ==================================================

    def test_calculates_panel_area(self):

        constraints = InstallationConstraints(
            available_area_m2=42.25,
            panel_width_m=1.13,
            panel_height_m=2.28,
            panel_power_wp=540,
        )

        assert constraints.panel_area_m2 == pytest.approx(
            2.5764
        )

    def test_calculates_panel_area_with_integer_dimensions(self):

        constraints = InstallationConstraints(
            available_area_m2=100.0,
            panel_width_m=2.0,
            panel_height_m=3.0,
            panel_power_wp=500,
        )

        assert constraints.panel_area_m2 == 6.0

    # ==================================================
    # maximum_panels_by_area
    # ==================================================

    def test_calculates_maximum_panels_by_area(self):

        constraints = InstallationConstraints(
            available_area_m2=42.25,
            panel_width_m=1.13,
            panel_height_m=2.28,
            panel_power_wp=540,
        )

        assert constraints.maximum_panels_by_area == 16

    def test_maximum_panels_by_area_rounds_down(self):

        constraints = InstallationConstraints(
            available_area_m2=10.9,
            panel_width_m=2.0,
            panel_height_m=2.0,
            panel_power_wp=500,
        )

        assert constraints.maximum_panels_by_area == 2

    def test_maximum_panels_by_area_when_less_than_one_panel_fits(self):

        constraints = InstallationConstraints(
            available_area_m2=1.0,
            panel_width_m=2.0,
            panel_height_m=1.0,
            panel_power_wp=500,
        )

        assert constraints.maximum_panels_by_area == 0

    def test_maximum_panels_by_area_exact_fit(self):

        constraints = InstallationConstraints(
            available_area_m2=12.0,
            panel_width_m=2.0,
            panel_height_m=2.0,
            panel_power_wp=500,
        )

        assert constraints.maximum_panels_by_area == 3

    # ==================================================
    # effective_max_panels
    # ==================================================

    def test_effective_max_panels_uses_area_limit_without_manual_limit(self):

        constraints = InstallationConstraints(
            available_area_m2=20.0,
            panel_width_m=2.0,
            panel_height_m=2.0,
            panel_power_wp=500,
        )

        assert constraints.maximum_panels_by_area == 5
        assert constraints.effective_max_panels == 5

    def test_effective_max_panels_uses_manual_limit_when_lower(self):

        constraints = InstallationConstraints(
            available_area_m2=100.0,
            panel_width_m=2.0,
            panel_height_m=2.0,
            panel_power_wp=500,
            max_panels=10,
        )

        assert constraints.maximum_panels_by_area == 25
        assert constraints.effective_max_panels == 10

    def test_effective_max_panels_uses_area_limit_when_lower_than_manual_limit(self):

        constraints = InstallationConstraints(
            available_area_m2=20.0,
            panel_width_m=2.0,
            panel_height_m=2.0,
            panel_power_wp=500,
            max_panels=10,
        )

        assert constraints.maximum_panels_by_area == 5
        assert constraints.effective_max_panels == 5

    def test_effective_max_panels_exactly_matches_manual_and_area_limits(self):

        constraints = InstallationConstraints(
            available_area_m2=20.0,
            panel_width_m=2.0,
            panel_height_m=2.0,
            panel_power_wp=500,
            max_panels=5,
        )

        assert constraints.maximum_panels_by_area == 5
        assert constraints.effective_max_panels == 5

    # ==================================================
    # Immutability
    # ==================================================

    def test_constraints_are_immutable(self):

        constraints = InstallationConstraints(
            available_area_m2=42.25,
            panel_width_m=1.13,
            panel_height_m=2.28,
            panel_power_wp=540,
        )

        with pytest.raises(
            AttributeError
        ):

            constraints.available_area_m2 = 50.0

    def test_rejects_zero_available_area(self):

        with pytest.raises(
            ValueError,
            match="Available area must be greater than zero.",
        ):
            self._constraints(
                available_area_m2=0.0
            )


    @pytest.mark.parametrize(
        "area",
        [-1.0, -10.0, -0.01],
    )
    def test_rejects_negative_available_area(
        self,
        area,
    ):

        with pytest.raises(
            ValueError,
            match="Available area must be greater than zero.",
        ):
            self._constraints(
                available_area_m2=area
            )


    @pytest.mark.parametrize(
        "width",
        [0.0, -1.0],
    )
    def test_rejects_non_positive_panel_width(
        self,
        width,
    ):

        with pytest.raises(
            ValueError,
            match="Panel width must be greater than zero.",
        ):
            self._constraints(
                panel_width_m=width
            )


    @pytest.mark.parametrize(
        "height",
        [0.0, -1.0],
    )
    def test_rejects_non_positive_panel_height(
        self,
        height,
    ):

        with pytest.raises(
            ValueError,
            match="Panel height must be greater than zero.",
        ):
            self._constraints(
                panel_height_m=height
            )


    @pytest.mark.parametrize(
        "power",
        [0.0, -1.0],
    )
    def test_rejects_non_positive_panel_power(
        self,
        power,
    ):

        with pytest.raises(
            ValueError,
            match="Panel power must be greater than zero.",
        ):
            self._constraints(
                panel_power_wp=power
            )


    def test_rejects_zero_minimum_panel_count(self):

        with pytest.raises(
            ValueError,
            match="Minimum number of panels must be at least one.",
        ):
            self._constraints(
                min_panels=0
            )


    @pytest.mark.parametrize(
        "min_panels",
        [-1, -5],
    )
    def test_rejects_negative_minimum_panel_count(
        self,
        min_panels,
    ):

        with pytest.raises(
            ValueError,
            match="Minimum number of panels must be at least one.",
        ):
            self._constraints(
                min_panels=min_panels
            )


    def test_rejects_maximum_below_minimum(self):

        with pytest.raises(
            ValueError,
            match=(
                "Maximum number of panels cannot be less "
                "than minimum number of panels."
            ),
        ):
            self._constraints(
                min_panels=10,
                max_panels=9,
            )
            
class TestInstallationConstraintsMaintenancePassage:

    def _constraints(self, **overrides):

        values = {
            "available_area_m2": 42.25,
            "panel_width_m": 1.134,
            "panel_height_m": 2.278,
            "panel_power_wp": 540,
        }

        values.update(overrides)

        return InstallationConstraints(
            **values
        )

    # ==================================================
    # Disabled
    # ==================================================

    def test_maintenance_passage_disabled_by_default(self):

        constraints = self._constraints()

        assert (
            constraints.maintenance_passage_required
            is False
        )

        assert (
            constraints.maintenance_passage_area_m2
            is None
        )

        assert (
            constraints.maintenance_passage_orientations
            == ()
        )

    # ==================================================
    # Horizontal
    # ==================================================

    def test_horizontal_passage(self):

        constraints = self._constraints(
            maintenance_passage_required=True,
            maintenance_passage_width_m=0.45,
            maintenance_passage_orientation="horizontal",
            roof_width_m=6.50,
            roof_height_m=6.50,
        )

        assert (
            constraints.maintenance_passage_area_m2
            == pytest.approx(2.925)
        )

        assert (
            constraints.maintenance_passage_orientations
            == ("horizontal",)
        )

    # ==================================================
    # Vertical
    # ==================================================

    def test_vertical_passage(self):

        constraints = self._constraints(
            maintenance_passage_required=True,
            maintenance_passage_width_m=0.45,
            maintenance_passage_orientation="vertical",
            roof_width_m=6.50,
            roof_height_m=6.50,
        )

        assert (
            constraints.maintenance_passage_area_m2
            == pytest.approx(2.925)
        )

        assert (
            constraints.maintenance_passage_orientations
            == ("vertical",)
        )

    # ==================================================
    # Auto
    # ==================================================

    def test_auto_passage_returns_both_orientations(self):

        constraints = self._constraints(
            maintenance_passage_required=True,
            maintenance_passage_width_m=0.45,
            maintenance_passage_orientation="auto",
            roof_width_m=6.50,
            roof_height_m=6.50,
        )

        assert (
            constraints.maintenance_passage_orientations
            == (
                "horizontal",
                "vertical",
            )
        )

        assert (
            constraints.maintenance_passage_area_m2
            is None
        )

    # ==================================================
    # Custom width
    # ==================================================

    def test_custom_passage_width(self):

        constraints = self._constraints(
            maintenance_passage_required=True,
            maintenance_passage_width_m=0.40,
            maintenance_passage_orientation="vertical",
            roof_width_m=6.50,
            roof_height_m=6.50,
        )

        assert (
            constraints.maintenance_passage_area_m2
            == pytest.approx(2.60)
        )

    # ==================================================
    # Passage requires roof width
    # ==================================================

    def test_passage_requires_roof_width(self):

        with pytest.raises(
            ValueError,
            match="Roof width is required",
        ):

            self._constraints(
                maintenance_passage_required=True,
                maintenance_passage_orientation="vertical",
                roof_height_m=6.50,
            )

    # ==================================================
    # Passage requires roof height
    # ==================================================

    def test_passage_requires_roof_height(self):

        with pytest.raises(
            ValueError,
            match="Roof height is required",
        ):

            self._constraints(
                maintenance_passage_required=True,
                maintenance_passage_orientation="vertical",
                roof_width_m=6.50,
            )

    # ==================================================
    # Invalid orientation
    # ==================================================

    def test_invalid_passage_orientation(self):

        with pytest.raises(
            ValueError,
            match=(
                "Maintenance passage orientation must be "
                "'horizontal', 'vertical' or 'auto'"
            ),
        ):

            self._constraints(
                maintenance_passage_required=True,
                maintenance_passage_orientation="diagonal",
                roof_width_m=6.50,
                roof_height_m=6.50,
            )

    # ==================================================
    # Invalid passage width
    # ==================================================

    @pytest.mark.parametrize(
        "width",
        [
            0,
            -0.10,
        ],
    )
    def test_invalid_passage_width(self, width):

        with pytest.raises(
            ValueError,
            match=(
                "Maintenance passage width must be "
                "greater than zero"
            ),
        ):

            self._constraints(
                maintenance_passage_width_m=width,
            )

    # ==================================================
    # Horizontal passage cannot consume whole roof
    # ==================================================

    def test_horizontal_passage_cannot_consume_roof_width(self):

        with pytest.raises(
            ValueError,
            match=(
                "Maintenance passage width cannot be "
                "greater than or equal to roof width"
            ),
        ):

            self._constraints(
                maintenance_passage_required=True,
                maintenance_passage_width_m=6.50,
                maintenance_passage_orientation="horizontal",
                roof_width_m=6.50,
                roof_height_m=6.50,
            )

    # ==================================================
    # Vertical passage cannot consume whole roof
    # ==================================================

    def test_vertical_passage_cannot_consume_roof_height(self):

        with pytest.raises(
            ValueError,
            match=(
                "Maintenance passage width cannot be "
                "greater than or equal to roof height"
            ),
        ):

            self._constraints(
                maintenance_passage_required=True,
                maintenance_passage_width_m=6.50,
                maintenance_passage_orientation="vertical",
                roof_width_m=6.50,
                roof_height_m=6.50,
            )

    # ==================================================
    # Auto validates both dimensions
    # ==================================================

    def test_auto_validates_width_and_height(self):

        with pytest.raises(
            ValueError,
            match=(
                "Maintenance passage width cannot be "
                "greater than or equal to roof height"
            ),
        ):

            self._constraints(
                maintenance_passage_required=True,
                maintenance_passage_width_m=6.50,
                maintenance_passage_orientation="auto",
                roof_width_m=10.0,
                roof_height_m=6.50,
            )

    # ==================================================
    # Disabled passage does not require roof geometry
    # ==================================================

    def test_disabled_passage_does_not_require_roof_geometry(self):

        constraints = self._constraints(
            maintenance_passage_required=False,
            roof_width_m=None,
            roof_height_m=None,
        )

        assert (
            constraints.maintenance_passage_orientations
            == ()
        )

    