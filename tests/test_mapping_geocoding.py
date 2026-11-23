"""Pruebas offline del cliente CartoCiudad."""

import io
import json
from urllib.error import URLError
from urllib.parse import parse_qs, urlsplit

import pytest

from helios.mapping.coordinates import GeoCoordinates
from helios.mapping.geocoding import (
    AddressCandidate, CartoCiudadGeocoder, GeocodingError,
)


class Response(io.BytesIO):
    def __init__(self, data):
        super().__init__(json.dumps(data).encode("utf-8"))


def test_search_candidates_and_explicit_selection():
    calls = []

    def opener(request, timeout):
        calls.append((request.full_url, timeout))
        if "/candidates?" in request.full_url:
            return Response([
                {"address": "Calle Mayor 1, Madrid", "lat": 40.4, "lon": -3.7},
                {"address": "Calle Mayor 2, Madrid"},
            ])
        return Response({"lat": 40.41, "lon": -3.71})

    geocoder = CartoCiudadGeocoder(opener=opener)
    candidates = geocoder.search("Calle Mayor, Madrid", limit=2)
    assert len(candidates) == 2
    assert candidates[0].coordinates == GeoCoordinates(40.4, -3.7)
    assert len(calls) == 1  # No se resuelve ni se elige automáticamente.
    assert parse_qs(urlsplit(calls[0][0]).query) == {"q": ["Calle Mayor, Madrid"], "limit": ["2"]}
    assert geocoder.resolve(candidates[1]) == GeoCoordinates(40.41, -3.71)
    assert parse_qs(urlsplit(calls[1][0]).query)["q"] == ["Calle Mayor 2, Madrid"]
    assert geocoder.resolve(candidates[0]) == GeoCoordinates(40.4, -3.7)
    assert len(calls) == 2


def test_empty_search():
    geocoder = CartoCiudadGeocoder(opener=lambda *_args, **_kwargs: Response([]))
    assert geocoder.search("dirección inexistente") == []


@pytest.mark.parametrize("query", ["", "  ", None])
def test_invalid_query(query):
    with pytest.raises(ValueError):
        CartoCiudadGeocoder().search(query)


@pytest.mark.parametrize("limit", [0, 21, True, 2.5])
def test_invalid_limit(limit):
    with pytest.raises(ValueError):
        CartoCiudadGeocoder().search("Madrid", limit=limit)


def test_network_error():
    def failing(_request, timeout):
        raise URLError("offline")

    with pytest.raises(GeocodingError, match="conectar"):
        CartoCiudadGeocoder(opener=failing).search("Madrid")


def test_malformed_json():
    def malformed(_request, timeout):
        return io.BytesIO(b"{bad json")

    with pytest.raises(GeocodingError, match="JSON"):
        CartoCiudadGeocoder(opener=malformed).search("Madrid")


def test_bad_response_format():
    with pytest.raises(GeocodingError, match="Formato"):
        CartoCiudadGeocoder(opener=lambda *_args, **_kwargs: Response({})).search("Madrid")


def test_missing_coordinates():
    geocoder = CartoCiudadGeocoder(
        opener=lambda *_args, **_kwargs: Response({"address": "Calle Mayor"})
    )
    with pytest.raises(GeocodingError, match="coordenadas"):
        geocoder.resolve(AddressCandidate("Calle Mayor"))


def test_geojson_point():
    geocoder = CartoCiudadGeocoder(
        opener=lambda *_args, **_kwargs: Response({
            "geometry": {"type": "Point", "coordinates": [-3.7, 40.4]}
        })
    )
    assert geocoder.resolve(AddressCandidate("Madrid")) == GeoCoordinates(40.4, -3.7)


def test_real_cartociudad_find_lat_lng():
    """Regresión: el servicio real usa 'lng', no 'lon'."""
    geocoder = CartoCiudadGeocoder(
        opener=lambda *_args, **_kwargs: Response({
            "id": "13.PV.MUN_280790145199",
            "type": "portal",
            "address": "MAYOR",
            "lat": 40.416461059323886,
            "lng": -3.7046584169537073,
            "state": 0,
        })
    )
    assert geocoder.resolve(AddressCandidate("CALLE MAYOR 1, Madrid")) == GeoCoordinates(
        40.416461059323886, -3.7046584169537073
    )
