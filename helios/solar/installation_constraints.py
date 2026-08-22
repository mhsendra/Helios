from dataclasses import dataclass


@dataclass(frozen=True)
class InstallationConstraints:

    available_area_m2: float

    panel_width_m: float
    panel_height_m: float
    panel_power_wp: float

    min_panels: int = 1
    max_panels: int | None = None

    # ==================================================
    # Maintenance passage
    # ==================================================

    maintenance_passage_required: bool = False

    maintenance_passage_width_m: float = 0.45

    maintenance_passage_orientation: str = "auto"

    # Optional roof geometry.
    # Required when a maintenance passage is enabled.
    roof_width_m: float | None = None
    roof_height_m: float | None = None

    def __post_init__(self):

        # ==================================================
        # Basic validation
        # ==================================================

        if self.available_area_m2 <= 0:

            raise ValueError(
                "Available area must be greater than zero."
            )

        if self.panel_width_m <= 0:

            raise ValueError(
                "Panel width must be greater than zero."
            )

        if self.panel_height_m <= 0:

            raise ValueError(
                "Panel height must be greater than zero."
            )

        if self.panel_power_wp <= 0:

            raise ValueError(
                "Panel power must be greater than zero."
            )

        if self.min_panels < 1:

            raise ValueError(
                "Minimum number of panels must be at least one."
            )

        if (
            self.max_panels is not None
            and self.max_panels < self.min_panels
        ):

            raise ValueError(
                "Maximum number of panels cannot be less "
                "than minimum number of panels."
            )

        # ==================================================
        # Maintenance passage validation
        # ==================================================

        if self.maintenance_passage_width_m <= 0:

            raise ValueError(
                "Maintenance passage width must be "
                "greater than zero."
            )

        valid_orientations = {
            "horizontal",
            "vertical",
            "auto",
        }

        if (
            self.maintenance_passage_orientation
            not in valid_orientations
        ):

            raise ValueError(
                "Maintenance passage orientation must be "
                "'horizontal', 'vertical' or 'auto'."
            )

        if self.maintenance_passage_required:

            if self.roof_width_m is None:

                raise ValueError(
                    "Roof width is required when a "
                    "maintenance passage is enabled."
                )

            if self.roof_height_m is None:

                raise ValueError(
                    "Roof height is required when a "
                    "maintenance passage is enabled."
                )

            if self.roof_width_m <= 0:

                raise ValueError(
                    "Roof width must be greater than zero."
                )

            if self.roof_height_m <= 0:

                raise ValueError(
                    "Roof height must be greater than zero."
                )

            if (
                self.maintenance_passage_width_m
                >= self.roof_width_m
                and self.maintenance_passage_orientation
                in {"horizontal", "auto"}
            ):

                raise ValueError(
                    "Maintenance passage width cannot be "
                    "greater than or equal to roof width."
                )

            if (
                self.maintenance_passage_width_m
                >= self.roof_height_m
                and self.maintenance_passage_orientation
                in {"vertical", "auto"}
            ):

                raise ValueError(
                    "Maintenance passage width cannot be "
                    "greater than or equal to roof height."
                )

    # ==================================================
    # Panel properties
    # ==================================================

    @property
    def panel_area_m2(self) -> float:

        return (
            self.panel_width_m
            * self.panel_height_m
        )

    @property
    def maximum_panels_by_area(self) -> int:

        return int(
            self.available_area_m2
            // self.panel_area_m2
        )

    @property
    def effective_max_panels(self) -> int:

        maximum_by_area = (
            self.maximum_panels_by_area
        )

        if self.max_panels is None:

            return maximum_by_area

        return min(
            maximum_by_area,
            self.max_panels
        )

    # ==================================================
    # Maintenance passage properties
    # ==================================================

    @property
    def maintenance_passage_area_m2(self) -> float | None:
        """
        Area reserved for the maintenance passage.

        Returns None when the passage is disabled.
        """

        if not self.maintenance_passage_required:

            return None

        if (
            self.roof_width_m is None
            or self.roof_height_m is None
        ):

            return None

        if self.maintenance_passage_orientation == "vertical":

            return (
                self.maintenance_passage_width_m
                * self.roof_height_m
            )

        if self.maintenance_passage_orientation == "horizontal":

            return (
                self.maintenance_passage_width_m
                * self.roof_width_m
            )

        # "auto" deliberately does not choose an orientation.
        #
        # The optimizer will evaluate both possibilities.
        return None

    @property
    def maintenance_passage_orientations(self) -> tuple[str, ...]:
        """
        Returns the orientations that the optimizer must evaluate.
        """

        if not self.maintenance_passage_required:

            return ()

        if self.maintenance_passage_orientation == "auto":

            return (
                "horizontal",
                "vertical",
            )

        return (
            self.maintenance_passage_orientation,
        )