from dataclasses import dataclass

import numpy_financial as npf


@dataclass(frozen=True)
class BatteryEconomicConfiguration:
    battery_cost_eur: float

    annual_savings_eur: float

    years: int = 30

    electricity_price_growth: float = 0.02

    # Degradación FV:
    # 1 % durante el primer año y 0.35 % anual posteriormente.
    pv_initial_degradation: float = 0.01
    pv_degradation: float = 0.0035

    # Degradación anual de la batería.
    battery_degradation: float = 0.02

    annual_maintenance_eur: float = 0.0
    maintenance_growth: float = 0.02

    discount_rate: float = 0.05
@dataclass(frozen=True)
class BatteryEconomicConfiguration:
    battery_cost_eur: float

    annual_savings_eur: float

    years: int = 30

    electricity_price_growth: float = 0.02
    pv_degradation: float = 0.0035
    battery_degradation: float = 0.02

    annual_maintenance_eur: float = 0.0
    maintenance_growth: float = 0.02

    discount_rate: float = 0.05

@dataclass(frozen=True)
class BatteryEconomicResult:
    cash_flows: list[float]
    cumulative_cash_flow: list[float]

    npv_eur: float
    irr_percent: float
    payback_years: float


class BatteryEconomicModel:

    def calculate(
        self,
        configuration: BatteryEconomicConfiguration,
    ) -> BatteryEconomicResult:

        cash_flows = [
            -configuration.battery_cost_eur
        ]

        cumulative_cash_flow = [
            -configuration.battery_cost_eur
        ]

        cumulative = -configuration.battery_cost_eur

        for year in range(1, configuration.years + 1):

            # ---------------------------------------------------------
            # FV degradation
            #
            # Year 1:
            #   initial degradation is applied once.
            #
            # Year 2 onwards:
            #   the annual degradation is compounded.
            # ---------------------------------------------------------
            pv_factor = (
                (1.0 - configuration.pv_degradation)
                ** (year - 1)
            )

            # ---------------------------------------------------------
            # Battery degradation
            #
            # Year 1 = 100 %
            # Year 2 = 98 %
            # Year 3 = 96.04 %
            # ---------------------------------------------------------
            battery_factor = (
                (1.0 - configuration.battery_degradation)
                ** (year - 1)
            )

            # ---------------------------------------------------------
            # Electricity price growth
            #
            # Year 1 = 100 %
            # Year 2 = 102 %
            # Year 3 = 104.04 %
            # ---------------------------------------------------------
            electricity_factor = (
                (1.0 + configuration.electricity_price_growth)
                ** (year - 1)
            )

            savings = (
                configuration.annual_savings_eur
                * pv_factor
                * battery_factor
                * electricity_factor
            )

            maintenance = (
                configuration.annual_maintenance_eur
                * (
                    (1.0 + configuration.maintenance_growth)
                    ** (year - 1)
                )
            )

            cash_flow = savings - maintenance

            cash_flows.append(cash_flow)

            cumulative += cash_flow
            cumulative_cash_flow.append(cumulative)

        # -------------------------------------------------------------
        # NPV
        # -------------------------------------------------------------
        npv = sum(
            cash_flow
            / (
                (1.0 + configuration.discount_rate) ** year
            )
            for year, cash_flow in enumerate(cash_flows)
        )

        # -------------------------------------------------------------
        # IRR
        # -------------------------------------------------------------
        try:
            irr = npf.irr(cash_flows)

            irr_percent = (
                float(irr) * 100
                if irr is not None
                else float("nan")
            )

        except (ValueError, TypeError):
            irr_percent = float("nan")

        # -------------------------------------------------------------
        # Payback
        #
        # Searches the first year in which cumulative cash flow
        # becomes >= 0 and interpolates within that year.
        #
        # If investment is not recovered within the configured
        # horizon, returns infinity.
        # -------------------------------------------------------------
        payback_years = float("inf")

        for year in range(1, len(cumulative_cash_flow)):

            previous = cumulative_cash_flow[year - 1]
            current = cumulative_cash_flow[year]

            if current >= 0:

                if current == previous:
                    payback_years = float(year)

                else:
                    fraction = (
                        -previous
                        / (current - previous)
                    )

                    payback_years = (
                        year - 1 + fraction
                    )

                break

        return BatteryEconomicResult(
            cash_flows=cash_flows,
            cumulative_cash_flow=cumulative_cash_flow,
            npv_eur=float(npv),
            irr_percent=irr_percent,
            payback_years=payback_years,
        )