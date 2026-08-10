from helios.reports.printer import ReportPrinter


class QualityReports:

    def quality(self, quality):

        ReportPrinter.title("DATA QUALITY REPORT")

        ReportPrinter.blank()

        ReportPrinter.count(
            "Registros totales",
            quality["total_hours"]
        )

        ...

        ReportPrinter.quality(
            "Calidad",
            quality["rating"]
        )

    def gap(self, summary):

        if summary is None:

            print("No se han detectado huecos.")
            return
        
    def duplicates(self, duplicates):

        ReportPrinter.title(
            "DUPLICATE TIMESTAMPS"
        )

        ReportPrinter.blank()

        ReportPrinter.count(
            "Duplicados encontrados",
            duplicates["count"]
        )

        if duplicates["count"] == 0:

            return

        ReportPrinter.blank()

        print(duplicates["duplicates"])
