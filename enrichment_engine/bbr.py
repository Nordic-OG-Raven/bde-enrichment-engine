"""
BBR (Bygnings- og Boligregistret) single-address lookup via Datafordeler's
BBR REST API. Auth: tjenestebruger username/password as query params (NOT
HTTP Basic Auth - returns 403). See docs/implementation-log.md, 2026-08-17.
"""

import logging
import time
from datetime import datetime

import requests

from enrichment_engine import codelists
from enrichment_engine.config import BBR_PASSWORD, BBR_USERNAME
from enrichment_engine.exceptions import BBRLookupError
from enrichment_engine.models import BuildingProfile

log = logging.getLogger(__name__)

BBR_REST = "https://services.datafordeler.dk/BBR/BBRPublic/1/REST"
MAX_RETRIES = 3


def _fetch_buildings_by_husnummer(husnummer: str) -> list[dict]:
    params = {"username": BBR_USERNAME, "password": BBR_PASSWORD, "husnummer": husnummer}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(f"{BBR_REST}/Bygning", params=params, timeout=30)
        except requests.RequestException as e:
            raise BBRLookupError(f"BBR request failed for husnummer {husnummer}: {e}") from e

        if resp.status_code == 429:
            wait = float(resp.headers.get("Retry-After", 2))
            log.warning("BBR rate limited (attempt %d/%d), waiting %.1fs", attempt, MAX_RETRIES, wait)
            time.sleep(wait)
            continue

        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            raise BBRLookupError(f"BBR returned {resp.status_code} for husnummer {husnummer}: {e}") from e

        return resp.json()

    raise BBRLookupError(f"BBR still rate limiting after {MAX_RETRIES} retries for husnummer {husnummer}")


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _pick_current(records: list[dict]) -> dict | None:
    """BBR returns full registration history per building, not just the
    current state. Prefer status == 6 ("opført" / constructed-current, per
    BBR Instruks - see codelists.py). Fall back to the record with populated
    year/area fields and the most recent registreringFra when no status-6
    record exists. See docs/reviews/2026-08-17-engine-v1-review.md, finding 5:
    this is a best-effort heuristic, not a fully verified complete mapping."""
    if not records:
        return None

    current_status = [r for r in records if r.get("status") == codelists.STATUS_CURRENT]
    candidates = current_status or records

    def sort_key(r: dict) -> tuple:
        has_year = r.get("byg026Opførelsesår") is not None
        has_area = r.get("byg038SamletBygningsareal") is not None
        timestamp = _parse_timestamp(r.get("registreringFra")) or datetime.min
        return (has_year, has_area, timestamp)

    return max(candidates, key=sort_key)


def lookup(husnummer: str) -> BuildingProfile | None:
    records = _fetch_buildings_by_husnummer(husnummer)
    record = _pick_current(records)
    if record is None:
        log.info("No BBR building found for husnummer %s", husnummer)
        return None

    use_code = record.get("byg021BygningensAnvendelse")
    wall_material = record.get("byg032YdervæggensMateriale")
    roof_material = record.get("byg033Tagdækningsmateriale")
    heating_type = record.get("byg056Varmeinstallation")

    return BuildingProfile(
        bbr_building_id=record.get("id_lokalId", ""),
        use_code=use_code,
        use_label=codelists.decode(codelists.USE_CODE, use_code),
        year_built=record.get("byg026Opførelsesår"),
        wall_material=wall_material,
        wall_material_label=codelists.decode(codelists.WALL_MATERIAL, wall_material),
        roof_material=roof_material,
        roof_material_label=codelists.decode(codelists.ROOF_MATERIAL, roof_material),
        total_area_sqm=record.get("byg038SamletBygningsareal"),
        footprint_sqm=record.get("byg041BebyggetAreal"),
        floors=record.get("byg054AntalEtager"),
        heating_type=heating_type,
        heating_type_label=codelists.decode(codelists.HEATING_TYPE, heating_type),
        registered_from=record.get("registreringFra"),
    )
