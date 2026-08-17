"""
Most recent sale price lookup via OIS.dk's public SVUR API (Statens Salgs-
og Vurderingsregister - the same authoritative register as EJF, exposed a
much simpler way).

NOT an official/documented API - discovered the same way aarhus_re found it
(src/data/collectors/ois.py, 2026-04-05): reverse-engineered from OIS's own
frontend, no auth beyond a browser-like Referer/User-Agent. Live-retested
2026-08-17 with a real BFE number end-to-end (via bfe.py) - still works,
same response shape. Best-effort like energimaerke.py, for the same reason:
unofficial source, shouldn't be able to break the rest of the page.
"""

import logging
import re

import requests

from enrichment_engine.models import SaleRecord

log = logging.getLogger(__name__)

OIS_BASE = "https://ois.dk/api/svur"
HEADERS = {
    "Referer": "https://ois.dk/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}
TIMEOUT = 15


def _parse_price(raw: str | None) -> int | None:
    """Parses a Danish price string like '28.500.000 DKK' -> 28500000."""
    if not raw:
        return None
    digits = re.sub(r"[^\d]", "", raw)
    return int(digits) if digits else None


def lookup_last_sale(bfe: int) -> SaleRecord | None:
    """Best-effort - returns None on any failure, or if there's no sale on
    record for this BFE (common for e.g. newly subdivided properties)."""
    try:
        resp = requests.get(f"{OIS_BASE}/get", params={"bfe": bfe}, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        log.warning("OIS price lookup failed for BFE %s: %s", bfe, e)
        return None

    senest = data.get("senestSalg")
    if not senest:
        return None

    sale = senest.get("hissalgMain") or {}
    price = _parse_price(sale.get("koebesum_beloeb"))
    date = sale.get("omregnings_dato")
    if price is None or not date:
        return None

    return SaleRecord(
        price_dkk=price,
        sale_date=str(date)[:10],
        sale_type=(sale.get("overdragelses_tekst") or "").strip(),
    )
