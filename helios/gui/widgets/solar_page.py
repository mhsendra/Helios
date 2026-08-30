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

    def setup_ui(self):

        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()

        layout.addWidget(self.tabs)

        self.configuration_tab = QWidget()
        self.production_tab = QWidget()
        self.balance_tab = QWidget()
        self.statistics_tab = QWidget()

        self.tabs.addTab(self.configuration_tab, "Configuración")
        self.tabs.addTab(self.production_tab, "Producción")
        self.tabs.addTab(self.balance_tab, "Balance")
        self.tabs.addTab(self.statistics_tab, "Estadísticas")

        self.build_configuration_tab()
        self.build_production_tab()
        self.build_balance_tab()
        self.build_statistics_tab()

        self.set_results_available(False)

    def configure_widgets(self):

        self.configure_peak_power()
        self.configure_pv_technology()
        self.configure_system_losses()
        self.configure_tilt()
        self.configure_azimuth()
        self.configure_mounting_place()

        self.configure_latitude()
        self.configure_longitude()

        self.configure_production_page()
        self.configure_monthly_production_table()

    def configure_peak_power(self):

        self.peak_power_spinbox.setRange(0.10, 100.00)
        self.peak_power_spinbox.setDecimals(2)
        self.peak_power_spinbox.setSingleStep(0.10)
        self.peak_power_spinbox.setSuffix(" kWp")

    def build_configuration_tab(self):

        layout = QVBoxLayout(self.configuration_tab)

        layout.addWidget(self.create_installation_group())
        layout.addWidget(self.create_location_group())

        layout.addStretch()

    def build_production_tab(self):

        layout = QVBoxLayout(self.production_tab)

        layout.addWidget(self.create_production_status_group())
        layout.addWidget(self.create_production_summary_group())
        layout.addWidget(self.create_monthly_production_group())

        layout.addStretch()

    def build_balance_tab(self):

        layout = QVBoxLayout(self.balance_tab)

        layout.addWidget(
            self.create_balance_summary_group()
        )

        layout.addWidget(
            self.create_balance_table()
        )

    def build_statistics_tab(self):

        layout = QVBoxLayout(self.statistics_tab)

        group = QGroupBox("Indicadores técnicos")

        form = QFormLayout(group)

        self.stats_annual_production_label = QLabel("-")
        self.stats_specific_production_label = QLabel("-")
        self.stats_equivalent_hours_label = QLabel("-")
        self.stats_capacity_factor_label = QLabel("-")

        self.stats_coverage_label = QLabel("-")
        self.stats_self_consumption_ratio_label = QLabel("-")
        self.stats_self_sufficiency_ratio_label = QLabel("-")

        self.stats_import_label = QLabel("-")
        self.stats_export_label = QLabel("-")

        self.stats_self_consumption_label = QLabel("-")
        self.stats_total_consumption_label = QLabel("-")

        form.addRow(
            "Producción anual",
            self.stats_annual_production_label
        )

        form.addRow(
            "Producción específica",
            self.stats_specific_production_label
        )

        form.addRow(
            "Horas equivalentes",
            self.stats_equivalent_hours_label
        )

        form.addRow(
            "Factor de capacidad",
            self.stats_capacity_factor_label
        )

        form.addRow(
            "Cobertura",
            self.stats_coverage_label
        )

        form.addRow(
            "Ratio de autoconsumo",
            self.stats_self_consumption_ratio_label
        )

        form.addRow(
            "Ratio de autosuficiencia",
            self.stats_self_sufficiency_ratio_label
        )

        form.addRow(
            "Importación de red",
            self.stats_import_label
        )

        form.addRow(
            "Exportación a red",
            self.stats_export_label
        )

        form.addRow(
            "Autoconsumo",
            self.stats_self_consumption_label
        )

        form.addRow(
            "Consumo total",
            self.stats_total_consumption_label
        )

        layout.addWidget(group)
        layout.addStretch()

    def create_installation_group(self):

        group = QGroupBox("Instalación")

        layout = QFormLayout(group)

        self.peak_power_spinbox = QDoubleSpinBox()
        self.pv_technology_combobox = QComboBox()
        self.system_losses_spinbox = QDoubleSpinBox()
        self.tilt_spinbox = QSpinBox()
        self.azimuth_spinbox = QSpinBox()
        self.mounting_place_combobox = QComboBox()

        layout.addRow("Potencia instalada",self.peak_power_spinbox)
        layout.addRow("Tecnología FV", self.pv_technology_combobox)
        layout.addRow("Pérdidas del sistema", self.system_losses_spinbox)
        layout.addRow("Inclinación", self.tilt_spinbox)
        layout.addRow("Orientación", self.azimuth_spinbox)
        layout.addRow("Montaje", self.mounting_place_combobox)

        return group

    def create_location_group(self):

        group = QGroupBox("Ubicación")

        layout = QFormLayout(group)

        self.latitude_spinbox = QDoubleSpinBox()
        self.longitude_spinbox = QDoubleSpinBox()

        layout.addRow("Latitud", self.latitude_spinbox)
        layout.addRow("Longitud", self.longitude_spinbox)

        # Futuro:
        # Cuando Helios disponga de una ubicación asociada al proyecto,
        # este botón permitirá cargar automáticamente la latitud y la
        # longitud en la configuración solar.

        # self.load_location_button = QPushButton(
        #     "Usar ubicación del proyecto"
        # )
        #
        # layout.addRow("", self.load_location_button)

        return group

    def configure_system_losses(self):

        self.system_losses_spinbox.setRange(0.0, 100.0)
        self.system_losses_spinbox.setDecimals(1)
        self.system_losses_spinbox.setSingleStep(0.5)
        self.system_losses_spinbox.setSuffix(" %")

    def configure_pv_technology(self):

        self.pv_technology_combobox.addItem(
            "Silicio cristalino",
            "crystSi"
        )

        self.pv_technology_combobox.addItem(
            "CIS",
            "CIS"
        )

        self.pv_technology_combobox.addItem(
            "CdTe",
            "CdTe"
        )

    def configure_latitude(self):

        self.latitude_spinbox.setRange(-90.0, 90.0)
        self.latitude_spinbox.setDecimals(6)
        self.latitude_spinbox.setSingleStep(0.000001)

    def configure_longitude(self):

        self.longitude_spinbox.setRange(-180.0, 180.0)
        self.longitude_spinbox.setDecimals(6)
        self.longitude_spinbox.setSingleStep(0.000001)

    def configure_tilt(self):

        self.tilt_spinbox.setRange(0, 90)
        self.tilt_spinbox.setSuffix(" °")

    def configure_azimuth(self):

        self.azimuth_spinbox.setRange(-180, 180)
        self.azimuth_spinbox.setSuffix(" °")

    def configure_mounting_place(self):

        self.mounting_place_combobox.addItem(
            "Estructura sobre el suelo",
            "free"
        )

        self.mounting_place_combobox.addItem(
            "Integrado en edificio",
            "building"
        )

    def create_production_status_group(self):

        group = QGroupBox("Estado de la producción")

        layout = QFormLayout(group)

        self.source_label = QLabel("-")
        self.database_label = QLabel("-")
        self.reference_year_label = QLabel("-")
        self.last_update_label = QLabel("-")
        self.production_status_label = QLabel("-")

        layout.addRow("Fuente", self.source_label)
        layout.addRow("Base de datos", self.database_label)
        layout.addRow("Año de referencia", self.reference_year_label)
        layout.addRow("Última actualización", self.last_update_label)
        layout.addRow("Estado", self.production_status_label)

        self.calculate_production_button = QPushButton(
            "Calcular producción"
        )

        layout.addRow("", self.calculate_production_button)

        return group

    def create_production_summary_group(self):

        group = QGroupBox("Resumen")

        layout = QFormLayout(group)

        self.production_annual_label = QLabel("-")
        self.production_specific_label = QLabel("-")
        self.production_coverage_label = QLabel("-")

        layout.addRow(
            "Producción anual",
            self.production_annual_label
        )

        layout.addRow(
            "Producción específica",
            self.production_specific_label
        )

        layout.addRow(
            "Cobertura",
            self.production_coverage_label
        )

        return group

    def configure_production_page(self):

        self.source_label.setText("PVGIS")

        self.database_label.setText("SARAH3")

        self.reference_year_label.setText("-")

        self.last_update_label.setText("Nunca")

        self.production_status_label.setText("No calculada")

        self.production_annual_label.setText("-")

        self.production_specific_label.setText("-")

        self.production_coverage_label.setText("-")

        self.calculate_production_button.setMinimumHeight(40)

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

        self.source_label.setText(source)

        self.database_label.setText(database)

        self.reference_year_label.setText(
            "-" if reference_year is None else str(reference_year)
        )

        self.last_update_label.setText(last_update)

        self.production_status_label.setText(status)

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

        configuration = self.project.solar_configuration

        if configuration is None:
            raise ValueError(
                "Solar configuration is required "
                "before calculating production."
            )

        self.update_production_status(
            source="PVGIS",
            database="SARAH3",
            reference_year=configuration.reference_year,
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

            self.set_results_available(True)

            if self.main_window is not None:
                self.main_window.set_solar_calculated(
                    True
                )

        except Exception as error:

            self.update_production_status(
                source="PVGIS",
                database="SARAH3",
                reference_year=configuration.reference_year,
                last_update="-",
                status=f"Error: {error}",
                annual_production=None,
                specific_production=None,
                coverage=None,
            )

    def get_configuration(self) -> SolarConfiguration:

        return SolarConfiguration(

            latitude=(
                self.latitude_spinbox.value()
            ),

            longitude=(
                self.longitude_spinbox.value()
            ),

            tilt=(
                self.tilt_spinbox.value()
            ),

            azimuth=(
                self.azimuth_spinbox.value()
            ),

            reference_year=2023,

            losses=(
                self.system_losses_spinbox.value()
            ),

            pv_technology=(
                self.pv_technology_combobox.currentData()
            ),

            mounting_place=(
                self.mounting_place_combobox.currentData()
            )
        )

    def refresh_production_results(self):

        solar = self.project.solar

        self.update_production_status(

            source="PVGIS",

            database="SARAH3",

            reference_year=(
                self.project.solar_configuration.reference_year
                if self.project.solar_configuration is not None
                else None
            ),

            last_update="Ahora",

            status="Disponible",

            annual_production=solar.annual_production,

            specific_production=solar.specific_production,

            coverage=solar.coverage,
        )

        self.update_monthly_production()
        self.update_balance()
        self.update_statistics()

    def create_monthly_production_group(self):

        group = QGroupBox("Producción mensual")

        layout = QVBoxLayout(group)

        self.monthly_production_table = QTableWidget()

        layout.addWidget(self.monthly_production_table)

        return group

    def configure_monthly_production_table(self):

        table = self.monthly_production_table

        table.setColumnCount(2)

        table.setHorizontalHeaderLabels(
            [
                "Mes",
                "Producción (kWh)"
            ]
        )

        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(24)

        table.setAlternatingRowColors(True)

        table.horizontalHeader().setStretchLastSection(True)

        table.horizontalHeader().setDefaultAlignment(
            Qt.AlignCenter
        )

        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.NoSelection)
        table.setFocusPolicy(Qt.NoFocus)

    def populate_monthly_table(
        self,
        table: QTableWidget,
        series: pd.Series
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

        table.setRowCount(len(series) + 1)

        total = 0.0

        for row, (date, value) in enumerate(series.items()):

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
                Qt.AlignRight | Qt.AlignVCenter
            )

            table.setItem(row, 0, month_item)
            table.setItem(row, 1, value_item)

        table.resizeColumnsToContents()

        total_row = len(series)

        total_label = QTableWidgetItem("TOTAL")
        total_value = QTableWidgetItem(f"{total:.2f}")

        font = QFont()
        font.setBold(True)

        total_label.setFont(font)
        total_value.setFont(font)

        total_value.setTextAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )

        table.setItem(total_row, 0, total_label)
        table.setItem(total_row, 1, total_value)
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        
    def update_monthly_production(self):

        solar = self.project.solar

        self.populate_monthly_table(
            self.monthly_production_table,
            solar.monthly_production
        )

    def update_balance(self):

        solar = self.project.solar

        self.update_balance_summary()

        self.populate_balance_table(
            self.balance_table,
            solar.monthly_energy_balance
        )

    def create_balance_table(self):

        self.balance_table = QTableWidget()

        self.balance_table.setColumnCount(4)

        self.balance_table.setHorizontalHeaderLabels(
            [
                "Mes",
                "Autoconsumo",
                "Importación",
                "Excedentes"
            ]
        )

        self.configure_balance_table()

        return self.balance_table

    def configure_balance_table(self):

        table = self.balance_table

        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)

        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.NoSelection)
        table.setFocusPolicy(Qt.NoFocus)
        table.setAlternatingRowColors(True)

        table.horizontalHeader().setDefaultAlignment(
            Qt.AlignCenter
        )

    def populate_balance_table(
        self,
        table: QTableWidget,
        balance: pd.DataFrame
    ):

        if balance is None or balance.empty:

            table.setRowCount(0)

            return

        months = [
            "Enero", "Febrero", "Marzo", "Abril",
            "Mayo", "Junio", "Julio", "Agosto",
            "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        table.setRowCount(len(balance) + 1)

        total_self = 0.0
        total_import = 0.0
        total_export = 0.0

        for row, (date, values) in enumerate(balance.iterrows()):

            self_consumption = values["self_consumption_kwh"]
            grid_import = values["grid_import_kwh"]
            grid_export = values["grid_export_kwh"]

            total_self += self_consumption
            total_import += grid_import
            total_export += grid_export

            month_item = QTableWidgetItem(
                months[date.month - 1]
            )

            month_item.setTextAlignment(
                Qt.AlignCenter
            )

            self_item = QTableWidgetItem(
                f"{self_consumption:.2f}"
            )

            import_item = QTableWidgetItem(
                f"{grid_import:.2f}"
            )

            export_item = QTableWidgetItem(
                f"{grid_export:.2f}"
            )

            for item in (
                self_item,
                import_item,
                export_item
            ):
                item.setTextAlignment(
                    Qt.AlignRight | Qt.AlignVCenter
                )

            table.setItem(row, 0, month_item)
            table.setItem(row, 1, self_item)
            table.setItem(row, 2, import_item)
            table.setItem(row, 3, export_item)

        total_row = len(balance)

        font = QFont()
        font.setBold(True)

        total_label = QTableWidgetItem("TOTAL")
        total_label.setFont(font)

        table.setItem(total_row, 0, total_label)

        totals = [
            total_self,
            total_import,
            total_export
        ]

        for column, value in enumerate(totals, start=1):

            item = QTableWidgetItem(f"{value:.2f}")

            item.setFont(font)

            item.setTextAlignment(
                Qt.AlignRight | Qt.AlignVCenter
            )

            table.setItem(total_row, column, item)

        table.resizeColumnsToContents()
        table.resizeRowsToContents()

    def create_balance_summary_group(self):

        group = QGroupBox("Resumen energético")

        layout = QFormLayout(group)

        self.balance_total_consumption_label = QLabel("-")
        self.balance_total_production_label = QLabel("-")

        self.balance_self_consumption_label = QLabel("-")
        self.balance_grid_import_label = QLabel("-")
        self.balance_grid_export_label = QLabel("-")

        self.balance_coverage_label = QLabel("-")

        layout.addRow(
            "Consumo total",
            self.balance_total_consumption_label
        )

        layout.addRow(
            "Producción FV",
            self.balance_total_production_label
        )

        layout.addRow(
            "Autoconsumo directo",
            self.balance_self_consumption_label
        )

        layout.addRow(
            "Importación de red",
            self.balance_grid_import_label
        )

        layout.addRow(
            "Excedentes",
            self.balance_grid_export_label
        )

        layout.addRow(
            "Cobertura",
            self.balance_coverage_label
        )

        return group

    def update_balance_summary(self):

        solar = self.project.solar

        balance = solar.energy_balance

        if balance is None or balance.empty:

            self.balance_total_consumption_label.setText("-")
            self.balance_total_production_label.setText("-")

            self.balance_self_consumption_label.setText("-")
            self.balance_grid_import_label.setText("-")
            self.balance_grid_export_label.setText("-")

            self.balance_coverage_label.setText("-")

            return

        total_consumption = (
            balance["consumption_kwh"].sum()
        )

        total_production = (
            balance["production_kwh"].sum()
        )

        self_consumption = (
            balance["self_consumption_kwh"].sum()
        )

        grid_import = (
            balance["grid_import_kwh"].sum()
        )

        grid_export = (
            balance["grid_export_kwh"].sum()
        )

        self.balance_total_consumption_label.setText(
            f"{total_consumption:,.2f} kWh"
        )

        self.balance_total_production_label.setText(
            f"{total_production:,.2f} kWh"
        )

        self.balance_self_consumption_label.setText(
            f"{self_consumption:,.2f} kWh"
        )

        self.balance_grid_import_label.setText(
            f"{grid_import:,.2f} kWh"
        )

        self.balance_grid_export_label.setText(
            f"{grid_export:,.2f} kWh"
        )

        if solar.coverage is not None:

            self.balance_coverage_label.setText(
                f"{solar.coverage:.1f} %"
            )

        else:

            self.balance_coverage_label.setText("-")

    def set_results_available(self, available: bool):

        self.tabs.setTabEnabled(
            self.tabs.indexOf(self.balance_tab),
            available
        )

        self.tabs.setTabEnabled(
            self.tabs.indexOf(self.statistics_tab),
            available
        )

    def update_statistics(self):

        solar = self.project.solar

        statistics = solar.statistics

        if statistics is None:

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

            for label in labels:
                label.setText("-")

            return

        # ==========================================
        # Producción
        # ==========================================

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

        # ==========================================
        # Balance energético
        # ==========================================

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

    def reset_results(self):

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

        self.balance_total_consumption_label.setText("-")
        self.balance_total_production_label.setText("-")
        self.balance_self_consumption_label.setText("-")
        self.balance_grid_import_label.setText("-")
        self.balance_grid_export_label.setText("-")
        self.balance_coverage_label.setText("-")

        self.stats_annual_production_label.setText("-")
        self.stats_specific_production_label.setText("-")
        self.stats_equivalent_hours_label.setText("-")
        self.stats_capacity_factor_label.setText("-")

        self.stats_coverage_label.setText("-")
        self.stats_self_consumption_ratio_label.setText("-")
        self.stats_self_sufficiency_ratio_label.setText("-")

        self.stats_import_label.setText("-")
        self.stats_export_label.setText("-")
        self.stats_self_consumption_label.setText("-")
        self.stats_total_consumption_label.setText("-")

        self.balance_table.setRowCount(0)

        self.set_results_available(False)