"""Paso 36: inspección de partes catastrales del edificio seleccionado.

Solo lectura. Las partes BuildingPart NO equivalen a viviendas ni a faldones.
EPSG:3857 -> superficie horizontal aproximada mediante cos(lat)^2.
"""
import argparse
import json
import math
from pathlib import Path
from xml.etree import ElementTree as ET

from helios.mapping.coordinates import GeoCoordinates
from helios.mapping.icgc import bounding_box, web_mercator

GML_NS = "{http://www.opengis.net/gml/3.2}"


def _rings(feature):
    result = []
    for pos in feature.iter(GML_NS + "posList"):
        if not pos.text:
            continue
        numbers = [float(v) for v in pos.text.split()]
        if len(numbers) >= 6 and len(numbers) % 2 == 0:
            result.append([(numbers[i], numbers[i+1])
                           for i in range(0, len(numbers), 2)])
    return result


def _features(path, kind):
    root = ET.parse(path).getroot()
    features = []
    for member in root:
        if member.tag.split("}")[-1] not in ("member", "featureMember"):
            continue
        for feature in member:
            if feature.tag.split("}")[-1] != kind:
                continue
            srs = [e.attrib["srsName"] for e in feature.iter()
                   if "srsName" in e.attrib]
            if not srs or any("3857" not in item for item in srs):
                raise ValueError(f"SRS ausente o distinto de EPSG:3857 en {path}")
            rings = _rings(feature)
            if rings:
                features.append({
                    "id": feature.attrib.get(GML_NS + "id", ""),
                    "rings": rings,
                })
    return features


def _area(ring):
    return abs(sum(a[0]*b[1] - b[0]*a[1]
                   for a, b in zip(ring, ring[1:] + ring[:1]))) / 2


def _centroid_bbox(ring):
    return ((min(x for x, _ in ring) + max(x for x, _ in ring))/2,
            (min(y for _, y in ring) + max(y for _, y in ring))/2)


def _inside(point, ring):
    x, y = point
    inside = False
    for a, b in zip(ring, ring[1:] + ring[:1]):
        if (a[1] > y) != (b[1] > y):
            crossing = a[0] + (y-a[1])*(b[0]-a[0])/(b[1]-a[1])
            if x < crossing:
                inside = not inside
    return inside


def _orientation(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])


def _on_segment(a, b, p, eps=1e-6):
    return abs(_orientation(a,b,p)) <= eps and (
        min(a[0],b[0])-eps <= p[0] <= max(a[0],b[0])+eps and
        min(a[1],b[1])-eps <= p[1] <= max(a[1],b[1])+eps
    )


def _segments_intersect(a,b,c,d):
    o1,o2,o3,o4 = (_orientation(a,b,c),_orientation(a,b,d),
                   _orientation(c,d,a),_orientation(c,d,b))
    if (o1 > 0 > o2 or o2 > 0 > o1) and (o3 > 0 > o4 or o4 > 0 > o3):
        return True
    return (_on_segment(a,b,c) or _on_segment(a,b,d)
            or _on_segment(c,d,a) or _on_segment(c,d,b))


def rings_intersect(a,b):
    """Intersección geométrica 2D; no interpreta huecos ni multipolígonos."""
    if any(_inside(p,b) for p in a[:-1]) or any(_inside(p,a) for p in b[:-1]):
        return True
    return any(_segments_intersect(p,q,r,s)
               for p,q in zip(a,a[1:]+a[:1])
               for r,s in zip(b,b[1:]+b[:1]))


def select_parts(building, parts):
    """Filtra partes que tocan o se solapan con el contorno seleccionado."""
    return [part for part in parts
            if any(rings_intersect(br,pr)
                   for br in building["rings"] for pr in part["rings"])]


def inspect(building_file, parts_file, building_id, point):
    buildings = _features(building_file, "Building")
    matches = [b for b in buildings if b["id"] == building_id]
    if len(matches) != 1:
        raise ValueError(f"Identificador no único o ausente: {building_id}")
    building = matches[0]
    parts = select_parts(building, _features(parts_file, "BuildingPart"))
    factor = math.cos(math.radians(point.latitude)) ** 2
    rows = []
    for index, part in enumerate(parts, 1):
        # Área bruta aproximada de anillos; los huecos no se restan.
        projected = sum(_area(r) for r in part["rings"])
        rows.append({
            "number": index,
            "id": part["id"],
            "area_3857_m2": round(projected, 2),
            "horizontal_area_approx_m2": round(projected*factor, 2),
            "rings": part["rings"],
        })
    return building, rows


def preview(image_file, output, point, span, building, rows):
    from PIL import Image, ImageDraw
    image = Image.open(image_file).convert("RGB")
    w,h = image.size
    xmin,ymin,xmax,ymax = bounding_box(point,span)
    def pixel(p):
        return ((p[0]-xmin)/(xmax-xmin)*w,
                (ymax-p[1])/(ymax-ymin)*h)
    draw = ImageDraw.Draw(image)
    for ring in building["rings"]:
        vertices = [pixel(p) for p in ring]
        draw.line(vertices+[vertices[0]], fill="cyan", width=5)
    for row in rows:
        for ring in row["rings"]:
            vertices = [pixel(p) for p in ring]
            draw.line(vertices+[vertices[0]], fill="lime", width=3)
        center = pixel(_centroid_bbox(row["rings"][0]))
        draw.text(center, str(row["number"]), fill="white",
                  stroke_width=3, stroke_fill="black")
    image.save(output)


def main():
    p = argparse.ArgumentParser(description="Paso 36: partes de edificio catastral")
    p.add_argument("--buildings", type=Path, default=Path("catastro_Building.gml"))
    p.add_argument("--parts", type=Path, default=Path("catastro_BuildingPart.gml"))
    p.add_argument("--building-id", required=True)
    p.add_argument("--image", type=Path, default=Path("icgc_vivienda_ampliada.png"))
    p.add_argument("--lat", type=float, required=True)
    p.add_argument("--lon", type=float, required=True)
    p.add_argument("--span", type=float, default=120)
    p.add_argument("--output", type=Path, default=Path("catastro_partes_23_25.png"))
    args = p.parse_args()
    point = GeoCoordinates(args.lat,args.lon)
    building,rows = inspect(args.buildings,args.parts,args.building_id,point)
    preview(args.image,args.output,point,args.span,building,rows)
    report = args.output.with_suffix(".parts.json")
    report.write_text(json.dumps({
        "status": "unverified_building_parts",
        "building_id": args.building_id,
        "note": "Partes que intersectan el edificio, no viviendas ni faldones. Áreas aproximadas sin descontar huecos.",
        "parts": [{k:v for k,v in row.items() if k != "rings"} for row in rows],
    },indent=2,ensure_ascii=False),encoding="utf-8")
    print("=== PARTES CATASTRALES DEL EDIFICIO ===")
    print("Edificio:",args.building_id)
    print("Partes que lo intersectan:",len(rows))
    for row in rows:
        print(f"{row['number']:>2}. {row['id']} | horizontal aprox. {row['horizontal_area_approx_m2']:.2f} m2")
    print("Imagen:",args.output.resolve())
    print("Informe:",report.resolve())
    print("IMPORTANTE: no se ha identificado la división jurídica 23/25.")


if __name__ == "__main__":
    main()
