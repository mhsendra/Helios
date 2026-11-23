"""Pruebas geométricas de asociación portal-edificio."""
import pytest
from helios.mapping.roof_building_match import distance_to_building, rank_buildings
from helios.mapping.coordinates import GeoCoordinates
from helios.mapping.icgc import web_mercator


def test_inside_building_distance_zero():
    square = [[(0, 0), (10, 0), (10, 10), (0, 10)]]
    assert distance_to_building((5, 5), square) == 0


def test_distance_to_edge_not_center():
    square = [[(0, 0), (10, 0), (10, 10), (0, 10)]]
    assert distance_to_building((13, 5), square) == pytest.approx(3)


def test_ranking_by_distance():
    point = GeoCoordinates(41.62, 2.095)
    x, y = web_mercator(point)
    near = [[(x+2, y), (x+4, y), (x+4, y+2), (x+2, y+2)]]
    far = [[(x+20, y), (x+22, y), (x+22, y+2), (x+20, y+2)]]
    ranked = rank_buildings([{"id":"far", "rings":far}, {"id":"near", "rings":near}], point)
    assert [v["id"] for v in ranked] == ["near", "far"]
