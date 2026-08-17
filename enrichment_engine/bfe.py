"""
Resolves a husnummer (adgangsadresse ID) to a BFE number (Bestemt Fast
Ejendom / samlet fast ejendom) via Datafordeler's official DAR_BFE_Public
REST service - same tjenestebruger auth as bbr.py, different service.

The BFE number is the join key into OIS's price lookup (ois.py) - unlike
BBR, this specific hop is small and official, but the overall "price"
feature stays best-effort (returns None rather than raising) since its
other half (ois.py) is an unofficial source and the two are only useful
together.
"""

import logging

import requests

from enrichment_engine.config import BBR_PASSWORD, BBR_USERNAME

log = logging.getLogger(__name__)

BFE_REST = "https://services.datafordeler.dk/DAR/DAR_BFE_Public/1/rest/husnummerTilBygningBfe"
TIMEOUT = 15


def lookup_bfe(husnummer: str) -> int | None:
    """Best-effort - returns None on any failure or if no jordstykke/BFE is
    linked to this husnummer (e.g. genuinely unbuilt land, or a request
    error), rather than raising."""
    try:
        resp = requests.get(
            BFE_REST,
            params={"username": BBR_USERNAME, "password": BBR_PASSWORD, "Format": "JSON", "husnummerId": husnummer},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        log.warning("BFE lookup failed for husnummer %s: %s", husnummer, e)
        return None

    jordstykker = data.get("jordstykkeList") or []
    if not jordstykker:
        return None

    # A husnummer can in principle map to more than one jordstykke; taking
    # the first is a simplification worth revisiting if it ever matters for
    # a real client (see docs/reviews for the same kind of caveat on BBR's
    # _pick_current heuristic).
    bfe = jordstykker[0].get("samletFastEjendom")
    return int(bfe) if bfe is not None else None
