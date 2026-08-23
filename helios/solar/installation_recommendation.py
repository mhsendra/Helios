from dataclasses import dataclass

from helios.solar.installation_evaluation import (
    InstallationEvaluation
)


@dataclass(frozen=True)
class InstallationRecommendation:

    evaluation: InstallationEvaluation
    annual_consumption_kwh: float
    annual_production_kwh: float

    @property
    def panel_count(self) -> int:

        return self.evaluation.panel_count

    @property
    def installed_power_kwp(self) -> float:

        return self.evaluation.installed_power_kwp

    @property
    def occupied_area_m2(self) -> float:

        return self.evaluation.occupied_area_m2

    @property
    def remaining_area_m2(self) -> float:

        return self.evaluation.remaining_area_m2

    @property
    def area_utilization_percent(self) -> float:

        return self.evaluation.area_utilization_percent

    # ==================================================
    # Physical layout
    # ==================================================

    @property
    def layout(self):

        return self.evaluation.layout

    @property
    def rows(self) -> int | None:

        if self.layout is None:
            return None

        return self.layout.rows

    @property
    def columns(self) -> int | None:

        if self.layout is None:
            return None

        return self.layout.columns

    @property
    def orientation(self) -> str | None:

        if self.layout is None:
            return None

        return self.layout.orientation

    @property
    def occupied_width_m(self) -> float | None:

        if self.layout is None:
            return None

        return self.layout.occupied_width_m

    @property
    def occupied_height_m(self) -> float | None:

        if self.layout is None:
            return None

        return self.layout.occupied_height_m

    @property
    def walkway_width_m(self) -> float | None:

        if self.layout is None:
            return None

        return self.layout.walkway_width_m

    @property
    def walkway_position(self) -> str | None:

        if self.layout is None:
            return None

        return self.layout.walkway_position

    # ==================================================
    # Energy information
    # ==================================================

    @property
    def self_consumption_kwh(self) -> float:

        return min(
            self.annual_consumption_kwh,
            self.annual_production_kwh,
        )

    @property
    def self_sufficiency_percent(self) -> float:

        if self.annual_consumption_kwh <= 0:
            return 0.0

        return min(
            self.annual_production_kwh
            / self.annual_consumption_kwh
            * 100,
            100.0,
        )

    @property
    def production_coverage_percent(self) -> float:

        if self.annual_production_kwh <= 0:
            return 0.0

        return min(
            self.annual_consumption_kwh
            / self.annual_production_kwh
            * 100,
            100.0,
        )

    @property
    def energy_surplus_kwh(self) -> float:

        return max(
            self.annual_production_kwh
            - self.annual_consumption_kwh,
            0.0,
        )

    @property
    def energy_deficit_kwh(self) -> float:

        return max(
            self.annual_consumption_kwh
            - self.annual_production_kwh,
            0.0,
        )


class InstallationRecommender:

    def recommend(
        self,
        evaluations: list[InstallationEvaluation],
        annual_consumption_kwh: float,
        annual_productions_kwh: dict[int, float],
    ) -> InstallationRecommendation:

        if not evaluations:

            raise ValueError(
                "At least one installation evaluation "
                "is required."
            )

        if not all(
            isinstance(
                evaluation,
                InstallationEvaluation
            )
            for evaluation in evaluations
        ):

            raise TypeError(
                "evaluations must contain only "
                "InstallationEvaluation instances."
            )

        panel_counts = [
            evaluation.panel_count
            for evaluation in evaluations
        ]

        if len(panel_counts) != len(set(panel_counts)):
            raise ValueError(
                "Duplicate panel count found in evaluations."
            )

        if (
            isinstance(annual_consumption_kwh, bool)
            or not isinstance(
                annual_consumption_kwh,
                (int, float),
            )
        ):
            raise TypeError(
                "annual_consumption_kwh must be a number."
            )

        if annual_consumption_kwh < 0:
            raise ValueError(
                "annual_consumption_kwh must be "
                "greater than or equal to zero."
            )

        if not isinstance(
            annual_productions_kwh,
            dict
        ):

            raise TypeError(
                "annual_productions_kwh must be a dictionary."
            )

        for evaluation in evaluations:

            if evaluation.panel_count not in (
                annual_productions_kwh
            ):

                raise ValueError(
                    "Missing annual production for "
                    f"{evaluation.panel_count} panels."
                )

        for evaluation in evaluations:

            panel_count = evaluation.panel_count

            production = annual_productions_kwh[panel_count]

            if (
                isinstance(production, bool)
                or not isinstance(
                    production,
                    (int, float),
                )
            ):
                raise TypeError(
                    "Annual production must be a number."
                )

            if production < 0:
                raise ValueError(
                    "Annual production must be "
                    "greater than or equal to zero."
                )

        # --------------------------------------------------
        # Candidates covering annual consumption
        # --------------------------------------------------

        covering = [
            evaluation
            for evaluation in evaluations
            if annual_productions_kwh[
                evaluation.panel_count
            ] >= annual_consumption_kwh
        ]

        if covering:

            # Among configurations that cover consumption,
            # choose the smallest one.
            #
            # If two configurations have the same number
            # of panels, prefer the one occupying less area.
            best = min(
                covering,
                key=lambda evaluation: (
                    evaluation.panel_count,
                    evaluation.occupied_area_m2,
                )
            )

        else:

            # No configuration covers consumption.
            # Choose the one producing the most energy.
            #
            # In case of equal production, prefer the
            # smaller occupied area.
            best = max(
                evaluations,
                key=lambda evaluation: (
                    annual_productions_kwh[
                        evaluation.panel_count
                    ],
                    -evaluation.occupied_area_m2,
                )
            )

        return InstallationRecommendation(
            evaluation=best,
            annual_consumption_kwh=annual_consumption_kwh,
            annual_production_kwh=annual_productions_kwh[
                best.panel_count
            ],
        )