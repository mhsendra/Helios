class ValidationEngine:

    def __init__(self):
        self.quality = None

    def calculate_gap_summary(
            self,
            dataset
        ):

            gaps = dataset[
                dataset["gap_id"].notna()
            ]

            if gaps.empty:
                return None

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

            return {

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
        
    def calculate(self, dataset):

            total_hours = len(dataset)

            missing_hours = (
                dataset["data_status"] == "missing"
            ).sum()

            valid_hours = total_hours - missing_hours

            duplicates = dataset.index.duplicated().sum()

            coverage = (valid_hours / total_hours) * 100

            if coverage >= 99:
                quality = "EXCELENTE"
            elif coverage >= 97:
                quality = "MUY BUENA"
            elif coverage >= 95:
                quality = "BUENA"
            else:
                quality = "REVISAR"

            self.quality = {
                "total_hours": total_hours,
                "valid_hours": valid_hours,
                "missing_hours": missing_hours,
                "duplicates": duplicates,
                "coverage": coverage,
                "quality": quality
            }

            return self.quality
    
    def find_duplicate_timestamps(self, dataset):

        duplicates = dataset.index[
            dataset.index.duplicated(keep=False)
        ]

        if len(duplicates) == 0:

            return {
                "count": 0,
                "duplicates": None
            }

        return {

            "count": len(duplicates),

            "duplicates": dataset.loc[duplicates]

        }