import pytest

from helios.solar.installation_layout import (
    InstallationLayout,
)


class TestInstallationLayout:

    # ==================================================
    # Helpers
    # ==================================================

    def _layout(
        self,
        rows=2,
        columns=3,
        panel_width_m=1.134,
        panel_height_m=2.273,
        orientation="vertical",
        walkway_width_m=0.0,
        walkway_position=None,
    ):

        return InstallationLayout(
            rows=rows,
            columns=columns,
            panel_width_m=panel_width_m,
            panel_height_m=panel_height_m,
            orientation=orientation,
            walkway_width_m=walkway_width_m,
            walkway_position=walkway_position,
        )

    # ==================================================
    # Construction
    # ==================================================

    def test_creates_layout(self):

        layout = self._layout()

        assert isinstance(
            layout,
            InstallationLayout,
        )

    def test_default_orientation_is_vertical(self):

        layout = self._layout()

        assert layout.orientation == "vertical"

    def test_default_walkway_width_is_zero(self):

        layout = self._layout()

        assert layout.walkway_width_m == pytest.approx(0.0)

    def test_default_walkway_position_is_none(self):

        layout = self._layout()

        assert layout.walkway_position is None

    # ==================================================
    # Input validation
    # ==================================================

    @pytest.mark.parametrize(
        "rows",
        [
            0,
            -1,
            -10,
        ],
    )
    def test_rejects_invalid_rows(self, rows):

        with pytest.raises(
            ValueError,
            match="Rows must be at least one.",
        ):

            self._layout(
                rows=rows
            )

    @pytest.mark.parametrize(
        "columns",
        [
            0,
            -1,
            -10,
        ],
    )
    def test_rejects_invalid_columns(self, columns):

        with pytest.raises(
            ValueError,
            match="Columns must be at least one.",
        ):

            self._layout(
                columns=columns
            )

    @pytest.mark.parametrize(
        "width",
        [
            0.0,
            -0.001,
            -1.0,
        ],
    )
    def test_rejects_invalid_panel_width(self, width):

        with pytest.raises(
            ValueError,
            match="Panel width must be greater than zero.",
        ):

            self._layout(
                panel_width_m=width
            )

    @pytest.mark.parametrize(
        "height",
        [
            0.0,
            -0.001,
            -1.0,
        ],
    )
    def test_rejects_invalid_panel_height(self, height):

        with pytest.raises(
            ValueError,
            match="Panel height must be greater than zero.",
        ):

            self._layout(
                panel_height_m=height
            )

    @pytest.mark.parametrize(
        "orientation",
        [
            "",
            "diagonal",
            "Vertical",
            "HORIZONTAL",
            "rotated",
            None,
        ],
    )
    def test_rejects_invalid_orientation(
        self,
        orientation,
    ):

        with pytest.raises(
            ValueError,
            match="Orientation must be 'vertical' or 'horizontal'.",
        ):

            self._layout(
                orientation=orientation
            )

    @pytest.mark.parametrize(
        "walkway_width",
        [
            -0.001,
            -1.0,
        ],
    )
    def test_rejects_negative_walkway_width(
        self,
        walkway_width,
    ):

        with pytest.raises(
            ValueError,
            match="Walkway width cannot be negative.",
        ):

            self._layout(
                walkway_width_m=walkway_width
            )

    @pytest.mark.parametrize(
        "position",
        [
            "",
            "diagonal",
            "Vertical",
            "HORIZONTAL",
            "invalid",
        ],
    )
    def test_rejects_invalid_walkway_position(
        self,
        position,
    ):

        with pytest.raises(
            ValueError,
            match=(
                "Walkway position must be "
                "'vertical', 'horizontal' or None."
            ),
        ):

            self._layout(
                walkway_width_m=1.0,
                walkway_position=position,
            )

    def test_rejects_walkway_width_without_position(self):

        with pytest.raises(
            ValueError,
            match=(
                "Walkway position is required "
                "when walkway width is greater than zero."
            ),
        ):

            self._layout(
                walkway_width_m=1.0,
                walkway_position=None,
            )

    @pytest.mark.parametrize(
        "position",
        [
            "vertical",
            "horizontal",
        ],
    )
    def test_rejects_walkway_position_without_width(
        self,
        position,
    ):

        with pytest.raises(
            ValueError,
            match=(
                "Walkway width must be greater than zero "
                "when walkway position is specified."
            ),
        ):

            self._layout(
                walkway_width_m=0.0,
                walkway_position=position,
            )

    # ==================================================
    # Panel count
    # ==================================================

    @pytest.mark.parametrize(
        "rows,columns,expected",
        [
            (1, 1, 1),
            (1, 5, 5),
            (5, 1, 5),
            (2, 3, 6),
            (4, 7, 28),
        ],
    )
    def test_panel_count(
        self,
        rows,
        columns,
        expected,
    ):

        layout = self._layout(
            rows=rows,
            columns=columns,
        )

        assert layout.panel_count == expected

    # ==================================================
    # Orientation
    # ==================================================

    def test_vertical_orientation_preserves_dimensions(self):

        layout = self._layout(
            panel_width_m=1.134,
            panel_height_m=2.273,
            orientation="vertical",
        )

        assert layout.oriented_panel_width_m == pytest.approx(
            1.134
        )

        assert layout.oriented_panel_height_m == pytest.approx(
            2.273
        )

    def test_horizontal_orientation_swaps_dimensions(self):

        layout = self._layout(
            panel_width_m=1.134,
            panel_height_m=2.273,
            orientation="horizontal",
        )

        assert layout.oriented_panel_width_m == pytest.approx(
            2.273
        )

        assert layout.oriented_panel_height_m == pytest.approx(
            1.134
        )

    # ==================================================
    # Panel dimensions
    # ==================================================

    def test_panels_width_vertical(self):

        layout = self._layout(
            rows=2,
            columns=3,
            panel_width_m=1.134,
            panel_height_m=2.273,
            orientation="vertical",
        )

        assert layout.panels_width_m == pytest.approx(
            3.402
        )

    def test_panels_height_vertical(self):

        layout = self._layout(
            rows=2,
            columns=3,
            panel_width_m=1.134,
            panel_height_m=2.273,
            orientation="vertical",
        )

        assert layout.panels_height_m == pytest.approx(
            4.546
        )

    def test_panels_width_horizontal(self):

        layout = self._layout(
            rows=2,
            columns=3,
            panel_width_m=1.134,
            panel_height_m=2.273,
            orientation="horizontal",
        )

        assert layout.panels_width_m == pytest.approx(
            6.819
        )

    def test_panels_height_horizontal(self):

        layout = self._layout(
            rows=2,
            columns=3,
            panel_width_m=1.134,
            panel_height_m=2.273,
            orientation="horizontal",
        )

        assert layout.panels_height_m == pytest.approx(
            2.268
        )

    # ==================================================
    # Occupied dimensions without walkway
    # ==================================================

    def test_occupied_width_without_walkway(self):

        layout = self._layout(
            rows=2,
            columns=3,
        )

        assert layout.occupied_width_m == pytest.approx(
            layout.panels_width_m
        )

    def test_occupied_height_without_walkway(self):

        layout = self._layout(
            rows=2,
            columns=3,
        )

        assert layout.occupied_height_m == pytest.approx(
            layout.panels_height_m
        )

    # ==================================================
    # Vertical walkway
    # ==================================================

    def test_vertical_walkway_increases_width_only(self):

        layout = self._layout(
            rows=2,
            columns=3,
            walkway_width_m=1.0,
            walkway_position="vertical",
        )

        assert layout.occupied_width_m == pytest.approx(
            layout.panels_width_m + 1.0
        )

        assert layout.occupied_height_m == pytest.approx(
            layout.panels_height_m
        )

    # ==================================================
    # Horizontal walkway
    # ==================================================

    def test_horizontal_walkway_increases_height_only(self):

        layout = self._layout(
            rows=2,
            columns=3,
            walkway_width_m=1.0,
            walkway_position="horizontal",
        )

        assert layout.occupied_width_m == pytest.approx(
            layout.panels_width_m
        )

        assert layout.occupied_height_m == pytest.approx(
            layout.panels_height_m + 1.0
        )

    # ==================================================
    # Panel area
    # ==================================================

    def test_panel_area(self):

        layout = self._layout(
            panel_width_m=1.134,
            panel_height_m=2.273,
        )

        assert layout.panel_area_m2 == pytest.approx(
            1.134 * 2.273
        )

    def test_panel_area_is_independent_of_orientation(self):

        vertical = self._layout(
            orientation="vertical"
        )

        horizontal = self._layout(
            orientation="horizontal"
        )

        assert horizontal.panel_area_m2 == pytest.approx(
            vertical.panel_area_m2
        )

    def test_panels_area(self):

        layout = self._layout(
            rows=2,
            columns=3,
            panel_width_m=1.134,
            panel_height_m=2.273,
        )

        expected = (
            6
            * 1.134
            * 2.273
        )

        assert layout.panels_area_m2 == pytest.approx(
            expected
        )

    # ==================================================
    # Occupied area
    # ==================================================

    def test_occupied_area_without_walkway(self):

        layout = self._layout(
            rows=2,
            columns=3,
        )

        assert layout.occupied_area_m2 == pytest.approx(
            layout.panels_area_m2
        )

    def test_occupied_area_with_vertical_walkway(self):

        layout = self._layout(
            rows=2,
            columns=3,
            walkway_width_m=1.0,
            walkway_position="vertical",
        )

        expected = (
            layout.occupied_width_m
            * layout.occupied_height_m
        )

        assert layout.occupied_area_m2 == pytest.approx(
            expected
        )

    def test_occupied_area_with_horizontal_walkway(self):

        layout = self._layout(
            rows=2,
            columns=3,
            walkway_width_m=1.0,
            walkway_position="horizontal",
        )

        expected = (
            layout.occupied_width_m
            * layout.occupied_height_m
        )

        assert layout.occupied_area_m2 == pytest.approx(
            expected
        )

    # ==================================================
    # Walkway area
    # ==================================================

    def test_walkway_area_is_zero_without_walkway(self):

        layout = self._layout()

        assert layout.walkway_area_m2 == pytest.approx(
            0.0
        )

    def test_vertical_walkway_area(self):

        layout = self._layout(
            rows=2,
            columns=3,
            walkway_width_m=1.0,
            walkway_position="vertical",
        )

        expected = (
            layout.occupied_area_m2
            - layout.panels_area_m2
        )

        assert layout.walkway_area_m2 == pytest.approx(
            expected
        )

    def test_horizontal_walkway_area(self):

        layout = self._layout(
            rows=2,
            columns=3,
            walkway_width_m=1.0,
            walkway_position="horizontal",
        )

        expected = (
            layout.occupied_area_m2
            - layout.panels_area_m2
        )

        assert layout.walkway_area_m2 == pytest.approx(
            expected
        )

    def test_area_is_conserved(self):

        layout = self._layout(
            rows=2,
            columns=3,
            walkway_width_m=0.8,
            walkway_position="vertical",
        )

        assert layout.panels_area_m2 + layout.walkway_area_m2 == pytest.approx(
            layout.occupied_area_m2
        )

    # ==================================================
    # Edge cases
    # ==================================================

    def test_single_panel_layout(self):

        layout = self._layout(
            rows=1,
            columns=1,
        )

        assert layout.panel_count == 1

        assert layout.panels_width_m == pytest.approx(
            1.134
        )

        assert layout.panels_height_m == pytest.approx(
            2.273
        )

        assert layout.occupied_area_m2 == pytest.approx(
            layout.panel_area_m2
        )

    def test_single_row_layout(self):

        layout = self._layout(
            rows=1,
            columns=4,
        )

        assert layout.panel_count == 4

        assert layout.panels_height_m == pytest.approx(
            2.273
        )

    def test_single_column_layout(self):

        layout = self._layout(
            rows=4,
            columns=1,
        )

        assert layout.panel_count == 4

        assert layout.panels_width_m == pytest.approx(
            1.134
        )

    def test_zero_width_walkway_is_valid_without_position(self):

        layout = self._layout(
            walkway_width_m=0.0,
            walkway_position=None,
        )

        assert layout.walkway_area_m2 == pytest.approx(
            0.0
        )

    # ==================================================
    # Immutability
    # ==================================================

    def test_layout_is_immutable(self):

        layout = self._layout()

        with pytest.raises(
            AttributeError
        ):

            layout.rows = 5

    def test_orientation_is_immutable(self):

        layout = self._layout()

        with pytest.raises(
            AttributeError
        ):

            layout.orientation = "horizontal"

    def test_walkway_is_immutable(self):

        layout = self._layout()

        with pytest.raises(
            AttributeError
        ):

            layout.walkway_width_m = 1.0

    # ==================================================
    # Determinism
    # ==================================================

    def test_calculations_are_deterministic(self):

        layout = self._layout(
            rows=3,
            columns=5,
            walkway_width_m=0.75,
            walkway_position="vertical",
        )

        first = (
            layout.panel_count,
            layout.panels_width_m,
            layout.panels_height_m,
            layout.occupied_width_m,
            layout.occupied_height_m,
            layout.panel_area_m2,
            layout.panels_area_m2,
            layout.occupied_area_m2,
            layout.walkway_area_m2,
        )

        second = (
            layout.panel_count,
            layout.panels_width_m,
            layout.panels_height_m,
            layout.occupied_width_m,
            layout.occupied_height_m,
            layout.panel_area_m2,
            layout.panels_area_m2,
            layout.occupied_area_m2,
            layout.walkway_area_m2,
        )

        assert first == second