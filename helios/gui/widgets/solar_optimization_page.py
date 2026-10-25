from dataclasses import replace

from PySide6.QtCore import Qt, QRectF
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QDoubleSpinBox,
    QSpinBox,
    QComboBox,
    QCheckBox,
    QPushButton,
    QLabel,
    QFrame,
    QScrollArea,
    QGroupBox,
    QSizePolicy,
    QSlider,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QGridLayout,
)

from PySide6.QtGui import (
    QPainter,
    QPen,
    QBrush,
    QColor,
    QFont,
)

from helios.solar.installation_configuration import (
    InstallationConfiguration,
)

from helios.gui.widgets.localized_double_spinbox import (
    LocalizedDoubleSpinBox,
)

from helios.solar.battery_configuration import BatteryConfiguration
from helios.solar.installation_costs import InstallationCostConfiguration

from helios.solar.battery_economic_configuration import (
    BatteryEconomicParameters,
)

from helios.solar.installation_component_selection import (
    InstallationComponentSelection,
)

from helios.solar.default_component_catalog import (
    build_default_component_catalog,
)

# Presupuesto de referencia HELIOS.
# Los importes originales de los componentes y de la mano de obra
# están expresados sin IVA.
INSTALLATION_VAT_RATE = 0.21

PANEL_COST_GROSS_EUR = 92.196 * (1 + INSTALLATION_VAT_RATE)

# Estructuras: 291,00 € + 101,27 € para los 15 paneles.
# Aproximación lineal para poder evaluar otros tamaños.
STRUCTURE_COST_GROSS_PER_PANEL_EUR = (
    (291.00 + 101.27) / 15
) * (1 + INSTALLATION_VAT_RATE)

INVERTER_COST_GROSS_EUR = 960.38 * (1 + INSTALLATION_VAT_RATE)

INSTALLATION_LABOUR_GROSS_EUR = 2950.00 * (
    1 + INSTALLATION_VAT_RATE
)

ELECTRICAL_PROTECTION_GROSS_EUR = 343.96 * (
    1 + INSTALLATION_VAT_RATE
)

# Cable solar, conectores MC4 y perfil de unión.
CABLING_AND_ACCESSORIES_GROSS_EUR = (
    110.58 + 14.78 + 14.18 + 8.27
) * (1 + INSTALLATION_VAT_RATE)

# Estimación de legalización expresada sin IVA.
LEGALIZATION_ESTIMATE_NET_EUR = 650.00

# Importe con IVA para utilizar en la configuración económica.
LEGALIZATION_ESTIMATE_EUR = (
    LEGALIZATION_ESTIMATE_NET_EUR
    * (1.0 + INSTALLATION_VAT_RATE)
)

# 4.145,27 € sin IVA por 16,6 kWh.
# Convertimos a precio unitario con IVA para el análisis económico.
BATTERY_COST_GROSS_PER_KWH_EUR = (
    4145.27 / 16.6
) * (1 + INSTALLATION_VAT_RATE)

