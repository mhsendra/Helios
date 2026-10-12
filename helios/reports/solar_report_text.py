from helios.reports.solar_report_data import SolarReportData

class SolarReportText:
    """Genera textos interpretativos para el informe solar."""

    @staticmethod
    def recommended_battery(
        data: SolarReportData,
    ):
        """
        Selecciona la batería con mejor VAN conjunto entre las
        capacidades cuyo VAN incremental de batería es positivo.

        Solo considera recomendaciones con ambos análisis económicos
        calculados. En caso de empate, prioriza el mayor VAN de batería
        y, después, la menor capacidad.
        """

        if data is None:
            raise ValueError("report data is required")

        recommendations = data.battery_recommendations

        if not recommendations:
            return None

        # No interpretar valores económicos predeterminados como
        # resultados de cálculos que todavía no se han realizado.
        if not all(
            recommendation.economic_analysis_calculated
            and recommendation.combined_economic_analysis_calculated
            for recommendation in recommendations
        ):
            return None

        viable = [
            recommendation
            for recommendation in recommendations
            if recommendation.economic_npv_eur > 0.0
        ]

        if not viable:
            return None

        return max(
            viable,
            key=lambda recommendation: (
                recommendation.combined_economic_npv_eur,
                recommendation.economic_npv_eur,
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

        if data.economic_analysis_calculated:
            if data.net_present_value_eur > 0:
                pv_message = (
                    "La instalación fotovoltaica es recomendable "
                    "bajo las hipótesis económicas consideradas."
                )
            elif data.net_present_value_eur < 0:
                pv_message = (
                    "La instalación fotovoltaica no resulta rentable "
                    "bajo las hipótesis económicas consideradas."
                )
            else:
                pv_message = (
                    "La instalación fotovoltaica se encuentra "
                    "aproximadamente en el punto de equilibrio económico."
                )
        else:
            pv_message = (
                "No puede establecerse una recomendación económica "
                "sobre la instalación fotovoltaica porque el análisis "
                "económico no se ha calculado."
            )

        battery = SolarReportText.recommended_battery(data)

        if battery is not None:
            battery_message = (
                f"Para el almacenamiento, la capacidad de "
                f"{battery.capacity_kwh:.1f} kWh ofrece el mejor "
                f"resultado conjunto entre las capacidades con "
                f"VAN incremental de batería positivo."
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
    def executive_summary(
        data: SolarReportData,
    ) -> str:
        """Genera el resumen ejecutivo del informe."""

        if data is None:
            raise ValueError("report data is required")

        summary = (
            f"La instalación fotovoltaica analizada tiene una "
            f"potencia instalada de "
            f"{data.installed_power_kwp:.2f} kWp y una producción "
            f"solar estimada de "
            f"{data.yearly_production_kwh:,.0f} kWh anuales. "
            f"Esta producción permite cubrir directamente "
            f"{data.self_sufficiency_rate_percent:.1f} % del "
            f"consumo eléctrico anual mediante energía solar. "
            f"El ahorro económico anual estimado es de "
            f"{data.yearly_savings_eur:,.2f} €."
        )

        if not data.economic_analysis_calculated:
            return (
                summary
                + " La inversión y su periodo de recuperación no "
                "se presentan como resultados validados porque "
                "el análisis económico no se ha calculado."
            )

        return (
            summary
            + f" La inversión es de {data.investment_eur:,.2f} € y "
            f"el periodo de recuperación de la inversión estimado "
            f"es de {data.payback_years:.2f} años."
        )

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

        if not data.economic_analysis_calculated:
            economic_message = (
                "ℹ No se puede evaluar la rentabilidad de la "
                "inversión porque el análisis económico no se ha calculado."
            )
        elif data.net_present_value_eur > 0:
            economic_message = (
                "✓ La inversión presenta un VAN positivo bajo las "
                "hipótesis económicas utilizadas."
            )
        elif data.net_present_value_eur < 0:
            economic_message = (
                "⚠ La inversión presenta un VAN negativo bajo las "
                "hipótesis económicas utilizadas."
            )
        else:
            economic_message = (
                "ℹ La inversión presenta un VAN aproximadamente nulo "
                "bajo las hipótesis económicas utilizadas."
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
        """
        Explica de forma directa cómo se distribuyen la generación
        fotovoltaica y la demanda eléctrica.
        """

        if data is None:
            raise ValueError("report data is required")

        if data.yearly_production_kwh > 0:
            self_consumption_of_production = (
                data.self_consumption_kwh
                / data.yearly_production_kwh
                * 100
            )
            export_of_production = (
                data.grid_export_kwh
                / data.yearly_production_kwh
                * 100
            )
        else:
            self_consumption_of_production = 0.0
            export_of_production = 0.0

        if data.yearly_consumption_kwh > 0:
            solar_share_of_consumption = (
                data.self_consumption_kwh
                / data.yearly_consumption_kwh
                * 100
            )
            grid_share_of_consumption = (
                data.grid_import_kwh
                / data.yearly_consumption_kwh
                * 100
            )
        else:
            solar_share_of_consumption = 0.0
            grid_share_of_consumption = 0.0

        return (
            f"De los {data.yearly_production_kwh:,.0f} kWh generados "
            f"por la instalación fotovoltaica, "
            f"{data.self_consumption_kwh:,.0f} kWh "
            f"({self_consumption_of_production:.1f} %) se utilizan "
            f"directamente en la vivienda y "
            f"{data.grid_export_kwh:,.0f} kWh "
            f"({export_of_production:.1f} %) se vierten a la red. "
            f"Desde el punto de vista de la demanda, de los "
            f"{data.yearly_consumption_kwh:,.0f} kWh consumidos "
            f"anualmente, {data.self_consumption_kwh:,.0f} kWh "
            f"({solar_share_of_consumption:.1f} %) quedan cubiertos "
            f"directamente por la generación solar y "
            f"{data.grid_import_kwh:,.0f} kWh "
            f"({grid_share_of_consumption:.1f} %) deben importarse "
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
        Resume el alcance y las limitaciones de la metodología utilizada.
        """

        if data is None:
            raise ValueError("report data is required")

        return (
            f"Los resultados se basan en una simulación energética "
            f"y económica referida al año de consumo "
            f"{data.consumption_reference_year}, calculada a partir "
            f"de los perfiles y las hipótesis definidos para el "
            f"proyecto. La simulación permite estimar el "
            f"comportamiento de la instalación bajo esas condiciones, "
            f"pero los resultados dependen de las hipótesis adoptadas "
            f"y de las condiciones reales de funcionamiento. "
            f"Por tanto, los resultados son estimaciones y "
            f"no constituyen una garantía de resultados futuros."
        )

    @staticmethod
    def economic_analysis(
        data: SolarReportData,
    ) -> str:
        """Interpreta los principales indicadores económicos."""

        if data is None:
            raise ValueError("report data is required")

        if not data.economic_analysis_calculated:
            return (
                "El análisis económico de la instalación no se ha "
                "calculado. Por tanto, no es posible interpretar "
                "el valor actual neto, la tasa interna de retorno "
                "ni el periodo de recuperación de la inversión. "
                f"El ahorro anual estimado a partir del balance "
                f"energético es de {data.yearly_savings_eur:,.2f} €."
            )

        if data.net_present_value_eur > 0:
            npv_assessment = (
                "El valor actual neto es positivo, lo que indica que la inversión "
                "genera valor por encima del valor exigido, una vez tenido en cuenta "
                "el valor del dinero en el tiempo."
            )
        elif data.net_present_value_eur < 0:
            npv_assessment = (
                "El valor actual neto es negativo, lo que indica que, bajo las "
                "hipótesis consideradas, el valor de los ahorros futuros no alcanza "
                "a compensar la inversión una vez tenido en cuenta el valor del dinero "
                "en el tiempo."
            )
        else:
            npv_assessment = (
                "El valor actual neto es aproximadamente nulo, lo que indica que, "
                "bajo las hipótesis consideradas, los ahorros futuros compensan "
                "aproximadamente la inversión una vez tenido en cuenta el valor "
                "del dinero en el tiempo."
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
            f"El periodo de recuperación de la inversión es de "
            f"{data.payback_years:.2f} años. "
            f"El valor actual neto alcanza "
            f"{data.net_present_value_eur:,.2f} €. "
            f"{irr_text} "
            f"{npv_assessment}"
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

        economic_calculated = all(
            recommendation.economic_analysis_calculated
            for recommendation in recommendations
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
            if recommendation.economic_npv_eur > 0.0
        ]

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
                if best_economic.economic_payback_years == float("inf")
                else (
                    f"{best_economic.economic_payback_years:.2f} años"
                )
            )

            marginal_payback = (
                "N/D"
                if best_economic.marginal_payback_years == float("inf")
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
                f"capacidades evaluadas presentan un VAN de batería "
                f"positivo bajo las hipótesis económicas utilizadas."
            )
        else:
            text += (
                " Ninguna de las capacidades de batería evaluadas "
                "presenta un VAN incremental positivo; no se "
                "recomienda añadir almacenamiento por rentabilidad "
                "económica bajo las hipótesis actuales."
            )

        if combined_calculated:
            best_combined = max(
                recommendations,
                key=lambda recommendation: (
                    recommendation.combined_economic_npv_eur,
                    -recommendation.capacity_kwh,
                ),
            )

            if viable and best_economic.capacity_kwh == best_combined.capacity_kwh:
                text += (
                    f" La capacidad de "
                    f"{best_combined.capacity_kwh:.1f} kWh presenta "
                    f"también el mayor VAN conjunto del sistema "
                    f"FV + batería, con "
                    f"{best_combined.combined_economic_npv_eur:,.2f} €. "
                )
            else:
                text += (
                    f" La capacidad de "
                    f"{best_combined.capacity_kwh:.1f} kWh presenta "
                    f"el mayor VAN conjunto del sistema FV + batería, "
                    f"con "
                    f"{best_combined.combined_economic_npv_eur:,.2f} €. "
                    f"Ambos indicadores deben considerarse conjuntamente "
                    f"antes de establecer una recomendación global."
                )
        else:
            text += (
                " No se ha calculado el VAN conjunto de la instalación "
                "fotovoltaica y la batería para todas las capacidades; "
                "por tanto, no puede establecerse una recomendación "
                "económica conjunta."
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
        Resume qué implica la situación energética de referencia.
        """

        if data is None:
            raise ValueError("report data is required")

        monthly_average = (
            data.yearly_consumption_kwh / 12
        )

        return (
            f"La demanda eléctrica de referencia alcanza "
            f"{data.yearly_consumption_kwh:,.0f} kWh anuales, "
            f"equivalentes a unos {monthly_average:,.0f} kWh mensuales. "
            f"Este nivel de consumo constituye la referencia frente a "
            f"la que debe valorarse tanto la producción fotovoltaica "
            f"como el grado real de autosuficiencia alcanzable."
        )

    @staticmethod
    def installation_conclusion(
        data: SolarReportData,
    ) -> str:
        """
        Resume el significado energético de la configuración FV.
        """

        if data is None:
            raise ValueError("report data is required")

        production_ratio = (
            data.yearly_production_kwh
            / data.yearly_consumption_kwh
            * 100
        )

        return (
            f"La configuración de {data.installed_power_kwp:.2f} kWp "
            f"permite generar anualmente un volumen de energía "
            f"equivalente aproximadamente al "
            f"{production_ratio:.1f} % del consumo eléctrico de referencia. "
            f"La comparación anual muestra una cobertura energética "
            f"significativa, aunque la utilización efectiva de esa "
            f"producción depende de la coincidencia horaria entre "
            f"generación y demanda."
        )

    @staticmethod
    def production_conclusion(
        data: SolarReportData,
    ) -> str:
        """
        Explica la relación entre producción anual, consumo y
        aprovechamiento directo de la energía solar.
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
            f"{data.yearly_production_kwh:,.0f} kWh/año, equivalentes "
            f"al {production_ratio:.1f} % del consumo eléctrico anual "
            f"de referencia. Sin embargo, la autosuficiencia energética "
            f"se sitúa en el {data.self_sufficiency_rate_percent:.1f} %. "
            f"Esta diferencia no representa una contradicción: refleja "
            f"la falta de coincidencia temporal entre la generación "
            f"fotovoltaica y la demanda eléctrica. "
            f"Una parte relevante de la energía generada se produce cuando "
            f"la vivienda no puede consumirla directamente y debe "
            f"utilizarse posteriormente, gestionarse mediante cargas "
            f"flexibles, almacenarse o verterse a la red."
        )

    @staticmethod
    def production_statistics_conclusion(
        data: SolarReportData,
    ) -> str:
        """
        Resume el significado de las estadísticas de producción.
        """

        if data is None:
            raise ValueError("report data is required")

        return (
            f"La producción presenta un comportamiento compatible con "
            f"una instalación fotovoltaica de {data.installed_power_kwp:.2f} kWp, "
            f"con {data.productive_hours:,} horas productivas estimadas "
            f"y un factor de capacidad del "
            f"{data.capacity_factor_percent:.2f} %. "
            f"Estas métricas describen el rendimiento global del sistema "
            f"y sirven como referencia para interpretar posteriormente "
            f"el balance entre generación y demanda."
        )

    @staticmethod
    def energy_balance_conclusion(
        data: SolarReportData,
    ) -> str:
        """
        Resume la consecuencia energética del balance FV-consumo.
        """

        if data is None:
            raise ValueError("report data is required")

        if data.grid_export_kwh > 0 and data.grid_import_kwh > 0:
            temporal_mismatch = (
                "La existencia simultánea de excedentes vertidos a la red "
                "y de energía importada muestra que una parte de la "
                "generación y de la demanda no coincide temporalmente."
            )
        else:
            temporal_mismatch = (
                "El balance no presenta simultáneamente excedentes "
                "vertidos e importación de red en los resultados analizados."
            )

        return (
            f"La instalación aprovecha directamente "
            f"{data.self_consumption_kwh:,.0f} kWh de generación solar, "
            f"mientras que {data.grid_export_kwh:,.0f} kWh se vierten a "
            f"la red y {data.grid_import_kwh:,.0f} kWh deben importarse. "
            f"{temporal_mismatch} "
            f"Por tanto, el balance energético es el punto de partida "
            f"para valorar posibles mecanismos de desplazamiento de energía, "
            f"como el almacenamiento."
        )

    @staticmethod
    def economic_conclusion(
        data: SolarReportData,
    ) -> str:
        """Resume la interpretación económica de la instalación FV."""

        if data is None:
            raise ValueError("report data is required")

        if not data.economic_analysis_calculated:
            return (
                "El análisis económico de la instalación fotovoltaica "
                "no se ha calculado. No es posible establecer una "
                "conclusión sobre su rentabilidad ni validar el "
                "periodo de recuperación de la inversión."
            )

        if data.net_present_value_eur > 0:
            npv_text = (
                "El VAN resulta positivo bajo las hipótesis utilizadas."
            )
        elif data.net_present_value_eur < 0:
            npv_text = (
                "El VAN resulta negativo bajo las hipótesis utilizadas."
            )
        else:
            npv_text = (
                "El VAN resulta aproximadamente nulo bajo las "
                "hipótesis utilizadas."
            )

        return (
            f"La inversión de {data.investment_eur:,.2f} € se compara "
            f"con un ahorro anual estimado de "
            f"{data.yearly_savings_eur:,.2f} € y un periodo de "
            f"recuperación de {data.payback_years:.2f} años. "
            f"{npv_text} "
            f"Estos resultados dependen directamente de las hipótesis "
            f"de precios, degradación, mantenimiento y tasa de descuento "
            f"utilizadas en la simulación."
        )

    @staticmethod
    def scenario_conclusion(
        data: SolarReportData,
    ) -> str:
        """
        Resume la sensibilidad del resultado económico.
        """

        if data is None:
            raise ValueError("report data is required")

        if not data.economic_analysis_calculated:
            return (
                "No se puede evaluar la sensibilidad del resultado "
                "económico porque el análisis económico no se ha "
                "calculado."
            )

        if not data.scenario_results:
            return (
                "No se han definido escenarios económicos alternativos "
                "que permitan evaluar la sensibilidad del resultado."
            )

        npvs = [
            result.npv
            for result in data.scenario_results
        ]

        return (
            f"Los escenarios económicos muestran un intervalo de VAN "
            f"entre {min(npvs):,.2f} € y {max(npvs):,.2f} €. "
            f"Este intervalo permite valorar la sensibilidad de la "
            f"rentabilidad estimada a las hipótesis económicas. "
            f"Los resultados deben interpretarse como un intervalo de "
            f"escenarios, no como un valor garantizado."
        )

    @staticmethod
    def battery_conclusion(
        data: SolarReportData,
    ) -> str:
        """
        Resume la implicación económica de las baterías evaluadas.
        """

        if data is None:
            raise ValueError("report data is required")

        if not data.battery_recommendations:
            return (
                "No se dispone de capacidades de batería evaluadas "
                "para formular una conclusión económica."
            )

        economic_calculated = all(
            recommendation.economic_analysis_calculated
            for recommendation in data.battery_recommendations
        )

        combined_calculated = all(
            recommendation.combined_economic_analysis_calculated
            for recommendation in data.battery_recommendations
        )

        if not economic_calculated:
            return (
                "No puede establecerse una conclusión económica sobre "
                "el almacenamiento porque el análisis económico "
                "incremental de las baterías no se ha calculado."
            )

        viable = [
            recommendation
            for recommendation in data.battery_recommendations
            if recommendation.economic_npv_eur > 0
        ]

        if not viable:
            return (
                "Ninguna de las capacidades de batería evaluadas "
                "presenta un VAN incremental positivo; no se "
                "recomienda añadir almacenamiento por rentabilidad "
                "económica bajo las hipótesis actuales."
            )

        best_battery = max(
            viable,
            key=lambda recommendation: (
                (
                    recommendation.combined_economic_npv_eur
                    if combined_calculated
                    else recommendation.economic_npv_eur
                ),
                recommendation.economic_npv_eur,
                -recommendation.capacity_kwh,
            ),
        )

        economic_payback = (
            "N/D"
            if best_battery.economic_payback_years == float("inf")
            else (
                f"{best_battery.economic_payback_years:.2f} años"
            )
        )

        annual_savings = (
            f"{best_battery.annual_additional_savings_eur:,.2f} €"
        )

        marginal_savings = (
            f"{best_battery.marginal_savings_per_kwh:,.2f} €/kWh"
        )

        conclusion = (
            f"La capacidad de batería de "
            f"{best_battery.capacity_kwh:.1f} kWh presenta el mayor "
            f"VAN positivo entre las capacidades evaluadas y "
            f"constituye la recomendación económica bajo las "
            f"hipótesis evaluadas. El VAN de batería positivo "
            f"respalda esta recomendación. El ahorro adicional anual "
            f"estimado es de {annual_savings}. "
            f"El ahorro anual adicional que proporciona asciende "
            f"a {annual_savings}. La recuperación económica "
            f"estimada es de {economic_payback}. "
            f"El ahorro marginal es de {marginal_savings}."
        )

        if combined_calculated:
            conclusion += (
                " La valoración conjunta de la instalación "
                "fotovoltaica y la batería debe considerarse para "
                "determinar la rentabilidad de la inversión completa."
            )

        return conclusion

    @staticmethod
    def final_recommendation(
        data: SolarReportData,
    ) -> str:
        """
        Genera una recomendación final orientada a la toma de decisión.

        Integra producción, autosuficiencia y resultado económico de la
        instalación fotovoltaica. La recomendación de almacenamiento o
        movilidad eléctrica se reserva para fases posteriores.
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

        if data.net_present_value_eur > 0:
            economic_message = (
                "El resultado económico es favorable, ya que el "
                "valor actual neto es positivo bajo las hipótesis utilizadas."
            )
            recommendation = (
                "Se recomienda la instalación fotovoltaica en el escenario "
                "analizado."
            )
        elif data.net_present_value_eur < 0:
            economic_message = (
                "El resultado económico no es favorable bajo las hipótesis "
                "utilizadas, ya que el valor actual neto es negativo."
            )
            recommendation = (
                "No se recomienda ejecutar la instalación sin revisar "
                "previamente sus condiciones económicas."
            )
        else:
            economic_message = (
                "El resultado económico se encuentra aproximadamente "
                "en el punto de equilibrio bajo las hipótesis utilizadas."
            )
            recommendation = (
                "La decisión de ejecutar la instalación requiere valorar "
                "también criterios energéticos y no económicos."
            )
         
        production_message = (
            f"La instalación genera aproximadamente "
            f"{data.yearly_production_kwh:,.0f} kWh/año, equivalentes "
            f"al {production_ratio:.1f} % del consumo eléctrico anual "
            f"de referencia."
        )

        flexibility_message = (
            "La diferencia entre la producción anual y la autosuficiencia "
            "pone de manifiesto un margen de mejora mediante una mejor "
            "gestión temporal de la energía, cargas flexibles y, cuando "
            "resulte económicamente justificado, almacenamiento."
        )

        return (
            f"<b>Recomendación final</b><br/>"
            f"{recommendation} "
            f"{production_message} "
            f"La autosuficiencia energética estimada es del "
            f"{data.self_sufficiency_rate_percent:.1f} %. "
            f"{economic_message} "
            f"{flexibility_message}"
        )

    @staticmethod
    def combined_economic_interpretation(
        data: SolarReportData,
    ) -> str:
        """
        Interpreta la rentabilidad conjunta de la instalación FV
        con las capacidades de batería evaluadas.
        """

        if data is None:
            raise ValueError("report data is required")

        recommendations = data.battery_recommendations

        if not recommendations:
            return (
                "No se dispone de una comparación económica conjunta "
                "de la instalación fotovoltaica con distintas "
                "capacidades de batería."
            )

        best_combined = max(
            recommendations,
            key=lambda recommendation: (
                recommendation.combined_economic_npv_eur,
                -recommendation.capacity_kwh,
            ),
        )

        positive_combined = [
            recommendation
            for recommendation in recommendations
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
            battery_npv_text = (
                f"{recommended.economic_npv_eur:,.2f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            )

            return (
                f"Al evaluar conjuntamente la instalación fotovoltaica "
                f"y el almacenamiento, la alternativa de "
                f"{recommended.capacity_kwh:.1f} kWh obtiene el mayor "
                f"VAN conjunto positivo entre las capacidades "
                f"económicamente favorables: {npv_text} €. "
                f"Este indicador corresponde al sistema completo y "
                f"no debe confundirse con el VAN incremental de la "
                f"batería considerada aisladamente "
                f"({battery_npv_text} €). "
                f"La recomendación se limita a las capacidades "
                f"evaluadas y depende de las hipótesis económicas "
                f"del escenario analizado."
            )

        if best_combined.combined_economic_npv_eur < 0.0:
            npv_text = (
                f"{best_combined.combined_economic_npv_eur:,.2f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            )

            return (
                f"Ninguna de las capacidades de batería evaluadas "
                f"presenta un VAN conjunto positivo. La alternativa "
                f"con mejor resultado es la de "
                f"{best_combined.capacity_kwh:.1f} kWh, con un VAN "
                f"conjunto de {npv_text} €. "
                f"Por tanto, bajo las hipótesis utilizadas, no se "
                f"justifica económicamente añadir almacenamiento "
                f"por su rentabilidad conjunta, aunque pueda aportar "
                f"beneficios de autosuficiencia o flexibilidad."
            )

        return (
            f"La alternativa de {best_combined.capacity_kwh:.1f} kWh "
            f"presenta un VAN conjunto aproximadamente nulo "
            f"({best_combined.combined_economic_npv_eur:,.2f} €). "
            f"El resultado se encuentra en el entorno del umbral "
            f"de rentabilidad, por lo que la decisión debe considerar "
            f"la incertidumbre de las hipótesis económicas y los "
            f"beneficios energéticos adicionales del almacenamiento."
        )

    @staticmethod
    def conclusion(
        data: SolarReportData,
    ) -> str:
        """
        Genera la conclusión final del informe solar.

        Resume producción, autosuficiencia y rentabilidad fotovoltaica,
        e interpreta la rentabilidad conjunta cuando existen resultados
        económicos de almacenamiento.
        """
        if data is None:
            raise ValueError("report data is required")

        if data.net_present_value_eur > 0:
            investment_assessment = (
                "El valor actual neto es positivo bajo las hipótesis "
                "utilizadas. La inversión fotovoltaica genera valor "
                "actual neto en el escenario analizado."
            )
        elif data.net_present_value_eur < 0:
            investment_assessment = (
                "El valor actual neto es negativo bajo las hipótesis "
                "utilizadas. Conviene revisar las condiciones "
                "económicas antes de ejecutar la inversión."
            )
        else:
            investment_assessment = (
                "El valor actual neto es aproximadamente nulo bajo "
                "las hipótesis económicas utilizadas."
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
            f"Desde el punto de vista económico, la instalación "
            f"genera un ahorro anual estimado de "
            f"{data.yearly_savings_eur:,.2f} €, con una inversión "
            f"neta de {data.investment_eur:,.2f} € y un "
            f"periodo de recuperación de la inversión estimado "
            f"de {data.payback_years:.2f} años. "
            f"{investment_assessment}"
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
            "la degradación de los equipos, el mantenimiento y la "
            "evolución de los precios de la electricidad. Los resultados "
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