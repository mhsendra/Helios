from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QBrush
from PySide6.QtWidgets import QWidget

from helios.solar.installation_layout import InstallationLayout


class InstallationLayoutWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._layout = None

        self.setMinimumSize(
            350,
            300,
        )

    def set_layout(
        self,
        installation_layout: InstallationLayout | None,
    ):

        self._layout = installation_layout

        self.update()

    def clear(self):

        self._layout = None

        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        painter.fillRect(
            self.rect(),
            self.palette().base(),
        )

        if self._layout is None:

            painter.drawText(
                self.rect(),
                Qt.AlignCenter,
                "Sin layout disponible",
            )

            return

        layout = self._layout

        # ------------------------------------------
        # Dimensiones físicas
        # ------------------------------------------

        occupied_width = (
            layout.occupied_width_m
        )

        occupied_height = (
            layout.occupied_height_m
        )

        if (
            occupied_width <= 0
            or occupied_height <= 0
        ):
            return

        # ------------------------------------------
        # Escala
        # ------------------------------------------

        margin = 30

        available_width = (
            self.width()
            - 2 * margin
        )

        available_height = (
            self.height()
            - 2 * margin
        )

        scale = min(
            available_width / occupied_width,
            available_height / occupied_height,
        )

        draw_width = (
            occupied_width * scale
        )

        draw_height = (
            occupied_height * scale
        )

        origin_x = (
            self.width() - draw_width
        ) / 2

        origin_y = (
            self.height() - draw_height
        ) / 2

        # ------------------------------------------
        # Panel dimensions
        # ------------------------------------------

        panel_width = (
            layout.oriented_panel_width_m
            * scale
        )

        panel_height = (
            layout.oriented_panel_height_m
            * scale
        )

        # ------------------------------------------
        # Paneles
        # ------------------------------------------

        pen = QPen()
        painter.setPen(pen)

        brush = QBrush(
            self.palette().highlight()
        )

        painter.setBrush(brush)

        for row in range(layout.rows):

            for column in range(layout.columns):

                x = (
                    origin_x
                    + column * panel_width
                )

                y = (
                    origin_y
                    + row * panel_height
                )

                painter.drawRect(
                    int(x),
                    int(y),
                    int(panel_width),
                    int(panel_height),
                )

        # ------------------------------------------
        # Pasillo
        # ------------------------------------------

        if layout.walkway_position == "vertical":

            walkway_x = (
                origin_x
                + layout.columns * panel_width
            )

            walkway_width = (
                layout.walkway_width_m
                * scale
            )

            painter.setBrush(
                self.palette().window()
            )

            painter.drawRect(
                int(walkway_x),
                int(origin_y),
                int(walkway_width),
                int(draw_height),
            )

        elif layout.walkway_position == "horizontal":

            walkway_y = (
                origin_y
                + layout.rows * panel_height
            )

            walkway_height = (
                layout.walkway_width_m
                * scale
            )

            painter.setBrush(
                self.palette().window()
            )

            painter.drawRect(
                int(origin_x),
                int(walkway_y),
                int(draw_width),
                int(walkway_height),
            )