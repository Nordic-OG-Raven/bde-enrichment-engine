"""
Resolves a free-text Danish address to an adgangsadresse ID via the free,
unauthenticated Dataforsyningen address API. That ID is what BBR calls
"husnummer" and is the join key into the BBR endpoints in bbr.py.
"""

import logging

import requests

from enrichment_engine.exceptions import AddressLookupError, AddressNotFoundError
from enrichment_engine.models import ResolvedAddress

log = logging.getLogger(__name__)

ADDRESS_API = "https://api.dataforsyningen.dk/adresser"


def resolve(query: str) -> ResolvedAddress:
    """Raises AddressNotFoundError if nothing matches, AddressLookupError on
    a request failure. Never returns None - callers can rely on either
    getting a ResolvedAddress or an exception, not a mix of both."""
    log.info("Resolving address: %r", query)
    try:
        resp = requests.get(ADDRESS_API, params={"q": query, "per_side": 5}, timeout=10)
        resp.raise_for_status()
        results = resp.json()
    except requests.RequestException as e:
        raise AddressLookupError(f"Address API request failed for {query!r}: {e}") from e

    if not results:
        log.warning("No address match for: %r", query)
        raise AddressNotFoundError(f"No address found matching {query!r}")

    match = results[0]
    adgangsadresse = match["adgangsadresse"]
    koordinater = (adgangsadresse.get("adgangspunkt") or {}).get("koordinater")
    lon, lat = koordinater if koordinater else (None, None)

    # Multiple results are normal for a multi-unit building - /adresser returns
    # one row per floor/door, all sharing the same adgangsadresse (building).
    # Only genuinely ambiguous if they point at *different* buildings.
    distinct_buildings = {r["adgangsadresse"]["id"] for r in results}
    ambiguous = len(distinct_buildings) > 1

    if ambiguous:
        log.warning("Ambiguous address query %r - %d candidates, using top match", query, len(results))

    return ResolvedAddress(
        query=query,
        display_name=adgangsadresse["adressebetegnelse"],
        adgangsadresse_id=adgangsadresse["id"],
        kommunekode=adgangsadresse["kommune"]["kode"],
        postnummer=adgangsadresse["postnummer"]["nr"],
        vejnavn=adgangsadresse["vejstykke"]["navn"],
        husnr=adgangsadresse["husnr"],
        lon=lon,
        lat=lat,
        ambiguous=ambiguous,
    )
