from dataclasses import dataclass

from helios.solar.installation_candidate import (
    InstallationCandidate
)

from helios.solar.installation_constraints import (
    InstallationConstraints
)

from helios.solar.installation_layout import (
    InstallationLayout
)

@dataclass(frozen=True)
class InstallationEvaluation:

    candidate: InstallationCandidate
    available_area_m2: float
    layout: InstallationLayout | None = None

    @property
    def installed_power_kwp(self) -> float:

        return self.candidate.installed_power_kwp

    @property
    def occupied_area_m2(self) -> float:

        return self.candidate.occupied_area_m2

    @property
    def remaining_area_m2(self) -> float:

        return (
            self.available_area_m2
            - self.occupied_area_m2
        )

    @property
    def area_utilization_percent(self) -> float:

        return (
            self.occupied_area_m2
            / self.available_area_m2
            * 100
        )

    @property
    def panel_count(self) -> int:

        return self.candidate.panel_count

    @property
    def is_within_area(self) -> bool:

        return (
            self.occupied_area_m2
            <= self.available_area_m2
        )


class InstallationEvaluator:

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

    def evaluate(
        self,
        candidate: InstallationCandidate
    ) -> InstallationEvaluation:

        if not isinstance(
            candidate,
            InstallationCandidate
        ):
            raise TypeError(
                "candidate must be an InstallationCandidate."
            )

        if not self._is_valid_candidate(candidate):

            raise ValueError(
                "Candidate exceeds installation constraints."
            )

        return InstallationEvaluation(
            candidate=candidate,
            available_area_m2=(
                self.constraints.available_area_m2
            ),
        )

    def _is_valid_candidate(
        self,
        candidate: InstallationCandidate
    ) -> bool:

        if (
            candidate.panel_count
            < self.constraints.min_panels
        ):
            return False

        if (
            self.constraints.max_panels is not None
            and candidate.panel_count
            > self.constraints.max_panels
        ):
            return False

        if (
            candidate.occupied_area_m2
            > self.constraints.available_area_m2
        ):
            return False

        return True

    def evaluate_layout(
        self,
        candidate: InstallationCandidate,
        layout: InstallationLayout
    ) -> InstallationEvaluation:

        if not isinstance(
            candidate,
            InstallationCandidate
        ):
            raise TypeError(
                "Candidate must be an InstallationCandidate."
            )

        if not isinstance(
            layout,
            InstallationLayout
        ):
            raise TypeError(
                "Layout must be an InstallationLayout."
            )

        if (
            layout.panel_count
            != candidate.panel_count
        ):
            raise ValueError(
                "Layout panel count must match "
                "candidate panel count."
            )

        if not self._is_valid_candidate(candidate):

            raise ValueError(
                "Candidate exceeds installation constraints."
            )

        return InstallationEvaluation(
            candidate=candidate,
            available_area_m2=(
                self.constraints.available_area_m2
            ),
            layout=layout,
        )