class RoofLayoutWidget(QWidget):
    """
    Representación gráfica a escala de una instalación FV.

    Muestra:

        - superficie completa del tejado;
        - paneles a escala;
        - paso de mantenimiento;
        - márgenes exteriores;
        - dimensiones físicas.
    """

    def __init__(self, parent=None):

        super().__init__(parent)

        self.roof_width = 0.0
        self.roof_height = 0.0

        self.panel_width = 0.0
        self.panel_height = 0.0

        self.rows = 0
        self.columns = 0

        self.panel_orientation = "vertical"

        self.walkway_width = 0.0
        self.walkway_position = None

        self.installation_width = 0.0
        self.installation_height = 0.0

        self.walkway_offset_percent = 50

        self.setMinimumHeight(360)
        self.setMinimumWidth(500)

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

    def _calculate_layout_rectangles(
        self,
        roof_x: float,
        roof_y: float,
        scale: float,
    ):
        """Calcula los rectángulos de paneles y pasillo en píxeles."""
        panel_width, panel_height = self._panel_dimensions()

        panel_width_px = panel_width * scale
        panel_height_px = panel_height * scale

        walkway_width_px = self.walkway_width * scale

        walkway_vertical = (
            self.walkway_width > 0
            and self.walkway_position == "vertical"
        )
        walkway_horizontal = (
            self.walkway_width > 0
            and self.walkway_position == "horizontal"
        )

        installation_width = (
            self.columns * panel_width
            + (
                self.walkway_width
                if walkway_vertical
                else 0.0
            )
        )
        installation_height = (
            self.rows * panel_height
            + (
                self.walkway_width
                if walkway_horizontal
                else 0.0
            )
        )

        # Centra el conjunto completo, incluido el pasillo.
        installation_x = (
            roof_x
            + (self.roof_width - installation_width)
            * scale
            / 2
        )
        installation_y = (
            roof_y
            + (self.roof_height - installation_height)
            * scale
            / 2
        )

        panel_rectangles = []
        walkway_rectangle = None

        if walkway_vertical:
            if self.columns > 1:
                split_index = round(
                    self.walkway_offset_percent
                    * self.columns
                    / 100
                )
                split_index = max(
                    1,
                    min(self.columns - 1, split_index),
                )
            else:
                # Con una sola columna, el pasillo solo puede
                # quedar a uno de sus lados.
                split_index = (
                    0
                    if self.walkway_offset_percent < 50
                    else 1
                )

            walkway_x = (
                installation_x
                + split_index * panel_width_px
            )

            walkway_rectangle = QRectF(
                walkway_x,
                installation_y,
                walkway_width_px,
                installation_height * scale,
            )

            for row in range(self.rows):
                for column in range(self.columns):
                    x = (
                        installation_x
                        + column * panel_width_px
                    )

                    if column >= split_index:
                        x += walkway_width_px

                    y = (
                        installation_y
                        + row * panel_height_px
                    )

                    panel_rectangles.append(
                        QRectF(
                            x,
                            y,
                            panel_width_px,
                            panel_height_px,
                        )
                    )

        elif walkway_horizontal:
            if self.rows > 1:
                split_index = round(
                    self.walkway_offset_percent
                    * self.rows
                    / 100
                )
                split_index = max(
                    1,
                    min(self.rows - 1, split_index),
                )
            else:
                split_index = (
                    0
                    if self.walkway_offset_percent < 50
                    else 1
                )

            walkway_y = (
                installation_y
                + split_index * panel_height_px
            )

            walkway_rectangle = QRectF(
                installation_x,
                walkway_y,
                installation_width * scale,
                walkway_width_px,
            )

            for row in range(self.rows):
                for column in range(self.columns):
                    x = (
                        installation_x
                        + column * panel_width_px
                    )
                    y = (
                        installation_y
                        + row * panel_height_px
                    )

                    if row >= split_index:
                        y += walkway_width_px

                    panel_rectangles.append(
                        QRectF(
                            x,
                            y,
                            panel_width_px,
                            panel_height_px,
                        )
                    )

        else:
            for row in range(self.rows):
                for column in range(self.columns):
                    panel_rectangles.append(
                        QRectF(
                            installation_x
                            + column * panel_width_px,
                            installation_y
                            + row * panel_height_px,
                            panel_width_px,
                            panel_height_px,
                        )
                    )

        return panel_rectangles, walkway_rectangle

    def set_layout_data(
        self,
        roof_width,
        roof_height,
        panel_width,
        panel_height,
        rows,
        columns,
        orientation,
        walkway_width=0.0,
        walkway_position=None,
        installation_width=0.0,
        installation_height=0.0,
    ):

        self.roof_width = float(roof_width)
        self.roof_height = float(roof_height)

        self.panel_width = float(panel_width)
        self.panel_height = float(panel_height)

        self.rows = int(rows)
        self.columns = int(columns)

        self.panel_orientation = orientation

        self.walkway_width = float(
            walkway_width or 0.0
        )

        self.walkway_position = walkway_position

        self.installation_width = float(
            installation_width or 0.0
        )

        self.installation_height = float(
            installation_height or 0.0
        )

        self.update()

    def set_walkway_offset(self, value: int):
        self.walkway_offset_percent = max(
            0,
            min(100, int(value)),
        )
        self.update()

    def clear(self):

        self.roof_width = 0.0
        self.roof_height = 0.0

        self.panel_width = 0.0
        self.panel_height = 0.0

        self.rows = 0
        self.columns = 0

        self.panel_orientation = "vertical"

        self.walkway_width = 0.0
        self.walkway_position = None

        self.installation_width = 0.0
        self.installation_height = 0.0

        self.walkway_offset_percent = 50

        self.update()

    def _panel_dimensions(self):

        if self.panel_orientation == "vertical":

            return (
                self.panel_width,
                self.panel_height,
            )

        return (
            self.panel_height,
            self.panel_width,
        )

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        painter.fillRect(
            self.rect(),
            QColor("#f5f7fa"),
        )

        if (
            self.roof_width <= 0
            or self.roof_height <= 0
            or self.rows <= 0
            or self.columns <= 0
        ):
            painter.setPen(QColor("#777777"))
            painter.drawText(
                self.rect(),
                Qt.AlignCenter,
                "No hay una distribución física disponible.",
            )
            return

        left_margin = 70
        right_margin = 35
        top_margin = 35
        bottom_margin = 60

        available_width = (
            self.width() - left_margin - right_margin
        )
        available_height = (
            self.height() - top_margin - bottom_margin
        )

        if available_width <= 0 or available_height <= 0:
            return

        scale = min(
            available_width / self.roof_width,
            available_height / self.roof_height,
        )

        roof_px_width = self.roof_width * scale
        roof_px_height = self.roof_height * scale

        roof_x = (
            left_margin
            + (available_width - roof_px_width) / 2
        )
        roof_y = (
            top_margin
            + (available_height - roof_px_height) / 2
        )

        roof_rect = QRectF(
            roof_x,
            roof_y,
            roof_px_width,
            roof_px_height,
        )

        painter.setPen(QPen(QColor("#404040"), 2))
        painter.setBrush(QBrush(QColor("#e5e7eb")))
        painter.drawRect(roof_rect)

        panel_rectangles, walkway_rectangle = (
            self._calculate_layout_rectangles(
                roof_x,
                roof_y,
                scale,
            )
        )

        painter.setPen(QPen(QColor("#164e8a"), 1))
        painter.setBrush(QBrush(QColor("#1976d2")))

        for panel_rect in panel_rectangles:
            painter.drawRoundedRect(
                panel_rect,
                2,
                2,
            )

        if walkway_rectangle is not None:
            painter.setPen(QPen(QColor("#c27c00"), 1))
            painter.setBrush(QBrush(QColor("#f6c453")))
            painter.drawRect(walkway_rectangle)

        painter.setPen(QColor("#444444"))

        font = QFont()
        font.setPointSize(9)
        painter.setFont(font)

        painter.drawText(
            QRectF(
                roof_x,
                roof_y + roof_px_height + 8,
                roof_px_width,
                25,
            ),
            Qt.AlignCenter,
            f"{self.roof_width:.2f} m",
        )

        painter.save()
        painter.translate(
            roof_x - 10,
            roof_y + roof_px_height / 2,
        )
        painter.rotate(-90)
        painter.drawText(
            QRectF(
                -roof_px_height / 2,
                -20,
                roof_px_height,
                20,
            ),
            Qt.AlignCenter,
            f"{self.roof_height:.2f} m",
        )
        painter.restore()

        legend_y = roof_y + roof_px_height + 35

        painter.setBrush(QColor("#1976d2"))
        painter.setPen(Qt.NoPen)
        painter.drawRect(
            QRectF(roof_x, legend_y, 14, 14)
        )

        painter.setPen(QColor("#444444"))
        painter.drawText(
            QRectF(
                roof_x + 20,
                legend_y - 2,
                100,
                20,
            ),
            Qt.AlignLeft,
            "Panel FV",
        )

        if self.walkway_width > 0:
            painter.setBrush(QColor("#f6c453"))
            painter.setPen(Qt.NoPen)
            painter.drawRect(
                QRectF(
                    roof_x + 110,
                    legend_y,
                    14,
                    14,
                )
            )

            painter.setPen(QColor("#444444"))
            painter.drawText(
                QRectF(
                    roof_x + 130,
                    legend_y - 2,
                    160,
                    20,
                ),
                Qt.AlignLeft,
                "Paso mantenimiento",
            )

