import pandas as pd


class SolarProductionEngine:

    @staticmethod
    def daily(hourly: pd.DataFrame) -> pd.Series:

        return (
            hourly["production_kwh"]
            .resample("D")
            .sum()
        )

    @staticmethod
    def monthly(daily: pd.Series) -> pd.Series:

        return (
            daily
            .resample("ME")
            .sum()
        )

    @staticmethod
    def yearly(monthly: pd.Series) -> pd.Series:

        return (
            monthly
            .resample("YE")
            .sum()
        )