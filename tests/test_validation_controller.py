import pandas as pd

from unittest.mock import MagicMock, call

from helios.core.controllers.validation_controller import (
    ValidationController
)


class TestValidationController:

    def setup_method(self):

        self.analyzer = MagicMock()

        self.analyzer.dataset = pd.DataFrame(
            {
                "Fecha": pd.to_datetime([]),
                "Hora": pd.Series(dtype=int),
                "AE_kWh": pd.Series(dtype=float),
            }
        )

        self.controller = ValidationController(
            self.analyzer
        )

    # ==================================================
    # Estado
    # ==================================================

    def test_controller_stores_analyzer(self):

        assert self.controller.analyzer is self.analyzer

    # ==================================================
    # Duplicados
    # ==================================================

    def test_find_duplicate_timestamps_delegates_and_stores_result(self):

        duplicates = pd.DataFrame(
            {
                "Hora": [10]
            }
        )

        (
            self.analyzer.validation_engine
            .find_duplicate_timestamps
            .return_value
        ) = duplicates

        self.controller.find_duplicate_timestamps()

        (
            self.analyzer.validation_engine
            .find_duplicate_timestamps
            .assert_called_once_with(
                self.analyzer.dataset
            )
        )

        assert self.analyzer.duplicates is duplicates

    # ==================================================
    # Gap summary
    # ==================================================

    def test_calculate_gap_summary_delegates_and_stores_result(self):

        summary = {
            "total_gaps": 3
        }

        (
            self.analyzer.validation_engine
            .calculate_gap_summary
            .return_value
        ) = summary

        self.controller.calculate_gap_summary()

        (
            self.analyzer.validation_engine
            .calculate_gap_summary
            .assert_called_once_with(
                self.analyzer.dataset
            )
        )

        assert self.analyzer.gap_summary is summary

    # ==================================================
    # Calidad
    # ==================================================

    def test_calculate_quality_delegates_and_stores_result(self):

        quality = {
            "missing_pct": 1.5
        }

        (
            self.analyzer.quality_engine
            .calculate
            .return_value
        ) = quality

        self.controller.calculate_quality()

        (
            self.analyzer.quality_engine
            .calculate
            .assert_called_once_with(
                self.analyzer.dataset
            )
        )

        assert self.analyzer.quality is quality

    # ==================================================
    # Reports individuales
    # ==================================================

    def test_quality_report_delegates_quality(self):

        self.analyzer.quality = {
            "score": 95
        }

        self.controller.quality_report()

        (
            self.analyzer.quality_reporter
            .quality
            .assert_called_once_with(
                self.analyzer.quality
            )
        )

    def test_duplicate_report_delegates_duplicates(self):

        self.analyzer.duplicates = ["duplicate"]

        self.controller.duplicate_report()

        (
            self.analyzer.quality_reporter
            .duplicates
            .assert_called_once_with(
                self.analyzer.duplicates
            )
        )

    def test_gap_report_delegates_gap_summary(self):

        self.analyzer.gap_summary = {
            "total": 2
        }

        self.controller.gap_report()

        (
            self.analyzer.quality_reporter
            .gap
            .assert_called_once_with(
                self.analyzer.gap_summary
            )
        )

    # ==================================================
    # reports()
    # ==================================================

    def test_reports_calls_all_reports_in_order(self):

        reporter = self.analyzer.quality_reporter

        self.controller.reports()

        assert reporter.mock_calls == [
            call.quality(
                self.analyzer.quality
            ),
            call.gap(
                self.analyzer.gap_summary
            ),
            call.duplicates(
                self.analyzer.duplicates
            ),
        ]

    # ==================================================
    # expected_hours_for_day()
    # ==================================================

    def test_expected_hours_for_normal_day(self):

        day = pd.Timestamp("2026-06-15")

        result = self.controller._expected_hours_for_day(
            day
        )

        assert result == set(range(1, 25))

    def test_expected_hours_for_summer_time_change(self):

        # Último domingo de marzo de 2026:
        # 29 de marzo

        day = pd.Timestamp("2026-03-29")

        result = self.controller._expected_hours_for_day(
            day
        )

        assert result == set(range(1, 24))

        assert len(result) == 23

    def test_expected_hours_for_winter_time_change(self):

        # Último domingo de octubre de 2026:
        # 25 de octubre

        day = pd.Timestamp("2026-10-25")

        result = self.controller._expected_hours_for_day(
            day
        )

        assert result == set(range(1, 26))

        assert len(result) == 25

    # ==================================================
    # find_missing_hours()
    # ==================================================

    def test_find_missing_hours_returns_valid_for_correct_normal_day(
        self
    ):

        date = pd.Timestamp("2026-06-15")

        self.analyzer.dataset = pd.DataFrame(
            {
                "Hora": list(range(1, 25))
            },
            index=[date] * 24
        )

        result = self.controller.find_missing_hours()

        assert result == {
            "valid": True,
            "errors": 0
        }

    def test_find_missing_hours_detects_missing_hour(
        self
    ):

        date = pd.Timestamp("2026-06-15")

        hours = list(range(1, 25))
        hours.remove(10)

        self.analyzer.dataset = pd.DataFrame(
            {
                "Hora": hours
            },
            index=[date] * len(hours)
        )

        result = self.controller.find_missing_hours()

        assert result == {
            "valid": False,
            "errors": 1
        }

    def test_find_missing_hours_detects_extra_hour(
        self
    ):

        date = pd.Timestamp("2026-06-15")

        hours = list(range(1, 26))

        self.analyzer.dataset = pd.DataFrame(
            {
                "Hora": hours
            },
            index=[date] * len(hours)
        )

        result = self.controller.find_missing_hours()

        assert result == {
            "valid": False,
            "errors": 1
        }

    def test_find_missing_hours_accepts_summer_time_change(
        self
    ):

        date = pd.Timestamp("2026-03-29")

        hours = list(range(1, 24))

        self.analyzer.dataset = pd.DataFrame(
            {
                "Hora": hours
            },
            index=[date] * len(hours)
        )

        result = self.controller.find_missing_hours()

        assert result == {
            "valid": True,
            "errors": 0
        }

    def test_find_missing_hours_accepts_winter_time_change(
        self
    ):

        date = pd.Timestamp("2026-10-25")

        hours = list(range(1, 26))

        self.analyzer.dataset = pd.DataFrame(
            {
                "Hora": hours
            },
            index=[date] * len(hours)
        )

        result = self.controller.find_missing_hours()

        assert result == {
            "valid": True,
            "errors": 0
        }

    def test_find_missing_hours_counts_multiple_invalid_days(
        self
    ):

        date_1 = pd.Timestamp("2026-06-15")
        date_2 = pd.Timestamp("2026-06-16")

        # Día 1: falta la hora 24
        df_1 = pd.DataFrame(
            {
                "Hora": list(range(1, 24))
            },
            index=[date_1] * 23
        )

        # Día 2: tiene una hora extra (25)
        df_2 = pd.DataFrame(
            {
                "Hora": list(range(1, 26))
            },
            index=[date_2] * 25
        )

        self.analyzer.dataset = pd.concat(
            [df_1, df_2]
        )

        result = self.controller.find_missing_hours()

        assert result == {
            "valid": False,
            "errors": 2
        }

    # ==================================================
    # calculate()
    # ==================================================

    def test_calculate_executes_all_steps_and_updates_stats(
        self
    ):

        self.analyzer.quality = {
            "missing_pct": 1.5,
            "corrected_pct": 2.0,
            "zero_days": 3,
            "anomaly_days": 4,
        }

        self.controller.validate_timeseries = MagicMock()
        self.controller.find_missing_hours = MagicMock()
        self.controller.find_duplicate_timestamps = MagicMock()

        self.controller.calculate_quality = MagicMock(
            side_effect=lambda: setattr(
                self.analyzer,
                "quality",
                {
                    "missing_pct": 1.5,
                    "corrected_pct": 2.0,
                    "zero_days": 3,
                    "anomaly_days": 4,
                }
            )
        )

        self.controller.calculate_gap_summary = MagicMock()

        self.controller.calculate()

        self.controller.validate_timeseries.assert_called_once_with()

        self.controller.find_missing_hours.assert_called_once_with()

        self.controller.find_duplicate_timestamps.assert_called_once_with()

        self.controller.calculate_quality.assert_called_once_with()

        self.controller.calculate_gap_summary.assert_called_once_with()

        assert self.analyzer.validation_stats == {
            "missing_pct": 1.5,
            "corrected_pct": 2.0,
            "zero_days": 3,
            "anomaly_days": 4,
        }

    def test_calculate_uses_default_values_for_missing_quality_keys(
        self
    ):

        self.analyzer.quality = {}

        self.controller.validate_timeseries = MagicMock()
        self.controller.find_missing_hours = MagicMock()
        self.controller.find_duplicate_timestamps = MagicMock()
        self.controller.calculate_quality = MagicMock()
        self.controller.calculate_gap_summary = MagicMock()

        self.controller.calculate()

        assert self.analyzer.validation_stats == {
            "missing_pct": 0,
            "corrected_pct": 0,
            "zero_days": 0,
            "anomaly_days": 0,
        }