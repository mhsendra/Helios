"""Pruebas del núcleo de coordenadas del editor cartográfico."""

import pytest

from helios.mapping.coordinates import GeoCoordinates, parse_coordinates


def test_parse_decimal_comma_and_whitespace():
    point = parse_coordinates(" 41,6165 ", " 2,0850 ")
    assert point == GeoCoordinates(41.6165, 2.085)
    assert point.lon_lat == (2.085, 41.6165)


@pytest.mark.parametrize("latitude,longitude", [(0, 0), (-90, -180), (90, 180)])
def test_valid_boundaries(latitude, longitude):
    assert parse_coordinates(latitude, longitude).lon_lat == (float(longitude), float(latitude))


@pytest.mark.parametrize("latitude,longitude", [
    (91, 0), (-91, 0), (0, 181), (0, -181),
    ("", 0), ("abc", 0), (float("nan"), 0), (0, float("inf")),
    (True, 0), (0, False), (None, 0),
])
def test_reject_invalid_coordinates(latitude, longitude):
    with pytest.raises(ValueError):
        parse_coordinates(latitude, longitude)
