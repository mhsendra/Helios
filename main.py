from helios.core.analyzer import ConsumptionAnalyzer

def main():
    analyzer = ConsumptionAnalyzer()

    analyzer.load_excel("data/raw/consumo electrico castellar.xlsx")
    analyzer.clean_data()
    analyzer.analyze_missing_data()
    analyzer.build_datetime()
    analyzer.validate_timeseries()
    analyzer.quality_report()
    analyzer.find_missing_hours()
    analyzer.find_duplicate_timestamps()
    analyzer.inspect_dst_days()

    print(analyzer.dataset.head())

if __name__ == "__main__":
    main()