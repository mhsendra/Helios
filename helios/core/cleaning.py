import pandas as pd


class ConsumptionCleaner:

    def mark_missing_data(self, df):

        df = df.copy()

        df["data_status"] = "original"

        df.loc[df["AE_kWh"].isna(), "data_status"] = "missing"

        return df