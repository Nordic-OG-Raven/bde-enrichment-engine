import logging

from enrichment_engine import address, bbr
from enrichment_engine.models import PropertyProfile

log = logging.getLogger(__name__)


def property_profile(address_query: str) -> PropertyProfile:
    """Raises AddressNotFoundError / AddressLookupError / BBRLookupError -
    callers should catch these rather than check for None. building=None on
    the returned profile specifically means "address exists, no BBR record",
    which is a different situation from "address not found" and is worth
    displaying differently to a user."""
    resolved = address.resolve(address_query)
    building = bbr.lookup(resolved.adgangsadresse_id)
    units = bbr.lookup_units(resolved.adgangsadresse_id)
    log.info(
        "Profile built for %r: building_found=%s, units=%d",
        address_query, building is not None, len(units),
    )
    return PropertyProfile(address=resolved, building=building, units=units)
