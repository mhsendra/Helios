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

    def installation_simulation(
        self,
        configuration,
        recommendation,
        solar_configuration,
        specific_production,
    ):

        if configuration is None:

            raise ValueError(
                "Installation configuration is not available."
            )

        if recommendation is None:

            raise ValueError(
                "Solar installation simulation "
                "has not been calculated."
            )

        ReportPrinter.title(
            "SOLAR INSTALLATION SIMULATION"
        )

        ReportPrinter.blank()

        # ==================================================
        # CONFIGURACIÓN DE LA INSTALACIÓN
        # ==================================================

        ReportPrinter.subtitle(
            "INSTALLATION CONFIGURATION"
        )

        ReportPrinter.value(
            "Superficie disponible",
            configuration.available_area_m2,
            "m²",
            decimals=2,
        )

        if configuration.roof_width_m is not None:

            ReportPrinter.value(
                "Anchura del tejado",
                configuration.roof_width_m,
                "m",
                decimals=2,
            )

        if configuration.roof_height_m is not None:

            ReportPrinter.value(
                "Altura del tejado",
                configuration.roof_height_m,
                "m",
                decimals=2,
            )

        ReportPrinter.value(
            "Anchura del panel",
            configuration.panel_width_m,
            "m",
            decimals=3,
        )

        ReportPrinter.value(
            "Altura del panel",
            configuration.panel_height_m,
            "m",
            decimals=3,
        )

        ReportPrinter.value(
            "Potencia del panel",
            configuration.panel_power_wp,
            "Wp",
            decimals=0,
        )

        ReportPrinter.count(
            "Mínimo de paneles",
            configuration.min_panels,
        )

        if configuration.max_panels is not None:

            ReportPrinter.count(
                "Máximo de paneles",
                configuration.max_panels,
            )

        ReportPrinter.text(
            "Orientación de paneles",
            configuration.panel_orientation,
        )

        ReportPrinter.blank()

        # ==================================================
        # MANTENIMIENTO
        # ==================================================

        ReportPrinter.subtitle(
            "MAINTENANCE"
        )

        ReportPrinter.text(
            "Pasillo de mantenimiento",
            (
                "Sí"
                if configuration.maintenance_passage_required
                else "No"
            ),
        )

        if configuration.maintenance_passage_required:

            ReportPrinter.value(
                "Anchura del pasillo",
                configuration.maintenance_passage_width_m,
                "m",
                decimals=2,
            )

            ReportPrinter.text(
                "Orientación del pasillo",
                configuration.maintenance_passage_orientation,
            )

        ReportPrinter.blank()

        # ==================================================
        # CONFIGURACIÓN SOLAR / PVGIS
        # ==================================================

        ReportPrinter.subtitle(
            "SOLAR / PVGIS"
        )

        if solar_configuration is not None:

            ReportPrinter.text(
                "Tecnología FV",
                solar_configuration.pv_technology,
            )

            ReportPrinter.value(
                "Inclinación",
                solar_configuration.tilt,
                "°",
            )

            ReportPrinter.value(
                "Orientación",
                solar_configuration.azimuth,
                "°",
            )

            ReportPrinter.percent(
                "Pérdidas",
                solar_configuration.losses,
                decimals=1,
            )

            ReportPrinter.value(
                "Año de referencia",
                solar_configuration.reference_year,
                "",
                decimals=0,
            )

        if specific_production is not None:

            ReportPrinter.value(
                "Producción específica",
                specific_production,
                "kWh/kWp/año",
                decimals=2,
            )

        ReportPrinter.blank()

        # ==================================================
        # RESULTADO DE LA SIMULACIÓN
        # ==================================================

        ReportPrinter.subtitle(
            "SIMULATION RESULT"
        )

        ReportPrinter.count(
            "Paneles recomendados",
            recommendation.panel_count,
        )

        ReportPrinter.value(
            "Potencia instalada",
            recommendation.installed_power_kwp,
            "kWp",
            decimals=2,
        )

        ReportPrinter.energy(
            "Consumo anual",
            recommendation.annual_consumption_kwh,
        )

        ReportPrinter.energy(
            "Producción anual",
            recommendation.annual_production_kwh,
        )

        ReportPrinter.percent(
            "Autosuficiencia",
            recommendation.self_sufficiency_percent,
        )

        ReportPrinter.percent(
            "Cobertura FV",
            recommendation.production_coverage_percent,
        )

        ReportPrinter.energy(
            "Excedente energético",
            recommendation.energy_surplus_kwh,
        )

        ReportPrinter.energy(
            "Déficit energético",
            recommendation.energy_deficit_kwh,
        )

        ReportPrinter.blank()

        # ==================================================
        # DISTRIBUCIÓN FÍSICA
        # ==================================================

        ReportPrinter.subtitle(
            "PHYSICAL LAYOUT"
        )

        evaluation = recommendation.evaluation
        layout = evaluation.layout

        if layout is None:

            ReportPrinter.text(
                "Distribución física",
                "No disponible",
            )

        else:

            ReportPrinter.count(
                "Filas",
                layout.rows,
            )

            ReportPrinter.count(
                "Columnas",
                layout.columns,
            )

            ReportPrinter.text(
                "Orientación",
                layout.orientation,
            )

            ReportPrinter.value(
                "Superficie ocupada",
                evaluation.occupied_area_m2,
                "m²",
                decimals=2,
            )

            ReportPrinter.text(
                "Dimensiones ocupadas",
                (
                    f"{layout.occupied_width_m:.2f} × "
                    f"{layout.occupied_height_m:.2f} m"
                ),
            )

            if layout.walkway_width_m > 0:

                ReportPrinter.value(
                    "Pasillo de mantenimiento",
                    layout.walkway_width_m,
                    "m",
                    decimals=2,
                )

                ReportPrinter.text(
                    "Posición del pasillo",
                    layout.walkway_position,
                )

            ReportPrinter.value(
                "Superficie restante",
                recommendation.remaining_area_m2,
                "m²",
                decimals=2,
            )