import pandas as pd

from dataclasses import dataclass

from helios.solar.installation_evaluation import (
    InstallationEvaluation
)

from helios.core.consumption_scenario import ConsumptionScenario
from helios.solar.production_profile import SolarProductionProfile

@dataclass(frozen=True)
class InstallationRecommendation:

    evaluation: InstallationEvaluation
    annual_consumption_kwh: float
    annual_production_kwh: float
    consumption_scenario: ConsumptionScenario | None = None
    production_profile: SolarProductionProfile | None = None

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

        if (
            self.consumption_scenario is not None
            and self.production_profile is not None
        ):
            consumption = self.consumption_scenario.hourly_consumption

            production = self.production_profile.hourly_production

            production_lookup = production.copy()
            production_lookup.index = (
                production_lookup.index.strftime("%m-%d-%H")
            )

            profile_key = consumption.index.strftime("%m-%d-%H")

            aligned_production = (
                pd.Series(profile_key, index=consumption.index)
                .map(production_lookup)
                .fillna(0.0)
            )

            return float(
                pd.concat(
                    [consumption, aligned_production],
                    axis=1,
                ).min(axis=1).sum()
            )

        return min(
            self.annual_consumption_kwh,
            self.annual_production_kwh,
        )

    @property
    def self_sufficiency_percent(self) -> float:

        if self.annual_consumption_kwh <= 0:
            return 0.0

        return min(
            self.self_consumption_kwh
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
        *,
        consumption_scenario: ConsumptionScenario | None = None,
        production_profiles: dict[int, SolarProductionProfile] | None = None,
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

        if consumption_scenario is not None and not isinstance(
            consumption_scenario,
            ConsumptionScenario,
        ):
            raise TypeError(
                "consumption_scenario must be a ConsumptionScenario."
            )

        if production_profiles is not None and not isinstance(
            production_profiles,
            dict,
        ):
            raise TypeError(
                "production_profiles must be a dictionary."
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
        # Hourly scenario-based recommendation
        # --------------------------------------------------

        if (
            consumption_scenario is not None
            and production_profiles is not None
        ):
            consumption = consumption_scenario.hourly_consumption

            def hourly_self_consumption(evaluation):
                panel_count = evaluation.panel_count
                profile = production_profiles[panel_count]

                production = profile.hourly_production.copy()

                production.index = production.index.strftime(
                    "%m-%d-%H"
                )

                consumption_keys = consumption.index.strftime(
                    "%m-%d-%H"
                )

                aligned_production = (
                    pd.Series(
                        consumption_keys,
                        index=consumption.index,
                    )
                    .map(production)
                    .fillna(0.0)
                )

                return float(
                    pd.concat(
                        [
                            consumption,
                            aligned_production,
                        ],
                        axis=1,
                    )
                    .min(axis=1)
                    .sum()
                )

            # Prefer the configuration that maximizes the
            # energy consumed directly from the PV production.
            #
            # If self-consumption is equal, prefer:
            #   1. fewer panels
            #   2. smaller occupied area
            best = max(
                evaluations,
                key=lambda evaluation: (
                    hourly_self_consumption(evaluation),
                    -evaluation.panel_count,
                    -evaluation.occupied_area_m2,
                )
            )

        else:

            # --------------------------------------------------
            # Legacy annual recommendation
            # --------------------------------------------------

            covering = [
                evaluation
                for evaluation in evaluations
                if annual_productions_kwh[
                    evaluation.panel_count
                ] >= annual_consumption_kwh
            ]

            if covering:

                best = min(
                    covering,
                    key=lambda evaluation: (
                        evaluation.panel_count,
                        evaluation.occupied_area_m2,
                    )
                )

            else:

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
            consumption_scenario=consumption_scenario,
            production_profile=(
                production_profiles[best.panel_count]
                if production_profiles is not None
                else None
            ),
        )