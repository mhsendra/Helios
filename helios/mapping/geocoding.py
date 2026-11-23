"""Cliente REST de CartoCiudad, independiente de la interfaz de Helios.

Fuente: https://www.cartociudad.es/web/portal/directorio-de-servicios/geoprocesamiento
Atribución: CC BY 4.0 www.scne.es/productos.html#CartoCiudad
"""

from dataclasses import dataclass
import json
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from helios.mapping.coordinates import GeoCoordinates

BASE_URL = "https://www.cartociudad.es/geocoder/api/geocoder"
ATTRIBUTION = "CC BY 4.0 www.scne.es/productos.html#CartoCiudad"


class GeocodingError(RuntimeError):
    """Error de comunicación o respuesta inválida del servicio."""


@dataclass(frozen=True)
class AddressCandidate:
    """Dirección candidata; no implica que sea la vivienda elegida."""

    label: str
    coordinates: GeoCoordinates | None = None


def _coordinates(data: dict) -> GeoCoordinates | None:
    """Extrae WGS84 cuando el servicio proporciona ambos valores."""
    lon = data.get("lng", data.get("lon", data.get("longitude")))
    lat = data.get("lat", data.get("latitude"))
    if lon is None or lat is None:
        geometry = data.get("geometry")
        if isinstance(geometry, dict) and geometry.get("type") == "Point":
            values = geometry.get("coordinates")
            if isinstance(values, (list, tuple)) and len(values) >= 2:
                lon, lat = values[:2]
    if lon is None or lat is None:
        return None
    try:
        return GeoCoordinates(lat, lon)
    except ValueError as exc:
        raise GeocodingError("CartoCiudad ha devuelto coordenadas inválidas.") from exc


class CartoCiudadGeocoder:
    """Busca candidatos y resuelve una selección explícita a coordenadas."""

    def __init__(self, *, timeout: float = 10.0, opener: Callable | None = None):
        if not 0 < timeout <= 60:
            raise ValueError("timeout debe estar entre 0 y 60 segundos.")
        self.timeout = timeout
        self._opener = opener or urlopen

    def _get(self, method: str, **params):
        url = f"{BASE_URL}/{method}?{urlencode(params)}"
        request = Request(url, headers={"Accept": "application/json", "User-Agent": "Helios/1.0"})
        try:
            with self._opener(request, timeout=self.timeout) as response:
                data = json.load(response)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise GeocodingError("No se ha podido conectar con CartoCiudad.") from exc
        except (ValueError, UnicodeError) as exc:
            raise GeocodingError("CartoCiudad ha devuelto JSON inválido.") from exc
        return data

    def search(self, query: str, *, limit: int = 5) -> list[AddressCandidate]:
        """Devuelve coincidencias; nunca selecciona automáticamente la primera."""
        query = query.strip() if isinstance(query, str) else ""
        if not query:
            raise ValueError("Introduce una dirección para buscar.")
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 20:
            raise ValueError("limit debe ser un entero entre 1 y 20.")
        data = self._get("candidates", q=query, limit=limit)
        if not isinstance(data, list):
            raise GeocodingError("Formato de candidatos inesperado.")
        results = []
        for item in data:
            if not isinstance(item, dict):
                raise GeocodingError("Candidato de dirección inválido.")
            label = item.get("address") or item.get("name")
            if not isinstance(label, str) or not label.strip():
                raise GeocodingError("Candidato sin dirección reconocible.")
            results.append(AddressCandidate(label.strip(), _coordinates(item)))
        return results

    def resolve(self, candidate: AddressCandidate) -> GeoCoordinates:
        """Resuelve únicamente el candidato elegido por el usuario."""
        if not isinstance(candidate, AddressCandidate):
            raise TypeError("Se necesita un AddressCandidate.")
        if candidate.coordinates is not None:
            return candidate.coordinates
        data = self._get("find", q=candidate.label)
        if not isinstance(data, dict):
            raise GeocodingError("Formato de geocodificación inesperado.")
        coordinates = _coordinates(data)
        if coordinates is None:
            raise GeocodingError("La dirección seleccionada no tiene coordenadas.")
        return coordinates
