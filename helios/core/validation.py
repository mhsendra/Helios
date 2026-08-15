import pandas as pd
class ValidationEngine:

    def __init__(self):
        self.gap_summary = None
        self.duplicates = None

    def calculate_gap_summary(
    self,
    dataset: pd.DataFrame
):

        gaps = dataset[
            dataset["gap_id"].notna()
        ]

        if gaps.empty:

            self.gap_summary = None

            return self.gap_summary

        summary = (
            gaps
            .groupby("gap_id")
            .agg(
                start=("gap_size", lambda s: s.index.min()),
                end=("gap_size", lambda s: s.index.max()),
                hours=("gap_size", "first"),
                gap_type=("gap_type", "first")
            )
        )

        distribution = (
            summary["hours"]
            .value_counts()
            .sort_index()
        )

        self.gap_summary = {

            "gaps": gaps,

            "summary": summary,

            "total_missing": (
                dataset["data_status"] == "missing"
            ).sum(),

            "total_blocks": len(summary),

            "largest_gap": gaps["gap_size"].max(),

            "small": (
                summary["gap_type"] == "small"
            ).sum(),

            "large": (
                summary["gap_type"] == "large"
            ).sum(),

            "distribution": distribution

        }

        return self.gap_summary
    
    def find_duplicate_timestamps(
        self,
        dataset: pd.DataFrame
    ):

        duplicated_mask = dataset.index.duplicated(
            keep=False
        )

        if not duplicated_mask.any():

            self.duplicates = {
                "count": 0,
                "duplicates": None
            }

            return self.duplicates

        self.duplicates = {

            "count": int(duplicated_mask.sum()),

            "duplicates": dataset.loc[duplicated_mask]

        }

        return self.duplicates