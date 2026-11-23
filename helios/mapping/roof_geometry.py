"""Geometría independiente de Qt para la edición de faldones."""

from dataclasses import dataclass
import math

from helios.mapping.coordinates import GeoCoordinates
from helios.mapping.icgc import web_mercator, EARTH_RADIUS_M


@dataclass(frozen=True)
class ImageGeoReference:
    bbox_3857: tuple[float, float, float, float]
    width: int
    height: int

    def __post_init__(self):
        x0, y0, x1, y1 = self.bbox_3857
        if not all(math.isfinite(v) for v in self.bbox_3857) or x1 <= x0 or y1 <= y0:
            raise ValueError("BBOX inválido.")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Dimensiones inválidas.")

    def pixel_to_mercator(self, px: float, py: float) -> tuple[float, float]:
        x0, y0, x1, y1 = self.bbox_3857
        return x0 + px / self.width * (x1 - x0), y1 - py / self.height * (y1 - y0)

    def mercator_to_pixel(self, x: float, y: float) -> tuple[float, float]:
        x0, y0, x1, y1 = self.bbox_3857
        return (x - x0) / (x1 - x0) * self.width, (y1 - y) / (y1 - y0) * self.height

    def pixel_to_wgs84(self, px: float, py: float) -> GeoCoordinates:
        x, y = self.pixel_to_mercator(px, py)
        lon = math.degrees(x / EARTH_RADIUS_M)
        lat = math.degrees(2 * math.atan(math.exp(y / EARTH_RADIUS_M)) - math.pi / 2)
        return GeoCoordinates(lat, lon)


def polygon_area(points: list[tuple[float, float]]) -> float:
    """Área en unidades cuadradas del sistema de entrada (no corrige distorsión)."""
    if len(points) < 3:
        return 0.0
    return abs(sum(x * points[(i + 1) % len(points)][1] -
                   points[(i + 1) % len(points)][0] * y
                   for i, (x, y) in enumerate(points))) / 2
