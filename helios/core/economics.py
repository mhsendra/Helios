class EconomicsEngine:

    def __init__(self):

        self.cost_without_pv = None
        self.cost_with_pv = None

        self.annual_savings = None
        self.export_income = None

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

        grid_cost = (
            data["grid_import_kwh"]
            * data["buy_price_eur_kwh"]
        ).sum()

        export_income = self.export_income

        self.cost_with_pv = (
            grid_cost
            - export_income
        )

        return self.cost_with_pv

    def calculate_annual_savings(self) -> float:

        self.annual_savings = (
            self.cost_without_pv
            - self.cost_with_pv
        )

        return self.annual_savings