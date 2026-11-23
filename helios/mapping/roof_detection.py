"""Prueba experimental M3.2: segmentación automática de cubierta cercana al GPS.

Requiere opencv-python y numpy. No modifica la geometría manual.
El contorno obtenido es una propuesta visual, NO una detección validada.
"""

import argparse
import json
import math
from pathlib import Path

from helios.mapping.coordinates import GeoCoordinates
from helios.mapping.icgc import bounding_box, web_mercator
from helios.mapping.roof_geometry import ImageGeoReference


def detect(image_path: Path, point: GeoCoordinates, span: float,
           output: Path, *, search_m: float = 18.0):
    try:
        import cv2
        import numpy as np
    except ImportError as exc:
        raise RuntimeError(
            "Faltan dependencias de la prueba. Instala: "
            "python -m pip install opencv-python numpy"
        ) from exc

    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"No se puede leer la imagen: {image_path}")
    height, width = image.shape[:2]
    bbox = bounding_box(point, span)
    reference = ImageGeoReference(bbox, width, height)
    mx, my = web_mercator(point)
    px, py = reference.mercator_to_pixel(mx, my)

    # La caja es solo una zona de búsqueda alrededor del portal.
    # En EPSG:3857 los metros proyectados no son metros de terreno.
    projected_radius = search_m / max(0.01, math.cos(math.radians(point.latitude)))
    radius_x = max(20, round(projected_radius * width / (bbox[2] - bbox[0])))
    radius_y = max(20, round(projected_radius * height / (bbox[3] - bbox[1])))
    x0 = max(1, round(px) - radius_x)
    y0 = max(1, round(py) - radius_y)
    x1 = min(width - 1, round(px) + radius_x)
    y1 = min(height - 1, round(py) + radius_y)
    if x1 - x0 < 10 or y1 - y0 < 10:
        raise ValueError("El punto GPS está demasiado cerca del borde de la imagen.")

    # GrabCut usa la caja como hipótesis; no conoce qué es un tejado.
    mask = np.zeros((height, width), dtype=np.uint8)
    bg = np.zeros((1, 65), np.float64)
    fg = np.zeros((1, 65), np.float64)
    cv2.grabCut(image, mask, (x0, y0, x1 - x0, y1 - y0),
                bg, fg, 5, cv2.GC_INIT_WITH_RECT)
    foreground = np.where(
        (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0
    ).astype(np.uint8)
    count, components, stats, centers = cv2.connectedComponentsWithStats(foreground)
    candidates = []
    for label in range(1, count):
        area = int(stats[label, cv2.CC_STAT_AREA])
        if area < 100:
            continue
        cx, cy = centers[label]
        distance = math.hypot(cx - px, cy - py)
        candidates.append((distance, -area, label))
    if not candidates:
        raise RuntimeError("No se ha obtenido ninguna región candidata.")

    # Elegimos la región cercana al punto, no afirmamos que sea la cubierta.
    _, _, label = min(candidates)
    selected = np.where(components == label, 255, 0).astype(np.uint8)
    contours, _ = cv2.findContours(selected, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    contour = max(contours, key=cv2.contourArea)
    perimeter = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.015 * perimeter, True)
    vertices = [(int(v[0][0]), int(v[0][1])) for v in approx]
    if len(vertices) < 3:
        raise RuntimeError("La región no produce un polígono válido.")

    preview = image.copy()
    tint = preview.copy()
    tint[selected > 0] = (0, 180, 255)
    preview = cv2.addWeighted(preview, 0.70, tint, 0.30, 0)
    cv2.polylines(preview, [approx], True, (0, 255, 0), 3)
    cv2.circle(preview, (round(px), round(py)), 10, (0, 0, 255), 3)
    cv2.rectangle(preview, (x0, y0), (x1, y1), (255, 160, 0), 2)
    if not cv2.imwrite(str(output), preview):
        raise OSError(f"No se pudo guardar {output}")

    # Resultado independiente: nunca sobreescribir el JSON manual.
    geo_vertices = [
        [geo.latitude, geo.longitude]
        for geo in (reference.pixel_to_wgs84(x, y) for x, y in vertices)
    ]
    result = {
        "status": "unverified_candidate",
        "method": "grabcut_gps_rectangle",
        "image": image_path.name,
        "bbox_3857": list(bbox),
        "search_radius_ground_m_approx": search_m,
        "vertices_pixels": vertices,
        "vertices_wgs84_lat_lon": geo_vertices,
    }
    metadata = output.with_suffix(".candidate.json")
    metadata.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("Imagen de diagnóstico:", output.resolve())
    print("Datos del candidato:", metadata.resolve())
    print("Vértices propuestos:", len(vertices))
    print("ADVERTENCIA: propuesta sin validar. No usar aún para calcular paneles.")


def main():
    parser = argparse.ArgumentParser(description="Detector experimental M3.2")
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--lat", required=True, type=float)
    parser.add_argument("--lon", required=True, type=float)
    parser.add_argument("--span", type=float, default=120)
    parser.add_argument("--search-m", type=float, default=18)
    parser.add_argument("--output", type=Path, default=Path("cubierta_candidata.png"))
    args = parser.parse_args()
    detect(args.image, GeoCoordinates(args.lat, args.lon), args.span,
           args.output, search_m=args.search_m)


if __name__ == "__main__":
    main()
