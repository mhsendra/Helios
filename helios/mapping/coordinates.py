"""Coordenadas geográficas WGS84 para el editor de cubiertas."""

from dataclasses import dataclass
import math


def _parse_decimal(value: float | str, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite decimal number.")
    if isinstance(value, str):
        value = value.strip().replace(",", ".")
        if not value:
            raise ValueError(f"{name} cannot be empty.")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite decimal number.") from exc
    if not math.isfinite(result):
        raise ValueError(f"{name} must be a finite decimal number.")
    return result


@dataclass(frozen=True)
class GeoCoordinates:
    """Latitud y longitud en grados decimales (EPSG:4326)."""

    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        latitude = _parse_decimal(self.latitude, "latitude")
        longitude = _parse_decimal(self.longitude, "longitude")
        if not -90.0 <= latitude <= 90.0:
            raise ValueError("latitude must be between -90 and 90 degrees.")
        if not -180.0 <= longitude <= 180.0:
            raise ValueError("longitude must be between -180 and 180 degrees.")
        object.__setattr__(self, "latitude", latitude)
        object.__setattr__(self, "longitude", longitude)

    @property
    def lon_lat(self) -> tuple[float, float]:
        """Orden habitual en servicios GIS: (longitud, latitud)."""
        return self.longitude, self.latitude


def parse_coordinates(latitude: float | str, longitude: float | str) -> GeoCoordinates:
    """Acepta punto o coma decimal y devuelve coordenadas WGS84 validadas."""
    return GeoCoordinates(latitude, longitude)
