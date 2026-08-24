import traceback

from PySide6.QtCore import Qt, QRectF
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGridLayout,
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

from helios.solar.installation_optimizer import (
    InstallationOptimizer,
)

from helios.solar.installation_evaluation import (
    InstallationEvaluator,
)

from helios.solar.installation_recommendation import (
    InstallationRecommender,
)

from helios.solar.installation_coordinator import (
    InstallationCoordinator,
)

from helios.solar.PVGIS_production import (
    PVGISProductionService,
)

from helios.solar.configuration import (
    SolarConfiguration,
)

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

        # Posición relativa del pasillo.
        # 0 = extremo izquierdo/superior
        # 100 = extremo derecho/inferior
        self.walkway_offset_percent = 50

        self.setMinimumHeight(360)
        self.setMinimumWidth(500)

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

    # ==================================================
    # CONFIGURACIÓN
    # ==================================================

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

    def set_walkway_offset(
        self,
        value: int,
    ):

        self.walkway_offset_percent = value

        self.update()

    def clear(self):
        """Limpia la distribución física mostrada."""

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
    # ==================================================
    # GEOMETRÍA
    # ==================================================

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

    # ==================================================
    # PAINT
    # ==================================================

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        painter.setRenderHint(
            QPainter.TextAntialiasing
        )

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
            painter.setPen(
                QColor("#777777")
            )

            painter.drawText(
                self.rect(),
                Qt.AlignCenter,
                "No hay una distribución física disponible.",
            )

            return

        # ==================================================
        # Márgenes gráficos
        # ==================================================

        left_margin = 70
        right_margin = 35
        top_margin = 35
        bottom_margin = 60

        available_width = (
            self.width()
            - left_margin
            - right_margin
        )

        available_height = (
            self.height()
            - top_margin
            - bottom_margin
        )

        if available_width <= 0 or available_height <= 0:
            return

        # ==================================================
        # Escala física → píxeles
        # ==================================================

        scale = min(
            available_width / self.roof_width,
            available_height / self.roof_height,
        )

        roof_px_width = (
            self.roof_width * scale
        )

        roof_px_height = (
            self.roof_height * scale
        )

        roof_x = (
            left_margin
            + (
                available_width
                - roof_px_width
            ) / 2
        )

        roof_y = (
            top_margin
            + (
                available_height
                - roof_px_height
            ) / 2
        )

        roof_rect = QRectF(
            roof_x,
            roof_y,
            roof_px_width,
            roof_px_height,
        )

        # ==================================================
        # Tejado
        # ==================================================

        painter.setPen(
            QPen(
                QColor("#404040"),
                2,
            )
        )

        painter.setBrush(
            QBrush(
                QColor("#e5e7eb")
            )
        )

        painter.drawRect(
            roof_rect
        )

        # ==================================================
        # Dimensiones del panel
        # ==================================================

        panel_width, panel_height = (
            self._panel_dimensions()
        )

        panel_width_px = (
            panel_width * scale
        )

        panel_height_px = (
            panel_height * scale
        )

        # ==================================================
        # Dimensiones reales de la instalación
        # ==================================================

        installation_width = (
            self.columns * panel_width
        )

        installation_height = (
            self.rows * panel_height
        )

        # ==================================================
        # Pasillo
        # ==================================================

        walkway_vertical = (
            self.walkway_width > 0
            and self.walkway_position == "vertical"
        )

        walkway_horizontal = (
            self.walkway_width > 0
            and self.walkway_position == "horizontal"
        )

        if walkway_vertical:
            installation_width += (
                self.walkway_width
            )

        if walkway_horizontal:
            installation_height += (
                self.walkway_width
            )

        # ==================================================
        # Posición centrada inicialmente
        # ==================================================

        remaining_width = (
            self.roof_width
            - installation_width
        )

        remaining_height = (
            self.roof_height
            - installation_height
        )

        margin_x = max(
            remaining_width / 2,
            0.0,
        )

        margin_y = max(
            remaining_height / 2,
            0.0,
        )

        installation_x = (
            roof_x
            + margin_x * scale
        )

        installation_y = (
            roof_y
            + margin_y * scale
        )

        # ==================================================
        # Pasillo desplazable
        # ==================================================

        walkway_x = None
        walkway_y = None

        if walkway_vertical:

            free_space = max(
                remaining_width,
                0.0,
            )

            max_offset = free_space

            offset = (
                max_offset
                * self.walkway_offset_percent
                / 100
            )

            installation_x = (
                roof_x
                + offset * scale
            )

        elif walkway_horizontal:

            free_space = max(
                remaining_height,
                0.0,
            )

            max_offset = free_space

            offset = (
                max_offset
                * self.walkway_offset_percent
                / 100
            )

            installation_y = (
                roof_y
                + offset * scale
            )

        # ==================================================
        # Dibujar paneles y pasillo
        # ==================================================

        panel_index = 0

        for row in range(self.rows):

            for column in range(self.columns):

                x = (
                    installation_x
                    + column
                    * panel_width_px
                )

                y = (
                    installation_y
                    + row
                    * panel_height_px
                )

                # ------------------------------------------
                # Desplazamiento por pasillo vertical
                # ------------------------------------------

                if (
                    walkway_vertical
                    and self.columns > 1
                ):

                    walkway_column = int(
                        round(
                            (
                                self.walkway_offset_percent
                                / 100
                            )
                            * self.columns
                        )
                    )

                    if column >= walkway_column:

                        x += (
                            self.walkway_width
                            * scale
                        )

                # ------------------------------------------
                # Desplazamiento por pasillo horizontal
                # ------------------------------------------

                if (
                    walkway_horizontal
                    and self.rows > 1
                ):

                    walkway_row = int(
                        round(
                            (
                                self.walkway_offset_percent
                                / 100
                            )
                            * self.rows
                        )
                    )

                    if row >= walkway_row:

                        y += (
                            self.walkway_width
                            * scale
                        )

                panel_rect = QRectF(
                    x,
                    y,
                    panel_width_px,
                    panel_height_px,
                )

                # ------------------------------------------
                # Panel
                # ------------------------------------------

                painter.setPen(
                    QPen(
                        QColor("#164e8a"),
                        1,
                    )
                )

                painter.setBrush(
                    QBrush(
                        QColor("#1976d2")
                    )
                )

                painter.drawRoundedRect(
                    panel_rect,
                    2,
                    2,
                )

                panel_index += 1

        # ==================================================
        # Dibujar pasillo
        # ==================================================

        if walkway_vertical:

            walkway_column = int(
                round(
                    (
                        self.walkway_offset_percent
                        / 100
                    )
                    * self.columns
                )
            )

            walkway_x = (
                installation_x
                + walkway_column
                * panel_width_px
            )

            walkway_rect = QRectF(
                walkway_x,
                installation_y,
                self.walkway_width * scale,
                installation_height * scale,
            )

            painter.setPen(
                QPen(
                    QColor("#c27c00"),
                    1,
                )
            )

            painter.setBrush(
                QBrush(
                    QColor("#f6c453")
                )
            )

            painter.drawRect(
                walkway_rect
            )

        elif walkway_horizontal:

            walkway_row = int(
                round(
                    (
                        self.walkway_offset_percent
                        / 100
                    )
                    * self.rows
                )
            )

            walkway_y = (
                installation_y
                + walkway_row
                * panel_height_px
            )

            walkway_rect = QRectF(
                installation_x,
                walkway_y,
                installation_width * scale,
                self.walkway_width * scale,
            )

            painter.setPen(
                QPen(
                    QColor("#c27c00"),
                    1,
                )
            )

            painter.setBrush(
                QBrush(
                    QColor("#f6c453")
                )
            )

            painter.drawRect(
                walkway_rect
            )

        # ==================================================
        # Cotas del tejado
        # ==================================================

        painter.setPen(
            QColor("#444444")
        )

        font = QFont()
        font.setPointSize(9)

        painter.setFont(font)

        painter.drawText(
            QRectF(
                roof_x,
                roof_y
                + roof_px_height
                + 8,
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

        # ==================================================
        # Leyenda
        # ==================================================

        legend_y = (
            roof_y
            + roof_px_height
            + 35
        )

        painter.setBrush(
            QColor("#1976d2")
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.drawRect(
            QRectF(
                roof_x,
                legend_y,
                14,
                14,
            )
        )

        painter.setPen(
            QColor("#444444")
        )

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

            painter.setBrush(
                QColor("#f6c453")
            )

            painter.setPen(
                Qt.NoPen
            )

            painter.drawRect(
                QRectF(
                    roof_x + 110,
                    legend_y,
                    14,
                    14,
                )
            )

            painter.setPen(
                QColor("#444444")
            )

            painter.drawText(
                QRectF(
                    roof_x + 130,
                    legend_y - 2,
                    140,
                    20,
                ),
                Qt.AlignLeft,
                "Paso mantenimiento",
            )

class SolarConfigPage(QWidget):
    """
    Página de configuración y dimensionamiento automático
    de la instalación fotovoltaica.

    La página:

        - muestra la configuración solar de referencia;
        - permite definir las restricciones físicas;
        - ejecuta la optimización;
        - muestra todos los resultados numéricos;
        - representa gráficamente el layout recomendado.

    La lógica de optimización permanece delegada en:

        InstallationCoordinator
        InstallationOptimizer
        InstallationEvaluator
        InstallationRecommender
    """

    def __init__(
        self,
        project,
        main_window=None,
    ):

        super().__init__()

        self.project = project
        self.main_window = main_window

        self.pvgis_service = PVGISProductionService()

        self.setup_ui()
        self.configure_widgets()
        self.connect_signals()
        self.load_solar_basis()

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

        layout.addWidget(
            self.create_simulation_basis_group()
        )

        layout.addWidget(
            self.create_installation_group()
        )

        layout.addWidget(
            self.create_panel_group()
        )

        layout.addWidget(
            self.create_maintenance_group()
        )

        layout.addWidget(
            self.create_action_group()
        )

        layout.addWidget(
            self.create_result_group()
        )

        layout.addStretch()

        self.scroll_area.setWidget(content)

        outer_layout.addWidget(
            self.scroll_area
        )

    # ==================================================
    # CABECERA
    # ==================================================

    def create_title(self):

        frame = QFrame()

        layout = QVBoxLayout(frame)

        title = QLabel(
            "<h2>Configuración de la simulación solar</h2>"
        )

        description = QLabel(
            "Define las condiciones físicas de la instalación "
            "que se utilizarán para buscar la mejor configuración "
            "fotovoltaica."
        )

        description.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(description)

        return frame

    # ==================================================
    # BASE SOLAR
    # ==================================================

    def create_simulation_basis_group(self):

        group = QGroupBox(
            "Base solar del cálculo"
        )

        layout = QFormLayout(group)

        self.latitude_label = QLabel("-")
        self.longitude_label = QLabel("-")
        self.tilt_label = QLabel("-")
        self.azimuth_label = QLabel("-")
        self.reference_year_label = QLabel("-")
        self.losses_label = QLabel("-")
        self.technology_label = QLabel("-")
        self.mounting_label = QLabel("-")

        layout.addRow(
            "Latitud",
            self.latitude_label,
        )

        layout.addRow(
            "Longitud",
            self.longitude_label,
        )

        layout.addRow(
            "Inclinación",
            self.tilt_label,
        )

        layout.addRow(
            "Orientación",
            self.azimuth_label,
        )

        layout.addRow(
            "Año de referencia",
            self.reference_year_label,
        )

        layout.addRow(
            "Pérdidas del sistema",
            self.losses_label,
        )

        layout.addRow(
            "Tecnología FV",
            self.technology_label,
        )

        layout.addRow(
            "Montaje",
            self.mounting_label,
        )

        return group

    # ==================================================
    # INSTALACIÓN
    # ==================================================

    def create_installation_group(self):

        group = QGroupBox(
            "Superficie disponible"
        )

        layout = QFormLayout(group)

        self.available_area_spinbox = QDoubleSpinBox()

        self.roof_width_spinbox = QDoubleSpinBox()

        self.roof_height_spinbox = QDoubleSpinBox()

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

        self.panel_width_spinbox = QDoubleSpinBox()
        self.panel_height_spinbox = QDoubleSpinBox()
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

        self.maintenance_width_spinbox = QDoubleSpinBox()

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
            "Configuración pendiente"
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

        # ==================================================
        # Panel izquierdo: datos numéricos
        # ==================================================

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

        # ==================================================
        # Panel derecho: layout físico
        # ==================================================

        layout_widget = QWidget()

        layout_widget.setMinimumWidth(
            350
        )

        layout_widget_layout = QVBoxLayout(
            layout_widget
        )

        layout_title = QLabel(
            "<b>Distribución física de los paneles</b>"
        )

        layout_title.setAlignment(
            Qt.AlignCenter
        )

        # ==================================================
        # Contenedor del layout gráfico
        # ==================================================

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

        self.roof_layout_widget = RoofLayoutWidget()

        # ==================================================
        # Control de posición del pasillo
        # ==================================================

        self.walkway_slider_label = QLabel(
            "Posición del pasillo de mantenimiento"
        )

        self.walkway_slider_label.setAlignment(
            Qt.AlignCenter
        )

        self.walkway_slider = QSlider(
            Qt.Horizontal
        )

        self.walkway_slider.setRange(
            0,
            100,
        )

        self.walkway_slider.setValue(
            50
        )

        self.walkway_slider.setEnabled(
            False
        )

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

        layout_container_layout.addWidget(
            self.roof_layout_widget,
            1,
        )

        # ==================================================
        # Información del layout
        # ==================================================

        self.layout_info_label = QLabel(
            "No hay una instalación calculada."
        )

        self.layout_info_label.setAlignment(
            Qt.AlignCenter
        )

        self.layout_info_label.setWordWrap(
            True
        )

        # ==================================================
        # Añadir elementos al panel derecho
        # ==================================================

        layout_widget_layout.addWidget(
            layout_title
        )

        layout_widget_layout.addWidget(
            self.layout_info_label
        )

        # IMPORTANTE:
        # El contenedor que incluye slider + RoofLayoutWidget
        # debe añadirse al layout visible.

        layout_widget_layout.addWidget(
            self.layout_grid_container,
            1,
        )

        # ==================================================
        # Paneles izquierdo y derecho
        # ==================================================

        main_layout.addWidget(
            data_widget,
            1,
        )

        main_layout.addWidget(
            layout_widget,
            1,
        )

        return group

    # ==================================================
    # CONFIGURACIÓN DE WIDGETS
    # ==================================================

    def configure_widgets(self):

        # ----------------------------------------------
        # Superficie
        # ----------------------------------------------

        self.available_area_spinbox.setRange(
            0.01,
            10000.0,
        )

        self.available_area_spinbox.setDecimals(
            2
        )

        self.available_area_spinbox.setSuffix(
            " m²"
        )

        self.roof_width_spinbox.setRange(
            0.0,
            500.0,
        )

        self.roof_width_spinbox.setDecimals(
            3
        )

        self.roof_width_spinbox.setSuffix(
            " m"
        )

        self.roof_height_spinbox.setRange(
            0.0,
            500.0,
        )

        self.roof_height_spinbox.setDecimals(
            3
        )

        self.roof_height_spinbox.setSuffix(
            " m"
        )

        # ----------------------------------------------
        # Panel
        # ----------------------------------------------

        self.panel_width_spinbox.setRange(
            0.01,
            10.0,
        )

        self.panel_width_spinbox.setDecimals(
            3
        )

        self.panel_width_spinbox.setSuffix(
            " m"
        )

        self.panel_height_spinbox.setRange(
            0.01,
            10.0,
        )

        self.panel_height_spinbox.setDecimals(
            3
        )

        self.panel_height_spinbox.setSuffix(
            " m"
        )

        self.panel_power_spinbox.setRange(
            1.0,
            2000.0,
        )

        self.panel_power_spinbox.setDecimals(
            0
        )

        self.panel_power_spinbox.setSuffix(
            " Wp"
        )

        # ----------------------------------------------
        # Número de paneles
        # ----------------------------------------------

        self.min_panels_spinbox.setRange(
            1,
            1000,
        )

        self.max_panels_spinbox.setRange(
            1,
            1000,
        )

        self.max_panels_spinbox.setEnabled(
            False
        )

        # ----------------------------------------------
        # Mantenimiento
        # ----------------------------------------------

        self.maintenance_width_spinbox.setRange(
            0.01,
            5.0,
        )

        self.maintenance_width_spinbox.setDecimals(
            2
        )

        self.maintenance_width_spinbox.setSuffix(
            " m"
        )

        self.maintenance_width_spinbox.setValue(
            0.45
        )

        self.maintenance_width_spinbox.setEnabled(
            False
        )

        self.maintenance_orientation_combobox.setEnabled(
            False
        )

        # ----------------------------------------------
        # Acción
        # ----------------------------------------------

        self.optimize_button.setMinimumHeight(
            40
        )

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
    # BASE SOLAR
    # ==================================================

    def load_solar_basis(self):

        configuration = (
            self.project
            .analyzer
            .solar_engine
            .configuration
        )

        if configuration is None:

            self.status_label.setText(
                "Configuración solar no disponible"
            )

            return

        self.latitude_label.setText(
            f"{configuration.latitude:.6f}°"
        )

        self.longitude_label.setText(
            f"{configuration.longitude:.6f}°"
        )

        self.tilt_label.setText(
            f"{configuration.tilt}°"
        )

        self.azimuth_label.setText(
            f"{configuration.azimuth}°"
        )

        self.reference_year_label.setText(
            str(configuration.reference_year)
        )

        self.losses_label.setText(
            f"{configuration.losses:.1f} %"
        )

        self.technology_label.setText(
            self.get_technology_name(
                configuration.pv_technology
            )
        )

        self.mounting_label.setText(
            self.get_mounting_name(
                configuration.mounting_place
            )
        )

        self.status_label.setText(
            "Configuración solar disponible"
        )

    # ==================================================
    # NOMBRES DESCRIPTIVOS
    # ==================================================

    @staticmethod
    def get_technology_name(
        technology: str,
    ) -> str:

        names = {
            "crystSi": "Silicio cristalino",
            "CIS": "CIS",
            "CdTe": "CdTe",
        }

        return names.get(
            technology,
            technology,
        )

    @staticmethod
    def get_mounting_name(
        mounting_place: str,
    ) -> str:

        names = {
            "free": "Estructura sobre el suelo",
            "building": "Integrado en edificio",
        }

        return names.get(
            mounting_place,
            mounting_place,
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
    # PVGIS
    # ==================================================

    def get_pvgis_configuration(
        self,
    ) -> SolarConfiguration:

        configuration = (
            self.project
            .analyzer
            .solar_engine
            .configuration
        )

        if configuration is None:

            raise ValueError(
                "La configuración solar no está disponible."
            )

        panel_power_kwp = (
            self.panel_power_spinbox.value()
            / 1000.0
        )

        if panel_power_kwp <= 0:

            raise ValueError(
                "La potencia del panel debe ser mayor que cero."
            )

        return SolarConfiguration(
            installed_power_kwp=panel_power_kwp,
            latitude=configuration.latitude,
            longitude=configuration.longitude,
            tilt=configuration.tilt,
            azimuth=configuration.azimuth,
            reference_year=configuration.reference_year,
            losses=configuration.losses,
            pv_technology=configuration.pv_technology,
            mounting_place=configuration.mounting_place,
        )

    # ==================================================
    # PRODUCCIÓN
    # ==================================================

    def _calculate_installation_production(
        self,
        candidate,
        specific_production: float,
    ) -> float:
        """
        Calcula la producción anual estimada a partir de:

            potencia instalada (kWp)
            × producción específica (kWh/kWp/año)
        """

        if specific_production <= 0:

            raise ValueError(
                "PVGIS specific production must be "
                "greater than zero."
            )

        production = (
            candidate.installed_power_kwp
            * specific_production
        )

        if production < 0:

            raise ValueError(
                "Annual production cannot be negative."
            )

        return float(production)

    # ==================================================
    # RESULTADO
    # ==================================================

    def show_optimization_result(
        self,
        result,
    ):

        configuration = (
            self.project
            .analyzer
            .solar_engine
            .configuration
        )

        # ==================================================
        # Datos básicos
        # ==================================================

        self.result_panel_count_label.setText(
            f"{result.panel_count}"
        )

        self.result_power_label.setText(
            f"{result.installed_power_kwp:.2f} kWp"
        )

        # ==================================================
        # Orientación solar
        # ==================================================

        if configuration is not None:

            azimuth = configuration.azimuth

            if azimuth == 0:

                orientation = "Sur"

            elif azimuth > 0:

                orientation = (
                    f"{azimuth}° respecto al Sur"
                )

            else:

                orientation = (
                    f"{azimuth}° respecto al Sur"
                )

            self.result_orientation_label.setText(
                f"{orientation} ({azimuth}°)"
            )

        else:

            self.result_orientation_label.setText(
                "-"
            )

        # ==================================================
        # Producción / consumo
        # ==================================================

        self.result_production_label.setText(
            f"{result.annual_production_kwh:,.0f} "
            "kWh/año"
        )

        self.result_consumption_label.setText(
            f"{result.annual_consumption_kwh:,.0f} "
            "kWh/año"
        )

        # ==================================================
        # Superficie
        # ==================================================

        self.result_occupied_area_label.setText(
            f"{result.occupied_area_m2:.2f} m²"
        )

        self.result_remaining_area_label.setText(
            f"{result.remaining_area_m2:.2f} m²"
        )

        self.result_utilization_label.setText(
            f"{result.area_utilization_percent:.1f} %"
        )

        # ==================================================
        # Balance energético
        # ==================================================

        self.result_self_sufficiency_label.setText(
            f"{result.self_sufficiency_percent:.1f} %"
        )

        self.result_coverage_label.setText(
            f"{result.production_coverage_percent:.1f} %"
        )

        self.result_surplus_label.setText(
            f"{result.energy_surplus_kwh:,.0f} "
            "kWh/año"
        )

        self.result_deficit_label.setText(
            f"{result.energy_deficit_kwh:,.0f} "
            "kWh/año"
        )

        # ==================================================
        # Layout físico
        # ==================================================

        self.show_installation_layout(
            result
        )

    # ==================================================
    # LAYOUT FÍSICO
    # ==================================================

    def show_installation_layout(
        self,
        result,
    ):

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

        # ==================================================
        # Información numérica
        # ==================================================

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
                    f"{layout.walkway_width_m:.2f} m "
                    "vertical"
                )

            elif layout.walkway_position == "horizontal":

                walkway_text = (
                    f"{layout.walkway_width_m:.2f} m "
                    "horizontal"
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

        # ==================================================
        # Tejado
        # ==================================================

        roof_width = (
            self.roof_width_spinbox.value()
        )

        roof_height = (
            self.roof_height_spinbox.value()
        )

        # ==================================================
        # Dibujar
        # ==================================================
        print(
            "LAYOUT DEBUG:",
            roof_width,
            roof_height,
            self.panel_width_spinbox.value(),
            self.panel_height_spinbox.value(),
            layout.rows,
            layout.columns,
            layout.orientation,
            layout.walkway_width_m,
            layout.walkway_position,
        )

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

            walkway_width=(
                layout.walkway_width_m
            ),

            walkway_position=(
                layout.walkway_position
            ),

            installation_width=(
                layout.occupied_width_m
            ),

            installation_height=(
                layout.occupied_height_m
            ),
        )

        # ==================================================
        # Información
        # ==================================================

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

        self.optimize_button.setEnabled(
            False
        )

        self.status_label.setText(
            "Buscando la mejor instalación..."
        )

        try:

            # ------------------------------------------
            # Configuración física
            # ------------------------------------------

            configuration = (
                self.get_installation_configuration()
            )

            # ------------------------------------------
            # Dataset
            # ------------------------------------------

            dataset = (
                self.project
                .analyzer
                .valid_dataset()
            )

            if dataset is None or dataset.empty:

                raise ValueError(
                    "A valid consumption dataset is required."
                )

            annual_consumption_kwh = float(
                dataset["AE_kWh"].sum()
            )

            if annual_consumption_kwh <= 0:

                raise ValueError(
                    "Annual consumption must be "
                    "greater than zero."
                )

            # ------------------------------------------
            # PVGIS
            # ------------------------------------------

            pvgis_configuration = (
                self.get_pvgis_configuration()
            )

            specific_production = (
                self.pvgis_service.get_specific_production(
                    pvgis_configuration
                )
            )

            if specific_production <= 0:

                raise ValueError(
                    "PVGIS specific production must "
                    "be greater than zero."
                )

            # ------------------------------------------
            # Restricciones
            # ------------------------------------------

            constraints = (
                configuration.to_constraints()
            )

            # ------------------------------------------
            # Coordinador
            # ------------------------------------------

            coordinator = InstallationCoordinator(

                optimizer=InstallationOptimizer(
                    constraints
                ),

                evaluator=InstallationEvaluator(
                    constraints
                ),

                recommender=InstallationRecommender(),

                production_calculator=(
                    lambda candidate:
                        self._calculate_installation_production(
                            candidate,
                            specific_production,
                        )
                ),
            )

            # ------------------------------------------
            # Recomendación
            # ------------------------------------------

            result = coordinator.recommend(

                configuration=configuration,

                annual_consumption_kwh=(
                    annual_consumption_kwh
                ),
            )

            # ------------------------------------------
            # Guardar
            # ------------------------------------------

            self.project.solar.sizing_result = result

            # ------------------------------------------
            # Mostrar
            # ------------------------------------------

            self.show_optimization_result(
                result
            )

            self.status_label.setText(
                "Optimización completada"
            )

        except Exception as error:

            traceback.print_exc()

            self.status_label.setText(
                f"Error: {error}"
            )

        finally:

            self.optimize_button.setEnabled(
                True
            )

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

        self.roof_layout_widget.clear()

        self.walkway_slider.setEnabled(
            False
        )

        self.walkway_position_label.setText(
            "50 %"
        )

        self.layout_info_label.setText(
            "No hay una instalación calculada."
        )

    def reset(self):

        self.clear_optimization_result()

        self.status_label.setText(
            "Configuración pendiente"
        )

        self.optimize_button.setEnabled(
            True
        )

        self.load_solar_basis()

    def update_data(self):

        self.load_solar_basis()

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