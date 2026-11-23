"""Pruebas de la georreferenciación y geometría sin Qt."""

import pytest

from helios.mapping.coordinates import GeoCoordinates
from helios.mapping.icgc import bounding_box, web_mercator
from helios.mapping.roof_geometry import ImageGeoReference, polygon_area


def test_center_of_image_is_reference_point():
    point = GeoCoordinates(41.620317, 2.09549)
    ref = ImageGeoReference(bounding_box(point, 120), 1536, 1536)
    geo = ref.pixel_to_wgs84(768, 768)
    assert geo.latitude == pytest.approx(point.latitude, abs=1e-9)
    assert geo.longitude == pytest.approx(point.longitude, abs=1e-9)


def test_pixel_projected_round_trip():
    point = GeoCoordinates(41.6, 2.1)
    ref = ImageGeoReference(bounding_box(point, 120), 1536, 1536)
    x, y = ref.pixel_to_mercator(400, 1100)
    assert ref.mercator_to_pixel(x, y) == pytest.approx((400, 1100))


def test_polygon_area():
    assert polygon_area([(0, 0), (10, 0), (10, 5), (0, 5)]) == 50
    assert polygon_area([(0, 0), (10, 0)]) == 0


def test_invalid_reference():
    with pytest.raises(ValueError):
        ImageGeoReference((1, 1, 0, 0), 100, 100)