class SolarOptimizationPage(QWidget):
    """
    Página de dimensionamiento y optimización de la instalación FV.

    Requiere que la configuración solar haya sido guardada y que
    exista un dataset cargado y analizado.
    """

    def __init__(
        self,
        project,
        main_window=None,
    ):

        super().__init__()

        self.project = project
        self.main_window = main_window

        self.setup_ui()
        self.configure_widgets()
        self._initialize_default_component_selection()
        self.connect_signals()

    # ==================================================
    # INTERFAZ
    # ==================================================

    def setup_ui(self):

        outer_layout = QVBoxLayout(self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        content = QWidget()

        layout = QVBoxLayout(content)
        layout.setSpacing(10)

        layout.addWidget(
            self.create_title()
        )

        # Distribución de los bloques de configuración.
        configuration_widget = QWidget()
        configuration_layout = QGridLayout(
            configuration_widget
        )
        configuration_layout.setContentsMargins(0, 0, 0, 0)
        configuration_layout.setHorizontalSpacing(10)
        configuration_layout.setVerticalSpacing(10)

        configuration_layout.addWidget(
            self.create_installation_group(),
            0,
            0,
        )

        configuration_layout.addWidget(
            self.create_panel_group(),
            0,
            1,
        )

        configuration_layout.addWidget(
            self.create_maintenance_group(),
            1,
            0,
            1,
            2,
        )

        configuration_layout.addWidget(
            self.create_action_group(),
            2,
            0,
            1,
            2,
        )

        configuration_layout.setColumnStretch(0, 1)
        configuration_layout.setColumnStretch(1, 1)

        layout.addWidget(configuration_widget)

        # Resultados de la optimización.
        layout.addWidget(
            self.create_result_group()
        )

        layout.addWidget(
            self.create_battery_economic_group()
        )

        layout.addStretch()

        self.scroll_area.setWidget(content)

        outer_layout.addWidget(
            self.scroll_area
        )

    def create_title(self):

        frame = QFrame()

        layout = QVBoxLayout(frame)

        title = QLabel(
            "<h2>Optimización solar</h2>"
        )

        description = QLabel(
            "Define las características físicas de la instalación "
            "para buscar la mejor configuración fotovoltaica "
            "compatible con el tejado y el consumo."
        )

        description.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(description)

        return frame

    # ==================================================
    # INSTALACIÓN
    # ==================================================

    def create_installation_group(self):

        group = QGroupBox(
            "Superficie disponible"
        )

        layout = QFormLayout(group)

        self.available_area_spinbox = LocalizedDoubleSpinBox()
        self.roof_width_spinbox = LocalizedDoubleSpinBox()
        self.roof_height_spinbox = LocalizedDoubleSpinBox()

        layout.addRow(
            "Superficie disponible",
            self.available_area_spinbox,
        )

        layout.addRow(
            "Anchura del tejado",
            self.roof_width_spinbox,
        )

        layout.addRow(
            "Altura del tejado",
            self.roof_height_spinbox,
        )

        return group

    # ==================================================
    # PANELES
    # ==================================================

    def create_panel_group(self):

        group = QGroupBox(
            "Características del panel"
        )

        layout = QFormLayout(group)

        self.panel_width_spinbox = LocalizedDoubleSpinBox()
        self.panel_height_spinbox = LocalizedDoubleSpinBox()
        self.panel_power_spinbox = QDoubleSpinBox()

        self.panel_orientation_combobox = QComboBox()

        self.panel_orientation_combobox.addItem(
            "Automática",
            "auto",
        )

        self.panel_orientation_combobox.addItem(
            "Vertical",
            "vertical",
        )

        self.panel_orientation_combobox.addItem(
            "Horizontal",
            "horizontal",
        )

        self.min_panels_spinbox = QSpinBox()
        self.max_panels_spinbox = QSpinBox()

        self.max_panels_checkbox = QCheckBox(
            "Establecer máximo de paneles"
        )

        layout.addRow(
            "Anchura del panel",
            self.panel_width_spinbox,
        )

        layout.addRow(
            "Altura del panel",
            self.panel_height_spinbox,
        )

        layout.addRow(
            "Potencia del panel",
            self.panel_power_spinbox,
        )

        layout.addRow(
            "Orientación física",
            self.panel_orientation_combobox,
        )

        layout.addRow(
            "Mínimo de paneles",
            self.min_panels_spinbox,
        )

        layout.addRow(
            self.max_panels_checkbox,
        )

        layout.addRow(
            "Máximo de paneles",
            self.max_panels_spinbox,
        )

        return group

    # ==================================================
    # MANTENIMIENTO
    # ==================================================

    def create_maintenance_group(self):

        group = QGroupBox(
            "Paso de mantenimiento"
        )

        layout = QFormLayout(group)

        self.maintenance_required_checkbox = QCheckBox(
            "Requiere paso de mantenimiento"
        )

        self.maintenance_width_spinbox = LocalizedDoubleSpinBox()

        self.maintenance_orientation_combobox = QComboBox()

        self.maintenance_orientation_combobox.addItem(
            "Automática",
            "auto",
        )

        self.maintenance_orientation_combobox.addItem(
            "Vertical",
            "vertical",
        )

        self.maintenance_orientation_combobox.addItem(
            "Horizontal",
            "horizontal",
        )

        layout.addRow(
            self.maintenance_required_checkbox,
        )

        layout.addRow(
            "Anchura del paso",
            self.maintenance_width_spinbox,
        )

        layout.addRow(
            "Orientación",
            self.maintenance_orientation_combobox,
        )

        return group

    # ==================================================
    # ACCIÓN
    # ==================================================

    def create_action_group(self):

        group = QGroupBox(
            "Optimización"
        )

        layout = QFormLayout(group)

        self.status_label = QLabel(
            "Pendiente de datos"
        )

        self.optimize_button = QPushButton(
            "Buscar mejor instalación"
        )

        layout.addRow(
            "Estado",
            self.status_label,
        )

        layout.addRow(
            "",
            self.optimize_button,
        )

        return group

    # ==================================================
    # RESULTADO
    # ==================================================

    def create_result_group(self):

        group = QGroupBox(
            "Resultado de la instalación recomendada"
        )

        main_layout = QHBoxLayout(group)

        data_widget = QWidget()

        data_layout = QFormLayout(data_widget)

        self.result_panel_count_label = QLabel("-")
        self.result_power_label = QLabel("-")
        self.result_production_label = QLabel("-")
        self.result_consumption_label = QLabel("-")
        self.result_occupied_area_label = QLabel("-")
        self.result_remaining_area_label = QLabel("-")
        self.result_utilization_label = QLabel("-")
        self.result_self_sufficiency_label = QLabel("-")
        self.result_coverage_label = QLabel("-")
        self.result_surplus_label = QLabel("-")
        self.result_deficit_label = QLabel("-")
        self.result_orientation_label = QLabel("-")
        self.result_rows_label = QLabel("-")
        self.result_columns_label = QLabel("-")
        self.result_dimensions_label = QLabel("-")
        self.result_walkway_label = QLabel("-")

        data_layout.addRow(
            "Paneles",
            self.result_panel_count_label,
        )

        data_layout.addRow(
            "Potencia instalada",
            self.result_power_label,
        )

        data_layout.addRow(
            "Orientación física",
            self.result_orientation_label,
        )

        data_layout.addRow(
            "Producción anual estimada",
            self.result_production_label,
        )

        data_layout.addRow(
            "Consumo anual",
            self.result_consumption_label,
        )

        data_layout.addRow(
            "Superficie ocupada",
            self.result_occupied_area_label,
        )

        data_layout.addRow(
            "Superficie restante",
            self.result_remaining_area_label,
        )

        data_layout.addRow(
            "Utilización de superficie",
            self.result_utilization_label,
        )

        data_layout.addRow(
            "Suficiencia energética",
            self.result_self_sufficiency_label,
        )

        data_layout.addRow(
            "Cobertura de producción",
            self.result_coverage_label,
        )

        data_layout.addRow(
            "Excedente anual",
            self.result_surplus_label,
        )

        data_layout.addRow(
            "Déficit anual",
            self.result_deficit_label,
        )

        data_layout.addRow(
            "Filas",
            self.result_rows_label,
        )

        data_layout.addRow(
            "Columnas",
            self.result_columns_label,
        )

        data_layout.addRow(
            "Dimensiones ocupadas",
            self.result_dimensions_label,
        )

        data_layout.addRow(
            "Paso de mantenimiento",
            self.result_walkway_label,
        )

        layout_widget = QWidget()

        layout_widget.setMinimumWidth(350)

        layout_widget_layout = QVBoxLayout(
            layout_widget
        )

        layout_title = QLabel(
            "<b>Distribución física de los paneles</b>"
        )

        layout_title.setAlignment(
            Qt.AlignCenter
        )

        self.layout_grid_container = QFrame()

        self.layout_grid_container.setFrameShape(
            QFrame.StyledPanel
        )

        self.layout_grid_container.setMinimumHeight(
            380
        )

        layout_container_layout = QVBoxLayout(
            self.layout_grid_container
        )

        self.walkway_slider_label = QLabel(
            "Posición del pasillo de mantenimiento"
        )

        self.walkway_slider_label.setAlignment(
            Qt.AlignCenter
        )

        self.walkway_slider = QSlider(
            Qt.Horizontal
        )

        self.walkway_slider.setRange(0, 100)
        self.walkway_slider.setValue(50)
        self.walkway_slider.setEnabled(False)

        self.walkway_position_label = QLabel(
            "50 %"
        )

        self.walkway_position_label.setAlignment(
            Qt.AlignCenter
        )

        layout_container_layout.addWidget(
            self.walkway_slider_label
        )

        layout_container_layout.addWidget(
            self.walkway_slider
        )

        layout_container_layout.addWidget(
            self.walkway_position_label
        )

        self.roof_layout_widget = RoofLayoutWidget()

        layout_container_layout.addWidget(
            self.roof_layout_widget,
            1,
        )

        self.layout_info_label = QLabel(
            "No hay una instalación calculada."
        )

        self.layout_info_label.setAlignment(
            Qt.AlignCenter
        )

        self.layout_info_label.setWordWrap(True)

        layout_widget_layout.addWidget(
            layout_title
        )

        layout_widget_layout.addWidget(
            self.layout_info_label
        )

        layout_widget_layout.addWidget(
            self.layout_grid_container,
            1,
        )

        main_layout.addWidget(
            data_widget,
            1,
        )

        main_layout.addWidget(
            layout_widget,
            1,
        )

        return group

    def create_battery_economic_group(self):

        group = QGroupBox(
            "Evaluación económica de baterías"
        )

        layout = QVBoxLayout(group)

        description = QLabel(
            "Comparación de distintas capacidades de batería "
            "sobre la instalación fotovoltaica calculada. "
            "Los resultados económicos incluyen ahorro anual, "
            "coste incremental, recuperación marginal, VAN y TIR."
        )

        description.setWordWrap(True)

        layout.addWidget(description)

        self.battery_status_label = QLabel(
            "No hay una evaluación de baterías disponible."
        )

        layout.addWidget(
            self.battery_status_label
        )

        self.combined_economic_label = QLabel(
            "Evaluación combinada FV + batería pendiente."
        )
        self.combined_economic_label.setWordWrap(True)

        layout.addWidget(self.combined_economic_label)

        self.battery_table = QTableWidget()

        self.battery_table.setColumnCount(8)

        self.battery_table.setHorizontalHeaderLabels(
            [
                "Capacidad",
                "Ahorro adicional",
                "Coste incremental",
                "Ahorro incremental",
                "Recuperación marginal",
                "VAN",
                "TIR",
                "Recuperación económica",
            ]
        )

        self.battery_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.battery_table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.battery_table.setSelectionMode(
            QTableWidget.SingleSelection
        )

        self.battery_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.battery_table.verticalHeader().setVisible(
            False
        )

        self.battery_table.setMinimumHeight(220)

        layout.addWidget(
            self.battery_table
        )

        return group

    # ==================================================
    # CONFIGURACIÓN
    # ==================================================

    def configure_widgets(self):

        self.available_area_spinbox.setRange(
            0.01,
            10000.0,
        )

        self.available_area_spinbox.setDecimals(2)
        self.available_area_spinbox.setSuffix(" m²")

        self.roof_width_spinbox.setRange(
            0.0,
            500.0,
        )

        self.roof_width_spinbox.setDecimals(3)
        self.roof_width_spinbox.setSuffix(" m")

        self.roof_height_spinbox.setRange(
            0.0,
            500.0,
        )

        self.roof_height_spinbox.setDecimals(3)
        self.roof_height_spinbox.setSuffix(" m")

        self.panel_width_spinbox.setRange(
            0.01,
            10.0,
        )

        self.panel_width_spinbox.setDecimals(3)
        self.panel_width_spinbox.setSuffix(" m")

        self.panel_height_spinbox.setRange(
            0.01,
            10.0,
        )

        self.panel_height_spinbox.setDecimals(3)
        self.panel_height_spinbox.setSuffix(" m")

        self.panel_power_spinbox.setRange(
            1.0,
            2000.0,
        )

        self.panel_power_spinbox.setDecimals(0)
        self.panel_power_spinbox.setSuffix(" Wp")

        self.min_panels_spinbox.setRange(1, 1000)

        self.max_panels_spinbox.setRange(1, 1000)
        self.max_panels_spinbox.setEnabled(False)

        self.maintenance_width_spinbox.setRange(
            0.01,
            5.0,
        )

        self.maintenance_width_spinbox.setDecimals(2)
        self.maintenance_width_spinbox.setSuffix(" m")
        self.maintenance_width_spinbox.setValue(0.45)
        self.maintenance_width_spinbox.setEnabled(False)

        self.maintenance_orientation_combobox.setEnabled(
            False
        )

        self.optimize_button.setMinimumHeight(40)

    # ==================================================
    # SEÑALES
    # ==================================================

    def connect_signals(self):

        self.max_panels_checkbox.toggled.connect(
            self.max_panels_spinbox.setEnabled
        )

        self.maintenance_required_checkbox.toggled.connect(
            self.maintenance_width_spinbox.setEnabled
        )

        self.maintenance_required_checkbox.toggled.connect(
            self.maintenance_orientation_combobox.setEnabled
        )

        self.optimize_button.clicked.connect(
            self.start_optimization
        )

        self.walkway_slider.valueChanged.connect(
            self.on_walkway_position_changed
        )

    # ==================================================
    # CONFIGURACIÓN DE INSTALACIÓN
    # ==================================================

    def get_installation_configuration(
        self,
    ) -> InstallationConfiguration:

        max_panels = None

        if self.max_panels_checkbox.isChecked():

            max_panels = (
                self.max_panels_spinbox.value()
            )

        return InstallationConfiguration(
            available_area_m2=(
                self.available_area_spinbox.value()
            ),
            panel_width_m=(
                self.panel_width_spinbox.value()
            ),
            panel_height_m=(
                self.panel_height_spinbox.value()
            ),
            panel_power_wp=(
                self.panel_power_spinbox.value()
            ),
            panel_orientation=(
                self.panel_orientation_combobox.currentData()
            ),
            min_panels=(
                self.min_panels_spinbox.value()
            ),
            max_panels=max_panels,
            maintenance_passage_required=(
                self.maintenance_required_checkbox.isChecked()
            ),
            maintenance_passage_width_m=(
                self.maintenance_width_spinbox.value()
            ),
            maintenance_passage_orientation=(
                self.maintenance_orientation_combobox.currentData()
            ),
            roof_width_m=(
                self.roof_width_spinbox.value()
                if self.roof_width_spinbox.value() > 0
                else None
            ),
            roof_height_m=(
                self.roof_height_spinbox.value()
                if self.roof_height_spinbox.value() > 0
                else None
            ),
        )

    # ==================================================
    # RESULTADO
    # ==================================================

    def show_optimization_result(self, result):

        configuration = self.project.solar_configuration

        self.result_panel_count_label.setText(
            f"{result.panel_count}"
        )

        self.result_power_label.setText(
            f"{result.installed_power_kwp:.2f} kWp"
        )

        if configuration is not None:

            azimuth = configuration.azimuth

            if azimuth == 0:
                orientation = "Sur"
            else:
                orientation = (
                    f"{azimuth}° respecto al Sur"
                )

            self.result_orientation_label.setText(
                f"{orientation} ({azimuth}°)"
            )

        else:

            self.result_orientation_label.setText("-")

        self.result_production_label.setText(
            f"{result.annual_production_kwh:,.0f} kWh/año"
        )

        self.result_consumption_label.setText(
            f"{result.annual_consumption_kwh:,.0f} kWh/año"
        )

        self.result_occupied_area_label.setText(
            f"{result.occupied_area_m2:.2f} m²"
        )

        self.result_remaining_area_label.setText(
            f"{result.remaining_area_m2:.2f} m²"
        )

        self.result_utilization_label.setText(
            f"{result.area_utilization_percent:.1f} %"
        )

        self.result_self_sufficiency_label.setText(
            f"{result.self_sufficiency_percent:.1f} %"
        )

        self.result_coverage_label.setText(
            f"{result.production_coverage_percent:.1f} %"
        )

        self.result_surplus_label.setText(
            f"{result.energy_surplus_kwh:,.0f} kWh/año"
        )

        self.result_deficit_label.setText(
            f"{result.energy_deficit_kwh:,.0f} kWh/año"
        )

        self.show_installation_layout(result)

    def evaluate_batteries(self):
        """Evalúa las capacidades de batería con el coste del presupuesto."""

        candidate_capacities_kwh = [
            5.0,
            8.3,
            16.6,
            24.9,
            30.0,
        ]

        recommendations = self.project.solar.evaluate_batteries(
            candidate_capacities_kwh,
            max_charge_power_kw=5.0,
            max_discharge_power_kw=5.0,
            battery_economic_parameters=BatteryEconomicParameters(
                cost_per_kwh_eur=self._battery_cost_per_kwh_eur(),
            )
        )

        self.show_battery_economic_results(recommendations)

        return recommendations

    def show_battery_economic_results(
        self,
        recommendations,
    ):

        self.battery_table.setRowCount(
            len(recommendations)
        )

        for row, recommendation in enumerate(
            recommendations
        ):

            values = [
                (
                    f"{recommendation.capacity_kwh:.1f} kWh"
                ),
                (
                    f"{recommendation.annual_additional_savings_eur:,.2f} €"
                ),
                (
                    f"{recommendation.incremental_battery_cost_eur:,.2f} €"
                ),
                (
                    f"{recommendation.incremental_savings_eur:,.2f} €"
                ),
                self._format_years(
                    recommendation.marginal_payback_years
                ),
                (
                    f"{recommendation.economic_npv_eur:,.2f} €"
                ),
                (
                    f"{recommendation.economic_irr_percent:.2f} %"
                ),
                self._format_years(
                    recommendation.economic_payback_years
                ),
            ]

            for column, value in enumerate(values):

                item = QTableWidgetItem(value)

                item.setTextAlignment(
                    Qt.AlignCenter
                )

                self.battery_table.setItem(
                    row,
                    column,
                    item,
                )

        if recommendations:

            self.battery_status_label.setText(
                "Evaluación económica completada. "
                f"{len(recommendations)} capacidades comparadas."
            )

        else:

            self.battery_status_label.setText(
                "No se han obtenido recomendaciones de batería."
            )


    @staticmethod
    def _format_years(value):

        if value == float("inf"):

            return "—"

        return f"{value:.2f} años"

    # ==================================================
    # LAYOUT FÍSICO
    # ==================================================

    def show_installation_layout(self, result):

        layout = result.layout

        if layout is None:

            self.result_rows_label.setText("-")
            self.result_columns_label.setText("-")
            self.result_dimensions_label.setText("-")
            self.result_walkway_label.setText("-")

            self.walkway_slider.setEnabled(False)

            self.layout_info_label.setText(
                "No hay una distribución física disponible."
            )

            return

        self.result_rows_label.setText(
            str(layout.rows)
        )

        self.result_columns_label.setText(
            str(layout.columns)
        )

        self.result_dimensions_label.setText(
            f"{layout.occupied_width_m:.2f} × "
            f"{layout.occupied_height_m:.2f} m"
        )

        if layout.walkway_width_m > 0:

            if layout.walkway_position == "vertical":

                walkway_text = (
                    f"{layout.walkway_width_m:.2f} m vertical"
                )

            elif layout.walkway_position == "horizontal":

                walkway_text = (
                    f"{layout.walkway_width_m:.2f} m horizontal"
                )

            else:

                walkway_text = (
                    f"{layout.walkway_width_m:.2f} m"
                )

            self.walkway_slider.setEnabled(True)

        else:

            walkway_text = "No requerido"

            self.walkway_slider.setEnabled(False)

        self.result_walkway_label.setText(
            walkway_text
        )

        roof_width = self.roof_width_spinbox.value()
        roof_height = self.roof_height_spinbox.value()

        self.roof_layout_widget.set_layout_data(
            roof_width=roof_width,
            roof_height=roof_height,
            panel_width=(
                self.panel_width_spinbox.value()
            ),
            panel_height=(
                self.panel_height_spinbox.value()
            ),
            rows=layout.rows,
            columns=layout.columns,
            orientation=layout.orientation,
            walkway_width=layout.walkway_width_m,
            walkway_position=layout.walkway_position,
            installation_width=layout.occupied_width_m,
            installation_height=layout.occupied_height_m,
        )

        orientation_name = (
            "Vertical"
            if layout.orientation == "vertical"
            else "Horizontal"
        )

        info_lines = [
            (
                f"{layout.rows} filas × "
                f"{layout.columns} columnas"
            ),
            (
                f"Orientación de los paneles: "
                f"{orientation_name}"
            ),
            (
                f"Superficie ocupada: "
                f"{layout.occupied_area_m2:.2f} m²"
            ),
            (
                f"Dimensiones ocupadas: "
                f"{layout.occupied_width_m:.2f} × "
                f"{layout.occupied_height_m:.2f} m"
            ),
            (
                f"Tejado: "
                f"{roof_width:.2f} × "
                f"{roof_height:.2f} m"
            ),
        ]

        if layout.walkway_width_m > 0:

            info_lines.append(
                (
                    f"Paso de mantenimiento: "
                    f"{layout.walkway_width_m:.2f} m"
                )
            )

        self.layout_info_label.setText(
            "\n".join(info_lines)
        )

    # ==================================================
    # OPTIMIZACIÓN
    # ==================================================

    def start_optimization(self):
        """Optimiza la instalación y separa el análisis energético del económico."""

        self.optimize_button.setEnabled(False)
        self.status_label.setText("Buscando la mejor instalación...")

        # Eliminar los resultados anteriores para evitar mostrar
        # recomendaciones económicas obsoletas.
        self.battery_table.setRowCount(0)
        self.battery_status_label.setText(
            "Evaluación económica de baterías pendiente."
        )

        try:
            configuration = self.get_installation_configuration()

            selection = getattr(
                self.project,
                "component_selection",
                None,
            )

            if isinstance(selection, InstallationComponentSelection):
                configuration = selection.apply_to(configuration)

            consumption_scenario = (
                self.project.analyzer.calculate_representative_consumption_scenario(
                    reference_year=2025
                )
            )

            if consumption_scenario is None:
                raise ValueError(
                    "A representative consumption scenario is required."
                )

            if consumption_scenario.annual_consumption <= 0:
                raise ValueError(
                    "Annual consumption must be greater than zero."
                )

            result = self.project.solar.recommend_installation(
                configuration=configuration,
                consumption_scenario=consumption_scenario,
            )

            self._configure_installation_costs(result)

            # La producción y el balance energético son independientes
            # de la disponibilidad de todos los costes de inversión.
            self.project.solar.calculate(
                self.project.solar_configuration,
                installed_power_kwp=result.installed_power_kwp,
            )

            self.show_optimization_result(result)

            economic_evaluation_available = (
                self._installation_economic_evaluation_available(
                    result
                )
            )

            # Evaluar las baterías incluso si falta el coste de
            # estructura. En ese caso no se podrá calcular el VAN
            # combinado, pero sí simular sus balances energéticos.
            battery_recommendations = self.evaluate_batteries()

            if not isinstance(
                battery_recommendations,
                (list, tuple),
            ):
                battery_recommendations = []

            if economic_evaluation_available:
                valid_combined_recommendations = [
                    recommendation
                    for recommendation in battery_recommendations
                    if recommendation.combined_economic_analysis_calculated
                ]

                battery_recommendation = (
                    max(
                        valid_combined_recommendations,
                        key=lambda recommendation: (
                            recommendation.combined_economic_npv_eur,
                            -recommendation.capacity_kwh,
                        ),
                    )
                    if valid_combined_recommendations
                    else None
                )

                if battery_recommendation is not None:
                    self.combined_economic_label.setText(
                        "Evaluación combinada FV + batería calculada. "
                        f"Capacidad seleccionada: "
                        f"{battery_recommendation.capacity_kwh:.1f} kWh. "
                        f"VAN combinado: "
                        f"{battery_recommendation.combined_economic_npv_eur:,.2f} €."
                    )
                else:
                    self.combined_economic_label.setText(
                        "No se dispone de un resultado válido de VAN "
                        "combinado para las baterías evaluadas."
                    )

                self._update_total_investment(
                    result,
                    battery_recommendation,
                )

            else:
                # No utilizar el presupuesto global como sustituto
                # ni mostrar un VAN combinado no calculado.
                battery_recommendation = None

                self.battery_status_label.setText(
                    "Simulación de baterías completada. "
                    "Evaluación económica combinada pendiente: "
                    "falta confirmar el coste de la estructura."
                )

                self.combined_economic_label.setText(
                    "Evaluación económica combinada FV + batería pendiente: "
                    "falta confirmar el coste de la estructura de montaje. "
                    "La tabla de baterías muestra los indicadores incrementales "
                    "que se hayan podido calcular."
                )

            if self.main_window is not None:
                self.main_window.set_solar_optimized(True)

            self.status_label.setText(
                "Optimización completada"
                if economic_evaluation_available
                else (
                    "Optimización energética completada; "
                    "evaluación económica combinada pendiente."
                )
            )

        except Exception as error:
            import traceback

            traceback.print_exc()
            self.status_label.setText(f"Error: {error}")

        finally:
            self.optimize_button.setEnabled(True)


    # ==================================================
    # RESET
    # ==================================================

    def clear_optimization_result(self):

        labels = [
            self.result_panel_count_label,
            self.result_power_label,
            self.result_production_label,
            self.result_consumption_label,
            self.result_occupied_area_label,
            self.result_remaining_area_label,
            self.result_utilization_label,
            self.result_self_sufficiency_label,
            self.result_coverage_label,
            self.result_surplus_label,
            self.result_deficit_label,
            self.result_orientation_label,
            self.result_rows_label,
            self.result_columns_label,
            self.result_dimensions_label,
            self.result_walkway_label,
        ]

        for label in labels:
            label.setText("-")

        self.battery_table.setRowCount(0)

        self.roof_layout_widget.clear()

        self.walkway_slider.setEnabled(False)

        self.walkway_position_label.setText("50 %")

        self.layout_info_label.setText(
            "No hay una instalación calculada."
        )
        self.battery_status_label.setText(
            "No hay una evaluación de baterías disponible."
        )

    def reset(self):

        self.clear_optimization_result()

        self.status_label.setText(
            "Pendiente de datos"
        )

        self.optimize_button.setEnabled(True)

    def update_data(self):

        if self.project.dataset is None:

            self.status_label.setText(
                "Pendiente de datos"
            )

            return

        self.status_label.setText(
            "Datos disponibles para optimización."
        )

    def on_walkway_position_changed(
        self,
        value: int,
    ):

        self.walkway_position_label.setText(
            f"{value} %"
        )

        if hasattr(
            self,
            "roof_layout_widget",
        ):

            self.roof_layout_widget.set_walkway_offset(
                value
            )

    def _configure_installation_costs(self, result) -> None:
        """Configura los costes a partir del catálogo o del presupuesto base.

        Los precios del catálogo se consideran netos y se convierten
        a importes con IVA una sola vez en esta capa.
        """

        selection = getattr(
            self.project,
            "component_selection",
            None,
        )

        if isinstance(selection, InstallationComponentSelection):
            category_by_id = {
                "installation": "installation",
                "electrical_protection_dc": "electrical_protection",
                "electrical_protection_ac": "electrical_protection",
                "solar_cabling_red": "cabling",
                "solar_cabling_black": "cabling",
                "connector_female": "cabling",
                "connector_male": "cabling",
                "joining_profiles": "cabling",
                "legalization_estimate": "legalization",
            }

            selected_auxiliary_ids = {
                item.id
                for item in selection.auxiliary_costs
            }

            auxiliary_cost_categories = {
                cost_id: category
                for cost_id, category in category_by_id.items()
                if cost_id in selected_auxiliary_ids
            }

            net_costs = InstallationCostConfiguration.from_selection(
                selection,
                auxiliary_cost_categories=auxiliary_cost_categories,
            )

            vat_multiplier = 1.0 + INSTALLATION_VAT_RATE

            cost_configuration = InstallationCostConfiguration(
                panel_unit_cost_eur=(
                    net_costs.panel_unit_cost_eur * vat_multiplier
                ),
                structure_unit_cost_eur=(
                    net_costs.structure_unit_cost_eur * vat_multiplier
                    if net_costs.structure_unit_cost_eur is not None
                    else None
                ),
                installation_cost_eur=(
                    net_costs.installation_cost_eur * vat_multiplier
                ),
                inverter_unit_cost_eur=(
                    net_costs.inverter_unit_cost_eur * vat_multiplier
                ),
                electrical_protection_cost_eur=(
                    net_costs.electrical_protection_cost_eur
                    * vat_multiplier
                ),
                cabling_cost_eur=(
                    net_costs.cabling_cost_eur * vat_multiplier
                ),
                legalization_cost_eur=(
                    net_costs.legalization_cost_eur * vat_multiplier
                ),
                auxiliary_panel_area_m2=(
                    net_costs.auxiliary_panel_area_m2
                ),
                auxiliary_cost_items=tuple(
                    replace(
                        item,
                        unit_price_eur=(
                            item.unit_price_eur * vat_multiplier
                        ),
                    )
                    for item in net_costs.auxiliary_cost_items
                ),
                auxiliary_cost_categories=(
                    net_costs.auxiliary_cost_categories
                ),
                structure_package_cost_eur=(
                    net_costs.structure_package_cost_eur * vat_multiplier
                    if net_costs.structure_package_cost_eur is not None
                    else None
                ),
                structure_package_panel_count=(
                    net_costs.structure_package_panel_count
                ),
            )

        else:
            cost_configuration = InstallationCostConfiguration(
                panel_unit_cost_eur=PANEL_COST_GROSS_EUR,
                structure_unit_cost_eur=(
                    STRUCTURE_COST_GROSS_PER_PANEL_EUR
                ),
                installation_cost_eur=INSTALLATION_LABOUR_GROSS_EUR,
                inverter_unit_cost_eur=INVERTER_COST_GROSS_EUR,
                electrical_protection_cost_eur=(
                    ELECTRICAL_PROTECTION_GROSS_EUR
                ),
                cabling_cost_eur=CABLING_AND_ACCESSORIES_GROSS_EUR,
                legalization_cost_eur=LEGALIZATION_ESTIMATE_EUR,
            )

        self.project.set_installation_cost_configuration(
            cost_configuration
        )

    def _update_installation_costs(self, result) -> None:
        """Actualiza la inversión económica de la instalación recomendada."""

        cost_configuration = (
            self.project.installation_cost_configuration
        )

        if cost_configuration is None:
            self._configure_installation_costs(result)
            cost_configuration = (
                self.project.installation_cost_configuration
            )

        economic_configuration = (
            cost_configuration.build_economic_configuration(
                result.evaluation
            )
        )

        self.project.economics.configuration.installation_cost = (
            economic_configuration.installation_cost_eur
        )

        self.project.economics._economic_data = None
        self.project.analyzer.economics_engine.economic_analysis_calculated = (
            False
        )

    def _update_total_investment(
        self,
        result,
        battery_recommendation,
    ) -> None:
        """Actualiza la inversión sin duplicar partidas de un presupuesto cerrado."""

        cost_configuration = (
            self.project.installation_cost_configuration
        )

        if cost_configuration is None:
            raise RuntimeError(
                "No se ha configurado el coste de la instalación FV."
            )

        using_closed_budget = False

        try:
            installation_economics = (
                cost_configuration.build_economic_configuration(
                    result.evaluation
                )
            )
            installation_cost = (
                installation_economics.installation_cost_eur
            )

        except ValueError as error:
            if (
                "coste de la estructura no está confirmado"
                not in str(error)
            ):
                raise

            installation_cost = getattr(
                self.project,
                "closed_installation_cost_eur",
                None,
            )

            if (
                isinstance(installation_cost, bool)
                or not isinstance(installation_cost, (int, float))
                or installation_cost <= 0
            ):
                raise ValueError(
                    "No se puede actualizar la inversión: falta un "
                    "presupuesto cerrado válido para la instalación FV."
                ) from error

            # El presupuesto cerrado ya incluye las baterías ofertadas.
            # La legalización se presupuesta aparte.
            installation_cost = (
                float(installation_cost)
                + cost_configuration.calculate_legalization_cost(
                    result.evaluation
                )
            )
            using_closed_budget = True

        battery_cost = 0.0

        # Solo se añade la batería cuando la inversión procede del
        # cálculo de catálogo. El presupuesto cerrado ya incluye batería.
        if (
            not using_closed_budget
            and battery_recommendation is not None
        ):
            battery_cost = (
                battery_recommendation.capacity_kwh
                * self._battery_cost_per_kwh_eur()
            )

        self.project.economics.configuration.installation_cost = (
            installation_cost + battery_cost
        )

        if battery_recommendation is not None:
            self.project.set_battery_configuration(
                BatteryConfiguration(
                    capacity_kwh=battery_recommendation.capacity_kwh,
                    max_charge_power_kw=5.0,
                    max_discharge_power_kw=5.0,
                    charge_efficiency=0.95,
                    discharge_efficiency=0.95,
                    min_soc=0.10,
                    max_soc=0.90,
                    initial_soc=0.10,
                )
            )
            self.project.solar.calculate_energy_balance()

        self.project.economics._economic_data = None
        self.project.analyzer.economics_engine.economic_analysis_calculated = (
            False
        )

    def _battery_cost_per_kwh_eur(self) -> float:
        """Devuelve el coste bruto estimado por kWh de batería."""

        selection = getattr(
            self.project,
            "component_selection",
            None,
        )

        if not isinstance(
            selection,
            InstallationComponentSelection,
        ):
            return BATTERY_COST_GROSS_PER_KWH_EUR

        if selection.battery_id is None:
            return BATTERY_COST_GROSS_PER_KWH_EUR

        battery = selection.battery

        return (
            battery.price_eur
            * (1.0 + INSTALLATION_VAT_RATE)
            / battery.capacity_kwh
        )

    def _initialize_default_component_selection(self) -> None:
        """Inicializa el catálogo y selecciona sus componentes por defecto."""

        from helios.solar.components_catalog import ComponentCatalog
        from helios.solar.default_component_catalog import (
            build_default_component_catalog,
        )
        from helios.solar.installation_component_selection import (
            InstallationComponentSelection,
        )

        catalog = getattr(self.project, "component_catalog", None)
        selection = getattr(self.project, "component_selection", None)

        # MagicMock puede devolver objetos simulados para cualquier atributo.
        # Solo reutilizamos objetos que sean instancias reales del tipo esperado.
        if not isinstance(catalog, ComponentCatalog):
            if isinstance(selection, InstallationComponentSelection):
                catalog = selection.catalog
            else:
                catalog = build_default_component_catalog()

            self.project.set_component_catalog(catalog)

            # Mantener los atributos coherentes también con proyectos simulados
            # en los tests, cuyos setters no necesariamente actualizan el estado.
            self.project.component_catalog = catalog

        if isinstance(selection, InstallationComponentSelection):
            if selection.catalog is not catalog:
                raise ValueError(
                    "La selección de componentes no pertenece "
                    "al catálogo configurado en el proyecto."
                )
        else:
            selection = InstallationComponentSelection(
                catalog=catalog,
                panel_id="longi lr7-60hvh-540m",
                inverter_id="goodwe-gw8k-eha-g20",
                mounting_system_id="mounting-arabic-tile",
                roof_type="teja_arabe",
                mounting_package_ids=(
                    "mounting-arabic-tile-3-panel",
                    "mounting-arabic-tile-2-panel",
                ),
                mounting_package_panel_count=15,
                auxiliary_cost_ids=(
                    "electrical_protection_dc",
                    "electrical_protection_ac",
                    "solar_cabling_red",
                    "solar_cabling_black",
                    "connector_female",
                    "connector_male",
                    "joining_profiles",
                    "installation",
                    "legalization_estimate",
                ),
            )

            self.project.set_component_selection(selection)
            self.project.component_selection = selection

            panel = selection.panel
            self.panel_width_spinbox.setValue(panel.width_m)
            self.panel_height_spinbox.setValue(panel.height_m)
            self.panel_power_spinbox.setValue(panel.power_wp)

    def _installation_economic_evaluation_available(
        self,
        result,
    ) -> bool:
        """Comprueba si existe una base válida para evaluar la inversión."""

        cost_configuration = (
            self.project.installation_cost_configuration
        )

        if cost_configuration is None:
            return False

        try:
            cost_configuration.calculate_installation_cost(
                result.evaluation
            )

        except ValueError as error:
            if (
                "coste de la estructura no está confirmado"
                not in str(error)
            ):
                raise

            closed_budget = getattr(
                self.project,
                "closed_installation_cost_eur",
                None,
            )

            return (
                isinstance(closed_budget, (int, float))
                and not isinstance(closed_budget, bool)
                and closed_budget > 0
            )

        return True