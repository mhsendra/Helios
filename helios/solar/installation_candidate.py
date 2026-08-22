from dataclasses import dataclass


@dataclass(frozen=True)
class InstallationCandidate:

    panel_count: int
    panel_power_wp: float
    panel_area_m2: float

    def __post_init__(self):

        # ==================================================
        # panel_count
        # ==================================================

        if (
            not isinstance(self.panel_count, int)
            or isinstance(self.panel_count, bool)
        ):

            raise TypeError(
                "Panel count must be an integer."
            )

        if self.panel_count < 1:

            raise ValueError(
                "Panel count must be at least one."
            )

        # ==================================================
        # panel_power_wp
        # ==================================================

        if (
            not isinstance(
                self.panel_power_wp,
                (int, float),
            )
            or isinstance(
                self.panel_power_wp,
                bool,
            )
        ):

            raise TypeError(
                "Panel power must be a number."
            )

        if self.panel_power_wp <= 0:

            raise ValueError(
                "Panel power must be greater than zero."
            )

        # ==================================================
        # panel_area_m2
        # ==================================================

        if (
            not isinstance(
                self.panel_area_m2,
                (int, float),
            )
            or isinstance(
                self.panel_area_m2,
                bool,
            )
        ):

            raise TypeError(
                "Panel area must be a number."
            )

        if self.panel_area_m2 <= 0:

            raise ValueError(
                "Panel area must be greater than zero."
            )

    @property
    def installed_power_kwp(self) -> float:

        return (
            self.panel_count
            * self.panel_power_wp
            / 1000
        )

    @property
    def occupied_area_m2(self) -> float:

        return (
            self.panel_count
            * self.panel_area_m2
        )