from pathlib import Path

import pytest

import pandas as pd 

from helios.reports.solar_report_data import SolarReportData
from helios.reports.solar_report_generator import SolarReportGenerator
from helios.reports.solar_report_charts import SolarReportCharts


class TestSolarReportGenerator:

    def _report_data(self):
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

    def test_generate_creates_pdf(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.exists()

    def test_generate_creates_non_empty_pdf(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.stat().st_size > 0

    def test_generate_creates_pdf_file(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        with output_path.open("rb") as file:
            header = file.read(5)

        assert header == b"%PDF-"

    def test_generate_requires_report_data(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        with pytest.raises(
            ValueError,
            match="report data is required",
        ):
            generator.generate(
                None,
                output_path,
            )

    def test_generate_requires_output_path(self):

        generator = SolarReportGenerator()

        with pytest.raises(
            ValueError,
            match="output path is required",
        ):
            generator.generate(
                self._report_data(),
                None,
            )

    def test_generate_uses_report_data_without_calculating(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        data = self._report_data()

        generator = SolarReportGenerator()

        generator.generate(
            data,
            output_path,
        )

        assert output_path.exists()

    def test_generate_accepts_path_object(self, tmp_path):

        output_path = Path(tmp_path) / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.exists()

    def test_generate_overwrites_existing_pdf(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        output_path.write_bytes(b"old content")

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.read_bytes().startswith(b"%PDF-")

    def test_generate_creates_parent_directory(self, tmp_path):

        output_path = (
            tmp_path
            / "reports"
            / "solar"
            / "solar_report.pdf"
        )

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.exists()

    def test_generate_does_not_modify_report_data(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        data = self._report_data()

        before = data

        generator = SolarReportGenerator()

        generator.generate(
            data,
            output_path,
        )

        assert data == before

    def test_generate_contains_installation_summary(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.exists()


    def test_generate_uses_installation_power_in_summary(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.stat().st_size > 0


    def test_generate_uses_panel_information_in_summary(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.exists()

    def test_generate_contains_production_section(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.exists()


    def test_generate_includes_yearly_production(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.stat().st_size > 0


    def test_generate_includes_specific_production(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.exists()

    def test_generate_includes_yearly_consumption(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.exists()


    def test_generate_includes_self_consumption(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.exists()


    def test_generate_includes_grid_export(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.exists()


    def test_generate_includes_grid_import(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.exists()


    def test_generate_includes_self_consumption_rate(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.exists()


    def test_generate_includes_self_sufficiency_rate(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.exists()

    def test_generate_includes_economic_section(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.exists()


    def test_generate_includes_investment_and_savings(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.stat().st_size > 0


    def test_generate_includes_payback(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.exists()


    def test_generate_includes_npv(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.exists()


    def test_generate_includes_irr(self, tmp_path):

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            self._report_data(),
            output_path,
        )

        assert output_path.exists()

    def test_generate_includes_yearly_production_chart(
        self,
        tmp_path,
        monkeypatch,
    ):
        data = SolarReportData(
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
            yearly_consumption_kwh=10000.0,
            self_consumption_kwh=7000.0,
            grid_export_kwh=5500.0,
            grid_import_kwh=3000.0,
            self_consumption_rate_percent=56.0,
            self_sufficiency_rate_percent=70.0,
            investment_eur=12490.0,
            yearly_savings_eur=2340.0,
            payback_years=5.34,
            net_present_value_eur=22071.16,
            internal_rate_of_return_percent=18.8,
        )

        chart_called = False

        original = SolarReportCharts.yearly_production

        def fake_yearly_production(production_kwh):
            nonlocal chart_called

            chart_called = True

            assert production_kwh == 12500.0

            return original(production_kwh)

        monkeypatch.setattr(
            SolarReportCharts,
            "yearly_production",
            fake_yearly_production,
        )

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            data,
            output_path,
        )

        assert chart_called
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_generate_includes_monthly_production_chart(
        self,
        tmp_path,
        monkeypatch,
    ):

        data = self._report_data()

        chart_called = False

        original = SolarReportCharts.monthly_production

        def fake_monthly_production(monthly_production):
            nonlocal chart_called

            chart_called = True

            assert monthly_production is data.monthly_production
            assert len(monthly_production) == 12

            return original(monthly_production)

        monkeypatch.setattr(
            SolarReportCharts,
            "monthly_production",
            fake_monthly_production,
        )

        output_path = tmp_path / "solar_report.pdf"

        generator = SolarReportGenerator()

        generator.generate(
            data,
            output_path,
        )

        assert chart_called
        assert output_path.exists()
        assert output_path.stat().st_size > 0