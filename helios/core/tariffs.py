import json

from pathlib import Path

from datetime import datetime

from collections.abc import Mapping

import pandas as pd

from helios.core.tariffs_model import TariffPrices

class TariffEngine:

    PERIODS = (
        "Punta",
        "Llano",
        "Valle"
    )

    def __init__(self):

        self.national_holidays = set()

        self.load_national_holidays()

        self.period_consumption = None
        
        self.period_percentage = None

        self.prices = TariffPrices()

    def is_national_holiday(
    self,
    timestamp
    ):

        return (
            timestamp.date()
            in self.national_holidays
        )

    def classify_period(
        self,
        timestamp
    ) -> str:

        weekday = timestamp.weekday()
        hour = timestamp.hour

        # Sábado y domingo → Valle
        if weekday >= 5:
            return "Valle"

        # Festivos nacionales → Valle
        if self.is_national_holiday(timestamp):
            return "Valle"

        # Laborables

        if 0 <= hour < 8:
            return "Valle"

        if 8 <= hour < 10:
            return "Llano"

        if 10 <= hour < 14:
            return "Punta"

        if 14 <= hour < 18:
            return "Llano"

        if 18 <= hour < 22:
            return "Punta"

        if 22 <= hour <= 23:
            return "Llano"

        raise ValueError(
            f"Hora no válida: {hour}"
        )

    def calculate_period_consumption(
        self,
        dataset: pd.DataFrame
    ) -> dict[str, float]:

        data = dataset.copy()

        data["Periodo"] = (
            data.index.map(
                self.classify_period
            )
        )

        self.period_consumption = (
            data
            .groupby("Periodo")["AE_kWh"]
            .sum()
        )

        self.period_consumption = (
            self.period_consumption
            .reindex(self.PERIODS)
            .fillna(0)
            .to_dict()
        )

        return self.period_consumption

    def calculate_period_percentage(self):

        total = sum(self.period_consumption.values())

        self.period_percentage = {
            period: consumption / total * 100
            for period, consumption
            in self.period_consumption.items()
        }

        return self.period_percentage
    
    def load_national_holidays(self):

        path = (
            Path(__file__).parent.parent
            / "resources"
            / "holidays"
            / "national_holidays.json"
        )

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            holidays = json.load(file)

        self.national_holidays = {

            datetime.strptime(
                date,
                "%Y-%m-%d"
            ).date()

            for date in holidays

        }

    def assign_buy_prices(
        self,
        dataset,
    ):
        """
        Assign purchase prices according to the tariff period.
        """

        period_prices = {
            "P1": self.prices.buy_p1,
            "P2": self.prices.buy_p2,
            "P3": self.prices.buy_p3,
        }

        dataset["buy_price_eur_kwh"] = (
            dataset["Periodo"]
            .map(period_prices)
            .fillna(0.0)
        )
        
    def assign_sell_price(
        self,
        dataset,
    ):
        """
        Assign export compensation price.
        """

        dataset["sell_price_eur_kwh"] = (
            self.prices.sell_price
        )

    def assign_tariff_periods(
        self,
        dataset: pd.DataFrame
    ):
        """
        Assign the tariff period to each dataset record.
        """

        dataset["Periodo"] = (
            dataset.index.map(
                self.classify_period
            )
        )