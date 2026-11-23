"""M3.3: candidatos de edificio catastral cercanos a un portal.

No identifica de forma concluyente una finca: clasifica proximidad geométrica.
Trabaja con GML EPSG:3857 descargados por el usuario, sin red ni Qt.
"""

import argparse
import json
import math
from pathlib import Path
from xml.etree import ElementTree as ET

from helios.mapping.coordinates import GeoCoordinates
from helios.mapping.icgc import bounding_box, web_mercator
from helios.mapping.roof_geometry import ImageGeoReference

GML = "{http://www.opengis.net/gml/3.2}"


def _ring_coordinates(node):
    rings = []
    for pos in node.iter(GML + "posList"):
        if not pos.text:
            continue
        values = [float(s) for s in pos.text.split()]
        if len(values) < 6 or len(values) % 2:
            continue
        rings.append([(values[i], values[i + 1]) for i in range(0, len(values), 2)])
    return rings


def load_buildings(path: Path):
    """Extrae geometrías por feature Building; conserva anillos separados."""
    root = ET.parse(path).getroot()
    buildings = []
    for member in root:
        if member.tag.split("}")[-1] not in ("member", "featureMember"):
            continue
        for feature in member:
            if feature.tag.split("}")[-1] != "Building":
                continue
            srs = {e.attrib["srsName"] for e in feature.iter() if "srsName" in e.attrib}
            if srs and any("3857" not in value for value in srs):
                raise ValueError("El GML no está en EPSG:3857.")
            rings = _ring_coordinates(feature)
            if rings:
                buildings.append({
                    "id": feature.attrib.get(GML + "id", f"building-{len(buildings)+1}"),
                    "rings": rings,
                })
    return buildings


def _point_in_ring(p, ring):
    x, y = p
    inside = False
    for a, b in zip(ring, ring[1:] + ring[:1]):
        if (a[1] > y) != (b[1] > y):
            intersection = (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]
            if x < intersection:
                inside = not inside
    return inside


def _segment_distance(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    denom = dx * dx + dy * dy
    if denom == 0:
        return math.dist(p, a)
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / denom))
    return math.dist(p, (a[0] + t * dx, a[1] + t * dy))


def distance_to_building(p, rings):
    """Distancia mínima al contorno; cero dentro del anillo exterior.

    Se preservan los anillos para dibujarlos, pero los huecos internos no se
    interpretan en esta primera versión: deben verificarse visualmente.
    """
    if not rings:
        raise ValueError("Edificio sin geometría.")
    if _point_in_ring(p, rings[0]):
        return 0.0
    return min(_segment_distance(p, a, b)
               for ring in rings for a, b in zip(ring, ring[1:] + ring[:1]))


def rank_buildings(buildings, point):
    px, py = web_mercator(point)
    factor = math.cos(math.radians(point.latitude))
    ranked = []
    for building in buildings:
        distance_projected = distance_to_building((px, py), building["rings"])
        ranked.append({
            "id": building["id"],
            "distance_projected": distance_projected,
            "distance_ground_approx_m": distance_projected * factor,
            "rings": building["rings"],
        })
    ranked.sort(key=lambda item: (item["distance_projected"], item["id"]))
    return ranked


def make_preview(image_path, point, span, ranked, output):
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise RuntimeError("Instala Pillow: python -m pip install Pillow") from exc
    image = Image.open(image_path).convert("RGB")
    ref = ImageGeoReference(bounding_box(point, span), *image.size)
    draw = ImageDraw.Draw(image)
    for index, building in enumerate(ranked, 1):
        color = "#ffbf00" if index == 1 else "#00bfff"
        for ring in building["rings"]:
            pixels = [ref.mercator_to_pixel(x, y) for x, y in ring]
            if len(pixels) >= 3:
                draw.line(pixels + [pixels[0]], fill=color, width=5 if index == 1 else 3)
        # Etiqueta en el centro de la caja envolvente, solo para identificar candidato.
        all_points = [p for ring in building["rings"] for p in ring]
        minx = min(p[0] for p in all_points)
        maxx = max(p[0] for p in all_points)
        miny = min(p[1] for p in all_points)
        maxy = max(p[1] for p in all_points)
        cx, cy = ref.mercator_to_pixel((minx + maxx) / 2, (miny + maxy) / 2)
        draw.text((cx, cy), str(index), fill="white", stroke_width=3, stroke_fill="black")
    gps = ref.mercator_to_pixel(*web_mercator(point))
    x, y = gps
    draw.ellipse((x-10, y-10, x+10, y+10), outline="red", width=5)
    image.save(output)


def main():
    parser = argparse.ArgumentParser(description="M3.3: asociación portal-edificio, preliminar")
    parser.add_argument("--gml", type=Path, default=Path("catastro_Building.gml"))
    parser.add_argument("--image", type=Path, default=Path("icgc_vivienda_ampliada.png"))
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--span", type=float, default=120)
    parser.add_argument("--output", type=Path, default=Path("catastro_candidatos.png"))
    args = parser.parse_args()
    point = GeoCoordinates(args.lat, args.lon)
    ranked = rank_buildings(load_buildings(args.gml), point)
    if not ranked:
        raise RuntimeError("No se han encontrado edificios en el GML.")
    make_preview(args.image, point, args.span, ranked, args.output)
    report = args.output.with_suffix(".ranking.json")
    report.write_text(json.dumps({
        "status": "unverified_proximity_ranking",
        "method": "portal_to_building_footprint_distance",
        "distance_note": "Aproximación local por cos(latitud), no distancia geodésica exacta.",
        "candidates": [
            {"rank": i, "id": item["id"],
             "distance_ground_approx_m": round(item["distance_ground_approx_m"], 2)}
            for i, item in enumerate(ranked, 1)
        ],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("=== CANDIDATOS CATASTRALES (SIN CONFIRMAR) ===")
    for i, item in enumerate(ranked, 1):
        print(f"{i}. {item['id']} - distancia aproximada: {item['distance_ground_approx_m']:.2f} m")
    print("Imagen:", args.output.resolve())
    print("Informe:", report.resolve())
    print("ATENCION: el candidato 1 NO está identificado como vivienda confirmada.")


if __name__ == "__main__":
    main()
