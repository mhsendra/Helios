from helios.reports.battery_report_data import BatteryReportData
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
            f"periodo de recuperación de la inversión de "
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
        Interpreta los resultados económicos de las capacidades
        de batería evaluadas.
        """

        if data is None:
            raise ValueError("report data is required")

        recommendations = data.battery_recommendations

        if not recommendations:
            return (
                "No se han realizado evaluaciones económicas de "
                "capacidades de batería para esta instalación."
            )

        viable = [
            recommendation
            for recommendation in recommendations
            if recommendation.economic_npv_eur >= 0
        ]

        best_additional_savings = max(
            recommendations,
            key=lambda recommendation:
            recommendation.annual_additional_savings_eur,
        )

        best_economic_npv = max(
            recommendations,
            key=lambda recommendation:
            recommendation.economic_npv_eur,
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

        text += (
            f" En términos del valor actual neto de la propia batería, "
            f"la capacidad de "
            f"{best_economic_npv.capacity_kwh:.1f} kWh obtiene "
            f"{best_economic_npv.economic_npv_eur:,.2f} € "
            f"bajo las hipótesis económicas utilizadas."
        )

        if viable:
            text += (
                f" {len(viable)} de las {len(recommendations)} "
                f"capacidades evaluadas presentan un valor actual neto "
                f"de la batería igual o superior a cero."
            )
        else:
            text += (
                " Ninguna de las capacidades evaluadas presenta un "
                "valor actual neto de la batería igual o superior a cero "
                "bajo las hipótesis consideradas."
            )

        text += (
            " El ahorro marginal por kWh representa el ahorro adicional "
            "obtenido por cada kWh de capacidad de batería añadido, "
            "mientras que el periodo de recuperación marginal expresa "
            "el tiempo estimado necesario para recuperar el coste "
            "incremental de esa capacidad mediante el ahorro incremental."
        )

        text += (
            " Los indicadores económicos conjuntos permiten además "
            "analizar el resultado de la inversión fotovoltaica y la "
            "batería como un único sistema."
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
            f"En conjunto, los resultados muestran que la inversión "
            f"mantiene una rentabilidad positiva bajo las diferentes "
            f"hipótesis analizadas, aunque su atractivo económico "
            f"varía según la evolución de los precios de la energía, "
            f"los costes de mantenimiento y el resto de supuestos "
            f"considerados."
        )

        return text

    @staticmethod
    def conclusion(
        data: SolarReportData,
    ) -> str:
        """
        Genera la conclusión final del informe solar.

        Incluye el resumen de la instalación fotovoltaica y,
        cuando existen resultados de batería, una síntesis de
        su comportamiento energético y económico.
        """

        if data is None:
            raise ValueError("report data is required")

        if data.net_present_value_eur > 0:
            investment_assessment = (
                "La inversión favorable bajo las hipótesis utilizadas."
            )
        elif data.net_present_value_eur < 0:
            investment_assessment = (
                "La inversión presenta una valoración prudente "
                "bajo las hipótesis utilizadas."
            )
        else:
            investment_assessment = (
                "La inversión presenta un valor actual neto "
                "aproximadamente nulo bajo las hipótesis utilizadas."
            )

        conclusion = (
            f"La instalación fotovoltaica analizada, con una "
            f"potencia instalada de {data.installed_power_kwp:.2f} kWp, "
            f"alcanza una producción solar anual estimada de "
            f"{data.yearly_production_kwh:,.0f} kWh. "
            f"Esta generación permite cubrir mediante energía solar "
            f"el {data.self_sufficiency_rate_percent:.1f} % del "
            f"consumo eléctrico anual, reduciendo la dependencia "
            f"de la red eléctrica."
            f"<br/><br/>"
            f"Desde el punto de vista económico, la instalación "
            f"genera un ahorro anual estimado de "
            f"{data.yearly_savings_eur:,.2f} €, con una inversión "
            f"neta de {data.investment_eur:,.2f} € y un periodo "
            f"de recuperación de la inversión de "
            f"{data.payback_years:.2f} años. "
            f"{investment_assessment}"
        )

        # ---------------------------------------------------------
        # Evaluación económica de las baterías
        # ---------------------------------------------------------

        if data.battery_recommendations:
            recommendations = data.battery_recommendations

            highest_savings = max(
                recommendations,
                key=lambda recommendation: (
                    recommendation.annual_additional_savings_eur
                ),
            )

            highest_npv = max(
                recommendations,
                key=lambda recommendation: (
                    recommendation.economic_npv_eur
                ),
            )

            viable_count = sum(
                recommendation.economic_npv_eur >= 0
                for recommendation in recommendations
            )

            capacities = [
                recommendation.capacity_kwh
                for recommendation in recommendations
            ]

            min_capacity = min(capacities)
            max_capacity = max(capacities)

        if highest_npv.economic_payback_years == float("inf"):
            payback_text = "no se recupera durante el horizonte analizado"
        else:
            payback_text = (
                f"{highest_npv.economic_payback_years:.2f} años"
            )

            conclusion += (
                f"<br/><br/>"
                f"También se ha evaluado el almacenamiento mediante "
                f"{len(recommendations)} capacidades de batería, entre "
                f"{min_capacity:.1f} y {max_capacity:.1f} kWh. "
                f"El mayor ahorro adicional anual obtenido en la "
                f"simulación corresponde a una capacidad de "
                f"{highest_savings.capacity_kwh:.1f} kWh, con un ahorro "
                f"adicional anual de "
                f"{highest_savings.annual_additional_savings_eur:,.2f} €."
                f"<br/><br/>"
                f"Desde el punto de vista económico de la propia batería, "
                f"la capacidad de {highest_npv.capacity_kwh:.1f} kWh "
                f"presenta el mayor valor actual neto, de "
                f"{highest_npv.economic_npv_eur:,.2f} €, con una TIR del "
                f"{highest_npv.economic_irr_percent:.2f} % y un periodo "
                f"de recuperación de {payback_text}. "
                f"En total, {viable_count} de las {len(recommendations)} "
                f"capacidades evaluadas presentan un valor actual neto "
                f"de la batería igual o superior a cero."
                f"<br/><br/>"
                f"Estos resultados muestran que aumentar la capacidad de "
                f"almacenamiento puede incrementar el ahorro anual, pero "
                f"ese incremento no implica necesariamente una mejora "
                f"proporcional de la rentabilidad económica de la batería."
            )

        # ---------------------------------------------------------
        # Cierre general
        # ---------------------------------------------------------

        conclusion += (
            f"<br/><br/>"
            f"En conjunto, los resultados indican que la instalación "
            f"presenta una capacidad significativa para reducir el "
            f"coste energético anual y mejorar el grado de "
            f"autosuficiencia eléctrica del sistema. La valoración "
            f"final debe entenderse dentro de las hipótesis de "
            f"producción, consumo, tarifas, degradación y evolución "
            f"de precios utilizadas en el análisis."
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