from helios.core.analyzer import ConsumptionAnalyzer


def main():

    analyzer = ConsumptionAnalyzer()

    # ==================================================
    # CARGA Y PREPARACIÓN
    # ==================================================

    analyzer.load_excel("data/raw/consumo electrico castellar.xlsx")

    analyzer.clean_data()
    analyzer.build_datetime()

    # ==================================================
    # VALIDACIÓN
    # ==================================================

    analyzer.validate_timeseries()
    analyzer.find_missing_hours()
    analyzer.quality_report()

    # ==================================================
    # ESTADÍSTICAS GENERALES
    # ==================================================

    analyzer.calculate_statistics()
    analyzer.statistics_report()

    # ==================================================
    # CONSUMOS
    # ==================================================

    analyzer.calculate_daily_consumption()
    analyzer.daily_report()

    analyzer.calculate_monthly_consumption()
    analyzer.monthly_report()

    analyzer.calculate_yearly_consumption()
    analyzer.yearly_report()

    # ==================================================
    # PERFILES
    # ==================================================

    analyzer.calculate_hourly_profile()
    analyzer.hourly_profile_report()

    analyzer.calculate_weekday_profile()
    analyzer.weekday_profile_report()

    analyzer.calculate_monthly_profile()
    analyzer.monthly_profile_report()

    analyzer.calculate_seasonal_profile()
    analyzer.seasonal_profile_report()

    analyzer.calculate_workweek_profile()
    analyzer.workweek_profile_report()

    # ==================================================
    # COMPARATIVAS
    # ==================================================

    analyzer.compare_months_by_year()
    analyzer.monthly_comparison_report()

    analyzer.calculate_monthly_variation()
    analyzer.monthly_variation_report()

    analyzer.compare_weeks_by_year()
    analyzer.weekly_comparison_report()

    analyzer.calculate_weekly_variation()
    analyzer.weekly_variation_report()

    analyzer.compare_years()
    analyzer.yearly_comparison_report()

    # ==================================================
    # GRÁFICOS
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

    analyzer.show_plots()


if __name__ == "__main__":
    main()