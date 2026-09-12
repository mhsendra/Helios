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
        self.representative_year_consumption: pd.Series | None = None
        self.representative_annual_consumption: float | None = None
        self.hourly_profile: pd.Series | None = None
        self.weekday_profile: pd.Series | None = None
        self.monthly_profile: pd.Series | None = None
        self.seasonal_profile: pd.Series | None = None
        self.workday_vs_weekend_profile: dict | None = None

    def calculate(self, df: pd.DataFrame) -> dict:
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

    def calculate_daily_consumption(self, df):
        self.daily_consumption = df["AE_kWh"].resample("D").sum()
        return self.daily_consumption

    def calculate_monthly_consumption(self, df):
        self.monthly_consumption = df["AE_kWh"].resample("ME").sum()
        return self.monthly_consumption

    def calculate_yearly_consumption(self, df):
        self.yearly_consumption = df["AE_kWh"].resample("YE").sum()
        return self.yearly_consumption

    def calculate_representative_year_consumption(
        self,
        df: pd.DataFrame,
        reference_year: int = 2025,
    ) -> pd.Series:
        """
        Construye un perfil horario anual representativo a partir del histórico.

        Conserva la estacionalidad mensual, el día de la semana y la hora del
        día. Usa la mediana para reducir el efecto de episodios puntuales y
        normaliza el perfil al consumo anualizado observado.
        """
        if "AE_kWh" not in df.columns:
            raise KeyError("AE_kWh")

        if df.empty:
            raise ValueError("Cannot calculate a representative year from an empty dataset.")

        consumption = df["AE_kWh"].dropna()

        if consumption.empty:
            raise ValueError("Cannot calculate a representative year without consumption data.")

        if not isinstance(consumption.index, pd.DatetimeIndex):
            raise TypeError("Dataset index must be a DatetimeIndex.")

        start_day = consumption.index.min().normalize()
        end_day = consumption.index.max().normalize()
        observed_days = (end_day - start_day).days + 1

        if observed_days <= 0:
            raise ValueError("Invalid observation period.")

        source = pd.DataFrame({"AE_kWh": consumption})
        source["month"] = source.index.month
        source["weekday"] = source.index.dayofweek
        source["hour"] = source.index.hour

        grouped = (
            source
            .groupby(["month", "weekday", "hour"], observed=True)["AE_kWh"]
            .median()
        )

        target_index = pd.date_range(
            start=f"{reference_year}-01-01 00:00:00",
            end=f"{reference_year}-12-31 23:00:00",
            freq="h",
        )

        target = pd.DataFrame(index=target_index)
        target["month"] = target.index.month
        target["weekday"] = target.index.dayofweek
        target["hour"] = target.index.hour
        target["AE_kWh"] = [
            grouped.get((month, weekday, hour), float("nan"))
            for month, weekday, hour in zip(
                target["month"],
                target["weekday"],
                target["hour"],
            )
        ]

        if target["AE_kWh"].isna().any():
            missing = int(target["AE_kWh"].isna().sum())
            raise ValueError(
                "Historical data does not contain enough temporal coverage "
                f"to build the representative year ({missing} missing slots)."
            )

        historical_annualized = consumption.sum() / observed_days * 365
        synthetic_total = target["AE_kWh"].sum()

        if synthetic_total <= 0:
            raise ValueError("Representative year has no positive consumption.")

        normalization_factor = historical_annualized / synthetic_total
        representative = target["AE_kWh"] * normalization_factor
        representative.name = "AE_kWh"

        self.representative_year_consumption = representative
        self.representative_annual_consumption = float(representative.sum())
        return self.representative_year_consumption

    def calculate_hourly_profile(self, df):
        self.hourly_profile = df["AE_kWh"].groupby(df.index.hour).mean()
        return self.hourly_profile

    def calculate_weekday_profile(self, df):
        self.weekday_profile = (
            df["AE_kWh"]
            .groupby(df.index.dayofweek)
            .mean()
            .reindex(range(7))
        )
        self.weekday_profile.index = [
            "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"
        ]
        return self.weekday_profile

    def calculate_monthly_profile(self, df):
        self.monthly_profile = (
            df["AE_kWh"]
            .groupby(df.index.month)
            .mean()
            .reindex(range(1, 13))
        )
        self.monthly_profile.index = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        return self.monthly_profile

    def calculate_seasonal_profile(self):
        if self.monthly_profile is None:
            raise RuntimeError("Monthly profile has not been calculated.")

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
        """Calcula el consumo medio en laborables vs fin de semana."""
        dataset = dataset.copy()
        dataset["weekday"] = dataset.index.weekday
        workdays = dataset[dataset["weekday"] < 5]["AE_kWh"].mean()
        weekend = dataset[dataset["weekday"] >= 5]["AE_kWh"].mean()
        self.workday_vs_weekend_profile = {
            "workdays": workdays,
            "weekend": weekend
        }
        return self.workday_vs_weekend_profile