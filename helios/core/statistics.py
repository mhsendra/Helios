"""
HELIOS
Statistics Engine
"""

import pandas as pd


class ConsumptionStatistics:

    def calculate(self, df: pd.DataFrame) -> dict:
        consumption = df["AE_kWh"]
        #print(df["AE_kWh"].min())
        #print(df["AE_kWh"].isna().sum())
        statistics = {}
        statistics["total_consumption"] = consumption.sum()
        statistics["mean_hourly"] = consumption.mean()
        statistics["max_consumption"] = consumption.max()
        statistics["max_consumption_time"] = consumption.idxmax()
        statistics["min_consumption"] = consumption.min()
        statistics["min_consumption_time"] = consumption.idxmin()
        statistics["std_consumption"] = consumption.std()

        return statistics
    
    def calculate_daily_consumption(self, df):

        daily = (
            df["AE_kWh"]
            .resample("D")
            .sum()
        )

        return daily
    
    def calculate_monthly_consumption(self, df):

        monthly = (
            df["AE_kWh"]
            .resample("ME")
            .sum()
        )

        return monthly
    
    def calculate_yearly_consumption(self, df):

        yearly = (
            df["AE_kWh"]
            .resample("YE")
            .sum()
        )

        return yearly
    
    def calculate_hourly_profile(self, df):

        profile = (
            df["AE_kWh"]
            .groupby(df.index.hour)
            .mean()
        )

        return profile
    