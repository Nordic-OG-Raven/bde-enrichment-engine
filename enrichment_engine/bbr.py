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
from enrichment_engine.models import BuildingProfile, Unit

log = logging.getLogger(__name__)

BBR_REST = "https://services.datafordeler.dk/BBR/BBRPublic/1/REST"
MAX_RETRIES = 3


def _fetch(endpoint: str, filter_params: dict[str, str]) -> list[dict]:
    """filter_params are endpoint-specific - BBR's REST filter fields differ
    per entity (confirmed via live testing: Bygning accepts `husnummer`,
    Enhed rejects it with "400 Parameter: husnummer unrecognized. Did you
    mean: id?" and needs `bygning` - the building's id_lokalId - instead)."""
    params = {"username": BBR_USERNAME, "password": BBR_PASSWORD, **filter_params}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(f"{BBR_REST}/{endpoint}", params=params, timeout=30)
        except requests.RequestException as e:
            raise BBRLookupError(f"BBR {endpoint} request failed for {filter_params}: {e}") from e

        if resp.status_code == 429:
            wait = float(resp.headers.get("Retry-After", 2))
            log.warning("BBR rate limited (attempt %d/%d), waiting %.1fs", attempt, MAX_RETRIES, wait)
            time.sleep(wait)
            continue

        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            raise BBRLookupError(f"BBR {endpoint} returned {resp.status_code} for {filter_params}: {e}") from e

        return resp.json()

    raise BBRLookupError(f"BBR {endpoint} still rate limiting after {MAX_RETRIES} retries for {filter_params}")


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _pick_current(records: list[dict], year_field: str, area_field: str) -> dict | None:
    """BBR returns full registration history per record, not just the current
    state. Prefer status == 6 ("opført" / constructed-current, per BBR
    Instruks - see codelists.py). Fall back to the record with populated
    year/area fields and the most recent registreringFra when no status-6
    record exists. See docs/reviews/2026-08-17-engine-v1-review.md, finding 5:
    this is a best-effort heuristic, not a fully verified complete mapping."""
    if not records:
        return None

    current_status = [r for r in records if r.get("status") == codelists.STATUS_CURRENT]
    candidates = current_status or records

    def sort_key(r: dict) -> tuple:
        has_year = r.get(year_field) is not None
        has_area = r.get(area_field) is not None
        timestamp = _parse_timestamp(r.get("registreringFra")) or datetime.min
        return (has_year, has_area, timestamp)

    return max(candidates, key=sort_key)


def _pick_current_per_unit(records: list[dict]) -> list[dict]:
    """Same current-record logic as _pick_current, but applied per distinct
    unit (grouped by id_lokalId) since a building can have many units and we
    want the current state of each, not just one overall winner."""
    by_unit_id: dict[str, list[dict]] = {}
    for r in records:
        by_unit_id.setdefault(r.get("id_lokalId", ""), []).append(r)

    current = []
    for unit_records in by_unit_id.values():
        picked = _pick_current(unit_records, "enh027ArealTilBeboelse", "enh026EnhedensSamledeAreal")
        if picked:
            current.append(picked)
    return current


def lookup(husnummer: str) -> BuildingProfile | None:
    records = _fetch("Bygning", {"husnummer": husnummer})
    record = _pick_current(records, "byg026Opførelsesår", "byg038SamletBygningsareal")
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


def lookup_units(husnummer: str) -> list[Unit]:
    """Enhed doesn't accept a husnummer filter (confirmed via live test - BBR
    returns "400 Parameter: husnummer unrecognized"), only `bygning` (the
    building's id_lokalId). An address can have multiple Bygning records
    (registration history / distinct structures at one address), and only
    some of those ids have linked Enhed records - querying every building id
    and combining non-empty results is the only reliable way to get all
    units without guessing which one "counts"."""
    building_records = _fetch("Bygning", {"husnummer": husnummer})
    building_ids = {r.get("id_lokalId") for r in building_records if r.get("id_lokalId")}

    all_records: list[dict] = []
    for building_id in building_ids:
        all_records.extend(_fetch("Enhed", {"bygning": building_id}))

    current = _pick_current_per_unit(all_records)

    units = []
    for record in current:
        use_code = record.get("enh020EnhedensAnvendelse")
        units.append(
            Unit(
                bbr_unit_id=record.get("id_lokalId", ""),
                use_code=use_code,
                use_label=codelists.decode(codelists.USE_CODE, use_code),
                living_area_sqm=record.get("enh027ArealTilBeboelse"),
                total_area_sqm=record.get("enh026EnhedensSamledeAreal"),
                num_rooms=record.get("enh031AntalVærelser"),
            )
        )
    return units
