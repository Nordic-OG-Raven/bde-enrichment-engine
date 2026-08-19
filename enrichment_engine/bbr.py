"""
BBR (Bygnings- og Boligregistret) single-address lookup via Datafordeler's
BBR GraphQL API (graphql.datafordeler.dk/BBR/v3), using our own dedicated
API-key - not the legacy REST endpoint / shared aarhus_re tjenestebruger
credential. Migrated 2026-08-19; see docs/implementation-log.md for the
discovery process (bitemporal `registreringstid` argument required, `where:`
filter-input shape rather than flat arguments, æ/ø/å transliterated to
ae/oe/aa in field names, `Enhed` needs a `bygning` filter same as REST did -
`husnummer` isn't accepted there).
"""

import logging
import time
from datetime import datetime, timezone

import requests

from enrichment_engine import codelists
from enrichment_engine.config import DATAFORDELER_API_KEY
from enrichment_engine.exceptions import BBRLookupError
from enrichment_engine.models import BuildingProfile, Unit

log = logging.getLogger(__name__)

BBR_GRAPHQL = "https://graphql.datafordeler.dk/BBR/v3"
MAX_RETRIES = 3

BYGNING_FIELDS = """
    id_lokalId status registreringFra
    byg021BygningensAnvendelse byg026Opfoerelsesaar
    byg032YdervaeggensMateriale byg033Tagdaekningsmateriale
    byg038SamletBygningsareal byg041BebyggetAreal byg054AntalEtager
    byg056Varmeinstallation
"""

ENHED_FIELDS = """
    id_lokalId status registreringFra
    enh020EnhedensAnvendelse enh026EnhedensSamledeAreal
    enh027ArealTilBeboelse enh031AntalVaerelser
"""

BYGNING_QUERY = f"""
query($husnummer: String!, $now: DafDateTime!) {{
  BBR_Bygning(first: 200, registreringstid: $now, where: {{husnummer: {{eq: $husnummer}}}}) {{
    edges {{ node {{ {BYGNING_FIELDS} }} }}
  }}
}}
"""

# Page size matters more here than for Bygning: a single building's Enhed
# history is (units x registration-history-rows-per-unit), which adds up fast
# - a 13-unit building had 81 rows. Confirmed live that first:50 silently
# truncated to 9 of 13 real units with no error or warning, just missing
# data. 500 has real headroom above that, but a large enough building could
# still in principle exceed it - if unit counts ever look suspiciously low
# for a big property, this is the first thing to check.
ENHED_QUERY = f"""
query($bygning: String!, $now: DafDateTime!) {{
  BBR_Enhed(first: 500, registreringstid: $now, where: {{bygning: {{eq: $bygning}}}}) {{
    edges {{ node {{ {ENHED_FIELDS} }} }}
  }}
}}
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _query(query: str, variables: dict) -> dict:
    params = {"apiKey": DATAFORDELER_API_KEY}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(
                BBR_GRAPHQL, params=params, json={"query": query, "variables": variables}, timeout=30
            )
        except requests.RequestException as e:
            raise BBRLookupError(f"BBR GraphQL request failed for {variables}: {e}") from e

        if resp.status_code == 429:
            wait = float(resp.headers.get("Retry-After", 2))
            log.warning("BBR GraphQL rate limited (attempt %d/%d), waiting %.1fs", attempt, MAX_RETRIES, wait)
            time.sleep(wait)
            continue

        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            raise BBRLookupError(f"BBR GraphQL returned {resp.status_code} for {variables}: {e}") from e

        body = resp.json()
        if "errors" in body:
            raise BBRLookupError(f"BBR GraphQL returned errors for {variables}: {body['errors']}")
        return body["data"]

    raise BBRLookupError(f"BBR GraphQL still rate limiting after {MAX_RETRIES} retries for {variables}")


def _fetch_buildings(husnummer: str) -> list[dict]:
    data = _query(BYGNING_QUERY, {"husnummer": husnummer, "now": _now()})
    return [edge["node"] for edge in data["BBR_Bygning"]["edges"]]


def _fetch_units(building_id: str) -> list[dict]:
    data = _query(ENHED_QUERY, {"bygning": building_id, "now": _now()})
    return [edge["node"] for edge in data["BBR_Enhed"]["edges"]]


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
    records = _fetch_buildings(husnummer)
    record = _pick_current(records, "byg026Opfoerelsesaar", "byg038SamletBygningsareal")
    if record is None:
        log.info("No BBR building found for husnummer %s", husnummer)
        return None

    use_code = record.get("byg021BygningensAnvendelse")
    wall_material = record.get("byg032YdervaeggensMateriale")
    roof_material = record.get("byg033Tagdaekningsmateriale")
    heating_type = record.get("byg056Varmeinstallation")

    return BuildingProfile(
        bbr_building_id=record.get("id_lokalId", ""),
        use_code=use_code,
        use_label=codelists.decode(codelists.USE_CODE, use_code),
        year_built=record.get("byg026Opfoerelsesaar"),
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
    """BBR_Enhed doesn't accept a husnummer filter (same limitation as REST
    had), only `bygning` (the building's id_lokalId). An address can have
    multiple Bygning records (registration history / distinct structures at
    one address), and only some of those ids have linked Enhed records -
    querying every building id and combining non-empty results is the only
    reliable way to get all units without guessing which one "counts"."""
    building_records = _fetch_buildings(husnummer)
    building_ids = {r.get("id_lokalId") for r in building_records if r.get("id_lokalId")}

    all_records: list[dict] = []
    for building_id in building_ids:
        all_records.extend(_fetch_units(building_id))

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
                num_rooms=record.get("enh031AntalVaerelser"),
            )
        )
    return units
