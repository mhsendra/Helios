from helios.reports.solar_report_data import SolarReportData


class SolarReportText:
    """Genera textos interpretativos para el informe solar."""

    @staticmethod
    def executive_summary(
        data: SolarReportData,
    ) -> str:
        """
        Genera el resumen ejecutivo del informe.
        """

        if data is None:
            raise ValueError("report data is required")

        return (
            f"La instalación fotovoltaica analizada tiene una "
            f"potencia instalada de "
            f"{data.installed_power_kwp:.2f} kWp y una producción "
            f"solar estimada de "
            f"{data.yearly_production_kwh:,.0f} kWh anuales. "
            f"Esta producción permite cubrir directamente "
            f"{data.self_sufficiency_rate_percent:.1f} % del "
            f"consumo eléctrico anual mediante energía solar. "
            f"El ahorro económico estimado alcanza "
            f"{data.yearly_savings_eur:,.2f} € al año, con una "
            f"inversión de {data.investment_eur:,.2f} € y un "
            f"periodo de retorno de "
            f"{data.payback_years:.2f} años."
        )

    @staticmethod
    def production_analysis(
        data: SolarReportData,
    ) -> str:
        """
        Interpreta los principales resultados de producción solar.
        """

        if data is None:
            raise ValueError("report data is required")

        if data.capacity_factor_percent < 10:
            production_assessment = (
                "El factor de capacidad indica un aprovechamiento "
                "relativamente bajo de la potencia instalada."
            )
        elif data.capacity_factor_percent < 20:
            production_assessment = (
                "El factor de capacidad refleja un nivel de "
                "aprovechamiento razonable de la potencia instalada "
                "para una instalación fotovoltaica."
            )
        else:
            production_assessment = (
                "El factor de capacidad refleja un elevado "
                "aprovechamiento de la potencia fotovoltaica instalada."
            )

        return (
            f"La instalación genera aproximadamente "
            f"{data.yearly_production_kwh:,.0f} kWh al año, "
            f"equivalentes a "
            f"{data.specific_production_kwh_kwp:,.0f} kWh/kWp "
            f"de producción específica. "
            f"Se registran aproximadamente "
            f"{data.productive_hours:,} horas productivas al año "
            f"y una producción media de "
            f"{data.monthly_average_kwh:,.0f} kWh mensuales. "
            f"{production_assessment}"
        )

    @staticmethod
    def energy_balance_analysis(
        data: SolarReportData,
    ) -> str:
        """
        Interpreta el balance entre generación y consumo.
        """

        if data is None:
            raise ValueError("report data is required")

        if data.self_consumption_rate_percent < 30:
            autoconsumption_assessment = (
                "La tasa de autoconsumo es relativamente baja, "
                "por lo que existe un margen significativo de energía "
                "solar que no coincide temporalmente con la demanda."
            )
        elif data.self_consumption_rate_percent < 60:
            autoconsumption_assessment = (
                "La tasa de autoconsumo muestra un aprovechamiento "
                "moderado de la energía generada directamente en la "
                "instalación."
            )
        else:
            autoconsumption_assessment = (
                "La elevada tasa de autoconsumo indica un buen "
                "aprovechamiento directo de la energía fotovoltaica."
            )

        return (
            f"El consumo eléctrico anual asciende a "
            f"{data.yearly_consumption_kwh:,.0f} kWh. "
            f"De la producción fotovoltaica, "
            f"{data.self_consumption_kwh:,.0f} kWh se consumen "
            f"directamente en la instalación, mientras que "
            f"{data.grid_export_kwh:,.0f} kWh se vierten a la red. "
            f"La energía importada de la red asciende a "
            f"{data.grid_import_kwh:,.0f} kWh. "
            f"La tasa de autoconsumo es del "
            f"{data.self_consumption_rate_percent:.1f} % y la "
            f"autosuficiencia alcanza el "
            f"{data.self_sufficiency_rate_percent:.1f} %. "
            f"{autoconsumption_assessment}"
        )

    @staticmethod
    def economic_analysis(
        data: SolarReportData,
    ) -> str:
        """
        Interpreta los principales indicadores económicos.
        """

        if data is None:
            raise ValueError("report data is required")

        if data.net_present_value_eur > 0:
            npv_assessment = (
                "El valor actual neto es positivo, lo que indica que "
                "la inversión genera valor por encima de la tasa de "
                "descuento considerada."
            )
        elif data.net_present_value_eur < 0:
            npv_assessment = (
                "El valor actual neto es negativo, lo que indica que "
                "la inversión no alcanza la rentabilidad exigida "
                "bajo las hipótesis consideradas."
            )
        else:
            npv_assessment = (
                "El valor actual neto es aproximadamente nulo, "
                "por lo que la inversión se sitúa en el umbral de "
                "rentabilidad definido por la tasa de descuento."
            )

        if data.internal_rate_of_return_percent is not None:
            irr_text = (
                f"La tasa interna de retorno estimada es del "
                f"{data.internal_rate_of_return_percent:.2f} %."
            )
        else:
            irr_text = (
                "No ha sido posible determinar una tasa interna "
                "de retorno para las hipótesis consideradas."
            )

        return (
            f"La inversión neta asciende a "
            f"{data.investment_eur:,.2f} € y genera un ahorro anual "
            f"estimado de {data.yearly_savings_eur:,.2f} €. "
            f"El periodo de retorno de la inversión es de "
            f"{data.payback_years:.2f} años. "
            f"El valor actual neto alcanza "
            f"{data.net_present_value_eur:,.2f} €. "
            f"{irr_text} "
            f"{npv_assessment}"
        )

    @staticmethod
    def scenario_analysis(
        data: SolarReportData,
    ) -> str:
        """
        Interpreta los escenarios económicos.
        """

        if data is None:
            raise ValueError("report data is required")

        if not data.scenario_results:
            return (
                "No se han definido escenarios económicos "
                "alternativos para el análisis."
            )

        best = max(
            data.scenario_results,
            key=lambda result: result.npv,
        )

        worst = min(
            data.scenario_results,
            key=lambda result: result.npv,
        )

        return (
            f"El análisis de escenarios muestra una variación de "
            f"la rentabilidad en función de las hipótesis económicas. "
            f"El escenario con mayor valor actual neto es "
            f"«{best.name}», con un VAN de "
            f"{best.npv:,.2f} €, mientras que el escenario con menor "
            f"valor actual neto es «{worst.name}», con "
            f"{worst.npv:,.2f} €. "
            f"Esta comparación permite valorar la sensibilidad de "
            f"la inversión ante diferentes condiciones económicas."
        )

    @staticmethod
    def conclusion(
        data: SolarReportData,
    ) -> str:
        """
        Genera la conclusión general del informe.
        """

        if data is None:
            raise ValueError("report data is required")

        if (
            data.net_present_value_eur > 0
            and data.payback_years
            < data.economic_horizon_years
        ):
            investment_assessment = (
                "Desde el punto de vista económico, los resultados "
                "indican una inversión favorable bajo las hipótesis "
                "consideradas."
            )
        else:
            investment_assessment = (
                "Desde el punto de vista económico, los resultados "
                "requieren una valoración prudente bajo las hipótesis "
                "consideradas."
            )

        return (
            f"La instalación fotovoltaica analizada presenta una "
            f"producción anual estimada de "
            f"{data.yearly_production_kwh:,.0f} kWh y permite cubrir "
            f"el {data.self_sufficiency_rate_percent:.1f} % del "
            f"consumo eléctrico anual mediante generación solar. "
            f"El ahorro anual estimado es de "
            f"{data.yearly_savings_eur:,.2f} €, con un periodo de "
            f"retorno de {data.payback_years:.2f} años. "
            f"{investment_assessment}"
        )