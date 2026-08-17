"""
BBR (Bygnings- og Boligregistret) single-address lookup via Datafordeler's
BBR REST API. Auth: tjenestebruger username/password as query params (NOT
HTTP Basic Auth - returns 403). See docs/implementation-log.md, 2026-08-17.
"""

import requests

from enrichment_engine.config import BBR_PASSWORD, BBR_USERNAME
from enrichment_engine.models import BuildingProfile

BBR_REST = "https://services.datafordeler.dk/BBR/BBRPublic/1/REST"


def _fetch_buildings_by_husnummer(husnummer: str) -> list[dict]:
    resp = requests.get(
        f"{BBR_REST}/Bygning",
        params={"username": BBR_USERNAME, "password": BBR_PASSWORD, "husnummer": husnummer},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _pick_current(records: list[dict]) -> dict | None:
    """BBR returns full registration history per building, not just the
    current state. Heuristic: prefer records with a populated year-built
    and area, then the most recently registered."""
    if not records:
        return None

    def sort_key(r: dict) -> tuple:
        has_year = r.get("byg026Opførelsesår") is not None
        has_area = r.get("byg038SamletBygningsareal") is not None
        return (has_year, has_area, r.get("registreringFra", ""))

    return max(records, key=sort_key)


def lookup(husnummer: str) -> BuildingProfile | None:
    records = _fetch_buildings_by_husnummer(husnummer)
    record = _pick_current(records)
    if record is None:
        return None

    return BuildingProfile(
        bbr_building_id=record.get("id_lokalId", ""),
        use_code=record.get("byg021BygningensAnvendelse"),
        year_built=record.get("byg026Opførelsesår"),
        wall_material=record.get("byg032YdervæggensMateriale"),
        roof_material=record.get("byg033Tagdækningsmateriale"),
        total_area_sqm=record.get("byg038SamletBygningsareal"),
        footprint_sqm=record.get("byg041BebyggetAreal"),
        floors=record.get("byg054AntalEtager"),
        heating_type=record.get("byg056Varmeinstallation"),
        registered_from=record.get("registreringFra"),
    )
