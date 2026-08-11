from helios.core.analyzer import ConsumptionAnalyzer
from helios.solar.configuration import SolarConfiguration
from dotenv import load_dotenv


def main():

    load_dotenv()

    analyzer = ConsumptionAnalyzer()

    # ==================================================
    # CARGA Y PREPARACIÓN
    # ==================================================

    analyzer.load_excel(
        "data/raw/consumo electrico castellar.xlsx"
    )

    analyzer.clean_data()

    analyzer.build_datetime()


    # ==================================================
    # VALIDACIÓN
    # ==================================================

    analyzer.calculate_validation()

    analyzer.validation_reports()


    # ==================================================
    # ESTADÍSTICAS
    # ==================================================

    analyzer.calculate_statistics()

    analyzer.statistics_reports()


    # ==================================================
    # PERFILES
    # ==================================================

    analyzer.calculate_profiles()

    analyzer.profile_reports()

    analyzer.profile_plots()


    # ==================================================
    # COMPARATIVAS
    # ==================================================

    analyzer.calculate_comparisons()

    analyzer.comparison_reports()

    analyzer.comparison_plots()


    # ==================================================
    # INDICADORES
    # ==================================================

    analyzer.calculate_indicators()

    analyzer.indicator_reports()


    # ==================================================
    # TARIFAS
    # ==================================================

    analyzer.calculate_tariffs()

    analyzer.tariff_reports()


    # ==================================================
    # PRODUCCIÓN SOLAR
    # ==================================================

    config = SolarConfiguration(
        installed_power_kwp=8.10,
        latitude=41.633,
        longitude=2.017,
        tilt=35,
        azimuth=0
    )

    analyzer.calculate_solar(config)

    analyzer.calculate_economics()

    analyzer.economics_reports()

    analyzer.solar_reports()

    # ==================================================
    # VISUALIZACIÓN
    # ==================================================

    analyzer.show_plots()


if __name__ == "__main__":
    main()