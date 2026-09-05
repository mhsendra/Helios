import pandas as pd

from helios.reports.solar_report_data import SolarReportData
from helios.reports.solar_report_generator import SolarReportGenerator


class TestScenario:
    def __init__(
        self,
        name,
        annual_savings,
        payback_years,
        npv,
        irr,
    ):
        self.name = name
        self.annual_savings = annual_savings
        self.payback_years = payback_years
        self.npv = npv
        self.irr = irr

def report_data():
    return SolarReportData(
        calculation_mode="manual",
        installed_power_kwp=8.1,
        panel_count=15,
        panel_power_wp=540.0,
        latitude=41.62,
        longitude=2.09,
        tilt=30,
        azimuth=0,
        reference_year=2023,
        losses=14.0,
        pv_technology="c-Si",
        mounting_place="building-integrated",
        yearly_production_kwh=12500.0,
        monthly_production=pd.Series(
            [
                850.0,
                1020.0,
                1250.0,
                1480.0,
                1650.0,
                1720.0,
                1800.0,
                1760.0,
                1510.0,
                1180.0,
                920.0,
                780.0,
            ],
            index=pd.date_range(
                "2025-01-31",
                periods=12,
                freq="ME",
            ),
        ),
        specific_production_kwh_kwp=1543.21,
        productive_hours=4380,
        daily_average_kwh=34.25,
        monthly_average_kwh=1041.67,
        maximum_power_kw=8.1,
        capacity_factor_percent=17.6,
        yearly_consumption_kwh=19541.72,
        self_consumption_kwh=8500.0,
        grid_export_kwh=4000.0,
        grid_import_kwh=11041.72,
        self_consumption_rate_percent=43.5,
        self_sufficiency_rate_percent=64.0,
        cost_without_pv_eur=4676.0,
        grid_import_cost_eur=2338.0,
        export_income_eur=0.0,
        cost_with_pv_eur=2338.0,
        self_consumption_savings_eur=2338.0,
        investment_eur=12490.0,
        yearly_savings_eur=2338.0,
        payback_years=5.34,
        net_present_value_eur=22071.16,
        internal_rate_of_return_percent=18.8,
        economic_horizon_years=25,
        first_year_degradation_percent=0.0,
        annual_degradation_percent=0.5,
        annual_electricity_price_growth_percent=2.0,
        annual_export_price_growth_percent=2.0,
        annual_maintenance_cost_eur=150.0,
        annual_maintenance_growth_percent=2.0,
        discount_rate_percent=5.0,
        scenario_results=[
            TestScenario(
                "Optimista",
                2800.0,
                4.46,
                28000.0,
                0.21,
            ),
            TestScenario(
                "Conservador",
                2100.0,
                5.95,
                18000.0,
                0.14,
            ),
        ],
    )


def main():
    output_path = "solar_report.pdf"

    generator = SolarReportGenerator()

    generator.generate(
        report_data(),
        output_path,
    )

    print()
    print(f"Informe generado correctamente: {output_path}")


if __name__ == "__main__":
    main()