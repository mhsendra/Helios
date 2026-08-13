from helios.core.analyzer import ConsumptionAnalyzer
from helios.solar.configuration import SolarConfiguration
from helios.core.economics_configuration import EconomicsConfiguration
from helios.core.economic_scenarios import EconomicScenario
from dotenv import load_dotenv


def main():
    
    economics_config = EconomicsConfiguration(
            installation_cost=12490.0
        )
    
    analyzer = ConsumptionAnalyzer(
        economics_config
    )

    load_dotenv()

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

    scenarios = [
        EconomicScenario(
            name="Conservador",
            buy_price_factor=0.90,
            sell_price_factor=0.90,
            annual_maintenance=200.0,
            annual_degradation=0.005,
        ),
        EconomicScenario(
            name="Base",
        ),
        EconomicScenario(
            name="Optimista",
            buy_price_factor=1.10,
            sell_price_factor=1.10,
            annual_maintenance=100.0,
            annual_degradation=0.0025,
        ),
    ]

    scenario_results = analyzer.economics.calculate_scenarios(
        scenarios
    )

    print()
    print("SCENARIOS")

    for result in scenario_results:
        print(result)
    
    analyzer.economics_reports()
    
    analyzer.solar_reports()

    # ==================================================
    # VISUALIZACIÓN
    # ==================================================

    analyzer.show_plots()


if __name__ == "__main__":
    main()