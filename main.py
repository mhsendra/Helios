from helios.core.analyzer import ConsumptionAnalyzer

def main():
    analyzer = ConsumptionAnalyzer()
    #carga
    analyzer.load_excel("data/raw/consumo electrico castellar.xlsx")
    #preparación
    #analyzer.inspect_data()
    analyzer.clean_data()
    #analyzer.analyze_missing_data()
    analyzer.build_datetime()
    #validación
    analyzer.validate_timeseries()
    analyzer.find_missing_hours()
    analyzer.quality_report()
    #analyzer.find_duplicate_timestamps()
    #analyzer.inspect_dst_days()

    analyzer.calculate_statistics()
    analyzer.statistics_report()

    #print(analyzer.statistics)

    #print(
        #analyzer.dataset["data_status"].value_counts()
    #)

    #print(analyzer.dataset.head())

    #print(analyzer.dataset["gap_size"].value_counts().sort_index())

    #print(
        #analyzer.dataset.loc[
            #analyzer.dataset["gap_size"] > 0,
            #["AE_kWh", "gap_size"]
        #].head(40)
    #)

if __name__ == "__main__":
    main()