from dataclasses import dataclass

from helios.solar.installation_evaluation import (
    InstallationEvaluation,
)


@dataclass(frozen=True)
class SolarSizingResult:

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
    def self_sufficiency_percent(self) -> float:

        if self.annual_consumption_kwh == 0:
            return 0.0

        return min(
            self.annual_production_kwh
            / self.annual_consumption_kwh
            * 100,
            100.0,
        )

    @property
    def production_coverage_percent(self) -> float:

        if self.annual_production_kwh == 0:
            return 0.0

        return min(
            self.annual_consumption_kwh
            / self.annual_production_kwh
            * 100,
            100.0,
        )

    @property
    def annual_surplus_kwh(self) -> float:

        return max(
            self.annual_production_kwh
            - self.annual_consumption_kwh,
            0.0,
        )

    @property
    def annual_deficit_kwh(self) -> float:

        return max(
            self.annual_consumption_kwh
            - self.annual_production_kwh,
            0.0,
        )

class SolarInstallationSizing:

    def recommend(
        self,
        evaluations: list[InstallationEvaluation],
        annual_consumption_kwh: float,
        annual_productions_kwh: dict[int, float],
    ) -> SolarSizingResult:

        # ==================================================
        # Annual consumption validation
        # ==================================================

        if (
            isinstance(annual_consumption_kwh, bool)
            or not isinstance(
                annual_consumption_kwh,
                (int, float),
            )
        ):
            raise TypeError(
                "Annual consumption must be a number."
            )

        if annual_consumption_kwh <= 0:
            raise ValueError(
                "Annual consumption must be greater than zero."
            )

        # ==================================================
        # Evaluations validation
        # ==================================================

        if not evaluations:
            raise ValueError(
                "At least one installation evaluation is required."
            )

        if not all(
            isinstance(
                evaluation,
                InstallationEvaluation,
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

        # ==================================================
        # Production mapping validation
        # ==================================================

        for evaluation in evaluations:

            panel_count = evaluation.panel_count

            if panel_count not in annual_productions_kwh:
                raise ValueError(
                    "Missing annual production for "
                    f"{panel_count} panels."
                )

            production = annual_productions_kwh[
                panel_count
            ]

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
                    "Annual production must be greater "
                    "than or equal to zero."
                )

        # ==================================================
        # First configuration capable of covering
        # the annual consumption.
        # ==================================================

        covering = [
            evaluation
            for evaluation in evaluations
            if annual_productions_kwh[
                evaluation.panel_count
            ] >= annual_consumption_kwh
        ]

        if covering:

            selected = min(
                covering,
                key=lambda evaluation: (
                    evaluation.panel_count,
                    evaluation.occupied_area_m2,
                ),
            )

        else:

            # If no configuration covers the consumption,
            # select the configuration with the highest
            # annual production.
            selected = max(
                evaluations,
                key=lambda evaluation: (
                    annual_productions_kwh[
                        evaluation.panel_count
                    ],
                    -evaluation.occupied_area_m2,
                ),
            )

        return SolarSizingResult(
            evaluation=selected,
            annual_consumption_kwh=annual_consumption_kwh,
            annual_production_kwh=annual_productions_kwh[
                selected.panel_count
            ],
        )