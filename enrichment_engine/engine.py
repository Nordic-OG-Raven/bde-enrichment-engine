import logging

from enrichment_engine import address, bbr, bfe, energimaerke, ois
from enrichment_engine.models import PropertyProfile

log = logging.getLogger(__name__)


def _lookup_last_sale(husnummer: str):
    bfe_number = bfe.lookup_bfe(husnummer)
    if bfe_number is None:
        return None
    return ois.lookup_last_sale(bfe_number)


def property_profile(address_query: str) -> PropertyProfile:
    """Raises AddressNotFoundError / AddressLookupError / BBRLookupError -
    callers should catch these rather than check for None. building=None on
    the returned profile specifically means "address exists, no BBR record",
    which is a different situation from "address not found" and is worth
    displaying differently to a user. energy_label and last_sale are
    best-effort (unofficial sources) and are simply None if unavailable -
    see energimaerke.py / bfe.py / ois.py."""
    resolved = address.resolve(address_query)
    building = bbr.lookup(resolved.adgangsadresse_id)
    units = bbr.lookup_units(resolved.adgangsadresse_id)
    energy_label = energimaerke.lookup(resolved.vejnavn, resolved.husnr, resolved.postnummer)
    last_sale = _lookup_last_sale(resolved.adgangsadresse_id)
    log.info(
        "Profile built for %r: building_found=%s, units=%d, energy_label=%s, last_sale=%s",
        address_query, building is not None, len(units), energy_label is not None, last_sale is not None,
    )
    return PropertyProfile(
        address=resolved, building=building, units=units, energy_label=energy_label, last_sale=last_sale,
    )
