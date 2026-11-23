"""Pruebas sin conexión del WMS de ortofoto local ICGC."""

import io
import math
import struct
from urllib.error import URLError
from urllib.parse import parse_qs, urlsplit

import pytest

from helios.mapping.coordinates import GeoCoordinates
from helios.mapping.icgc import (
    ICGCOrthophotoClient, OrthophotoError, bounding_box, web_mercator,
)


class FakeResponse(io.BytesIO):
    def __init__(self, data, content_type="image/png"):
        super().__init__(data)
        self.headers = {"Content-Type": content_type}


def png_header(width=768, height=768):
    return b"\\x89PNG\\r\\n\\x1a\\n" + b"\\x00\\x00\\x00\\x0dIHDR" + struct.pack(">II", width, height)


def test_web_mercator_origin():
    assert web_mercator(GeoCoordinates(0, 0)) == pytest.approx((0, 0), abs=1e-7)


def test_bbox_dimensions():
    bbox = bounding_box(GeoCoordinates(41.6, 2.1), 120)
    assert bbox[2] - bbox[0] == pytest.approx(120)
    assert bbox[3] - bbox[1] == pytest.approx(120)


@pytest.mark.parametrize("span", [0, -1, float("nan"), float("inf"), 2001, True])
def test_bad_span(span):
    with pytest.raises(ValueError):
        bounding_box(GeoCoordinates(41.6, 2.1), span)


def test_wms_request_and_metadata():
    requests = []

    def opener(request, timeout):
        requests.append(request.full_url)
        return FakeResponse(png_header())

    result = ICGCOrthophotoClient(opener=opener).fetch(GeoCoordinates(41.6, 2.1))
    params = parse_qs(urlsplit(requests[0]).query)
    assert params["LAYERS"] == ["orto-local-rgb-vigents"]
    assert params["SRS"] == ["EPSG:3857"]
    assert params["REQUEST"] == ["GetMap"]
    assert result.width == result.height == 768
    assert result.projected_pixel_size == pytest.approx((100 / 768, 100 / 768))


def test_service_exception_xml():
    client = ICGCOrthophotoClient(
        opener=lambda *_args, **_kwargs: FakeResponse(b"<ServiceExceptionReport/>", "text/xml")
    )
    with pytest.raises(OrthophotoError, match="PNG"):
        client.fetch(GeoCoordinates(41.6, 2.1))


def test_network_error():
    def failing(_request, timeout):
        raise URLError("offline")

    with pytest.raises(OrthophotoError, match="conexión"):
        ICGCOrthophotoClient(opener=failing).fetch(GeoCoordinates(41.6, 2.1))


def test_bad_png_dimensions():
    client = ICGCOrthophotoClient(
        opener=lambda *_args, **_kwargs: FakeResponse(png_header(256, 256))
    )
    with pytest.raises(OrthophotoError, match="Dimensiones"):
        client.fetch(GeoCoordinates(41.6, 2.1))


def test_invalid_dimensions():
    with pytest.raises(ValueError):
        ICGCOrthophotoClient(opener=lambda *_args, **_kwargs: None).fetch(
            GeoCoordinates(41.6, 2.1), width=32
        )
