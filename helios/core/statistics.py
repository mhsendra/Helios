"""
HELIOS
Statistics Engine
"""

import pandas as pd

class ConsumptionStatistics:

    def __init__(self):

        self.statistics: dict | None = None

        self.daily_consumption: pd.Series | None = None

        self.monthly_consumption: pd.Series | None = None

        self.yearly_consumption: pd.Series | None = None

        self.hourly_profile: pd.Series | None = None

        self.weekday_profile: pd.Series | None = None

        self.monthly_profile: pd.Series | None = None

        self.seasonal_profile: pd.Series | None = None

        self.workday_vs_weekend_profile: dict | None = None

    def calculate(
        self,
        df: pd.DataFrame
    ) -> dict:

        consumption = df["AE_kWh"]

        self.statistics = {
            "total_consumption": consumption.sum(),
            "mean_hourly": consumption.mean(),
            "max_consumption": consumption.max(),
            "max_consumption_time": consumption.idxmax(),
            "min_consumption": consumption.min(),
            "min_consumption_time": consumption.idxmin(),
            "std_consumption": consumption.std(),
        }

        return self.statistics
    
    def calculate_daily_consumption(
        self,
        df
    ):

        self.daily_consumption = (
            df["AE_kWh"]
            .resample("D")
            .sum()
        )

        return self.daily_consumption
    
    def calculate_monthly_consumption(
        self,
        df
    ):

        self.monthly_consumption = (
            df["AE_kWh"]
            .resample("ME")
            .sum()
        )

        return self.monthly_consumption
    
    def calculate_yearly_consumption(
        self,
        df
    ):

        self.yearly_consumption = (
            df["AE_kWh"]
            .resample("YE")
            .sum()
        )

        return self.yearly_consumption
    
    def calculate_hourly_profile(self, df):

        self.hourly_profile = (
            df["AE_kWh"]
            .groupby(df.index.hour)
            .mean()
        )

        return self.hourly_profile
    
    def calculate_weekday_profile(
        self,
        df
    ):

        self.weekday_profile = (
            df["AE_kWh"]
            .groupby(df.index.dayofweek)
            .mean()
            .reindex(range(7))
        )

        self.weekday_profile.index = [
            "Lunes",
            "Martes",
            "Miércoles",
            "Jueves",
            "Viernes",
            "Sábado",
            "Domingo"
        ]

        return self.weekday_profile

    def calculate_monthly_profile(
        self,
        df
    ):

        self.monthly_profile = (
            df["AE_kWh"]
            .groupby(df.index.month)
            .mean()
            .reindex(range(1, 13))
        )

        self.monthly_profile.index = [
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre"
        ]

        return self.monthly_profile
    
    def calculate_seasonal_profile(self):

        if self.monthly_profile is None:

            raise RuntimeError(
                "Monthly profile has not been calculated."
            )        

        profile = {
            "Invierno": (
                self.monthly_profile["Diciembre"]
                + self.monthly_profile["Enero"]
                + self.monthly_profile["Febrero"]
            ) / 3,

            "Primavera": (
                self.monthly_profile["Marzo"]
                + self.monthly_profile["Abril"]
                + self.monthly_profile["Mayo"]
            ) / 3,

            "Verano": (
                self.monthly_profile["Junio"]
                + self.monthly_profile["Julio"]
                + self.monthly_profile["Agosto"]
            ) / 3,

            "Otoño": (
                self.monthly_profile["Septiembre"]
                + self.monthly_profile["Octubre"]
                + self.monthly_profile["Noviembre"]
            ) / 3
        }

        self.seasonal_profile = pd.Series(profile)

        return self.seasonal_profile
    
    def calculate_workday_vs_weekend_profile(self, dataset):
        """
        Calcula el consumo medio en laborables vs fin de semana.

        Devuelve un diccionario con dos claves:
        'workdays' y 'weekend'.
        """

        dataset = dataset.copy()
        dataset["weekday"] = dataset.index.weekday

        workdays = (
            dataset[dataset["weekday"] < 5]["AE_kWh"].mean()
        )

        weekend = (
            dataset[dataset["weekday"] >= 5]["AE_kWh"].mean()
        )

        self.workday_vs_weekend_profile = {
            "workdays": workdays,
            "weekend": weekend
        }

        return self.workday_vs_weekend_profile