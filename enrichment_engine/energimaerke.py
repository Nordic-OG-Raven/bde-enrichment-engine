"""
Energy certificate (energimærke) lookup via tjekenergimaerke.emoweb.dk.

NOT an official Datafordeler/Energistyrelsen API - the sanctioned path
(EMOData) requires a separate approval request to sparenergi@ens.dk (see
docs/implementation-log.md, 2026-08-17). This instead scrapes the public
search form the same way the aarhus_re project already validated
(src/data/collectors/energy_labels.py) - a 2-step GET (CSRF token) + POST,
no auth. Live-retested 2026-08-17: still works, same HTML column layout.

Because this is an unofficial, unsanctioned-format source (liable to break
if emoweb.dk changes their markup) rather than a documented API like BBR,
failures here are treated as "no data available" (return None, log a
warning) rather than raising - a broken scrape shouldn't take down the rest
of the property profile.
"""

import logging

import requests
from bs4 import BeautifulSoup

from enrichment_engine.models import EnergyLabel

log = logging.getLogger(__name__)

BASE_URL = "https://tjekenergimaerke.emoweb.dk"
TIMEOUT = 15


def _get_token(sess: requests.Session) -> str | None:
    resp = sess.get(f"{BASE_URL}/", timeout=TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    token_input = soup.find("input", {"name": "__RequestVerificationToken"})
    return token_input["value"] if token_input else None


def _parse_results(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"id": "singleDataTable"})
    if not table:
        return []
    tbody = table.find("tbody")
    if not tbody:
        return []

    rows = []
    for tr in tbody.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 11:
            continue
        rows.append(
            {
                "energy_class": tds[5].text.strip(),
                "energimaerkenr": tds[6].text.strip(),
                "valid_from": tds[7].text.strip(),
                "valid_to": tds[8].text.strip(),
                "is_historic": "historic-entry" in tr.get("class", []),
            }
        )
    return rows


def lookup(vejnavn: str, husnr: str, postnummer: str) -> EnergyLabel | None:
    """Best-effort - returns None on any failure (network, parsing, no
    result) rather than raising. See module docstring for why."""
    try:
        sess = requests.Session()
        token = _get_token(sess)
        if token is None:
            log.warning("Energy label lookup: CSRF token not found on %s", BASE_URL)
            return None

        resp = sess.post(
            f"{BASE_URL}/?handler=SingleSearch",
            data={
                "StreetName": vejnavn,
                "HouseNumber": husnr,
                "PostalCode": postnummer,
                "Floor": "",
                "SideOrDoor": "",
                "__RequestVerificationToken": token,
            },
            headers={"Origin": BASE_URL, "Referer": f"{BASE_URL}/"},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        results = _parse_results(resp.text)
    except requests.RequestException as e:
        log.warning("Energy label lookup failed for %s %s, %s: %s", vejnavn, husnr, postnummer, e)
        return None

    if not results:
        return None

    # Prefer a current (non-historic) certificate; fall back to most recent historic.
    current = next((r for r in results if not r["is_historic"]), results[0])
    return EnergyLabel(**current)
