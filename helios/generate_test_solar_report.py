import pandas as pd

from helios.reports.solar_report_data import SolarReportData
from helios.reports.solar_report_generator import SolarReportGenerator


def report_data():
    return SolarReportData(
        installed_power_kwp=8.1,
        panel_count=15,
        panel_power_wp=540.0,
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
        yearly_consumption_kwh=19541.72,
        self_consumption_kwh=8500.0,
        grid_export_kwh=4000.0,
        grid_import_kwh=11041.72,
        self_consumption_rate_percent=43.5,
        self_sufficiency_rate_percent=64.0,
        investment_eur=12490.0,
        yearly_savings_eur=2338.0,
        payback_years=5.34,
        net_present_value_eur=22071.16,
        internal_rate_of_return_percent=18.8,
    )


def main():
    output_path = "solar_report.pdf"

    generator = SolarReportGenerator()

    generator.generate(
        report_data(),
        output_path,
    )

    print(f"Informe generado: {output_path}")


if __name__ == "__main__":
    main()