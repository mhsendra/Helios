from helios.reports.solar_report_data import SolarReportData


class SolarReportDataFactory:
    """
    Construye los datos necesarios para el informe solar.

    No realiza cálculos de producción ni económicos.
    Recoge resultados ya calculados por los engines.
    """

    @staticmethod
    def create(
        solar_controller,
        economics_controller,
    ) -> SolarReportData:

        if solar_controller is None:
            raise ValueError(
                "solar controller is required"
            )

        if economics_controller is None:
            raise ValueError(
                "economics controller is required"
            )

        sizing_result = (
            solar_controller.sizing_result
        )

        if sizing_result is None:
            raise ValueError(
                "solar installation sizing is required"
            )

        economics = (
            economics_controller
            .analyzer
            .economics_engine
        )

        return SolarReportData(
            installed_power_kwp=sizing_result.installed_power_kwp,
            panel_count=sizing_result.panel_count,
            panel_power_wp=sizing_result.evaluation.candidate.panel_power_wp,
            yearly_production_kwh=sizing_result.annual_production_kwh,
            monthly_production=solar_controller.monthly_production,
            specific_production_kwh_kwp=solar_controller.specific_production,
            yearly_consumption_kwh=sizing_result.annual_consumption_kwh,
            self_consumption_kwh=solar_controller.self_consumption,
            grid_export_kwh=solar_controller.grid_export,
            grid_import_kwh=solar_controller.grid_import,
            self_consumption_rate_percent=solar_controller.coverage,
            self_sufficiency_rate_percent=sizing_result.self_sufficiency_percent,
            investment_eur=economics.net_investment,
            yearly_savings_eur=economics.annual_savings,
            payback_years=economics.payback_years,
            net_present_value_eur=economics.npv,
            internal_rate_of_return_percent=(
                economics.irr * 100
                if economics.irr is not None
                else None
            ),
        )