import math

from helios.reports.solar_report_data import SolarReportData

class SolarReportText:
    """Genera textos interpretativos para el informe solar."""

    @staticmethod
    def _is_finite_metric(value: float | None) -> bool:
        """Indica si un indicador numérico está disponible y es finito."""
        return value is not None and math.isfinite(value)

    @staticmethod
    def _primary_economic_analysis_calculated(
        data: SolarReportData,
    ) -> bool:
        if data.selected_option_available:
            return data.selected_economic_analysis_calculated

        return data.economic_analysis_calculated

    @staticmethod
    def _primary_npv_eur(
        data: SolarReportData,
    ) -> float | None:
        if data.selected_option_available:
            return data.selected_net_present_value_eur

        return data.net_present_value_eur

    @staticmethod
    def _primary_payback_years(
        data: SolarReportData,
    ) -> float | None:
        if data.selected_option_available:
            return data.selected_payback_years

        return data.payback_years

    @staticmethod
    def _primary_irr_percent(
        data: SolarReportData,
    ) -> float | None:
        if data.selected_option_available:
            return data.selected_internal_rate_of_return_percent

        return data.internal_rate_of_return_percent

    @staticmethod
    def recommended_battery(
        data: SolarReportData,
    ):
        """Selecciona la batería con mayor VAN combinado positivo."""

        if data is None:
            raise ValueError("report data is required")

        recommendations = data.battery_recommendations or []

        viable = [
            recommendation
            for recommendation in recommendations
            if (
                recommendation.combined_economic_analysis_calculated
                and recommendation.combined_economic_npv_eur > 0.0
            )
        ]

        if not viable:
            return None

        return max(
            viable,
            key=lambda recommendation: (
                recommendation.combined_economic_npv_eur,
                -recommendation.capacity_kwh,
            ),
        )

    @staticmethod
    def executive_recommendation(
        data: SolarReportData,
    ) -> str:
        """Genera una recomendación breve para el resumen ejecutivo."""

        if data is None:
            raise ValueError("report data is required")

        primary_npv = SolarReportText._primary_npv_eur(data)
        primary_analysis_calculated = (
            SolarReportText._primary_economic_analysis_calculated(data)
        )

        if (
            primary_analysis_calculated
            and SolarReportText._is_finite_metric(primary_npv)
        ):
            if primary_npv > 0:
                pv_message = (
                    "La opción de instalación seleccionada "
                    "es recomendable bajo las hipótesis "
                    "económicas consideradas."
                )
            elif primary_npv < 0:
                pv_message = (
                    "La opción de instalación seleccionada no "
                    "resulta rentable bajo las hipótesis "
                    "económicas consideradas."
                )
            else:
                pv_message = (
                    "La opción de instalación seleccionada se "
                    "encuentra aproximadamente en el punto de "
                    "equilibrio económico."
                )
        else:
            pv_message = (
                "No puede establecerse una recomendación económica "
                "porque no hay un VAN válido disponible para la "
                "opción seleccionada ni para el análisis de referencia."
            )

        battery = SolarReportText.recommended_battery(data)

        if battery is not None:
            battery_message = (
                f"Para el almacenamiento, la capacidad de "
                f"{battery.capacity_kwh:.1f} kWh presenta el mejor "
                f"equilibrio entre ahorro, rentabilidad y valor "
                f"económico conjunto."
            )
        elif data.battery_recommendations and all(
            recommendation.economic_analysis_calculated
            and recommendation.combined_economic_analysis_calculated
            for recommendation in data.battery_recommendations
        ):
            battery_message = (
                "Ninguna de las capacidades de batería evaluadas "
                "presenta un VAN incremental positivo; no se "
                "recomienda añadir almacenamiento por rentabilidad "
                "económica bajo las hipótesis actuales."
            )
        elif data.battery_recommendations:
            battery_message = (
                "No puede establecerse una recomendación económica "
                "de almacenamiento porque el análisis no se ha "
                "completado para todas las capacidades evaluadas."
            )
        else:
            battery_message = (
                "No se dispone de una evaluación económica "
                "de capacidades de batería."
            )

        return (
            "<b>Recomendación general</b><br/>"
            f"{pv_message}<br/>"
            f"{battery_message}"
        )

    @staticmethod
    def executive_summary(data: SolarReportData) -> str:
        """Genera el resumen ejecutivo del informe solar."""

        if data is None:
            raise ValueError("report data is required")

        installed_power = (
            f"{data.installed_power_kwp:.2f} kWp"
            if (
                data.installed_power_kwp is not None
                and math.isfinite(data.installed_power_kwp)
            )
            else "potencia no disponible"
        )

        panel_description = ""
        if (
            data.panel_count is not None
            and data.panel_power_wp is not None
            and math.isfinite(data.panel_power_wp)
        ):
            panel_description = (
                f" y {data.panel_count} paneles de "
                f"{data.panel_power_wp:.0f} W"
            )

        production = (
            f"{data.yearly_production_kwh:,.0f} kWh"
            if (
                data.yearly_production_kwh is not None
                and math.isfinite(data.yearly_production_kwh)
            )
            else "producción no disponible"
        )

        summary = (
            f"La instalación fotovoltaica propuesta cuenta con "
            f"{installed_power}{panel_description}, con una producción "
            f"anual estimada de {production}."
        )

        if (
            data.self_sufficiency_rate_percent is not None
            and math.isfinite(data.self_sufficiency_rate_percent)
        ):
            summary += (
                " La autosuficiencia energética estimada es del "
                f"{data.self_sufficiency_rate_percent:.1f} %."
            )

        if not SolarReportText._primary_economic_analysis_calculated(data):
            summary += (
                " El análisis económico no se ha calculado; "
                "no se presentan estimaciones económicas."
            )
            return summary

        if (
            data.yearly_savings_eur is not None
            and math.isfinite(data.yearly_savings_eur)
        ):
            summary += (
                " El ahorro anual estimado es de "
                f"{data.yearly_savings_eur:,.2f} €."
            )

        
        if (
            data.investment_eur is not None
            and math.isfinite(data.investment_eur)
        ):
            summary += (
                " La inversión inicial estimada es de "
                f"{data.investment_eur:,.2f} €."
            )
        
        
        if (
            SolarReportText._primary_economic_analysis_calculated(data)
            and SolarReportText._primary_payback_years(data) is not None
            and math.isfinite(
                SolarReportText._primary_payback_years(data)
            )
        ):
            summary += (
                " El periodo de recuperación de la inversión "
                f"es de {SolarReportText._primary_payback_years(data):.2f} años."
            )

        return summary

    @staticmethod
    def quick_diagnostic(
        data: SolarReportData,
    ) -> str:
        """
        Genera un diagnóstico ejecutivo breve y orientado a decisión.

        Resume producción frente a consumo, aprovechamiento solar,
        excedentes, dependencia de red y viabilidad económica.
        """

        if data is None:
            raise ValueError("report data is required")

        if data.yearly_consumption_kwh > 0:
            production_ratio = (
                data.yearly_production_kwh
                / data.yearly_consumption_kwh
                * 100
            )
        else:
            production_ratio = 0.0

        if data.yearly_production_kwh > 0:
            export_ratio = (
                data.grid_export_kwh
                / data.yearly_production_kwh
                * 100
            )
        else:
            export_ratio = 0.0

        if production_ratio >= 100:
            production_message = (
                f"✓ La instalación puede generar el "
                f"{production_ratio:.1f} % del consumo anual de referencia."
            )
        else:
            production_message = (
                f"⚠ La producción anual cubre aproximadamente el "
                f"{production_ratio:.1f} % del consumo anual de referencia."
            )

        if export_ratio >= 50:
            export_message = (
                f"⚠ Aproximadamente el {export_ratio:.1f} % de la "
                f"energía generada se vierte a la red."
            )
        elif export_ratio > 0:
            export_message = (
                f"ℹ Existe un excedente equivalente al "
                f"{export_ratio:.1f} % de la producción."
            )
        else:
            export_message = (
                "✓ No se han identificado excedentes fotovoltaicos "
                "significativos en el escenario analizado."
            )

        primary_analysis_calculated = (
            SolarReportText._primary_economic_analysis_calculated(data)
        )
        primary_npv = SolarReportText._primary_npv_eur(data)
        primary_payback = SolarReportText._primary_payback_years(data)
        primary_irr = SolarReportText._primary_irr_percent(data)

        if not primary_analysis_calculated:
            economic_message = (
                "ℹ No se puede evaluar la rentabilidad porque "
                "el análisis económico no se ha calculado."
            )
        else:
            economic_parts = []

            if SolarReportText._is_finite_metric(primary_npv):
                economic_parts.append(
                    f"VAN de {primary_npv:,.2f} €"
                )

            if SolarReportText._is_finite_metric(primary_payback):
                economic_parts.append(
                    "recuperación de la inversión en "
                    f"{primary_payback:.2f} años"
                )

            if SolarReportText._is_finite_metric(primary_irr):
                economic_parts.append(
                    "TIR del "
                    f"{primary_irr:.2f} %"
                )

            if economic_parts:
                economic_message = (
                    "✓ Evaluación económica de la opción seleccionada: "
                    + "; ".join(economic_parts)
                    + "."
                )
            else:
                economic_message = (
                    "ℹ El análisis económico está marcado como "
                    "calculado, pero no hay indicadores económicos "
                    "válidos disponibles para la opción seleccionada."
                )

        if (
            data.grid_export_kwh > 0
            and data.grid_import_kwh > 0
        ):
            flexibility_message = (
                "✓ Existe potencial para aumentar el aprovechamiento "
                "solar mediante gestión de cargas y/o almacenamiento."
            )
        else:
            flexibility_message = (
                "ℹ El balance energético presenta un menor margen "
                "para desplazar energía mediante almacenamiento."
            )

        return "<br/>".join(
            [
                "<b>Diagnóstico rápido</b>",
                production_message,
                (
                    f"✓ La autosuficiencia energética estimada es del "
                    f"{data.self_sufficiency_rate_percent:.1f} %."
                ),
                export_message,
                economic_message,
                flexibility_message,
            ]
        )

    @staticmethod
    def energy_flow_summary(
        data: SolarReportData,
    ) -> str:
        """Resume el reparto de la producción y la demanda eléctrica."""

        if data is None:
            raise ValueError("report data is required")

        battery_losses_kwh = max(
            0.0,
            data.yearly_battery_losses_kwh,
        )

        battery_losses_text = ""

        if battery_losses_kwh > 0:
            battery_losses_text = (
                f" y {battery_losses_kwh:,.0f} kWh se pierden en los "
                f"procesos de carga y descarga de la batería"
            )

        return (
            f"De los {data.yearly_production_kwh:,.0f} kWh generados "
            f"por la instalación fotovoltaica, "
            f"{data.self_consumption_kwh:,.0f} kWh se utilizan "
            f"directamente en la vivienda y "
            f"{data.grid_export_kwh:,.0f} kWh se vierten a la red"
            f"{battery_losses_text}. "
            f"En cuanto a la demanda, de los "
            f"{data.yearly_consumption_kwh:,.0f} kWh consumidos "
            f"anualmente, {data.self_consumption_kwh:,.0f} kWh "
            f"quedan cubiertos por la generación solar y "
            f"{data.grid_import_kwh:,.0f} kWh deben importarse "
            f"de la red."
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
        """Interpreta el balance entre generación y consumo."""

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

        battery_losses_kwh = max(
            0.0,
            data.yearly_battery_losses_kwh,
        )

        battery_losses_analysis = ""

        if battery_losses_kwh > 0:
            battery_losses_percent = (
                battery_losses_kwh / data.yearly_production_kwh * 100
                if data.yearly_production_kwh > 0
                else 0.0
            )

            battery_losses_analysis = (
                f" Las pérdidas energéticas asociadas a los procesos "
                f"de carga y descarga de la batería ascienden a "
                f"{battery_losses_kwh:,.0f} kWh, equivalentes al "
                f"{battery_losses_percent:.1f} % de la producción "
                f"fotovoltaica."
            )

        return (
            f"El consumo eléctrico anual asciende a "
            f"{data.yearly_consumption_kwh:,.0f} kWh. "
            f"De la producción fotovoltaica, "
            f"{data.self_consumption_kwh:,.0f} kWh se consumen "
            f"directamente en la instalación, mientras que "
            f"{data.grid_export_kwh:,.0f} kWh se vierten a la red."
            f"{battery_losses_analysis} "
            f"La energía importada de la red asciende a "
            f"{data.grid_import_kwh:,.0f} kWh. "
            f"La tasa de autoconsumo es del "
            f"{data.self_consumption_rate_percent:.1f} % y la "
            f"autosuficiencia alcanza el "
            f"{data.self_sufficiency_rate_percent:.1f} %. "
            f"{autoconsumption_assessment}"
        )

    @staticmethod
    def energy_situation_analysis(
        data: SolarReportData,
    ) -> str:
        """Interpreta la situación energética de referencia."""

        if data is None:
            raise ValueError("report data is required")

        monthly_average = (
            data.yearly_consumption_kwh / 12
        )

        return (
            f"El consumo eléctrico anual de referencia asciende a "
            f"{data.yearly_consumption_kwh:,.2f} kWh, con un consumo medio "
            f"de aproximadamente {monthly_average:,.2f} kWh al mes. "
            f"Este perfil de consumo constituye la base utilizada para "
            f"comparar la generación fotovoltaica con la demanda eléctrica "
            f"y para evaluar el autoconsumo, la autosuficiencia y la "
            f"necesidad de energía importada de la red. "
            f"El análisis utiliza el año de referencia "
            f"{data.consumption_reference_year} como año representativo "
            f"del consumo."
        )

    @staticmethod
    def methodology_analysis(
        data: SolarReportData,
    ) -> str:
        """
        Explica la metodología utilizada para interpretar los resultados.
        """

        if data is None:
            raise ValueError("report data is required")

        return (
            f"El análisis energético utiliza un perfil de consumo "
            f"representativo correspondiente al año "
            f"{data.consumption_reference_year}. La producción "
            "fotovoltaica se simula con resolución horaria y se "
            "compara con dicho perfil para determinar el autoconsumo, "
            "la autosuficiencia, la energía importada y los excedentes. "
            "El análisis económico utiliza las hipótesis de inversión, "
            "degradación, evolución de los precios de la electricidad, "
            "mantenimiento y tasa de descuento definidas para el proyecto. "
            "Los resultados representan una simulación basada en estas "
            "hipótesis y deben interpretarse como una estimación del "
            "comportamiento esperado, no como una garantía de resultados "
            "futuros."
        )

    @staticmethod
    def methodology_conclusion(
        data: SolarReportData,
    ) -> str:
        """
        Resume las limitaciones prácticas de los resultados simulados.
        """

        if data is None:
            raise ValueError("report data is required")

        return (
            "Los resultados reales pueden diferir de las estimaciones "
            "por variaciones meteorológicas, cambios en los hábitos "
            "de consumo, degradación de los equipos y evolución de "
            "los precios de la electricidad. Antes de tomar una "
            "decisión de inversión, conviene contrastar estas "
            "estimaciones con las condiciones concretas de la "
            "instalación y revisar las hipótesis económicas aplicadas."
        )

    @staticmethod
    def economic_analysis(
        data: SolarReportData,
    ) -> str:
        """Interpreta los principales indicadores económicos."""

        if data is None:
            raise ValueError("report data is required")

        selected_option = data.selected_option_available

        if not SolarReportText._primary_economic_analysis_calculated(data):
            message = (
                "El análisis económico de la instalación no se ha "
                "calculado. Por tanto, no es posible interpretar "
                "el valor actual neto, la tasa interna de retorno "
                "ni el periodo de recuperación de la inversión."
            )

            if not selected_option and SolarReportText._is_finite_metric(
                data.yearly_savings_eur
            ):
                message += (
                    " El ahorro anual estimado a partir del balance "
                    "energético de referencia es de "
                    f"{data.yearly_savings_eur:,.2f} €."
                )

            return message

        primary_npv = SolarReportText._primary_npv_eur(data)
        primary_payback = SolarReportText._primary_payback_years(data)
        primary_irr = SolarReportText._primary_irr_percent(data)

        npv_is_finite = SolarReportText._is_finite_metric(
            primary_npv
        )
        payback_is_finite = SolarReportText._is_finite_metric(
            primary_payback
        )
        irr_is_finite = SolarReportText._is_finite_metric(
            primary_irr
        )

        if not npv_is_finite:
            npv_text = (
                "El valor actual neto no está disponible como indicador "
                "válido para la opción seleccionada, por lo que no puede "
                "determinarse su rentabilidad a partir de este resultado."
            )
        elif primary_npv > 0:
            npv_text = (
                "El valor actual neto de la opción seleccionada alcanza "
                f"{primary_npv:,.2f} €. "
                "El valor actual neto es positivo, lo que indica que la "
                "inversión genera valor por encima del valor exigido, "
                "una vez tenido en cuenta el valor del dinero en el tiempo."
            )
        elif primary_npv < 0:
            npv_text = (
                "El valor actual neto de la opción seleccionada alcanza "
                f"{primary_npv:,.2f} €. "
                "El valor actual neto es negativo, lo que indica que, "
                "bajo las hipótesis consideradas, el valor de los ahorros "
                "futuros no alcanza a compensar la inversión una vez "
                "tenido en cuenta el valor del dinero en el tiempo."
            )
        else:
            npv_text = (
                "El valor actual neto de la opción seleccionada es "
                "aproximadamente nulo, lo que indica que, bajo las "
                "hipótesis consideradas, los ahorros futuros compensan "
                "aproximadamente la inversión una vez tenido en cuenta "
                "el valor del dinero en el tiempo."
            )

        if irr_is_finite:
            irr_text = (
                "La tasa interna de retorno estimada de la opción "
                "seleccionada es del "
                f"{primary_irr:.2f} %."
            )
        else:
            irr_text = (
                "No ha sido posible determinar una tasa interna de "
                "retorno válida para la opción seleccionada."
            )

        if payback_is_finite:
            payback_text = (
                "El periodo de recuperación de la inversión de la "
                "opción seleccionada es de "
                f"{primary_payback:.2f} años."
            )
        else:
            payback_text = (
                "El periodo de recuperación de la inversión de la "
                "opción seleccionada no está disponible como "
                "indicador válido."
            )

        if selected_option:
            investment = data.selected_investment_eur
            savings = data.selected_yearly_savings_eur

            investment_label = "La inversión neta de la opción seleccionada"
            savings_label = (
                "El ahorro neto estimado del primer año de la opción seleccionada"
            )
        else:
            investment = data.investment_eur
            savings = data.yearly_savings_eur

            investment_label = "La inversión neta de referencia"
            savings_label = "El ahorro anual de referencia"

        if SolarReportText._is_finite_metric(investment):
            investment_text = (
                f"{investment_label} asciende a {investment:,.2f} €."
            )
        else:
            investment_text = (
                f"{investment_label.lower()} no está disponible."
            )

        if SolarReportText._is_finite_metric(savings):
            savings_text = (
                f"{savings_label} es de {savings:,.2f} €."
            )
        else:
            savings_text = (
                f"{savings_label} no está disponible."
            )

        return (
            "Los indicadores de VAN, TIR y periodo de recuperación "
            "corresponden a la opción seleccionada por el optimizador. "
            f"{investment_text} {savings_text} "
            f"{payback_text} {npv_text} {irr_text}"
        )

    @staticmethod
    def battery_analysis(
        data: SolarReportData,
    ) -> str:
        """
        Interpreta los resultados técnicos y económicos de las
        capacidades de batería evaluadas.
        """
        if data is None:
            raise ValueError("report data is required")

        recommendations = data.battery_recommendations

        if not recommendations:
            return (
                "No se han realizado evaluaciones económicas de "
                "capacidades de batería para esta instalación."
            )

        best_additional_savings = max(
            recommendations,
            key=lambda recommendation:
            recommendation.annual_additional_savings_eur,
        )

        text = (
            f"Se han evaluado {len(recommendations)} capacidades "
            f"de batería entre "
            f"{min(r.capacity_kwh for r in recommendations):.1f} kWh "
            f"y {max(r.capacity_kwh for r in recommendations):.1f} kWh. "
            f"La batería permite almacenar parte del excedente "
            f"fotovoltaico para utilizarlo posteriormente, reduciendo "
            f"la energía que debe importarse de la red."
        )

        text += (
            f" La capacidad de "
            f"{best_additional_savings.capacity_kwh:.1f} kWh "
            f"alcanza el mayor ahorro adicional anual, con "
            f"{best_additional_savings.annual_additional_savings_eur:,.2f} € "
            f"respecto a la instalación fotovoltaica sin batería."
        )

        if (
            best_additional_savings.annual_import_savings_eur
            is not None
            and best_additional_savings.annual_export_compensation_lost_eur
            is not None
        ):
            text += (
                f" De ese resultado, "
                f"{best_additional_savings.annual_import_savings_eur:,.2f} € "
                f"corresponden al ahorro por menor importación de red, "
                f"mientras que "
                f"{best_additional_savings.annual_export_compensation_lost_eur:,.2f} € "
                f"representan la compensación de excedentes no percibida "
                f"por almacenar esa energía. El ahorro neto ya indicado "
                f"descuenta este último importe."
            )

        positive_recommendations = [
            recommendation
            for recommendation in recommendations
            if recommendation.capacity_kwh > 0.0
        ]

        economic_calculated = bool(positive_recommendations) and all(
            recommendation.economic_analysis_calculated
            for recommendation in positive_recommendations
        )

        combined_calculated = all(
            recommendation.combined_economic_analysis_calculated
            for recommendation in recommendations
        )

        if not economic_calculated:
            text += (
                " No se ha realizado el cálculo de rentabilidad "
                "del almacenamiento para todas las capacidades "
                "evaluadas. Los valores económicos de VAN, TIR y "
                "recuperación de la inversión no permiten establecer "
                "una conclusión de rentabilidad. Por tanto, el mayor "
                "ahorro anual no debe interpretarse por sí solo como "
                "la capacidad económicamente óptima."
            )

            if not combined_calculated:
                text += (
                    " Tampoco se ha calculado el VAN conjunto de la "
                    "instalación fotovoltaica y la batería para todas "
                    "las capacidades."
                )

            return text

        viable = [
            recommendation
            for recommendation in recommendations
            if (
                recommendation.economic_npv_eur is not None
                and math.isfinite(recommendation.economic_npv_eur)
                and recommendation.economic_npv_eur > 0.0
            )
        ]

        best_economic = None

        if viable:
            best_economic = max(
                viable,
                key=lambda recommendation: (
                    recommendation.economic_npv_eur,
                    -recommendation.capacity_kwh,
                ),
            )

            economic_payback = (
                "N/D"
                if (
                    best_economic.economic_payback_years is None
                    or not math.isfinite(
                        best_economic.economic_payback_years
                    )
                )
                else (
                    f"{best_economic.economic_payback_years:.2f} años"
                )
            )

            marginal_payback = (
                "N/D"
                if (
                    best_economic.marginal_payback_years is None
                    or not math.isfinite(
                        best_economic.marginal_payback_years
                    )
                )
                else (
                    f"{best_economic.marginal_payback_years:.2f} años"
                )
            )

            text += (
                f" La capacidad de "
                f"{best_economic.capacity_kwh:.1f} kWh presenta el "
                f"mayor VAN de batería, con "
                f"{best_economic.economic_npv_eur:,.2f} €. "
                f"Su ahorro adicional anual es de "
                f"{best_economic.annual_additional_savings_eur:,.2f} € "
                f"y su recuperación económica estimada es de "
                f"{economic_payback}."
            )

            text += (
                f" Para esta capacidad, el ahorro incremental respecto "
                f"a la capacidad anterior es de "
                f"{best_economic.incremental_savings_eur:,.2f} €, "
                f"equivalente a "
                f"{best_economic.marginal_savings_per_kwh:,.2f} €/kWh "
                f"de capacidad añadida, con una recuperación marginal "
                f"estimada de {marginal_payback}."
            )

            text += (
                f" {len(viable)} de las {len(recommendations)} "
                f"capacidades evaluadas presentan un VAN incremental "
                f"de batería positivo bajo las hipótesis económicas utilizadas."
            )
        else:
            text += (
                " Ninguna de las capacidades evaluadas presenta "
                "un VAN incremental positivo de batería. Esto no "
                "determina por sí solo la recomendación global: "
                "debe evaluarse por separado el VAN conjunto de "
                "la instalación fotovoltaica y la batería."
            )

        # El análisis del VAN conjunto se mantiene separado del
        # análisis incremental de la batería.
        if not combined_calculated:
            text += (
                " No se ha calculado el VAN conjunto de la instalación "
                "fotovoltaica y la batería para todas las capacidades; "
                "por tanto, no puede establecerse una recomendación "
                "económica conjunta."
            )
        else:
            valid_combined = [
                recommendation
                for recommendation in recommendations
                if (
                    recommendation.combined_economic_npv_eur is not None
                    and math.isfinite(
                        recommendation.combined_economic_npv_eur
                    )
                )
            ]

            if not valid_combined:
                text += (
                    " No hay valores finitos de VAN conjunto para "
                    "establecer una comparación económica fiable."
                )
            else:
                valid_combined_viable = [
                    recommendation
                    for recommendation in valid_combined
                    if recommendation in viable
                ]

                best_combined_overall = max(
                    valid_combined,
                    key=lambda recommendation: (
                        recommendation.combined_economic_npv_eur,
                        -recommendation.capacity_kwh,
                    ),
                )

                best_combined_viable = (
                    max(
                        valid_combined_viable,
                        key=lambda recommendation: (
                            recommendation.combined_economic_npv_eur,
                            recommendation.economic_npv_eur,
                            -recommendation.capacity_kwh,
                        ),
                    )
                    if valid_combined_viable
                    else None
                )

                if best_combined_viable is not None:

                    text += (
                        f" La capacidad de "
                        f"{best_combined_viable.capacity_kwh:.1f} kWh "
                        f"presenta el mayor VAN conjunto del sistema FV + batería, "
                        f"con "
                        f"{best_combined_viable.combined_economic_npv_eur:,.2f} €, "
                        f"entre las alternativas con VAN incremental positivo."
                    )

                    if (
                        best_economic is not None
                        and best_combined_overall.capacity_kwh
                        != best_economic.capacity_kwh
                    ):
                        text += (
                            " Ambos indicadores deben considerarse "
                            "conjuntamente antes de establecer una "
                            "recomendación global."
                        )

                else:
                    text += (
                        " Ninguna capacidad con VAN incremental de batería "
                        "positivo dispone de un VAN conjunto válido para "
                        "establecer una recomendación global."
                        if not viable
                        else
                        " Ninguna capacidad con VAN incremental de batería "
                        "positivo tiene un VAN conjunto finito para "
                        "comparar las alternativas."
                    )

                if (
                    best_combined_overall.capacity_kwh
                    != (
                        best_combined_viable.capacity_kwh
                        if best_combined_viable is not None
                        else None
                    )
                ):
                    text += (
                        f" Considerando todas las capacidades con VAN "
                        f"conjunto válido, el mayor VAN conjunto es de "
                        f"{best_combined_overall.combined_economic_npv_eur:,.2f} € "
                        f"para {best_combined_overall.capacity_kwh:.1f} kWh."
                    )

                    if best_combined_overall not in valid_combined_viable:
                        text += (
                            " Esta alternativa no presenta un VAN "
                            "incremental positivo de batería y, por tanto, "
                            "el mayor VAN conjunto no basta por sí solo "
                            "para recomendar añadir almacenamiento."
                        )

                # Clasificar la neutralidad y la falta de rentabilidad
                # conjunta con el 1 % de la inversión total como margen.
                neutral_capacities = []
                unprofitable_larger = []

                largest_viable_capacity = (
                    max(
                        recommendation.capacity_kwh
                        for recommendation in viable
                    )
                    if viable
                    else None
                )

                for recommendation in valid_combined:
                    total_investment_eur = (
                        data.investment_eur
                        + recommendation.incremental_battery_cost_eur
                    )

                    if (
                        not math.isfinite(total_investment_eur)
                        or total_investment_eur <= 0.0
                    ):
                        continue

                    neutral_tolerance_eur = (
                        total_investment_eur * 0.01
                    )
                    combined_npv = (
                        recommendation.combined_economic_npv_eur
                    )

                    if abs(combined_npv) <= neutral_tolerance_eur:
                        neutral_capacities.append(
                            recommendation.capacity_kwh
                        )
                    elif (
                        combined_npv < -neutral_tolerance_eur
                        and largest_viable_capacity is not None
                        and recommendation.capacity_kwh
                        > largest_viable_capacity
                    ):
                        unprofitable_larger.append(
                            recommendation.capacity_kwh
                        )

                if neutral_capacities:
                    neutral_capacity_labels = sorted(
                        {
                            f"{capacity:.1f} kWh"
                            for capacity in neutral_capacities
                        },
                        key=lambda label: float(label.split()[0]),
                    )

                    capacities_text = ", ".join(
                        neutral_capacity_labels
                    )

                    if len(neutral_capacity_labels) == 1:
                        text += (
                            f" La capacidad de {capacities_text} presenta "
                            f"un VAN conjunto próximo al umbral de "
                            f"neutralidad económica, considerando como "
                            f"margen el 1 % de la inversión total de "
                            f"cada alternativa. Por tanto, su resultado "
                            f"debe interpretarse como económicamente "
                            f"neutro bajo las hipótesis consideradas."
                        )
                    else:
                        text += (
                            f" Las capacidades {capacities_text} presentan "
                            f"un VAN conjunto próximo al umbral de "
                            f"neutralidad económica, considerando como "
                            f"margen el 1 % de la inversión total de "
                            f"cada alternativa. Por tanto, sus resultados "
                            f"deben interpretarse como económicamente "
                            f"neutros bajo las hipótesis consideradas."
                        )

                if unprofitable_larger:
                    capacities_text = ", ".join(
                        f"{capacity:.1f} kWh"
                        for capacity in sorted(unprofitable_larger)
                    )

                    if len(unprofitable_larger) == 1:
                        text += (
                            f" La capacidad de {capacities_text} no "
                            f"resulta rentable en términos de VAN "
                            f"conjunto bajo las hipótesis consideradas."
                        )
                    else:
                        text += (
                            f" Las capacidades de {capacities_text} "
                            f"no resultan rentables en términos de "
                            f"VAN conjunto bajo las hipótesis "
                            f"consideradas."
                        )

        text += (
            " El ahorro marginal por kWh representa el ahorro adicional "
            "obtenido por cada kWh de capacidad de batería añadido, "
            "mientras que el periodo de recuperación marginal expresa "
            "el tiempo estimado necesario para recuperar el coste "
            "incremental de esa capacidad."
        )

        return text

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

        base = next(
            (
                result
                for result in data.scenario_results
                if result.name.lower() == "base"
            ),
            None,
        )

        text = (
            f"El análisis de escenarios muestra cómo la rentabilidad "
            f"de la instalación varía en función de las hipótesis "
            f"económicas consideradas. "
        )

        if base is not None:
            text += (
                f"En el escenario «Base», el ahorro anual estimado es "
                f"de {base.annual_savings:,.2f} €, con un periodo de "
                f"recuperación de la inversión de {base.payback_years:.2f} años "
                f"y un VAN de "
                f"{base.npv:,.2f} €. "
            )

        text += (
            f"En el escenario «{worst.name}», el VAN se sitúa en "
            f"{worst.npv:,.2f} €, mientras que el escenario "
            f"«{best.name}» alcanza {best.npv:,.2f} €. "
            f"El intervalo entre ambos resultados muestra la sensibilidad "
            f"de la rentabilidad económica a las hipótesis utilizadas."
        )

        return text

    @staticmethod
    def energy_situation_conclusion(
        data: SolarReportData,
    ) -> str:
        """
        Resume la importancia del perfil de consumo de referencia
        sin repetir las cifras presentadas en el análisis.
        """

        if data is None:
            raise ValueError("report data is required")

        return (
            f"El perfil de consumo de referencia constituye la base "
            f"para valorar la producción fotovoltaica y la "
            f"autosuficiencia alcanzable. Además del consumo total, "
            f"su distribución temporal condiciona qué parte de la "
            f"generación solar puede aprovecharse directamente."
        )

    @staticmethod
    def installation_conclusion(
        data: SolarReportData,
    ) -> str:
        """
        Resume la configuración fotovoltaica sin anticipar
        el análisis de producción y del balance energético.
        """

        if data is None:
            raise ValueError("report data is required")

        return (
            f"La configuración fotovoltaica tiene una potencia "
            f"instalada de {data.installed_power_kwp:.2f} kWp. "
            f"Este valor constituye la base para estimar la "
            f"producción solar y evaluar el aprovechamiento "
            f"energético de la instalación en los apartados "
            f"siguientes."
        )

    @staticmethod
    def production_conclusion(
        data: SolarReportData,
    ) -> str:
        """
        Explica la diferencia entre producción anual
        y autosuficiencia energética.
        """

        if data is None:
            raise ValueError("report data is required")

        if data.yearly_consumption_kwh > 0:
            production_ratio = (
                data.yearly_production_kwh
                / data.yearly_consumption_kwh
                * 100
            )
        else:
            production_ratio = 0.0

        return (
            f"La instalación genera aproximadamente "
            f"{data.yearly_production_kwh:,.0f} kWh/año, "
            f"equivalentes al {production_ratio:.1f} % del consumo "
            f"eléctrico anual de referencia. Sin embargo, la "
            f"autosuficiencia energética se sitúa en el "
            f"{data.self_sufficiency_rate_percent:.1f} %. "
            f"Esta diferencia se debe a que la generación "
            f"fotovoltaica y la demanda eléctrica no siempre "
            f"coinciden temporalmente. Por ello, la producción "
            f"anual no equivale a la energía solar que la vivienda "
            f"puede aprovechar directamente."
        )

    @staticmethod
    def production_statistics_conclusion(
        data: SolarReportData,
    ) -> str:
        """
        Interpreta el valor de las estadísticas de producción
        sin repetir las métricas mostradas en la tabla.
        """

        if data is None:
            raise ValueError("report data is required")

        return (
            "Las estadísticas complementan la estimación de "
            "producción anual y ayudan a contextualizar el "
            "rendimiento de la instalación. Para interpretar "
            "adecuadamente estos resultados, también debe "
            "considerarse cómo se distribuye la generación "
            "a lo largo del año."
        )

    @staticmethod
    def energy_balance_conclusion(
        data: SolarReportData,
    ) -> str:
        """
        Interpreta las consecuencias del balance energético
        sin repetir los valores de la tabla.
        """

        if data is None:
            raise ValueError("report data is required")

        if data.grid_export_kwh > 0 and data.grid_import_kwh > 0:
            return (
                "La presencia simultánea de excedentes fotovoltaicos "
                "y energía importada confirma que la generación y "
                "la demanda no siempre coinciden temporalmente. "
                "Desplazar consumos hacia las horas de mayor producción "
                "o incorporar almacenamiento podría aumentar el "
                "aprovechamiento de la energía solar. La conveniencia "
                "de estas medidas debe evaluarse teniendo en cuenta "
                "el perfil horario y sus costes."
            )

        return (
            "El balance no presenta simultáneamente excedentes "
            "fotovoltaicos e importación de energía en los resultados "
            "analizados. La utilidad de desplazar consumos o incorporar "
            "almacenamiento debe valorarse a partir del perfil horario "
            "y de los costes asociados."
        )

    @staticmethod
    def economic_conclusion(
        data: SolarReportData,
    ) -> str:
        """
        Sintetiza la rentabilidad de la opción seleccionada
        sin repetir los indicadores económicos de la tabla.
        """

        if data is None:
            raise ValueError("report data is required")

        if not SolarReportText._primary_economic_analysis_calculated(data):
            return (
                "El análisis económico no se ha calculado. Por tanto, "
                "todavía no es posible establecer una conclusión "
                "fundamentada sobre la rentabilidad de la opción "
                "seleccionada."
            )

        primary_npv = SolarReportText._primary_npv_eur(data)

        if not SolarReportText._is_finite_metric(primary_npv):
            assessment = (
                "El VAN de la opción seleccionada no está disponible "
                "como indicador válido, por lo que no puede determinarse "
                "su rentabilidad con este resultado."
            )
        elif primary_npv > 0:
            assessment = (
                "El VAN positivo indica que la opción seleccionada "
                "genera valor bajo las hipótesis económicas consideradas."
            )
        elif primary_npv < 0:
            assessment = (
                "El VAN negativo indica que la opción seleccionada "
                "no alcanza la rentabilidad exigida bajo las hipótesis "
                "consideradas."
            )
        else:
            assessment = (
                "El VAN aproximadamente nulo indica que la opción "
                "seleccionada se sitúa en torno al umbral de rentabilidad "
                "establecido por las hipótesis del análisis."
            )

        return (
            f"{assessment} La conclusión depende de la evolución "
            f"de los precios de la electricidad, la degradación "
            f"de los equipos, los costes de mantenimiento y la "
            f"tasa de descuento. Conviene revisar estas hipótesis "
            f"mediante los escenarios económicos antes de tomar "
            f"una decisión de inversión."
        )

    @staticmethod
    def scenario_conclusion(data: SolarReportData) -> str:
        """Resume la sensibilidad de la rentabilidad entre escenarios."""

        if data is None:
            raise ValueError("report data is required")

        if not data.economic_analysis_calculated:
            return (
                "No se puede evaluar la sensibilidad económica porque "
                "no se ha calculado la rentabilidad de la inversión."
            )

        if not data.scenario_results:
            return (
                "No se han definido escenarios económicos alternativos "
                "para evaluar la sensibilidad de la inversión."
            )

        worst = min(
            data.scenario_results,
            key=lambda result: result.npv,
        )
        best = max(
            data.scenario_results,
            key=lambda result: result.npv,
        )

        if worst.npv > 0.0:
            assessment = (
                "Todos los escenarios evaluados presentan un VAN positivo. "
                "La rentabilidad de la inversión es positiva bajo todas "
                "las hipótesis económicas analizadas."
            )
        elif best.npv < 0.0:
            assessment = (
                "Todos los escenarios evaluados presentan un VAN negativo. "
                "Bajo las hipótesis analizadas, la inversión no alcanza "
                "el umbral de rentabilidad."
            )
        elif worst.npv == 0.0 and best.npv == 0.0:
            assessment = (
                "Todos los escenarios evaluados presentan un VAN nulo, "
                "por lo que la inversión se sitúa en el umbral de rentabilidad."
            )
        else:
            assessment = (
                f"La rentabilidad cambia según las hipótesis consideradas: "
                f"el escenario «{worst.name}» presenta un VAN de "
                f"{worst.npv:,.2f} €, mientras que el escenario "
                f"«{best.name}» alcanza {best.npv:,.2f} €. "
                f"Los resultados muestran que la inversión puede quedar "
                f"por debajo o por encima del umbral de rentabilidad."
            )

        return (
            f"{assessment} La comparación permite valorar la sensibilidad "
            f"de la inversión ante cambios en los ahorros, los precios de la "
            f"electricidad, los costes de mantenimiento y la tasa de descuento. "
            f"Los resultados son estimaciones sujetas a las hipótesis utilizadas, "
            f"no garantías de resultados futuros."
        )

    @staticmethod
    def battery_conclusion(
        data: SolarReportData,
    ) -> str:
        """Resume la recomendación económica de las baterías evaluadas."""

        if data is None:
            raise ValueError("report data is required")

        recommendations = data.battery_recommendations

        if not recommendations:
            return (
                "No se dispone de capacidades de batería evaluadas "
                "para formular una conclusión económica."
            )

        positive_recommendations = [
            recommendation
            for recommendation in recommendations
            if recommendation.capacity_kwh > 0.0
        ]

        economic_calculated = bool(positive_recommendations) and all(
            recommendation.economic_analysis_calculated
            for recommendation in positive_recommendations
        )

        combined_calculated = all(
            recommendation.combined_economic_analysis_calculated
            for recommendation in recommendations
        )

        if not economic_calculated:
            return (
                "No puede establecerse una conclusión económica sobre "
                "el almacenamiento porque el análisis económico "
                "incremental de las baterías no se ha calculado "
                "para todas las capacidades evaluadas."
            )

        viable = [
            recommendation
            for recommendation in recommendations
            if recommendation.economic_npv_eur > 0.0
        ]

        if not viable:
            return (
                "Ninguna de las capacidades de batería evaluadas "
                "presenta un VAN incremental positivo. Por tanto, "
                "no se recomienda añadir almacenamiento por su "
                "rentabilidad económica bajo las hipótesis actuales."
            )

        # Mejor resultado económico de la batería considerada
        # de forma incremental, sin confundirlo con el VAN conjunto.
        best_economic = max(
            viable,
            key=lambda recommendation: (
                recommendation.economic_npv_eur,
                -recommendation.capacity_kwh,
            ),
        )

        economic_payback = (
            "N/D"
            if not math.isfinite(
                best_economic.economic_payback_years
            )
            else (
                f"{best_economic.economic_payback_years:.2f} años"
            )
        )

        conclusion = (
            f"La capacidad de batería de "
            f"{best_economic.capacity_kwh:.1f} kWh presenta el "
            f"mayor VAN positivo de batería entre las capacidades "
            f"evaluadas ({best_economic.economic_npv_eur:,.2f} €) "
            f"y constituye la recomendación económica por su "
            f"rentabilidad incremental. El ahorro adicional anual "
            f"estimado es de "
            f"{best_economic.annual_additional_savings_eur:,.2f} €. "
            f"La recuperación económica estimada es de "
            f"{economic_payback}. "
            f"El ahorro marginal es de "
            f"{best_economic.marginal_savings_per_kwh:,.2f} €/kWh."
        )

        if not combined_calculated:
            conclusion += (
                " No se ha completado el análisis económico conjunto "
                "para todas las capacidades; por tanto, todavía no "
                "puede establecerse una recomendación global basada "
                "en el VAN de la instalación fotovoltaica y la batería."
            )
            return conclusion

        
        # Solo utilizar alternativas con VAN conjunto válido y finito.
        valid_combined_viable = [
            recommendation
            for recommendation in viable
            if (
                recommendation.combined_economic_npv_eur is not None
                and math.isfinite(
                    recommendation.combined_economic_npv_eur
                )
            )
        ]

        best_combined = (
            max(
                valid_combined_viable,
                key=lambda recommendation: (
                    recommendation.combined_economic_npv_eur,
                    recommendation.economic_npv_eur,
                    -recommendation.capacity_kwh,
                ),
            )
            if valid_combined_viable
            else None
        )

        if best_combined is not None:
            if best_combined.combined_economic_npv_eur > 0.0:
                if math.isclose(
                    best_economic.capacity_kwh,
                    best_combined.capacity_kwh,
                    rel_tol=0.0,
                    abs_tol=1e-6,
                ):
                    conclusion += (
                        f" La capacidad de "
                        f"{best_combined.capacity_kwh:.1f} kWh "
                        f"constituye la opción recomendada para la "
                        f"inversión conjunta FV + batería, al "
                        f"presentar simultáneamente el mayor VAN "
                        f"de batería "
                        f"({best_economic.economic_npv_eur:,.2f} €) "
                        f"y el mayor VAN conjunto FV + batería "
                        f"({best_combined.combined_economic_npv_eur:,.2f} €) "
                        f"entre las alternativas con VAN incremental "
                        f"positivo."
                    )
                else:
                    conclusion += (
                        f" Desde la perspectiva de la inversión completa, "
                        f"la capacidad de "
                        f"{best_combined.capacity_kwh:.1f} kWh ofrece el "
                        f"mayor VAN conjunto FV + batería entre las "
                        f"alternativas con VAN incremental positivo "
                        f"({best_combined.combined_economic_npv_eur:,.2f} €). "
                        f"Esta capacidad difiere de la que maximiza el VAN "
                        f"incremental de batería; la recomendación global "
                        f"debe priorizar el resultado conjunto."
                    )
            else:
                conclusion += (
                    f" Aunque la capacidad de "
                    f"{best_combined.capacity_kwh:.1f} kWh ofrece el mejor "
                    f"resultado conjunto entre las alternativas con VAN "
                    f"incremental positivo, su VAN conjunto es negativo "
                    f"({best_combined.combined_economic_npv_eur:,.2f} €). "
                    f"No puede recomendarse como inversión conjunta "
                    f"rentable bajo las hipótesis consideradas."
                )
        else:
            conclusion += (
                " No puede establecerse una recomendación conjunta "
                "entre las capacidades con VAN incremental positivo "
                "porque sus VAN conjuntos no contienen valores "
                "válidos y finitos."
            )

        # Informar del máximo VAN conjunto global, aunque esa
        # alternativa no tenga VAN incremental positivo.
        valid_combined = [
            recommendation
            for recommendation in recommendations
            if (
                recommendation.combined_economic_npv_eur is not None
                and math.isfinite(
                    recommendation.combined_economic_npv_eur
                )
            )
        ]

        if valid_combined:
            best_combined_overall = max(
                valid_combined,
                key=lambda recommendation: (
                    recommendation.combined_economic_npv_eur,
                    -recommendation.capacity_kwh,
                ),
            )

            if (
                best_combined_overall.economic_npv_eur is not None
                and math.isfinite(
                    best_combined_overall.economic_npv_eur
                )
                and best_combined_overall.economic_npv_eur <= 0.0
            ):
                conclusion += (
                    f" El mayor VAN conjunto global corresponde a "
                    f"{best_combined_overall.capacity_kwh:.1f} kWh "
                    f"({best_combined_overall.combined_economic_npv_eur:,.2f} €), "
                    f"pero esta alternativa no presenta un VAN "
                    f"incremental positivo de batería. Por tanto, "
                    f"el resultado conjunto no justifica por sí solo "
                    f"recomendar la instalación de esa batería."
                )

                # Clasificar las capacidades próximas a la neutralidad
        # utilizando el 1 % de la inversión total de cada alternativa.
        neutral_capacities = []

        for recommendation in recommendations:
            combined_npv = recommendation.combined_economic_npv_eur

            # Los valores ausentes o no finitos no se pueden
            # clasificar como económicamente neutros.
            if (
                combined_npv is None
                or not math.isfinite(combined_npv)
            ):
                continue

            total_investment_eur = (
                data.investment_eur
                + recommendation.incremental_battery_cost_eur
            )

            if (
                not math.isfinite(total_investment_eur)
                or total_investment_eur <= 0.0
            ):
                continue

            neutral_tolerance_eur = total_investment_eur * 0.01

            if abs(combined_npv) <= neutral_tolerance_eur:
                neutral_capacities.append(recommendation)

        if neutral_capacities:
            neutral_capacity_labels = sorted(
                {
                    f"{recommendation.capacity_kwh:.1f} kWh"
                    for recommendation in neutral_capacities
                },
                key=lambda label: float(label.split()[0]),
            )

            capacities_text = ", ".join(
                neutral_capacity_labels
            )

            if len(neutral_capacity_labels) == 1:
                conclusion += (
                    f" La capacidad de {capacities_text} presenta un VAN "
                    f"conjunto próximo a la neutralidad económica, "
                    f"considerando como margen el 1 % de la inversión "
                    f"total de cada alternativa. Por tanto, su resultado "
                    f"debe interpretarse como económicamente neutro "
                    f"bajo las hipótesis consideradas."
                )
            else:
                conclusion += (
                    f" Las capacidades {capacities_text} presentan un VAN "
                    f"conjunto próximo a la neutralidad económica, "
                    f"considerando como margen el 1 % de la inversión "
                    f"total de cada alternativa. Por tanto, sus resultados "
                    f"deben interpretarse como económicamente neutros "
                    f"bajo las hipótesis consideradas."
                )

        # Las capacidades neutrales no deben etiquetarse como
        # no rentables. Solo se clasifican como no rentables las
        # capacidades superiores a la mayor capacidad con VAN
        # incremental positivo cuyo VAN conjunto sea inferior
        # al umbral negativo de neutralidad.

        largest_viable_capacity = max(
            recommendation.capacity_kwh
            for recommendation in viable
        )

        neutral_capacity_set = {
            recommendation.capacity_kwh
            for recommendation in neutral_capacities
        }

        unprofitable_larger = []

        for recommendation in recommendations:
            capacity_kwh = recommendation.capacity_kwh
            combined_npv = recommendation.combined_economic_npv_eur

            if (
                capacity_kwh <= largest_viable_capacity
                or capacity_kwh in neutral_capacity_set
                or combined_npv is None
                or not math.isfinite(combined_npv)
            ):
                continue

            total_investment_eur = (
                data.investment_eur
                + recommendation.incremental_battery_cost_eur
            )

            if (
                not math.isfinite(total_investment_eur)
                or total_investment_eur <= 0.0
            ):
                continue

            neutral_tolerance_eur = total_investment_eur * 0.01

            if combined_npv < -neutral_tolerance_eur:
                unprofitable_larger.append(capacity_kwh)

        unprofitable_larger.sort()

        if unprofitable_larger:
            capacities_text = " y ".join(
                f"{capacity:.1f} kWh"
                for capacity in unprofitable_larger
            )

            if len(unprofitable_larger) == 1:
                conclusion += (
                    f" La capacidad de {capacities_text} no resulta "
                    f"rentable en términos de VAN conjunto bajo "
                    f"las hipótesis consideradas."
                )
            else:
                conclusion += (
                    f" Las capacidades de {capacities_text} no resultan "
                    f"rentables en términos de VAN conjunto bajo "
                    f"las hipótesis consideradas."
                )

        return conclusion

    @staticmethod
    def final_recommendation(
        data: SolarReportData,
    ) -> str:
        """Genera una recomendación final orientada a la toma de decisión."""

        if data is None:
            raise ValueError("report data is required")

        if data.yearly_consumption_kwh > 0:
            production_ratio = (
                data.yearly_production_kwh
                / data.yearly_consumption_kwh
                * 100
            )
        else:
            production_ratio = 0.0

        primary_analysis_calculated = (
            SolarReportText._primary_economic_analysis_calculated(data)
        )
        primary_npv = SolarReportText._primary_npv_eur(data)

        if not primary_analysis_calculated:
            recommendation = (
                "No puede establecerse todavía una recomendación "
                "de inversión basada en la rentabilidad."
            )
            economic_message = (
                "El análisis económico no se ha calculado, por lo que "
                "no puede determinarse si el VAN de la opción "
                "seleccionada es positivo o negativo."
            )
        elif not SolarReportText._is_finite_metric(primary_npv):
            recommendation = (
                "No puede establecerse una recomendación de inversión "
                "hasta disponer de un VAN válido para la opción "
                "seleccionada."
            )
            economic_message = (
                "El análisis económico está marcado como calculado, "
                "pero el VAN de la opción seleccionada no es válido."
            )
        elif primary_npv > 0:
            recommendation = (
                "Se recomienda la instalación fotovoltaica "
                "en el escenario analizado. La opción evaluada "
                "corresponde a la selección del optimizador."
            )
            economic_message = (
                "El resultado económico es favorable, ya que el "
                "valor actual neto es positivo para la opción "
                "seleccionada bajo las hipótesis utilizadas."
            )
        elif primary_npv < 0:
            recommendation = (
                "No se recomienda ejecutar la instalación sin revisar "
                "previamente sus condiciones económicas."
            )
            economic_message = (
                "El resultado económico no es favorable bajo las "
                "hipótesis utilizadas, ya que el valor actual neto "
                "es negativo para la opción seleccionada."
            )
        else:
            recommendation = (
                "La decisión de ejecutar la instalación requiere "
                "valorar también criterios energéticos y no económicos."
            )
            economic_message = (
                "El VAN de la opción seleccionada se encuentra "
                "aproximadamente en el punto de equilibrio bajo "
                "las hipótesis utilizadas."
            )

        production_message = (
            f"La instalación genera aproximadamente "
            f"{data.yearly_production_kwh:,.0f} kWh/año, equivalentes "
            f"al {production_ratio:.1f} % del consumo eléctrico anual "
            f"de referencia. La autosuficiencia energética estimada "
            f"es del {data.self_sufficiency_rate_percent:.1f} %."
        )

        flexibility_message = (
            "La diferencia entre la producción anual y la autosuficiencia "
            "pone de manifiesto que la generación y la demanda no "
            "coinciden temporalmente. Existe un margen de mejora mediante "
            "la gestión temporal de la energía, cargas flexibles y, "
            "cuando resulte económicamente justificado, almacenamiento."
        )

        future_consumption_message = ""

        if data.economic_analysis_calculated:
            for battery in data.battery_recommendations:
                if not math.isclose(
                    battery.capacity_kwh,
                    16.6,
                    rel_tol=0.0,
                    abs_tol=1e-6,
                ):
                    continue

                if not battery.combined_economic_analysis_calculated:
                    continue

                total_investment_eur = (
                    data.investment_eur
                    + battery.incremental_battery_cost_eur
                )

                if total_investment_eur <= 0:
                    continue

                margin_eur = total_investment_eur * 0.01

                if (
                    abs(battery.combined_economic_npv_eur)
                    > margin_eur
                ):
                    continue

                future_consumption_message = (
                    "Escenario de incremento futuro del consumo: "
                    "la alternativa con batería de 16,6 kWh merece "
                    "una evaluación adicional si se prevé un aumento "
                    "del consumo eléctrico. Esta posibilidad no "
                    "constituye una recomendación de ampliación "
                    "inmediata y debe reevaluarse con la demanda "
                    "futura y sus hipótesis económicas."
                )
                break

        battery_closing = ""

        if data.economic_analysis_calculated:
            battery = SolarReportText.recommended_battery(data)

            if battery is not None:
                battery_closing = (
                    f" Bajo las hipótesis económicas consideradas, "
                    f"la instalación fotovoltaica resulta recomendable "
                    f"y la capacidad de batería de "
                    f"{battery.capacity_kwh:.1f} kWh representa la "
                    f"alternativa con mejor equilibrio entre "
                    f"aprovechamiento energético y rentabilidad "
                    f"económica entre las capacidades evaluadas."
                )
            elif data.battery_recommendations and all(
                item.economic_analysis_calculated
                and item.combined_economic_analysis_calculated
                for item in data.battery_recommendations
            ):
                battery_closing = (
                    " Bajo las hipótesis económicas consideradas, "
                    "la instalación fotovoltaica debe valorarse "
                    "independientemente de la decisión de añadir "
                    "almacenamiento: ninguna capacidad evaluada "
                    "cumple el criterio de VAN incremental positivo."
                )

        return (
            f"<b>Recomendación final</b><br/>"
            f"{recommendation} "
            f"{production_message} "
            f"{economic_message} "
            f"{flexibility_message} "
            f"{future_consumption_message}"
            f"{battery_closing}"
        )

    @staticmethod
    def combined_economic_interpretation(
        data: SolarReportData,
    ) -> str:
        """Interpreta la rentabilidad conjunta usando solo resultados calculados."""

        if data is None:
            raise ValueError("report data is required")

        recommendations = data.battery_recommendations

        if not recommendations:
            return (
                "No se dispone de una comparación económica conjunta "
                "de la instalación fotovoltaica con distintas "
                "capacidades de batería."
            )

        evaluated = [
            recommendation
            for recommendation in recommendations
            if recommendation.combined_economic_analysis_calculated
        ]

        if not evaluated:
            return (
                "El análisis económico conjunto de la instalación "
                "fotovoltaica y las baterías no se ha calculado. "
                "No puede establecerse una recomendación económica "
                "conjunta a partir de los resultados disponibles."
            )

        best_combined = max(
            evaluated,
            key=lambda recommendation: (
                recommendation.combined_economic_npv_eur,
                -recommendation.capacity_kwh,
            ),
        )

        positive_combined = [
            recommendation
            for recommendation in evaluated
            if recommendation.combined_economic_npv_eur > 0.0
        ]

        if positive_combined:
            recommended = max(
                positive_combined,
                key=lambda recommendation: (
                    recommendation.combined_economic_npv_eur,
                    -recommendation.capacity_kwh,
                ),
            )

            npv_text = (
                f"{recommended.combined_economic_npv_eur:,.2f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            )

            if recommended.economic_analysis_calculated:
                battery_npv_text = (
                    f"{recommended.economic_npv_eur:,.2f}"
                    .replace(",", "X")
                    .replace(".", ",")
                    .replace("X", ".")
                )
                battery_npv_message = (
                    f" El VAN incremental de esa batería, evaluada "
                    f"por separado, es de {battery_npv_text} €."
                )
            else:
                battery_npv_message = (
                    " El VAN incremental de esa batería no está "
                    "disponible, por lo que no debe inferirse "
                    "su rentabilidad individual."
                )

            return (
                f"Entre las capacidades con análisis conjunto "
                f"calculado y VAN positivo, la alternativa de "
                f"{recommended.capacity_kwh:.1f} kWh presenta el "
                f"mayor VAN conjunto: {npv_text} €. Este indicador "
                f"corresponde al sistema fotovoltaico más batería, "
                f"no exclusivamente al almacenamiento."
                f"{battery_npv_message} La recomendación se limita "
                f"a las alternativas evaluadas y depende de las "
                f"hipótesis económicas utilizadas."
            )

        if best_combined.combined_economic_npv_eur < 0.0:
            npv_text = (
                f"{best_combined.combined_economic_npv_eur:,.2f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            )

            return (
                "Ninguna de las capacidades de batería evaluadas "
                "presenta un VAN conjunto positivo. La alternativa "
                f"con mejor resultado es la de "
                f"{best_combined.capacity_kwh:.1f} kWh, con un VAN "
                f"conjunto de {npv_text} €. Por tanto, bajo las "
                "hipótesis utilizadas, no se justifica económicamente "
                "añadir almacenamiento por su rentabilidad conjunta, "
                "aunque pueda aportar beneficios de autosuficiencia "
                "o flexibilidad."
            )

        npv_text = (
            f"{best_combined.combined_economic_npv_eur:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        return (
            f"La alternativa de {best_combined.capacity_kwh:.1f} kWh "
            f"presenta un VAN conjunto aproximadamente nulo "
            f"({npv_text} €). El resultado se encuentra cerca del "
            f"umbral de rentabilidad; la decisión debe considerar "
            f"la incertidumbre de las hipótesis económicas y los "
            f"beneficios energéticos adicionales del almacenamiento."
        )

    @staticmethod
    def conclusion(
        data: SolarReportData,
    ) -> str:
        """Genera la conclusión final del informe solar."""

        if data is None:
            raise ValueError("report data is required")

        primary_npv = SolarReportText._primary_npv_eur(data)

        npv_is_finite = SolarReportText._is_finite_metric(
            primary_npv
        )

        if not npv_is_finite:
            investment_assessment = (
                "El valor actual neto no está disponible como indicador "
                "válido bajo las hipótesis económicas utilizadas, por lo "
                "que no puede determinarse la rentabilidad de la inversión "
                "con este resultado."
            )
        elif primary_npv > 0:
            investment_assessment = (
                "El valor actual neto es positivo bajo las hipótesis utilizadas. "
                "Este resultado corresponde a la opción seleccionada "
                "por el optimizador."
            )
        elif primary_npv < 0:
            investment_assessment = (
                "El valor actual neto es negativo bajo las hipótesis utilizadas. "
                "Este resultado corresponde a la opción seleccionada "
                "por el optimizador."
            )
        else:
            investment_assessment = (
                "El valor actual neto es aproximadamente nulo bajo las "
                "hipótesis utilizadas. Este resultado corresponde a la "
                "opción seleccionada por el optimizador."
            )

        if data.yearly_consumption_kwh > 0:
            production_ratio = (
                data.yearly_production_kwh
                / data.yearly_consumption_kwh
                * 100
            )
        else:
            production_ratio = 0.0

        if (
            data.yearly_consumption_kwh > 0
            and production_ratio >= 100
        ):
            energy_interpretation = (
                f"La producción anual equivale al "
                f"{production_ratio:.1f} % del consumo anual de "
                f"referencia. Esto no significa que la vivienda "
                f"sea autosuficiente durante todo el año: la "
                f"generación y la demanda no coinciden necesariamente "
                f"en el tiempo. La autosuficiencia estimada, que "
                f"refleja la parte del consumo cubierta directamente "
                f"por energía solar en el escenario analizado, es "
                f"del {data.self_sufficiency_rate_percent:.1f} %."
            )
        else:
            energy_interpretation = (
                f"La autosuficiencia energética estimada es del "
                f"{data.self_sufficiency_rate_percent:.1f} %. "
                f"Este porcentaje refleja la parte del consumo "
                f"cubierta directamente por la generación solar; "
                f"la producción anual total, por sí sola, no determina "
                f"cuánta energía debe importarse de la red."
            )

        if SolarReportText._primary_economic_analysis_calculated(data):
            if data.selected_option_available:
                savings_value = data.selected_yearly_savings_eur
                investment_value = data.selected_investment_eur

                savings_label = (
                    "el ahorro neto estimado del primer año de la opción seleccionada"
                )
                investment_label = (
                    "la inversión neta de la opción seleccionada"
                )
            else:
                savings_value = data.yearly_savings_eur
                investment_value = data.investment_eur

                savings_label = "el ahorro anual estimado"
                investment_label = "la inversión neta de referencia"

            if SolarReportText._is_finite_metric(savings_value):
                savings_text = (
                    f"{savings_label} de "
                    f"{savings_value:,.2f} €"
                )
            else:
                savings_text = f"{savings_label} no disponible"

            if SolarReportText._is_finite_metric(investment_value):
                investment_text = (
                    f"{investment_label} de "
                    f"{investment_value:,.2f} €"
                )
            else:
                investment_text = f"{investment_label} no disponible"

            primary_payback = (
                SolarReportText._primary_payback_years(data)
            )

            if SolarReportText._is_finite_metric(primary_payback):
                payback_text = (
                    "el periodo de recuperación de la inversión "
                    "de la opción seleccionada estimado en "
                    f"{primary_payback:.2f} años"
                )
            else:
                payback_text = (
                    "el periodo de recuperación de la inversión "
                    "de la opción seleccionada no disponible "
                    "como indicador válido"
                )

            economic_summary = (
                "Desde el punto de vista económico, la instalación "
                f"presenta {savings_text}, {investment_text} y "
                f"{payback_text}. {investment_assessment}"
            )
        else:
            economic_summary = (
                "No se dispone de una evaluación económica calculada. "
                f"{investment_assessment}"
            )

        conclusion = (
            f"La instalación fotovoltaica analizada, con una "
            f"potencia instalada de {data.installed_power_kwp:.2f} kWp, "
            f"alcanza una producción solar anual estimada de "
            f"{data.yearly_production_kwh:,.0f} kWh frente a un "
            f"consumo anual de referencia de "
            f"{data.yearly_consumption_kwh:,.0f} kWh."
            f"<br/><br/>"
            f"{energy_interpretation}"
            f"<br/><br/>"
            f"{economic_summary}"
        )

        if data.battery_recommendations:
            conclusion += (
                "<br/><br/>"
                f"{SolarReportText.combined_economic_interpretation(data)}"
            )

        conclusion += (
            "<br/><br/>"
            "La decisión final debe considerar el perfil horario "
            "de consumo, la energía importada y exportada, el coste "
            "de la instalación y del almacenamiento cuando se evalúe, "
            "la degradación de los equipos, el mantenimiento y "
            "la evolución de los precios de la electricidad. Los resultados "
            "constituyen una estimación basada en las hipótesis de "
            "simulación, no una garantía de ahorro o rentabilidad futuros."
        )

        return conclusion

    @staticmethod
    def glossary() -> list[tuple[str, str]]:
        """Devuelve las definiciones de los principales términos del informe."""

        return [
            (
                "kWp (kilovatio pico)",
                "Unidad utilizada para expresar la potencia nominal de una "
                "instalación fotovoltaica en condiciones estándar de ensayo.",
            ),
            (
                "kWh (kilovatio hora)",
                "Unidad de energía utilizada para medir tanto la producción "
                "fotovoltaica como el consumo eléctrico.",
            ),
            (
                "Producción anual",
                "Cantidad estimada de energía que genera la instalación "
                "fotovoltaica durante un año.",
            ),
            (
                "Producción específica",
                "Energía producida anualmente por cada kWp de potencia "
                "instalada. Permite comparar el rendimiento de instalaciones "
                "de distinto tamaño.",
            ),
            (
                "Horas productivas",
                "Número de horas durante las cuales la instalación "
                "fotovoltaica genera energía.",
            ),
            (
                "Factor de capacidad",
                "Relación entre la energía realmente producida y la energía "
                "que produciría la instalación si funcionara continuamente "
                "a su potencia nominal durante todo el periodo.",
            ),
            (
                "Autoconsumo",
                "Energía fotovoltaica producida que se utiliza directamente "
                "en la vivienda, sin necesidad de importarla de la red.",
            ),
            (
                "Energía vertida a red",
                "Excedente de energía fotovoltaica que no se consume "
                "directamente en la vivienda y se envía a la red eléctrica.",
            ),
            (
                "Energía importada de red",
                "Energía que la vivienda necesita obtener de la red cuando "
                "la producción fotovoltaica disponible no es suficiente "
                "para cubrir el consumo.",
            ),
            (
                "Tasa de autoconsumo",
                "Porcentaje de la producción fotovoltaica que se consume "
                "directamente en la vivienda.",
            ),
            (
                "Tasa de autosuficiencia",
                "Porcentaje del consumo eléctrico de la vivienda que queda "
                "cubierto mediante la energía fotovoltaica.",
            ),
            (
                "Ahorro anual",
                "Reducción estimada del coste anual de la electricidad "
                "gracias a la instalación fotovoltaica.",
            ),
            (
                "Periodo de recuperación de la inversión",
                "Tiempo estimado necesario para recuperar la inversión "
                "inicial mediante los ahorros y otros beneficios económicos "
                "generados por la instalación.",
            ),
            (
                "VAN (Valor Actual Neto)",
                "Indicador económico que representa el valor que genera "
                "la inversión durante el horizonte analizado, teniendo "
                "en cuenta el valor del dinero en el tiempo.",
            ),
            (
                "TIR (Tasa Interna de Retorno)",
                "Indicador que expresa la rentabilidad anual estimada de "
                "la inversión durante el periodo analizado.",
            ),
            (
                "Degradación",
                "Reducción gradual de la capacidad de producción de los "
                "módulos fotovoltaicos a lo largo de su vida útil.",
            ),
            (
                "Valor del dinero en el tiempo",
                "Porcentaje utilizado para expresar en euros de hoy los "
                "ahorros que se producirán en el futuro. Por ejemplo, con "
                "un 5 %, 1.000 € dentro de un año equivalen aproximadamente "
                "a 952 € de hoy. No es lo mismo que el IPC: el IPC mide "
                "la evolución general de los precios, mientras que este "
                "valor permite comparar económicamente cantidades recibidas "
                "en distintos momentos.",
            ),
            (
                "Ahorro adicional anual de la batería",
                "Ahorro anual que proporciona una batería respecto a la "
                "misma instalación fotovoltaica funcionando sin batería.",
            ),
            (
                "Coste incremental de la batería",
                "Coste asociado a incorporar la capacidad de batería "
                "evaluada respecto a la capacidad de referencia.",
            ),
            (
                "Ahorro incremental",
                "Ahorro económico adicional generado por una capacidad "
                "de batería respecto a la capacidad de referencia.",
            ),
            (
                "Ahorro marginal por kWh de batería",
                "Ahorro incremental obtenido por cada kWh adicional "
                "de capacidad de batería instalada.",
            ),
            (
                "Periodo de recuperación marginal",
                "Tiempo estimado necesario para recuperar el coste "
                "incremental de una capacidad adicional de batería "
                "mediante el ahorro incremental que proporciona.",
            ),
            (
                "Ciclos equivalentes",
                "Número estimado de ciclos completos de carga y descarga "
                "que representa el uso anual de la batería.",
            ),
            (
                "VAN de la batería",
                "Valor actual neto de la inversión adicional en la batería, "
                "considerando sus ahorros futuros y el valor del dinero "
                "en el tiempo.",
            ),
            (
                "Economía conjunta FV + batería",
                "Evaluación económica de la instalación fotovoltaica y "
                "la batería consideradas conjuntamente como una única "
                "inversión.",
            ),
        ]