from enrichment_engine import address, bbr
from enrichment_engine.models import PropertyProfile


def property_profile(address_query: str) -> PropertyProfile | None:
    resolved = address.resolve(address_query)
    if resolved is None:
        return None

    building = bbr.lookup(resolved.adgangsadresse_id)
    return PropertyProfile(address=resolved, building=building)
