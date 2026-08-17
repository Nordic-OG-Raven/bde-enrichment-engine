"""
Resolves a free-text Danish address to an adgangsadresse ID via the free,
unauthenticated Dataforsyningen address API. That ID is what BBR calls
"husnummer" and is the join key into the BBR endpoints in bbr.py.
"""

import requests

from enrichment_engine.models import ResolvedAddress

ADDRESS_API = "https://api.dataforsyningen.dk/adresser"


def resolve(query: str) -> ResolvedAddress | None:
    resp = requests.get(ADDRESS_API, params={"q": query, "per_side": 1}, timeout=10)
    resp.raise_for_status()
    results = resp.json()
    if not results:
        return None

    match = results[0]
    adgangsadresse = match["adgangsadresse"]

    return ResolvedAddress(
        query=query,
        display_name=adgangsadresse["adressebetegnelse"],
        adgangsadresse_id=adgangsadresse["id"],
        kommunekode=adgangsadresse["kommune"]["kode"],
        postnummer=adgangsadresse["postnummer"]["nr"],
        vejnavn=adgangsadresse["vejstykke"]["navn"],
        husnr=adgangsadresse["husnr"],
    )
