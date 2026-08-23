from helios.solar.installation_candidate import (
    InstallationCandidate
)
from helios.solar.installation_constraints import (
    InstallationConstraints
)

from helios.solar.installation_layout import InstallationLayout


class InstallationOptimizer:

    def __init__(
        self,
        constraints: InstallationConstraints
    ):

        if not isinstance(
            constraints,
            InstallationConstraints
        ):
            raise TypeError(
                "constraints must be an InstallationConstraints."
            )

        self.constraints = constraints

    def generate_candidates(
        self
    ) -> list[InstallationCandidate]:

        maximum_panels = (
            self.constraints.effective_max_panels
        )

        minimum_panels = (
            self.constraints.min_panels
        )

        if maximum_panels < minimum_panels:
            return []

        return [
            InstallationCandidate(
                panel_count=panel_count,
                panel_power_wp=(
                    self.constraints.panel_power_wp
                ),
                panel_area_m2=(
                    self.constraints.panel_area_m2
                ),
            )
            for panel_count in range(
                minimum_panels,
                maximum_panels + 1
            )
        ]

    def generate_layouts(
        self,
        panel_count: int,
        orientation: str | None = None,
        walkway_width_m: float = 0.0,
        walkway_position: str | None = None,
    ) -> list[InstallationLayout]:

        if panel_count < 1:
            raise ValueError(
                "Panel count must be at least one."
            )

        if panel_count < self.constraints.min_panels:
            return []

        if panel_count > self.constraints.effective_max_panels:
            return []

        if orientation is not None and orientation not in (
            "vertical",
            "horizontal",
        ):
            raise ValueError(
                "Orientation must be 'vertical' or 'horizontal'."
            )

        if walkway_width_m < 0:
            raise ValueError(
                "Walkway width cannot be negative."
            )

        if (
            walkway_position is not None
            and walkway_position not in (
                "vertical",
                "horizontal",
            )
        ):
            raise ValueError(
                "Walkway position must be 'vertical', "
                "'horizontal' or None."
            )

        layouts = []

        panel_width = self.constraints.panel_width_m
        panel_height = self.constraints.panel_height_m

        for rows in range(1, panel_count + 1):

            if panel_count % rows != 0:
                continue

            columns = panel_count // rows

            orientations = (
                [orientation]
                if orientation is not None
                else ["vertical", "horizontal"]
            )

            for current_orientation in orientations:

                layout = InstallationLayout(
                    rows=rows,
                    columns=columns,
                    panel_width_m=panel_width,
                    panel_height_m=panel_height,
                    orientation=current_orientation,
                    walkway_width_m=walkway_width_m,
                    walkway_position=walkway_position,
                )

                if (
                    layout.occupied_area_m2
                    > self.constraints.available_area_m2
                ):
                    continue

                # Surface area is only the first filter. When the actual
                # rectangular roof dimensions are known, the complete
                # layout must also fit within width and height.
                if (
                    self.constraints.roof_width_m is not None
                    and layout.occupied_width_m
                    > self.constraints.roof_width_m
                ):
                    continue

                if (
                    self.constraints.roof_height_m is not None
                    and layout.occupied_height_m
                    > self.constraints.roof_height_m
                ):
                    continue

                layouts.append(layout)

        return layouts