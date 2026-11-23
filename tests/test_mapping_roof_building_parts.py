"""Pruebas de asociación geométrica de partes."""
from helios.mapping.roof_building_parts import rings_intersect, select_parts, _area


def test_overlap():
    a=[(0,0),(4,0),(4,4),(0,4)]
    b=[(3,3),(6,3),(6,6),(3,6)]
    assert rings_intersect(a,b)


def test_separated():
    a=[(0,0),(4,0),(4,4),(0,4)]
    b=[(5,5),(6,5),(6,6),(5,6)]
    assert not rings_intersect(a,b)


def test_enclosed():
    a=[(0,0),(10,0),(10,10),(0,10)]
    b=[(2,2),(3,2),(3,3),(2,3)]
    assert rings_intersect(a,b)


def test_select_parts():
    building={"rings":[[(0,0),(10,0),(10,10),(0,10)]]}
    parts=[{"id":"inside","rings":[[(2,2),(3,2),(3,3),(2,3)]]},
           {"id":"outside","rings":[[(20,20),(21,20),(21,21),(20,21)]]}]
    assert [p["id"] for p in select_parts(building,parts)] == ["inside"]


def test_area():
    assert _area([(0,0),(6,0),(6,4),(0,4)]) == 24
