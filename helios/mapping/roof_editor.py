"""Visor independiente para delimitar faldones sobre una ortofotografía.

Uso:
python -m helios.mapping.roof_editor --image icgc_vivienda_ampliada.png --lat LAT --lon LON --span 120
"""

import argparse
import json
from pathlib import Path
import sys

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QBrush, QPen, QPixmap, QPolygonF
from PySide6.QtWidgets import (
    QApplication, QGraphicsEllipseItem, QGraphicsPixmapItem,
    QGraphicsPolygonItem, QGraphicsScene, QGraphicsView,
    QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPushButton,
    QVBoxLayout, QWidget, QFileDialog,
)

from helios.mapping.coordinates import GeoCoordinates
from helios.mapping.icgc import bounding_box
from helios.mapping.roof_geometry import ImageGeoReference, polygon_area


class RoofView(QGraphicsView):
    def __init__(self, scene, click_callback):
        super().__init__(scene)
        self.click_callback = click_callback
        self.setRenderHints(self.renderHints())
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self._panning = False
        self._pan_origin = None

    def wheelEvent(self, event):
        factor = 1.2 if event.angleDelta().y() > 0 else 1 / 1.2
        current = self.transform().m11()
        if 0.08 <= current * factor <= 25:
            self.scale(factor, factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._pan_origin = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton:
            p = self.mapToScene(event.position().toPoint())
            self.click_callback(p.x(), p.y())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._panning:
            new = event.position().toPoint()
            delta = new - self._pan_origin
            self._pan_origin = new
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self.unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)


class RoofEditor(QMainWindow):
    def __init__(self, image_path: Path, reference: ImageGeoReference):
        super().__init__()
        self.image_path = image_path
        self.reference = reference
        self.polygons = []
        self.current = []
        self.overlays = []
        self.setWindowTitle("Helios · Editor de faldones (M3.1)")
        pixmap = QPixmap(str(image_path))
        if pixmap.isNull():
            raise ValueError("No se puede abrir la ortofotografía.")
        if (pixmap.width(), pixmap.height()) != (reference.width, reference.height):
            raise ValueError("La imagen no coincide con las dimensiones geográficas.")

        scene = QGraphicsScene(self)
        scene.addPixmap(pixmap)
        scene.setSceneRect(0, 0, pixmap.width(), pixmap.height())
        self.scene = scene
        self.view = RoofView(scene, self.add_point)
        self.view.fitInView(scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.status = QLabel("Clic izquierdo: vértice · Rueda: zoom · Botón central: desplazar")

        controls = QHBoxLayout()
        for title, handler in [
            ("Cerrar faldón", self.close_polygon),
            ("Deshacer punto", self.undo),
            ("Nuevo faldón", self.new_polygon),
            ("Guardar JSON", self.save),
            ("Ajustar vista", self.fit),
        ]:
            button = QPushButton(title)
            button.clicked.connect(handler)
            controls.addWidget(button)
        root = QVBoxLayout()
        root.addLayout(controls)
        root.addWidget(self.view)
        root.addWidget(self.status)
        container = QWidget()
        container.setLayout(root)
        self.setCentralWidget(container)
        self.resize(1100, 900)
        self.redraw()

    def fit(self):
        self.view.resetTransform()
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def add_point(self, px, py):
        if not (0 <= px <= self.reference.width and 0 <= py <= self.reference.height):
            return
        self.current.append((px, py))
        self.redraw()

    def redraw(self):
        for item in self.overlays:
            self.scene.removeItem(item)
        self.overlays.clear()
        for index, points in enumerate(self.polygons):
            self._draw_polygon(points, QColor(0, 210, 90, 65), QColor(0, 220, 100))
        if self.current:
            self._draw_polygon(self.current, QColor(255, 185, 0, 40), QColor(255, 180, 0))
        self.status.setText(
            f"Faldones cerrados: {len(self.polygons)} · Vértices en edición: {len(self.current)}"
            " · Rueda: zoom · Botón central: desplazar"
        )

    def _draw_polygon(self, points, fill, border):
        if len(points) >= 3:
            item = self.scene.addPolygon(
                QPolygonF([QPointF(x, y) for x, y in points]),
                QPen(border, 3), QBrush(fill)
            )
            self.overlays.append(item)
        elif len(points) == 2:
            item = self.scene.addLine(*points[0], *points[1], QPen(border, 3))
            self.overlays.append(item)
        for x, y in points:
            marker = self.scene.addEllipse(x - 5, y - 5, 10, 10,
                                           QPen(Qt.GlobalColor.white, 2), QBrush(border))
            self.overlays.append(marker)

    def close_polygon(self):
        if len(self.current) < 3:
            QMessageBox.warning(self, "Faldón incompleto", "Marca al menos tres vértices.")
            return
        if polygon_area(self.current) < 1:
            QMessageBox.warning(self, "Faldón inválido", "Los vértices no delimitan un área.")
            return
        self.polygons.append(self.current.copy())
        self.current.clear()
        self.redraw()

    def undo(self):
        if self.current:
            self.current.pop()
            self.redraw()

    def new_polygon(self):
        if self.current:
            reply = QMessageBox.question(self, "Descartar puntos",
                                         "¿Descartar los vértices del faldón sin cerrar?")
            if reply != QMessageBox.StandardButton.Yes:
                return
        self.current.clear()
        self.redraw()

    def save(self):
        if self.current:
            QMessageBox.warning(self, "Faldón sin cerrar",
                                "Cierra o descarta el faldón en edición antes de guardar.")
            return
        if not self.polygons:
            QMessageBox.warning(self, "Sin faldones", "Marca al menos un faldón.")
            return
        destination, _ = QFileDialog.getSaveFileName(
            self, "Guardar faldones", str(self.image_path.with_suffix(".roof.json")), "JSON (*.json)"
        )
        if not destination:
            return
        result = {
            "schema_version": 1,
            "image": self.image_path.name,
            "crs": "EPSG:3857",
            "bbox_3857": list(self.reference.bbox_3857),
            "image_size": [self.reference.width, self.reference.height],
            "area_note": "Áreas en unidades proyectadas EPSG:3857; no son superficies reales de cubierta.",
            "roof_planes": [
                {
                    "id": index + 1,
                    "pixels": [[x, y] for x, y in points],
                    "wgs84_lat_lon": [
                        [geo.latitude, geo.longitude]
                        for geo in (self.reference.pixel_to_wgs84(x, y) for x, y in points)
                    ],
                    "area_mercator_units_squared": polygon_area(
                        [self.reference.pixel_to_mercator(x, y) for x, y in points]
                    ),
                }
                for index, points in enumerate(self.polygons)
            ],
        }
        Path(destination).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        QMessageBox.information(self, "Guardado", f"Faldones guardados en:\n{destination}")


def main():
    parser = argparse.ArgumentParser(description="Editor de cubiertas Helios M3.1")
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--span", type=float, default=120.0)
    args = parser.parse_args()
    point = GeoCoordinates(args.lat, args.lon)
    bbox = bounding_box(point, args.span)
    app = QApplication(sys.argv[:1])
    pixmap = QPixmap(str(args.image))
    if pixmap.isNull():
        parser.error(f"Imagen inexistente o no válida: {args.image}")
    reference = ImageGeoReference(bbox, pixmap.width(), pixmap.height())
    window = RoofEditor(args.image, reference)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
