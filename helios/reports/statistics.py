from helios.reports.printer import ReportPrinter


class StatisticsReports:

    def statistics(self,statistics):

        if statistics is None:
            print("No hay estadísticas calculadas.")
            return
        
        ReportPrinter.title(
            "STATISTICS REPORT"
        )
        
        ReportPrinter.energy(
            "Consumo total",
            statistics["total_consumption"]
        )

        ReportPrinter.energy(
            "Consumo medio horario",
            statistics["mean_hourly"],
            decimals=3
        )

        ReportPrinter.energy(
            "Consumo máximo",
            statistics["max_consumption"],
            decimals=3
        )

        ReportPrinter.datetime(
            "Fecha del máximo",
            statistics["max_consumption_time"]
        )

        ReportPrinter.energy(
            "Consumo mínimo",
            statistics["min_consumption"],
            decimals=3
        )

        ReportPrinter.datetime(
            "Fecha del mínimo",
            statistics["min_consumption_time"]
        )

        ReportPrinter.energy(
            "Desv. estándar",
            statistics["std_consumption"],
            decimals=3
        )
  
    def daily(self, daily_consumption):

        if daily_consumption is None:

            print("No hay consumos diarios calculados.")
            return

        ReportPrinter.title(
            "DAILY CONSUMPTION REPORT"
        )

        ReportPrinter.blank()

        ReportPrinter.count(
            "Días analizados",
            len(daily_consumption)
        )

        ReportPrinter.energy(
            "Consumo total",
            daily_consumption.sum()
        )

        ReportPrinter.energy(
            "Consumo diario medio",
            daily_consumption.mean()
        )

        ReportPrinter.blank()

        ReportPrinter.energy(
            "Consumo máximo diario",
            daily_consumption.max(),
            decimals=3
        )

        ReportPrinter.day(
            "Fecha del máximo",
            daily_consumption.idxmax()
        )

        ReportPrinter.energy(
            "Consumo mínimo diario",
            daily_consumption.min(),
            decimals=3
        )

        ReportPrinter.day(
            "Fecha del mínimo",
            daily_consumption.idxmin()
        )

    def monthly(self, monthly_consumption):

        if monthly_consumption is None:

            print("No hay consumos mensuales calculados.")
            return

        ReportPrinter.title(
            "MONTHLY CONSUMPTION REPORT"
        )

        ReportPrinter.blank()

        ReportPrinter.count(
            "Meses analizados",
            len(monthly_consumption)
        )

        ReportPrinter.energy(
            "Consumo total",
            monthly_consumption.sum(),
            decimals=3
        )

        ReportPrinter.energy(
            "Consumo mensual medio",
            monthly_consumption.mean()
        )

        ReportPrinter.blank()

        ReportPrinter.energy(
            "Consumo máximo mensual",
            monthly_consumption.max(),
            decimals=3
        )

        ReportPrinter.month(
            "Mes del máximo",
            monthly_consumption.idxmax()
        )

        ReportPrinter.energy(
            "Consumo mínimo mensual",
            monthly_consumption.min(),
            decimals=3
        )

        ReportPrinter.month(
            "Mes del mínimo",
            monthly_consumption.idxmin()
        )

    def yearly(self, yearly_consumption):

        if yearly_consumption is None:

            print("No hay consumos anuales calculados.")
            return

        ReportPrinter.title(
            "YEARLY CONSUMPTION REPORT"
        )

        ReportPrinter.blank()

        ReportPrinter.count(
            "Años analizados",
            len(yearly_consumption)
        )

        ReportPrinter.energy(
            "Consumo total",
            yearly_consumption.sum(),
            decimals=3
        )

        ReportPrinter.energy(
            "Consumo anual medio",
            yearly_consumption.mean()
        )

        ReportPrinter.blank()

        ReportPrinter.energy(
            "Consumo máximo anual",
            yearly_consumption.max(),
            decimals=3
        )

        ReportPrinter.year(
            "Año del máximo",
            yearly_consumption.idxmax()
        )

        ReportPrinter.energy(
            "Consumo mínimo anual",
            yearly_consumption.min(),
            decimals=3
        )

        ReportPrinter.year(
            "Año del mínimo",
            yearly_consumption.idxmin()
        )
