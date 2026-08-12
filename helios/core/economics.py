class EconomicsEngine:

    def __init__(self):

        self.cost_without_pv = None
        self.cost_with_pv = None

        self.annual_savings = None
        self.export_income = None

        self.annual_savings = None

        self.net_investment = None
        
        self.payback_years = None

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

        self.annual_savings = (
            self.cost_without_pv
            - self.cost_with_pv
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

        if self.net_investment is None:
            raise RuntimeError(
                "Net investment has not been calculated."
            )

        if self.annual_savings is None:
            raise RuntimeError(
                "Annual savings have not been calculated."
            )

        if self.annual_savings <= 0:
            raise ValueError(
                "Annual savings must be positive."
            )

        self.payback_years = (
            self.net_investment
            / self.annual_savings
        )

        return self.payback_years