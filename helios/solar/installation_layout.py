from dataclasses import dataclass


@dataclass(frozen=True)
class InstallationLayout:

    rows: int
    columns: int

    panel_width_m: float
    panel_height_m: float

    orientation: str = "vertical"

    walkway_width_m: float = 0.0
    walkway_position: str | None = None

    def __post_init__(self):

        if self.rows < 1:

            raise ValueError(
                "Rows must be at least one."
            )

        if self.columns < 1:

            raise ValueError(
                "Columns must be at least one."
            )

        if self.panel_width_m <= 0:

            raise ValueError(
                "Panel width must be greater than zero."
            )

        if self.panel_height_m <= 0:

            raise ValueError(
                "Panel height must be greater than zero."
            )

        if self.orientation not in (
            "vertical",
            "horizontal",
        ):

            raise ValueError(
                "Orientation must be 'vertical' "
                "or 'horizontal'."
            )

        if self.walkway_width_m < 0:

            raise ValueError(
                "Walkway width cannot be negative."
            )

        if (
            self.walkway_position is not None
            and self.walkway_position not in (
                "vertical",
                "horizontal",
            )
        ):

            raise ValueError(
                "Walkway position must be 'vertical', "
                "'horizontal' or None."
            )

        if (
            self.walkway_position is None
            and self.walkway_width_m != 0
        ):

            raise ValueError(
                "Walkway position is required "
                "when walkway width is greater than zero."
            )

        if (
            self.walkway_position is not None
            and self.walkway_width_m == 0
        ):

            raise ValueError(
                "Walkway width must be greater than zero "
                "when walkway position is specified."
            )

    @property
    def panel_count(self) -> int:

        return (
            self.rows
            * self.columns
        )

    @property
    def oriented_panel_width_m(self) -> float:

        if self.orientation == "vertical":

            return self.panel_width_m

        return self.panel_height_m

    @property
    def oriented_panel_height_m(self) -> float:

        if self.orientation == "vertical":

            return self.panel_height_m

        return self.panel_width_m

    @property
    def panels_width_m(self) -> float:

        return (
            self.columns
            * self.oriented_panel_width_m
        )

    @property
    def panels_height_m(self) -> float:

        return (
            self.rows
            * self.oriented_panel_height_m
        )

    @property
    def occupied_width_m(self) -> float:

        width = self.panels_width_m

        if self.walkway_position == "vertical":

            width += self.walkway_width_m

        return width

    @property
    def occupied_height_m(self) -> float:

        height = self.panels_height_m

        if self.walkway_position == "horizontal":

            height += self.walkway_width_m

        return height

    @property
    def panel_area_m2(self) -> float:

        return (
            self.panel_width_m
            * self.panel_height_m
        )

    @property
    def panels_area_m2(self) -> float:

        return (
            self.panel_count
            * self.panel_area_m2
        )

    @property
    def occupied_area_m2(self) -> float:

        return (
            self.occupied_width_m
            * self.occupied_height_m
        )

    @property
    def walkway_area_m2(self) -> float:

        return (
            self.occupied_area_m2
            - self.panels_area_m2
        )