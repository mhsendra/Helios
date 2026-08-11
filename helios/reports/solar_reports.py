from helios.reports.printer import ReportPrinter


class SolarReports:

    def production_statistics(
        self,
        statistics,
        configuration
    ):

        if not statistics:

            raise ValueError(
                "Solar statistics have not been calculated."
            )

        ReportPrinter.title(
            "SOLAR PRODUCTION REPORT"
        )

        ReportPrinter.blank()

        ReportPrinter.text(
            "Tecnología FV",
            configuration.pv_technology
        )

        ReportPrinter.value(
            "Potencia instalada",
            configuration.installed_power_kwp,
            "kWp",
            decimals=2
        )

        ReportPrinter.value(
            "Inclinación",
            configuration.tilt,
            "°"
        )

        ReportPrinter.value(
            "Orientación",
            configuration.azimuth,
            "°"
        )

        ReportPrinter.percent(
            "Pérdidas consideradas",
            configuration.losses,
            decimals=1
        )

        ReportPrinter.blank()

        ReportPrinter.subtitle(
            "PRODUCCIÓN"
        )

        ReportPrinter.blank()

        ReportPrinter.count(
            "Horas del periodo analizado",
            statistics["hours"]
        )

        ReportPrinter.energy(
            "Producción estimada anual (PVGIS)",
            statistics["annual_production"]
        )

        ReportPrinter.energy(
            "Producción simulada del periodo",
            statistics["period_production"]
        )

        ReportPrinter.energy(
            "Producción media diaria",
            statistics["daily_average"]
        )

        ReportPrinter.value(
            "Potencia máxima",
            statistics["maximum_power"],
            "kW",
            decimals=2
        )

        ReportPrinter.value(
            "Potencia mínima (>0)",
            statistics["minimum_power"],
            "kW",
            decimals=2
        )

        ReportPrinter.value(
            "Horas equivalentes",
            statistics["equivalent_hours"],
            "h",
            decimals=2
        )

        ReportPrinter.percent(
            "Factor de capacidad",
            statistics["capacity_factor"]
        )

    def energy_balance(
        self,
        statistics
    ):

        if statistics is None:

            raise RuntimeError(
                "Energy statistics have not been calculated."
            )

        ReportPrinter.title(
            "ENERGY BALANCE"
        )

        ReportPrinter.blank()

        ReportPrinter.energy(
            "Consumo total periodo",
            statistics["consumption"]
        )

        ReportPrinter.energy(
            "Producción periodo",
            statistics["period_production"]
        )

        ReportPrinter.blank()

        ReportPrinter.energy(
            "Autoconsumo total",
            statistics["self_consumption"]
        )

        ReportPrinter.energy(
            "Importación de red",
            statistics["grid_import"]
        )

        ReportPrinter.energy(
            "Exportación a red",
            statistics["grid_export"]
        )

        ReportPrinter.blank()

        ReportPrinter.percent(
            "Autosuficiencia",
            statistics["self_sufficiency"]
        )

        ReportPrinter.percent(
            "Autoconsumo FV",
            statistics["self_consumption_ratio"]
        )

        ReportPrinter.percent(
            "Cobertura FV",
            statistics["coverage_ratio"]
        )

        ReportPrinter.percent(
            "Excedentes",
            statistics["surplus_ratio"]
        )

    def monthly_production(
        self,
        monthly_production
    ):

        ReportPrinter.title(
            "MONTHLY PV PRODUCTION"
        )

        ReportPrinter.blank()

        for month, value in monthly_production.items():

            ReportPrinter.energy(
                month.strftime("%m-%Y"),
                value
            )