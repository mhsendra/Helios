import pandas as pd
import numpy_financial as npf

class EconomicsEngine:

    def __init__(self):

        self.cost_without_pv = None
        self.cost_with_pv = None

        self.annual_savings = None
        self.export_income = None
        
        self.self_consumption_savings = None
        
        self.net_investment = None
        
        self.payback_years = None
        
        self.cash_flow = None
        self.cumulative_cash_flow = None
        
        self.npv = None
        self.irr = None
        
    def calculate_cost_without_pv(
        self,
        dataset,
    ) -> float:
        """
        Calculate the annual electricity cost
        without photovoltaic generation.
        """

        self.cost_without_pv = (
            dataset["AE_kWh"]
            * dataset["buy_price_eur_kwh"]
        ).sum()

        return self.cost_without_pv

    def calculate_export_income(
        self,
        energy_balance,
        tariff_data,
    ) -> float:
        """
        Calculate annual income from photovoltaic
        energy exported to the grid.
        """

        data = energy_balance.join(
            tariff_data[
                ["sell_price_eur_kwh"]
            ]
        )

        self.export_income = (
            data["grid_export_kwh"]
            * data["sell_price_eur_kwh"]
        ).sum()

        return self.export_income

    def calculate_cost_with_pv(
        self,
        energy_balance,
        tariff_data,
    ) -> float:
        """
        Calculate the annual net electricity cost
        with photovoltaic generation.
        """

        data = energy_balance.join(
            tariff_data[
                ["buy_price_eur_kwh"]
            ]
        )

        self.grid_import_cost = (
            data["grid_import_kwh"]
            * data["buy_price_eur_kwh"]
        ).sum()

        self.cost_with_pv = (
            self.grid_import_cost
            - self.export_income
        )

        return self.cost_with_pv

    def calculate_annual_savings(self) -> float:

        if self.cost_without_pv is None:
            raise RuntimeError(
                "Cost without PV has not been calculated."
            )

        if self.cost_with_pv is None:
            raise RuntimeError(
                "Cost with PV has not been calculated."
            )

        if self.export_income is None:
            raise RuntimeError(
                "Export income has not been calculated."
            )

        self.self_consumption_savings = (
            self.cost_without_pv
            - (
                self.cost_with_pv
                + self.export_income
            )
        )

        self.annual_savings = (
            self.self_consumption_savings
            + self.export_income
        )

        return self.annual_savings

    def calculate_net_investment(
        self,
        configuration
    ) -> float:

        self.net_investment = (
            configuration.installation_cost
            - configuration.subsidies
            - configuration.tax_deductions
        )

        return self.net_investment
    
    def calculate_payback(self) -> float:

        if self.cash_flow is None:
            raise RuntimeError(
                "Cash flow has not been calculated."
            )

        for i in range(1, len(self.cash_flow)):

            previous_cumulative = (
                self.cash_flow
                .iloc[i - 1]["cumulative_cash_flow"]
            )

            current_cumulative = (
                self.cash_flow
                .iloc[i]["cumulative_cash_flow"]
            )

            if (
                previous_cumulative < 0
                and current_cumulative >= 0
            ):

                recovery = -previous_cumulative

                annual_cash_flow = (
                    self.cash_flow
                    .iloc[i]["cash_flow"]
                )

                fraction = (
                    recovery / annual_cash_flow
                )

                self.payback_years = (
                    self.cash_flow.iloc[i - 1]["year"]
                    + fraction
                )

                return self.payback_years

        self.payback_years = None

        return self.payback_years
    
    def calculate_cash_flow(
        self,
        configuration,
        years: int = 25
    ) -> pd.DataFrame:

        if self.net_investment is None:
            raise RuntimeError(
                "Net investment has not been calculated."
            )

        if self.annual_savings is None:
            raise RuntimeError(
                "Annual savings have not been calculated."
            )

        if years <= 0:
            raise ValueError(
                "Years must be greater than zero."
            )

        rows = [
            {
                "year": 0,
                "self_consumption_savings": 0.0,
                "export_income": 0.0,
                "maintenance_cost": 0.0,
                "cash_flow": -self.net_investment,
                "cumulative_cash_flow": -self.net_investment,
            }
        ]

        cumulative = -self.net_investment

        for year in range(1, years + 1):

            degradation_factor = (
                self.calculate_degradation_factor(
                    year,
                    configuration
                )
            )

            electricity_price_factor = (
                self.calculate_electricity_price_factor(
                    year,
                    configuration
                )
            )

            self_consumption_savings = (
                self.self_consumption_savings
                * degradation_factor
                * electricity_price_factor
            )

            export_price_factor = (
                self.calculate_export_price_factor(
                    year,
                    configuration
                )
            )

            export_income = (
                self.export_income
                * degradation_factor
                * export_price_factor
            )

            maintenance_cost = (
                self.calculate_maintenance_cost(
                    year,
                    configuration
                )
            )

            annual_cash_flow = (
                self_consumption_savings
                + export_income
                - maintenance_cost
            )

            cumulative += annual_cash_flow

            rows.append(
                {
                    "year": year,
                    "self_consumption_savings":
                        self_consumption_savings,
                    "export_income":
                        export_income,
                    "maintenance_cost":
                        maintenance_cost,
                    "cash_flow":
                        annual_cash_flow,
                    "cumulative_cash_flow":
                        cumulative,
                }
            )

        self.cash_flow = pd.DataFrame(rows)

        self.cumulative_cash_flow = (
            self.cash_flow["cumulative_cash_flow"]
            .tolist()
        )

        return self.cash_flow
    
    def calculate_degradation_factor(
        self,
        year: int,
        configuration
    ) -> float:

        if year <= 0:
            return 1.0

        if year == 1:
            return (
                1
                - configuration.first_year_degradation
            )

        return (
            1
            - configuration.first_year_degradation
            - (
                configuration.annual_degradation
                * (year - 1)
            )
        )
        
    def calculate_electricity_price_factor(
        self,
        year: int,
        configuration
    ) -> float:

        if year <= 0:
            return 1.0

        return (
            1
            + configuration.annual_electricity_price_growth
        ) ** (year - 1)
        
    def calculate_export_price_factor(
        self,
        year: int,
        configuration
    ) -> float:

        if year <= 0:
            return 1.0

        return (
            1
            + configuration.annual_export_price_growth
        ) ** (year - 1)
        
    def calculate_maintenance_cost(
        self,
        year: int,
        configuration
    ) -> float:

        if year <= 0:
            return 0.0

        return (
            configuration.annual_maintenance_cost
            * (
                1
                + configuration.annual_maintenance_growth
            ) ** (year - 1)
        )
        
    def calculate_npv(
        self,
        discount_rate: float
    ) -> float:

        if self.cash_flow is None:
            raise RuntimeError(
                "Cash flow has not been calculated."
            )

        if discount_rate < 0:
            raise ValueError(
                "Discount rate cannot be negative."
            )

        discounted_cash_flows = (
            self.cash_flow["cash_flow"]
            / (
                1 + discount_rate
            ) ** self.cash_flow["year"]
        )

        self.npv = discounted_cash_flows.sum()

        return self.npv
    
    def calculate_irr(self) -> float:

        if self.cash_flow is None:
            raise RuntimeError(
                "Cash flow has not been calculated."
            )

        cash_flows = (
            self.cash_flow["cash_flow"]
            .tolist()
        )

        # IRR requires at least one negative
        # and one positive cash flow.
        if not (
            any(value < 0 for value in cash_flows)
            and any(value > 0 for value in cash_flows)
        ):
            raise RuntimeError(
                "IRR cannot be calculated: "
                "cash flows must contain at least "
                "one negative and one positive value."
            )

        try:
            irr = npf.irr(cash_flows)
        except Exception as exc:
            raise RuntimeError(
                "Unable to calculate IRR."
            ) from exc

        if irr is None or pd.isna(irr):
            raise RuntimeError(
                "IRR could not be calculated."
            )

        self.irr = float(irr)

        return self.irr

    def calculate_economic_indicators(
        self,
        discount_rate: float
    ) -> dict:

        if self.cash_flow is None:
            raise RuntimeError(
                "Cash flow has not been calculated."
            )

        self.calculate_payback()

        self.calculate_npv(
            discount_rate
        )

        self.calculate_irr()

        return {
            "payback_years": self.payback_years,
            "npv": self.npv,
            "irr": self.irr,
        }

    def economic_summary(self) -> pd.DataFrame:

        if self.cash_flow is None:
            raise RuntimeError(
                "Cash flow has not been calculated."
            )

        return self.cash_flow.copy()