from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QGroupBox,
    QFormLayout,
    QDoubleSpinBox,
    QComboBox,
    QPushButton,
    QSpinBox,
    QLabel,
    QTableWidget,
    QAbstractItemView,
    QTableWidgetItem,
)

import pandas as pd

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from helios.solar.configuration import SolarConfiguration


class SolarPage(QWidget):

    def __init__(self, project, main_window=None):
        super().__init__()

        self.project = project
        self.main_window = main_window

        self.setup_ui()

        self.configure_widgets()

        self.connect_signals()

    # ==========================================================
    # UI
    # ==========================================================

    def setup_ui(self):

        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()

        layout.addWidget(self.tabs)

        self.configuration_tab = QWidget()
        self.production_tab = QWidget()
        self.balance_tab = QWidget()
        self.statistics_tab = QWidget()

        self.tabs.addTab(
            self.configuration_tab,
            "Configuración",
        )

        self.tabs.addTab(
            self.production_tab,
            "Producción",
        )

        self.tabs.addTab(
            self.balance_tab,
            "Balance",
        )

        self.tabs.addTab(
            self.statistics_tab,
            "Estadísticas",
        )

        self.build_configuration_tab()
        self.build_production_tab()
        self.build_balance_tab()
        self.build_statistics_tab()

        self.set_results_available(False)

    def configure_widgets(self):

        self.configure_pv_technology()
        self.configure_system_losses()
        self.configure_tilt()
        self.configure_azimuth()
        self.configure_mounting_place()

        self.configure_latitude()
        self.configure_longitude()

        self.configure_production_page()
        self.configure_monthly_production_table()
        self.configure_balance_table()

    # ==========================================================
    # Configuration tab
    # ==========================================================

    def build_configuration_tab(self):

        layout = QVBoxLayout(
            self.configuration_tab
        )

        layout.addWidget(
            self.create_installation_group()
        )

        layout.addWidget(
            self.create_location_group()
        )

        layout.addStretch()

    def create_installation_group(self):

        group = QGroupBox("Instalación")

        layout = QFormLayout(group)

        self.pv_technology_combobox = QComboBox()
        self.system_losses_spinbox = QDoubleSpinBox()
        self.tilt_spinbox = QSpinBox()
        self.azimuth_spinbox = QSpinBox()
        self.mounting_place_combobox = QComboBox()

        layout.addRow(
            "Tecnología FV",
            self.pv_technology_combobox,
        )

        layout.addRow(
            "Pérdidas del sistema",
            self.system_losses_spinbox,
        )

        layout.addRow(
            "Inclinación",
            self.tilt_spinbox,
        )

        layout.addRow(
            "Orientación",
            self.azimuth_spinbox,
        )

        layout.addRow(
            "Montaje",
            self.mounting_place_combobox,
        )

        return group

    def create_location_group(self):

        group = QGroupBox("Ubicación")

        layout = QFormLayout(group)

        self.latitude_spinbox = QDoubleSpinBox()
        self.longitude_spinbox = QDoubleSpinBox()

        layout.addRow(
            "Latitud",
            self.latitude_spinbox,
        )

        layout.addRow(
            "Longitud",
            self.longitude_spinbox,
        )

        return group

    def configure_system_losses(self):

        self.system_losses_spinbox.setRange(
            0.0,
            100.0,
        )

        self.system_losses_spinbox.setDecimals(1)

        self.system_losses_spinbox.setSingleStep(
            0.5
        )

        self.system_losses_spinbox.setSuffix(
            " %"
        )

    def configure_pv_technology(self):

        self.pv_technology_combobox.addItem(
            "Silicio cristalino",
            "crystSi",
        )

        self.pv_technology_combobox.addItem(
            "CIS",
            "CIS",
        )

        self.pv_technology_combobox.addItem(
            "CdTe",
            "CdTe",
        )

    def configure_latitude(self):

        self.latitude_spinbox.setRange(
            -90.0,
            90.0,
        )

        self.latitude_spinbox.setDecimals(6)

        self.latitude_spinbox.setSingleStep(
            0.000001
        )

    def configure_longitude(self):

        self.longitude_spinbox.setRange(
            -180.0,
            180.0,
        )

        self.longitude_spinbox.setDecimals(6)

        self.longitude_spinbox.setSingleStep(
            0.000001
        )

    def configure_tilt(self):

        self.tilt_spinbox.setRange(
            0,
            90,
        )

        self.tilt_spinbox.setSuffix(
            " °"
        )

    def configure_azimuth(self):

        self.azimuth_spinbox.setRange(
            -180,
            180,
        )

        self.azimuth_spinbox.setSuffix(
            " °"
        )

    def configure_mounting_place(self):

        self.mounting_place_combobox.addItem(
            "Estructura sobre el suelo",
            "free",
        )

        self.mounting_place_combobox.addItem(
            "Integrado en edificio",
            "building",
        )

    def get_configuration(self) -> SolarConfiguration:

        return SolarConfiguration(
            latitude=self.latitude_spinbox.value(),
            longitude=self.longitude_spinbox.value(),
            tilt=self.tilt_spinbox.value(),
            azimuth=self.azimuth_spinbox.value(),
            reference_year=2023,
            losses=self.system_losses_spinbox.value(),
            pv_technology=(
                self.pv_technology_combobox.currentData()
            ),
            mounting_place=(
                self.mounting_place_combobox.currentData()
            ),
        )

    # ==========================================================
    # Production tab
    # ==========================================================

    def build_production_tab(self):

        layout = QVBoxLayout(
            self.production_tab
        )

        layout.addWidget(
            self.create_production_status_group()
        )

        layout.addWidget(
            self.create_production_summary_group()
        )

        layout.addWidget(
            self.create_monthly_production_group()
        )

        layout.addStretch()

    def create_production_status_group(self):

        group = QGroupBox(
            "Estado de la producción"
        )

        layout = QFormLayout(group)

        self.source_label = QLabel("-")
        self.database_label = QLabel("-")
        self.reference_year_label = QLabel("-")
        self.last_update_label = QLabel("-")
        self.production_status_label = QLabel("-")

        layout.addRow(
            "Fuente",
            self.source_label,
        )

        layout.addRow(
            "Base de datos",
            self.database_label,
        )

        layout.addRow(
            "Año de referencia",
            self.reference_year_label,
        )

        layout.addRow(
            "Última actualización",
            self.last_update_label,
        )

        layout.addRow(
            "Estado",
            self.production_status_label,
        )

        self.calculate_production_button = QPushButton(
            "Calcular producción"
        )

        layout.addRow(
            "",
            self.calculate_production_button,
        )

        return group

    def create_production_summary_group(self):

        group = QGroupBox("Resumen")

        layout = QFormLayout(group)

        self.production_annual_label = QLabel("-")
        self.production_specific_label = QLabel("-")
        self.production_coverage_label = QLabel("-")

        layout.addRow(
            "Producción anual",
            self.production_annual_label,
        )

        layout.addRow(
            "Producción específica",
            self.production_specific_label,
        )

        layout.addRow(
            "Cobertura",
            self.production_coverage_label,
        )

        return group

    def configure_production_page(self):

        self.source_label.setText(
            "PVGIS"
        )

        self.database_label.setText(
            "SARAH3"
        )

        self.reference_year_label.setText(
            "-"
        )

        self.last_update_label.setText(
            "Nunca"
        )

        self.production_status_label.setText(
            "No calculada"
        )

        self.production_annual_label.setText(
            "-"
        )

        self.production_specific_label.setText(
            "-"
        )

        self.production_coverage_label.setText(
            "-"
        )

        self.calculate_production_button.setMinimumHeight(
            40
        )

        self.calculate_production_button.setToolTip(
            "Obtiene la producción fotovoltaica desde PVGIS."
        )

    def update_production_status(
        self,
        source: str,
        database: str,
        reference_year: int | None,
        last_update: str,
        status: str,
        annual_production: float | None,
        specific_production: float | None,
        coverage: float | None,
    ):

        self.source_label.setText(
            source
        )

        self.database_label.setText(
            database
        )

        self.reference_year_label.setText(
            "-"
            if reference_year is None
            else str(reference_year)
        )

        self.last_update_label.setText(
            last_update
        )

        self.production_status_label.setText(
            status
        )

        self.production_annual_label.setText(
            "-"
            if annual_production is None
            else f"{annual_production:,.1f} kWh"
        )

        self.production_specific_label.setText(
            "-"
            if specific_production is None
            else f"{specific_production:,.1f} kWh/kWp"
        )

        self.production_coverage_label.setText(
            "-"
            if coverage is None
            else f"{coverage:.1f} %"
        )

    def connect_signals(self):

        self.calculate_production_button.clicked.connect(
            self.calculate_production
        )

    def calculate_production(self):

        configuration = (
            self.project.solar_configuration
        )

        if configuration is None:

            raise ValueError(
                "Solar configuration is required "
                "before calculating production."
            )

        self.update_production_status(
            source="PVGIS",
            database="SARAH3",
            reference_year=(
                configuration.reference_year
            ),
            last_update="Calculando...",
            status="Calculando...",
            annual_production=None,
            specific_production=None,
            coverage=None,
        )

        try:

            self.project.solar.calculate(
                configuration
            )

            self.refresh_production_results()

            self.set_results_available(
                True
            )

            if self.main_window is not None:

                self.main_window.set_solar_calculated(
                    True
                )

        except Exception as error:

            self.update_production_status(
                source="PVGIS",
                database="SARAH3",
                reference_year=(
                    configuration.reference_year
                ),
                last_update="-",
                status=f"Error: {error}",
                annual_production=None,
                specific_production=None,
                coverage=None,
            )

    def refresh_production_results(self):

        solar = self.project.solar

        configuration = (
            self.project.solar_configuration
        )

        self.update_production_status(
            source="PVGIS",
            database="SARAH3",
            reference_year=(
                configuration.reference_year
                if configuration is not None
                else None
            ),
            last_update="Ahora",
            status="Disponible",
            annual_production=(
                solar.annual_production
            ),
            specific_production=(
                solar.specific_production
            ),
            coverage=(
                solar.coverage
            ),
        )

        self.update_monthly_production()
        self.update_balance()
        self.update_statistics()

    # ==========================================================
    # Monthly production
    # ==========================================================

    def create_monthly_production_group(self):

        group = QGroupBox(
            "Producción mensual"
        )

        layout = QVBoxLayout(group)

        self.monthly_production_table = (
            QTableWidget()
        )

        layout.addWidget(
            self.monthly_production_table
        )

        return group

    def configure_monthly_production_table(self):

        table = (
            self.monthly_production_table
        )

        table.setColumnCount(2)

        table.setHorizontalHeaderLabels(
            [
                "Mes",
                "Producción (kWh)",
            ]
        )

        table.verticalHeader().setVisible(
            False
        )

        table.verticalHeader().setDefaultSectionSize(
            24
        )

        table.setAlternatingRowColors(
            True
        )

        table.horizontalHeader().setStretchLastSection(
            True
        )

        table.horizontalHeader().setDefaultAlignment(
            Qt.AlignCenter
        )

        table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        table.setSelectionMode(
            QAbstractItemView.NoSelection
        )

        table.setFocusPolicy(
            Qt.NoFocus
        )

    def update_monthly_production(self):

        solar = self.project.solar

        series = getattr(
            solar,
            "monthly_production",
            None,
        )

        self.populate_monthly_table(
            self.monthly_production_table,
            series,
        )

    def populate_monthly_table(
        self,
        table: QTableWidget,
        series: pd.Series,
    ):

        if series is None or series.empty:

            table.setRowCount(0)

            return

        months = [
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre",
        ]

        table.setRowCount(
            len(series) + 1
        )

        total = 0.0

        for row, (date, value) in enumerate(
            series.items()
        ):

            total += value

            month_item = QTableWidgetItem(
                months[date.month - 1]
            )

            month_item.setTextAlignment(
                Qt.AlignCenter
            )

            value_item = QTableWidgetItem(
                f"{value:.2f}"
            )

            value_item.setTextAlignment(
                Qt.AlignRight
                | Qt.AlignVCenter
            )

            table.setItem(
                row,
                0,
                month_item,
            )

            table.setItem(
                row,
                1,
                value_item,
            )

        total_row = len(series)

        total_label = QTableWidgetItem(
            "TOTAL"
        )

        total_value = QTableWidgetItem(
            f"{total:.2f}"
        )

        font = QFont()
        font.setBold(True)

        total_label.setFont(font)
        total_value.setFont(font)

        total_value.setTextAlignment(
            Qt.AlignRight
            | Qt.AlignVCenter
        )

        table.setItem(
            total_row,
            0,
            total_label,
        )

        table.setItem(
            total_row,
            1,
            total_value,
        )

        table.resizeColumnsToContents()

    # ==========================================================
    # Balance tab
    # ==========================================================

    def build_balance_tab(self):

        layout = QVBoxLayout(
            self.balance_tab
        )

        layout.addWidget(
            self.create_balance_summary_group()
        )

        layout.addWidget(
            self.create_balance_table()
        )

    def create_balance_summary_group(self):

        group = QGroupBox(
            "Resumen del balance"
        )

        layout = QFormLayout(group)

        self.balance_total_consumption_label = (
            QLabel("-")
        )

        self.balance_total_production_label = (
            QLabel("-")
        )

        self.balance_self_consumption_label = (
            QLabel("-")
        )

        self.balance_grid_import_label = (
            QLabel("-")
        )

        self.balance_grid_export_label = (
            QLabel("-")
        )

        self.balance_coverage_label = (
            QLabel("-")
        )

        layout.addRow(
            "Consumo total",
            self.balance_total_consumption_label,
        )

        layout.addRow(
            "Producción total",
            self.balance_total_production_label,
        )

        layout.addRow(
            "Autoconsumo",
            self.balance_self_consumption_label,
        )

        layout.addRow(
            "Importación de red",
            self.balance_grid_import_label,
        )

        layout.addRow(
            "Exportación a red",
            self.balance_grid_export_label,
        )

        layout.addRow(
            "Cobertura",
            self.balance_coverage_label,
        )

        return group

    def create_balance_table(self):

        group = QGroupBox(
            "Balance mensual"
        )

        layout = QVBoxLayout(group)

        self.balance_table = QTableWidget()

        layout.addWidget(
            self.balance_table
        )

        return group

    def configure_balance_table(self):

        table = self.balance_table

        table.setColumnCount(4)

        table.setHorizontalHeaderLabels(
            [
                "Mes",
                "Autoconsumo (kWh)",
                "Importación (kWh)",
                "Exportación (kWh)",
            ]
        )

        table.verticalHeader().setVisible(
            False
        )

        table.verticalHeader().setDefaultSectionSize(
            24
        )

        table.setAlternatingRowColors(
            True
        )

        table.horizontalHeader().setStretchLastSection(
            True
        )

        table.horizontalHeader().setDefaultAlignment(
            Qt.AlignCenter
        )

        table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        table.setSelectionMode(
            QAbstractItemView.NoSelection
        )

        table.setFocusPolicy(
            Qt.NoFocus
        )

    def update_balance(self):

        solar = self.project.solar

        balance = getattr(
            solar,
            "energy_balance",
            None,
        )

        self.populate_balance_table(
            self.balance_table,
            balance,
        )

        self.update_balance_summary()

    def populate_balance_table(
        self,
        table: QTableWidget,
        balance: pd.DataFrame,
    ):

        if balance is None or balance.empty:

            table.setRowCount(0)

            return

        months = [
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre",
        ]

        table.setRowCount(
            len(balance) + 1
        )

        total_self_consumption = 0.0
        total_grid_import = 0.0
        total_grid_export = 0.0

        for row, (date, values) in enumerate(
            balance.iterrows()
        ):

            self_consumption = float(
                values["self_consumption_kwh"]
            )

            grid_import = float(
                values["grid_import_kwh"]
            )

            grid_export = float(
                values["grid_export_kwh"]
            )

            total_self_consumption += (
                self_consumption
            )

            total_grid_import += (
                grid_import
            )

            total_grid_export += (
                grid_export
            )

            month_item = QTableWidgetItem(
                months[date.month - 1]
            )

            month_item.setTextAlignment(
                Qt.AlignCenter
            )

            values_items = [
                QTableWidgetItem(
                    f"{self_consumption:.2f}"
                ),
                QTableWidgetItem(
                    f"{grid_import:.2f}"
                ),
                QTableWidgetItem(
                    f"{grid_export:.2f}"
                ),
            ]

            for item in values_items:

                item.setTextAlignment(
                    Qt.AlignRight
                    | Qt.AlignVCenter
                )

            table.setItem(
                row,
                0,
                month_item,
            )

            table.setItem(
                row,
                1,
                values_items[0],
            )

            table.setItem(
                row,
                2,
                values_items[1],
            )

            table.setItem(
                row,
                3,
                values_items[2],
            )

        total_row = len(balance)

        total_label = QTableWidgetItem(
            "TOTAL"
        )

        total_items = [
            QTableWidgetItem(
                f"{total_self_consumption:.2f}"
            ),
            QTableWidgetItem(
                f"{total_grid_import:.2f}"
            ),
            QTableWidgetItem(
                f"{total_grid_export:.2f}"
            ),
        ]

        font = QFont()
        font.setBold(True)

        total_label.setFont(font)

        for item in total_items:

            item.setFont(font)

            item.setTextAlignment(
                Qt.AlignRight
                | Qt.AlignVCenter
            )

        table.setItem(
            total_row,
            0,
            total_label,
        )

        for column, item in enumerate(
            total_items,
            start=1,
        ):

            table.setItem(
                total_row,
                column,
                item,
            )

        table.resizeColumnsToContents()

    def update_balance_summary(self):

        solar = self.project.solar

        balance = getattr(
            solar,
            "energy_balance",
            None,
        )

        if balance is None or balance.empty:

            labels = [
                self.balance_total_consumption_label,
                self.balance_total_production_label,
                self.balance_self_consumption_label,
                self.balance_grid_import_label,
                self.balance_grid_export_label,
                self.balance_coverage_label,
            ]

            for label in labels:

                label.setText("-")

            return

        self.balance_total_consumption_label.setText(
            f"{balance['consumption_kwh'].sum():.2f} kWh"
        )

        self.balance_total_production_label.setText(
            f"{balance['production_kwh'].sum():.2f} kWh"
        )

        self.balance_self_consumption_label.setText(
            f"{balance['self_consumption_kwh'].sum():.2f} kWh"
        )

        self.balance_grid_import_label.setText(
            f"{balance['grid_import_kwh'].sum():.2f} kWh"
        )

        self.balance_grid_export_label.setText(
            f"{balance['grid_export_kwh'].sum():.2f} kWh"
        )

        coverage = getattr(
            solar,
            "coverage",
            None,
        )

        self.balance_coverage_label.setText(
            "-"
            if coverage is None
            else f"{coverage:.1f} %"
        )

    # ==========================================================
    # Statistics tab
    # ==========================================================

    def build_statistics_tab(self):

        layout = QVBoxLayout(
            self.statistics_tab
        )

        group = QGroupBox(
            "Indicadores técnicos"
        )

        form = QFormLayout(group)

        self.stats_annual_production_label = (
            QLabel("-")
        )

        self.stats_specific_production_label = (
            QLabel("-")
        )

        self.stats_equivalent_hours_label = (
            QLabel("-")
        )

        self.stats_capacity_factor_label = (
            QLabel("-")
        )

        self.stats_coverage_label = (
            QLabel("-")
        )

        self.stats_self_consumption_ratio_label = (
            QLabel("-")
        )

        self.stats_self_sufficiency_ratio_label = (
            QLabel("-")
        )

        self.stats_import_label = (
            QLabel("-")
        )

        self.stats_export_label = (
            QLabel("-")
        )

        self.stats_self_consumption_label = (
            QLabel("-")
        )

        self.stats_total_consumption_label = (
            QLabel("-")
        )

        form.addRow(
            "Producción anual",
            self.stats_annual_production_label,
        )

        form.addRow(
            "Producción específica",
            self.stats_specific_production_label,
        )

        form.addRow(
            "Horas equivalentes",
            self.stats_equivalent_hours_label,
        )

        form.addRow(
            "Factor de capacidad",
            self.stats_capacity_factor_label,
        )

        form.addRow(
            "Cobertura",
            self.stats_coverage_label,
        )

        form.addRow(
            "Ratio de autoconsumo",
            self.stats_self_consumption_ratio_label,
        )

        form.addRow(
            "Ratio de autosuficiencia",
            self.stats_self_sufficiency_ratio_label,
        )

        form.addRow(
            "Importación de red",
            self.stats_import_label,
        )

        form.addRow(
            "Exportación a red",
            self.stats_export_label,
        )

        form.addRow(
            "Autoconsumo",
            self.stats_self_consumption_label,
        )

        form.addRow(
            "Consumo total",
            self.stats_total_consumption_label,
        )

        layout.addWidget(group)

        layout.addStretch()

    def update_statistics(self):

        solar = self.project.solar

        statistics = getattr(
            solar,
            "statistics",
            None,
        )

        labels = [
            self.stats_annual_production_label,
            self.stats_specific_production_label,
            self.stats_equivalent_hours_label,
            self.stats_capacity_factor_label,
            self.stats_coverage_label,
            self.stats_self_consumption_ratio_label,
            self.stats_self_sufficiency_ratio_label,
            self.stats_import_label,
            self.stats_export_label,
            self.stats_self_consumption_label,
            self.stats_total_consumption_label,
        ]

        if not statistics:

            for label in labels:

                label.setText("-")

            return

        self.stats_annual_production_label.setText(
            f"{statistics['period_production']:,.2f} kWh"
        )

        self.stats_specific_production_label.setText(
            f"{statistics['specific_yield']:,.2f} kWh/kWp"
        )

        self.stats_equivalent_hours_label.setText(
            f"{statistics['equivalent_hours']:,.0f} h"
        )

        self.stats_capacity_factor_label.setText(
            f"{statistics['capacity_factor']:.1f} %"
        )

        self.stats_coverage_label.setText(
            f"{statistics['coverage_ratio']:.1f} %"
        )

        self.stats_self_consumption_ratio_label.setText(
            f"{statistics['self_consumption_ratio']:.1f} %"
        )

        self.stats_self_sufficiency_ratio_label.setText(
            f"{statistics['self_sufficiency']:.1f} %"
        )

        self.stats_import_label.setText(
            f"{statistics['grid_import']:,.2f} kWh"
        )

        self.stats_export_label.setText(
            f"{statistics['grid_export']:,.2f} kWh"
        )

        self.stats_self_consumption_label.setText(
            f"{statistics['self_consumption']:,.2f} kWh"
        )

        self.stats_total_consumption_label.setText(
            f"{statistics['consumption']:,.2f} kWh"
        )

    # ==========================================================
    # Results state
    # ==========================================================

    def set_results_available(
        self,
        available: bool,
    ):

        balance_index = self.tabs.indexOf(
            self.balance_tab
        )

        statistics_index = self.tabs.indexOf(
            self.statistics_tab
        )

        self.tabs.setTabEnabled(
            balance_index,
            available,
        )

        self.tabs.setTabEnabled(
            statistics_index,
            available,
        )

    # ==========================================================
    # Reset
    # ==========================================================

    def reset(self):

        self.set_results_available(
            False
        )

        self.update_production_status(
            source="PVGIS",
            database="SARAH3",
            reference_year=None,
            last_update="Nunca",
            status="No calculada",
            annual_production=None,
            specific_production=None,
            coverage=None,
        )

        self.monthly_production_table.setRowCount(
            0
        )

        self.balance_table.setRowCount(
            0
        )

        self.update_balance_summary()

        self.update_statistics()

    def reset_results(self):
        """
        Resetea los resultados solares de la página.

        No modifica la configuración solar persistente.
        """

        solar = self.project.solar

        solar.annual_production = None
        solar.specific_production = None
        solar.coverage = None
        solar.monthly_production = None
        solar.energy_balance = None
        solar.statistics = None

        self.update_production_status(
            source="PVGIS",
            database="SARAH3",
            reference_year=None,
            last_update="Nunca",
            status="No calculada",
            annual_production=None,
            specific_production=None,
            coverage=None,
        )

        self.monthly_production_table.setRowCount(0)
        self.balance_table.setRowCount(0)

        self.update_balance_summary()
        self.update_statistics()

        self.set_results_available(False)