"""
Renders a small map image centered on a coordinate, server-side, from raw
OpenStreetMap tiles - deliberately NOT st.map()/deck.gl, which needs WebGL
and fails silently (blank space, no error) when WebGL is unavailable, as
confirmed live 2026-08-17 (see docs/implementation-log.md). A plain PNG via
st.image() only needs the browser to render an <img> tag, which works
everywhere WebGL doesn't.

Uses OSM's standard tile server directly under their tile usage policy
(https://operations.osmfoundation.org/policies/tiles/): identifying
User-Agent, low volume (one property lookup = a handful of 256x256 tile
requests, not bulk/cached use).
"""

import io
import logging
import math

import requests
from PIL import Image, ImageDraw

log = logging.getLogger(__name__)

TILE_SIZE = 256
USER_AGENT = "bde-enrichment-engine/0.1 (property lookup demo; contact: jonas.haahr@aol.com)"
TIMEOUT = 10


def _lonlat_to_pixel(lon: float, lat: float, zoom: int) -> tuple[float, float]:
    """Standard slippy-map projection: geographic coords -> pixel position
    on the full world map at a given zoom level."""
    lat_rad = math.radians(lat)
    n = 2.0**zoom
    x = (lon + 180.0) / 360.0 * n * TILE_SIZE
    y = (1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n * TILE_SIZE
    return x, y


def render(lon: float, lat: float, zoom: int = 16, width: int = 500, height: int = 280) -> bytes | None:
    """Best-effort - returns PNG bytes centered on (lon, lat) with a marker,
    or None on any failure (network, tile fetch). See module docstring for
    why this doesn't raise."""
    try:
        center_x, center_y = _lonlat_to_pixel(lon, lat, zoom)
        left, top = center_x - width / 2, center_y - height / 2

        tile_x_min, tile_y_min = int(left // TILE_SIZE), int(top // TILE_SIZE)
        tile_x_max = int((left + width) // TILE_SIZE)
        tile_y_max = int((top + height) // TILE_SIZE)

        canvas = Image.new(
            "RGB",
            ((tile_x_max - tile_x_min + 1) * TILE_SIZE, (tile_y_max - tile_y_min + 1) * TILE_SIZE),
        )
        for tx in range(tile_x_min, tile_x_max + 1):
            for ty in range(tile_y_min, tile_y_max + 1):
                resp = requests.get(
                    f"https://tile.openstreetmap.org/{zoom}/{tx}/{ty}.png",
                    headers={"User-Agent": USER_AGENT},
                    timeout=TIMEOUT,
                )
                resp.raise_for_status()
                tile_img = Image.open(io.BytesIO(resp.content))
                canvas.paste(tile_img, ((tx - tile_x_min) * TILE_SIZE, (ty - tile_y_min) * TILE_SIZE))

        crop_left = int(left - tile_x_min * TILE_SIZE)
        crop_top = int(top - tile_y_min * TILE_SIZE)
        cropped = canvas.crop((crop_left, crop_top, crop_left + width, crop_top + height))

        draw = ImageDraw.Draw(cropped)
        cx, cy, r = width // 2, height // 2, 8
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(214, 39, 40), outline=(255, 255, 255), width=2)

        buf = io.BytesIO()
        cropped.save(buf, format="PNG")
        return buf.getvalue()
    except Exception as e:
        log.warning("Static map render failed for (%s, %s): %s", lon, lat, e)
        return None
