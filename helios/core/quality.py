import pandas as pd

class DataQualityEngine:

    def calculate(self, dataset):

        total_hours = len(dataset)

        missing_hours = (
            dataset["data_status"] == "missing"
        ).sum()

        valid_hours = total_hours - missing_hours

        duplicates = dataset.index.duplicated().sum()

        if total_hours == 0:
            coverage = 0.0
        else:
            coverage = (valid_hours / total_hours) * 100

        if coverage >= 99:
            rating = "EXCELENTE"
        elif coverage >= 97:
            rating = "MUY BUENA"
        elif coverage >= 95:
            rating = "BUENA"
        else:
            rating = "REVISAR"

        self.quality = {
            "total_hours": total_hours,
            "valid_hours": valid_hours,
            "missing_hours": missing_hours,
            "duplicates": duplicates,
            "coverage": coverage,
            "rating": rating
        }

        return self.quality