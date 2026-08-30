from helios.reports.printer import ReportPrinter


class ProfilesReports:

    def hourly_profile(self, hourly_profile):

        if hourly_profile is None:
            return

        ReportPrinter.title(
            "HOURLY PROFILE REPORT"
        )

        ReportPrinter.blank()

        ReportPrinter.count(
            "Horas analizadas",
            len(hourly_profile)
        )

        ReportPrinter.energy(
            "Consumo medio horario",
            hourly_profile.mean(),
            decimals=3
        )

        ReportPrinter.blank()

        ReportPrinter.text(
            "Hora de mayor consumo",
            f"{hourly_profile.idxmax():02d}:00"
        )

        ReportPrinter.energy(
            "Consumo máximo",
            hourly_profile.max(),
            decimals=3
        )

        ReportPrinter.blank()

        ReportPrinter.text(
            "Hora de menor consumo",
            f"{hourly_profile.idxmin():02d}:00"
        )

        ReportPrinter.energy(
            "Consumo mínimo",
            hourly_profile.min(),
            decimals=3
        )

        ReportPrinter.blank()

        ReportPrinter.subtitle(
            "Top 5 horas de consumo"
        )

        top5 = (
            hourly_profile
            .sort_values(ascending=False)
            .head(5)
        )

        for hour, value in top5.items():

            ReportPrinter.text(
                f"Hora {hour:02d}:00",
                f"{value:.3f} kWh"
            )

    def weekday_profile(self, weekday_profile):

        if weekday_profile is None:
            return

        laborables = weekday_profile.iloc[:5].mean()
        fin_semana = weekday_profile.iloc[5:].mean()

        incremento = (
            (fin_semana - laborables)
            / laborables
            * 100
        )

        ReportPrinter.title(
            "WEEKDAY PROFILE REPORT"
        )

        ReportPrinter.blank()

        ReportPrinter.energy(
            "Consumo medio semanal",
            weekday_profile.mean(),
            decimals=3
        )

        ReportPrinter.blank()

        ReportPrinter.energy(
            "Media laborables",
            laborables,
            decimals=3
        )

        ReportPrinter.energy(
            "Media fin de semana",
            fin_semana,
            decimals=3
        )

        ReportPrinter.percent(
            "Incremento fin de semana",
            incremento,
            decimals=1
        )

        ReportPrinter.blank()

        ReportPrinter.text(
            "Día de mayor consumo",
            weekday_profile.idxmax()
        )

        ReportPrinter.energy(
            "Consumo máximo",
            weekday_profile.max(),
            decimals=3
        )

        ReportPrinter.blank()

        ReportPrinter.text(
            "Día de menor consumo",
            weekday_profile.idxmin()
        )

        ReportPrinter.energy(
            "Consumo mínimo",
            weekday_profile.min(),
            decimals=3
        )

        ReportPrinter.blank()

        ReportPrinter.subtitle(
            "Consumo medio por día"
        )

        for day, value in weekday_profile.items():

            ReportPrinter.text(
                f"{day}",
                f"{value:.3f} kWh"
            )

    def monthly_profile(self, monthly_profile):

        if monthly_profile is None:
            return

        incremento = (
            (
                monthly_profile.max()
                - monthly_profile.min()
            )
            / monthly_profile.min()
            * 100
        )

        mes_max = (
            f"{monthly_profile.idxmax()} "
            "(promedio multianual)"
        )

        mes_min = (
            f"{monthly_profile.idxmin()} "
            "(promedio multianual)"
        )

        valor_max = monthly_profile.max()
        valor_min = monthly_profile.min()

        ReportPrinter.title(
            "MONTHLY PROFILE REPORT"
        )

        ReportPrinter.blank()

        ReportPrinter.text(
            "Mes de mayor consumo",
            mes_max
        )

        ReportPrinter.energy(
            "Consumo máximo",
            valor_max,
            decimals=3
        )

        ReportPrinter.blank()

        ReportPrinter.text(
            "Mes de menor consumo",
            mes_min
        )

        ReportPrinter.energy(
            "Consumo mínimo",
            valor_min,
            decimals=3
        )

        ReportPrinter.blank()

        ReportPrinter.percent(
            "Variación estacional",
            incremento,
            decimals=1
        )

        ReportPrinter.blank()

        ReportPrinter.subtitle(
            "Consumo medio por mes"
        )

        for month, value in monthly_profile.items():

            ReportPrinter.text(
                f"{month}",
                f"{value:.3f} kWh"
            )

    def seasonal_profile(self, seasonal_profile):

        if seasonal_profile is None:
            return

        incremento = (
            (
                seasonal_profile.max()
                - seasonal_profile.min()
            )
            / seasonal_profile.min()
            * 100
        )

        estacion_max = (
            f"{seasonal_profile.idxmax()} "
            "(promedio multianual)"
        )

        estacion_min = (
            f"{seasonal_profile.idxmin()} "
            "(promedio multianual)"
        )

        valor_max = seasonal_profile.max()
        valor_min = seasonal_profile.min()

        ReportPrinter.title(
            "SEASONAL PROFILE REPORT"
        )

        ReportPrinter.blank()

        ReportPrinter.text(
            "Estación de mayor consumo",
            estacion_max
        )

        ReportPrinter.energy(
            "Consumo máximo",
            valor_max,
            decimals=3
        )

        ReportPrinter.blank()

        ReportPrinter.text(
            "Estación de menor consumo",
            estacion_min
        )

        ReportPrinter.energy(
            "Consumo mínimo",
            valor_min,
            decimals=3
        )

        ReportPrinter.blank()

        ReportPrinter.percent(
            "Variación estacional",
            incremento,
            decimals=1
        )

        ReportPrinter.blank()

        ReportPrinter.subtitle(
            "Consumo medio por estación"
        )

        for season, value in seasonal_profile.items():

            ReportPrinter.text(
                f"{season}",
                f"{value:.3f} kWh"
            )
