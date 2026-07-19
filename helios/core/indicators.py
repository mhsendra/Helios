import pandas as pd


class IndicatorsEngine:

    def __init__(self):
        pass

    def calculate_mean_consumption(
        self,
        df: pd.DataFrame
    ) -> dict:

        daily = (
            df["AE_kWh"]
            .resample("D")
            .sum()
        )

        weekly = (
            df["AE_kWh"]
            .resample("W")
            .sum()
        )

        monthly = (
            df["AE_kWh"]
            .resample("ME")
            .sum()
        )

        yearly = (
            df["AE_kWh"]
            .resample("YE")
            .sum()
        )

        workdays = (
            daily[daily.index.dayofweek < 5]
        )

        weekends = (
            daily[daily.index.dayofweek >= 5]
        )

        return {

            "hourly": df["AE_kWh"].mean(),

            "daily": daily.mean(),

            "weekly": weekly.mean(),

            "monthly": monthly.mean(),

            "yearly": yearly.mean(),

            "workday": workdays.mean(),

            "weekend": weekends.mean()
        }
    
    def calculate_extremes(
        self,
        dataset: pd.DataFrame,
        daily: pd.Series,
        monthly: pd.Series,
        weekly: pd.DataFrame
        ) -> dict:

            hourly = dataset["AE_kWh"]

            weekly_series = weekly.stack()

            return {

                "hourly_max": (hourly.idxmax(), hourly.max()),
                "hourly_min": (hourly.idxmin(), hourly.min()),

                "daily_max": (daily.idxmax(), daily.max()),
                "daily_min": (daily.idxmin(), daily.min()),

                "weekly_max": (weekly_series.idxmax(), weekly_series.max()),
                "weekly_min": (weekly_series.idxmin(), weekly_series.min()),

                "monthly_max": (monthly.idxmax(), monthly.max()),
                "monthly_min": (monthly.idxmin(), monthly.min())
            }
    
    def calculate_base_load(
        self,
        dataset: pd.DataFrame
    ) -> float:

        return dataset["AE_kWh"].quantile(0.10)