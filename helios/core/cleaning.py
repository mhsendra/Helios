import pandas as pd


class ConsumptionCleaner:

    def mark_missing_data(self, df):

        df = df.copy()

        df["data_status"] = "original"

        df.loc[df["AE_kWh"].isna(), "data_status"] = "missing"

        return df
    
    def classify_gaps(self, df):

        df = df.copy()

        missing = df["AE_kWh"].isna()

        # Identificar cambios entre missing / no missing
        groups = (missing != missing.shift()).cumsum()

        # Tamaño de cada bloque
        sizes = missing.groupby(groups).transform("sum")

        df["gap_size"] = sizes.where(missing, 0).astype(int)

        # Crear gap_id
        df["gap_id"] = pd.NA

        gap_counter = 1

        for group in groups[missing].unique():

            df.loc[groups == group, "gap_id"] = gap_counter

            gap_counter += 1

        return df
