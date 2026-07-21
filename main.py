from helios.core.analyzer import ConsumptionAnalyzer
from helios.core.solar import SolarConfiguration

def main():

    analyzer = ConsumptionAnalyzer()

    # ==================================================
    # 1. CARGA Y PREPARACIÓN
    # ==================================================

    analyzer.load_excel("data/raw/consumo electrico castellar.xlsx")

    analyzer.clean_data()
    analyzer.build_datetime()

    # ==================================================
    # 2. VALIDACIÓN
    # ==================================================

    analyzer.validate_timeseries()
    analyzer.find_missing_hours()
    analyzer.quality_report()


    # ==================================================
    # 3. CÁLCULOS
    # ==================================================

    # Estadísticas
    analyzer.calculate_statistics()

    # Consumos
    analyzer.calculate_daily_consumption()
    analyzer.calculate_monthly_consumption()
    analyzer.calculate_yearly_consumption()

    # Perfiles
    analyzer.calculate_hourly_profile()
    analyzer.calculate_weekday_profile()
    analyzer.calculate_monthly_profile()
    analyzer.calculate_seasonal_profile()
    analyzer.calculate_workweek_profile()

    # Comparativas
    analyzer.compare_months_by_year()
    analyzer.calculate_monthly_variation()

    analyzer.compare_weeks_by_year()
    analyzer.calculate_weekly_variation()

    analyzer.compare_years()

    #   Producción solar

    config = SolarConfiguration(
    installed_power_kwp=8.10,
    latitude=41.633,
    longitude=2.017,
    tilt=35,
    azimuth=0
    )

    analyzer.calculate_solar_production(config)
    analyzer.calculate_solar_statistics()
    analyzer.calculate_monthly_solar_production()
    

    # ==================================================
    # INDICADORES
    # ==================================================

    analyzer.calculate_mean_consumption()

    analyzer.calculate_extremes()

    analyzer.calculate_base_load()

    analyzer.calculate_tariff_periods()

    # ==================================================
    # 4. INFORMES
    # ==================================================

    analyzer.statistics_report()

    analyzer.daily_report()
    analyzer.monthly_report()
    analyzer.yearly_report()

    analyzer.hourly_profile_report()
    analyzer.weekday_profile_report()
    analyzer.monthly_profile_report()
    analyzer.seasonal_profile_report()
    analyzer.workweek_profile_report()

    analyzer.monthly_comparison_report()
    analyzer.monthly_variation_report()

    analyzer.weekly_comparison_report()
    analyzer.weekly_variation_report()

    analyzer.yearly_comparison_report()

    analyzer.mean_consumption_report()

    analyzer.extremes_report()

    analyzer.base_load_report()

    analyzer.tariff_periods_report()

    #analyzer.solar_production_report()

    analyzer.solar_statistics_report()

    analyzer.monthly_solar_production_report()

    # ==================================================
    # 5. GRÁFICOS
    # ==================================================

    analyzer.plot_hourly_profile()
    analyzer.plot_weekday_profile()
    analyzer.plot_monthly_profile()
    analyzer.plot_seasonal_profile()
    analyzer.plot_workweek_profile()

    analyzer.plot_monthly_comparison()
    analyzer.plot_monthly_variation()

    analyzer.plot_weekly_comparison()
    analyzer.plot_weekly_variation()

    analyzer.plot_yearly_comparison()

    # ==================================================
    # 6. VISUALIZACIÓN
    # ==================================================

    analyzer.show_plots()


if __name__ == "__main__":
    main()