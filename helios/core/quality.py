import pandas as pd

class DataQualityEngine:

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