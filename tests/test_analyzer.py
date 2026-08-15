import pandas as pd
import pytest

from helios.core.analyzer import ConsumptionAnalyzer


class TestConsumptionAnalyzer:

    # ==================================================
    # INITIALIZATION
    # ==================================================

    def test_initial_state(self):

        economics_configuration = {}

        analyzer = ConsumptionAnalyzer(
            economics_configuration
        )

        assert analyzer.dataset is None

        assert analyzer.cleaner is not None
        assert analyzer.statistics_engine is not None
        assert analyzer.comparisons_engine is not None
        assert analyzer.indicators_engine is not None
        assert analyzer.tariff_engine is not None
        assert analyzer.solar_engine is not None
        assert analyzer.quality_engine is not None
        assert analyzer.validation_engine is not None
        assert analyzer.economics_engine is not None

        assert analyzer.validation is not None
        assert analyzer.profiles is not None
        assert analyzer.comparisons is not None
        assert analyzer.indicators is not None
        assert analyzer.tariffs is not None
        assert analyzer.solar is not None
        assert analyzer.economics is not None
        assert analyzer.statistics is not None

        assert analyzer.statistics_reporter is not None
        assert analyzer.profile_reporter is not None
        assert analyzer.quality_reporter is not None
        assert analyzer.indicator_reporter is not None
        assert analyzer.tariff_reporter is not None

        assert analyzer.plotter is not None

        assert analyzer.quality is None
        assert analyzer.gap_summary is None

    # ==================================================
    # DATA LOADING
    # ==================================================

    def test_load_excel(self, tmp_path):

        file_path = tmp_path / "test.xlsx"

        dataframe = pd.DataFrame(
            {
                "Fecha": pd.to_datetime(
                    ["2025-01-01"]
                ),
                "Hora": [1],
                "AE_kWh": [1.5],
            }
        )

        with pd.ExcelWriter(file_path) as writer:
            dataframe.to_excel(
                writer,
                sheet_name="18_06_2025",
                index=False
            )

        analyzer = ConsumptionAnalyzer({})

        analyzer.load_excel(file_path)

        assert analyzer.dataset is not None
        assert len(analyzer.dataset) == 1
        assert list(analyzer.dataset.columns) == [
            "Fecha",
            "Hora",
            "AE_kWh",
        ]

    # ==================================================
    # DATA CLEANING
    # ==================================================

    def test_clean_data_delegates_to_cleaner(
        self,
        monkeypatch
    ):

        analyzer = ConsumptionAnalyzer({})

        dataset = pd.DataFrame(
            {
                "Fecha": pd.to_datetime(
                    ["2025-01-01"]
                ),
                "Hora": [1],
                "AE_kWh": [1.5],
            }
        )

        analyzer.dataset = dataset

        calls = []

        def fake_mark_missing(data):
            calls.append("mark_missing")
            return data

        def fake_classify_gaps(data):
            calls.append("classify_gaps")
            return data

        monkeypatch.setattr(
            analyzer.cleaner,
            "mark_missing_data",
            fake_mark_missing
        )

        monkeypatch.setattr(
            analyzer.cleaner,
            "classify_gaps",
            fake_classify_gaps
        )

        analyzer.clean_data()

        assert calls == [
            "mark_missing",
            "classify_gaps",
        ]

        assert analyzer.dataset is dataset

    # ==================================================
    # DATETIME
    # ==================================================

    def test_build_datetime(self):

        analyzer = ConsumptionAnalyzer({})

        analyzer.dataset = pd.DataFrame(
            {
                "Fecha": pd.to_datetime(
                    [
                        "2025-01-01",
                        "2025-01-01",
                        "2025-01-01",
                    ]
                ),
                "Hora": [1, 2, 3],
                "AE_kWh": [1.0, 2.0, 3.0],
            }
        )

        analyzer.build_datetime()

        assert isinstance(
            analyzer.dataset.index,
            pd.DatetimeIndex
        )

        assert list(analyzer.dataset.index) == [
            pd.Timestamp("2025-01-01 00:00:00"),
            pd.Timestamp("2025-01-01 01:00:00"),
            pd.Timestamp("2025-01-01 02:00:00"),
        ]

    def test_build_datetime_handles_hour_24(self):

        analyzer = ConsumptionAnalyzer({})

        analyzer.dataset = pd.DataFrame(
            {
                "Fecha": pd.to_datetime(
                    [
                        "2025-01-01",
                        "2025-01-01",
                    ]
                ),
                "Hora": [23, 24],
                "AE_kWh": [1.0, 2.0],
            }
        )

        analyzer.build_datetime()

        assert list(analyzer.dataset.index) == [
            pd.Timestamp("2025-01-01 22:00:00"),
            pd.Timestamp("2025-01-01 23:00:00"),
        ]

    def test_build_datetime_handles_hour_greater_than_24(self):

        analyzer = ConsumptionAnalyzer({})

        analyzer.dataset = pd.DataFrame(
            {
                "Fecha": pd.to_datetime(
                    [
                        "2025-01-01",
                        "2025-01-01",
                    ]
                ),
                "Hora": [24, 25],
                "AE_kWh": [1.0, 2.0],
            }
        )

        analyzer.build_datetime()

        assert list(analyzer.dataset.index) == [
            pd.Timestamp("2025-01-01 23:00:00"),
            pd.Timestamp("2025-01-01 23:30:00"),
        ]

    # ==================================================
    # VALID DATASET
    # ==================================================

    def test_valid_dataset_returns_only_valid_records(self):

        analyzer = ConsumptionAnalyzer({})

        analyzer.dataset = pd.DataFrame(
            {
                "AE_kWh": [1.0, 2.0, 3.0],
                "data_status": [
                    "valid",
                    "missing",
                    "valid",
                ],
            }
        )

        result = analyzer.valid_dataset()

        assert len(result) == 2
        assert list(result["AE_kWh"]) == [
            1.0,
            3.0,
        ]

    # ==================================================
    # VALIDATION
    # ==================================================

    def test_calculate_validation_delegates(
        self,
        monkeypatch
    ):

        analyzer = ConsumptionAnalyzer({})

        called = []

        monkeypatch.setattr(
            analyzer.validation,
            "calculate",
            lambda: called.append(True)
        )

        analyzer.calculate_validation()

        assert called == [True]

    def test_validation_reports_delegates(
        self,
        monkeypatch
    ):

        analyzer = ConsumptionAnalyzer({})

        called = []

        monkeypatch.setattr(
            analyzer.validation,
            "reports",
            lambda: called.append(True)
        )

        analyzer.validation_reports()

        assert called == [True]

    # ==================================================
    # STATISTICS
    # ==================================================

    def test_statistics_methods_delegate(
        self,
        monkeypatch
    ):

        analyzer = ConsumptionAnalyzer({})

        methods = [
            "calculate",
            "statistics_report",
            "daily_report",
            "monthly_report",
            "yearly_report",
            "reports",
        ]

        called = []

        for method in methods:
            monkeypatch.setattr(
                analyzer.statistics,
                method,
                lambda method=method: called.append(method)
            )

        analyzer.calculate_statistics()
        analyzer.statistics_report()
        analyzer.daily_report()
        analyzer.monthly_report()
        analyzer.yearly_report()
        analyzer.statistics_reports()

        assert called == methods

    # ==================================================
    # PROFILES
    # ==================================================

    def test_profile_methods_delegate(
        self,
        monkeypatch
    ):

        analyzer = ConsumptionAnalyzer({})

        called = []

        monkeypatch.setattr(
            analyzer.profiles,
            "calculate",
            lambda: called.append("calculate")
        )

        monkeypatch.setattr(
            analyzer.profiles,
            "reports",
            lambda: called.append("reports")
        )

        monkeypatch.setattr(
            analyzer.profiles,
            "plots",
            lambda: called.append("plots")
        )

        analyzer.calculate_profiles()
        analyzer.profile_reports()
        analyzer.profile_plots()

        assert called == [
            "calculate",
            "reports",
            "plots",
        ]

    # ==================================================
    # COMPARISONS
    # ==================================================

    def test_comparison_methods_delegate(
        self,
        monkeypatch
    ):

        analyzer = ConsumptionAnalyzer({})

        called = []

        monkeypatch.setattr(
            analyzer.comparisons,
            "calculate",
            lambda: called.append("calculate")
        )

        monkeypatch.setattr(
            analyzer.comparisons,
            "reports",
            lambda: called.append("reports")
        )

        monkeypatch.setattr(
            analyzer.comparisons,
            "plots",
            lambda: called.append("plots")
        )

        analyzer.calculate_comparisons()
        analyzer.comparison_reports()
        analyzer.comparison_plots()

        assert called == [
            "calculate",
            "reports",
            "plots",
        ]

    # ==================================================
    # INDICATORS
    # ==================================================

    def test_indicator_methods_delegate(
        self,
        monkeypatch
    ):

        analyzer = ConsumptionAnalyzer({})

        called = []

        monkeypatch.setattr(
            analyzer.indicators,
            "calculate",
            lambda: called.append("calculate")
        )

        monkeypatch.setattr(
            analyzer.indicators,
            "reports",
            lambda: called.append("reports")
        )

        analyzer.calculate_indicators()
        analyzer.indicator_reports()

        assert called == [
            "calculate",
            "reports",
        ]

    # ==================================================
    # TARIFFS
    # ==================================================

    def test_tariff_methods_delegate(
        self,
        monkeypatch
    ):

        analyzer = ConsumptionAnalyzer({})

        called = []

        monkeypatch.setattr(
            analyzer.tariffs,
            "calculate",
            lambda: called.append("calculate")
        )

        monkeypatch.setattr(
            analyzer.tariffs,
            "reports",
            lambda: called.append("reports")
        )

        analyzer.calculate_tariffs()
        analyzer.tariff_reports()

        assert called == [
            "calculate",
            "reports",
        ]

    # ==================================================
    # ECONOMICS
    # ==================================================

    def test_calculate_economics_delegates(
        self,
        monkeypatch
    ):

        analyzer = ConsumptionAnalyzer({})

        called = []

        monkeypatch.setattr(
            analyzer.economics,
            "calculate",
            lambda: called.append(True)
        )

        analyzer.calculate_economics()

        assert called == [True]

    def test_calculate_economic_scenarios_delegates(
        self,
        monkeypatch
    ):

        analyzer = ConsumptionAnalyzer({})

        scenarios = ["base", "optimistic"]
        expected = {"result": 123}

        def fake_calculate(scenarios_arg, years):

            assert scenarios_arg == scenarios
            assert years == 30

            return expected

        monkeypatch.setattr(
            analyzer.economics,
            "calculate_scenarios",
            fake_calculate
        )

        result = analyzer.calculate_economic_scenarios(
            scenarios,
            30
        )

        assert result == expected

    def test_economics_reports_delegates(
        self,
        monkeypatch
    ):

        analyzer = ConsumptionAnalyzer({})

        called = []

        monkeypatch.setattr(
            analyzer.economics,
            "reports",
            lambda: called.append(True)
        )

        analyzer.economics_reports()

        assert called == [True]

    # ==================================================
    # SOLAR
    # ==================================================

    def test_solar_methods_delegate(
        self,
        monkeypatch
    ):

        analyzer = ConsumptionAnalyzer({})

        called = []

        configuration = {
            "power": 5.0
        }

        def fake_calculate(config):

            called.append(config)

        monkeypatch.setattr(
            analyzer.solar,
            "calculate",
            fake_calculate
        )

        monkeypatch.setattr(
            analyzer.solar,
            "reports",
            lambda: called.append("reports")
        )

        analyzer.calculate_solar(configuration)
        analyzer.solar_reports()

        assert called == [
            configuration,
            "reports",
        ]

    # ==================================================
    # PLOTS
    # ==================================================

    def test_show_plots_delegates(
        self,
        monkeypatch
    ):

        analyzer = ConsumptionAnalyzer({})

        called = []

        monkeypatch.setattr(
            analyzer.plotter,
            "show",
            lambda: called.append(True)
        )

        analyzer.show_plots()

        assert called == [True]