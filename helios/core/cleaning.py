import pandas as pd

SMALL_GAP_MAX = 3
LARGE_GAP_MAX = 12

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

        # Crear gap_type
        df["gap_type"] = pd.NA

        small_gaps = (df["gap_size"] > 0) & (df["gap_size"] <= SMALL_GAP_MAX)
        large_gaps = df["gap_size"] > SMALL_GAP_MAX

        df.loc[small_gaps, "gap_type"] = "small"
        df.loc[large_gaps, "gap_type"] = "large"

        gap_counter = 1

        for group in groups[missing].unique():

            df.loc[groups == group, "gap_id"] = gap_counter

            gap_counter += 1

        return df
