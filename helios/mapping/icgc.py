"""Descarga de ortofotografía local del ICGC mediante WMS 1.1.1.

Documentación: https://www.icgc.cat/es/Geoinformacion-y-mapas/Servicios-en-linea-Geoservicios/WMS-Ortoimagenes/WMS-Ortofoto-local
"""

from dataclasses import dataclass
import math
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from helios.mapping.coordinates import GeoCoordinates

ICGC_WMS_URL = "https://geoserveis.icgc.cat/servei/catalunya/orto-local/wms"
ICGC_LAYER = "orto-local-rgb-vigents"
MAX_MERCATOR_LATITUDE = 85.05112878
EARTH_RADIUS_M = 6378137.0


class OrthophotoError(RuntimeError):
    """La ortofotografía no se ha podido obtener o validar."""


@dataclass(frozen=True)
class Orthophoto:
    """Imagen PNG y recuadro de coordenadas proyectadas EPSG:3857."""

    image: bytes
    bbox_3857: tuple[float, float, float, float]
    width: int
    height: int
    provider: str = "ICGC"
    layer: str = ICGC_LAYER
    crs: str = "EPSG:3857"

    @property
    def projected_pixel_size(self) -> tuple[float, float]:
        """Tamaño del píxel en unidades proyectadas; NO metros reales sobre terreno."""
        xmin, ymin, xmax, ymax = self.bbox_3857
        return (xmax - xmin) / self.width, (ymax - ymin) / self.height


def web_mercator(point: GeoCoordinates) -> tuple[float, float]:
    """Proyecta WGS84 a Web Mercator, sin dependencias externas."""
    if abs(point.latitude) > MAX_MERCATOR_LATITUDE:
        raise ValueError("Latitud fuera del dominio Web Mercator.")
    x = EARTH_RADIUS_M * math.radians(point.longitude)
    y = EARTH_RADIUS_M * math.log(math.tan(math.pi / 4 + math.radians(point.latitude) / 2))
    return x, y


def bounding_box(point: GeoCoordinates, span_m: float = 100.0) -> tuple[float, float, float, float]:
    """Cuadro centrado de extensión proyectada span_m (EPSG:3857)."""
    if not isinstance(span_m, (int, float)) or isinstance(span_m, bool) or not math.isfinite(span_m) or not 5 <= span_m <= 2000:
        raise ValueError("span_m debe estar entre 5 y 2000.")
    x, y = web_mercator(point)
    half = span_m / 2
    return (x - half, y - half, x + half, y + half)


class ICGCOrthophotoClient:
    def __init__(self, *, timeout: float = 20.0, opener=None):
        if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or not math.isfinite(timeout) or not 0 < timeout <= 120:
            raise ValueError("timeout inválido.")
        self.timeout = timeout
        self._opener = opener or urlopen

    def fetch(self, point: GeoCoordinates, *, span_m: float = 100.0,
              width: int = 768, height: int = 768) -> Orthophoto:
        if not isinstance(point, GeoCoordinates):
            raise TypeError("point debe ser GeoCoordinates.")
        if any(isinstance(v, bool) or not isinstance(v, int) or not 64 <= v <= 2048 for v in (width, height)):
            raise ValueError("Dimensiones fuera de rango (64-2048).")
        bbox = bounding_box(point, span_m)
        params = {
            "SERVICE": "WMS", "VERSION": "1.1.1", "REQUEST": "GetMap",
            "LAYERS": ICGC_LAYER, "STYLES": "", "FORMAT": "image/png",
            "TRANSPARENT": "TRUE", "SRS": "EPSG:3857",
            "BBOX": ",".join(f"{v:.3f}" for v in bbox),
            "WIDTH": width, "HEIGHT": height,
            "EXCEPTIONS": "application/vnd.ogc.se_xml",
        }
        request = Request(f"{ICGC_WMS_URL}?{urlencode(params)}",
                          headers={"User-Agent": "Helios/1.0", "Accept": "image/png"})
        try:
            with self._opener(request, timeout=self.timeout) as response:
                content_type = response.headers.get("Content-Type", "").lower()
                image = response.read(15_000_001)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise OrthophotoError("Error de conexión con el WMS del ICGC.") from exc
        if len(image) > 15_000_000:
            raise OrthophotoError("Imagen demasiado grande.")
        if not image.startswith(b"\\x89PNG\\r\\n\\x1a\\n") or "image/png" not in content_type:
            raise OrthophotoError("El ICGC no ha devuelto una imagen PNG válida.")
        if len(image) < 24:
            raise OrthophotoError("Imagen PNG incompleta.")
        actual_width = int.from_bytes(image[16:20], "big")
        actual_height = int.from_bytes(image[20:24], "big")
        if (actual_width, actual_height) != (width, height):
            raise OrthophotoError("Dimensiones PNG inesperadas.")
        return Orthophoto(image=image, bbox_3857=bbox, width=width, height=height)
