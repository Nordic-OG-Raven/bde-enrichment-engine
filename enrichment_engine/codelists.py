"""
BBR field codelists, sourced from BBR Instruks (instruks.bbr.dk) and BBR Teknik
(teknik.bbr.dk), 2026-08-17. These are not guaranteed complete - unmapped codes
fall back to a visible placeholder rather than silently disappearing.

Sources:
- byg021 (use):    https://teknik.bbr.dk/kodelister/0/1/0/BygAnvendelse
- byg032 (wall):   https://instruks.bbr.dk/ydervaeggenesmateriale/0/31
- byg033 (roof):   https://instruks.bbr.dk/tagdaekningsmateriale/0/30
- byg056 (heat):   https://instruks.bbr.dk/varmeinstallation1/0/30
"""

USE_CODE = {
    "110": "Stuehus til landbrugsejendom",
    "120": "Fritliggende enfamiliehus",
    "130": "Række-, kæde- eller dobbelthus (udfases)",
    "140": "Etagebolig-bygning, flerfamiliehus eller to-familiehus",
    "150": "Kollegium",
    "160": "Boligbygning til døgninstitution",
    "185": "Anneks i tilknytning til helårsbolig",
    "190": "Anden bygning til helårsbeboelse",
    "320": "Bygning til kontor, handel, lager mv. (udfases)",
    "321": "Bygning til kontor",
    "322": "Bygning til detailhandel",
}

WALL_MATERIAL = {
    "1": "Mursten (tegl, kalksandsten, cementsten)",
    "2": "Letbeton (lette bloksten, gasbeton)",
    "3": "Fibercementplader, herunder asbest",
    "4": "Bindingsværk (udvendigt synligt træværk)",
    "5": "Træbeklædning",
    "6": "Betonelementer",
    "8": "Metalplader",
    "10": "Fibercementplader (asbestfri)",
    "11": "PVC",
    "12": "Glas",
    "90": "Andet materiale",
}

ROOF_MATERIAL = {
    "1": "Built-up (fladt tag)",
    "2": "Tagpap (med taghældning)",
    "3": "Fibercement, herunder asbest",
    "4": "Cementsten",
    "5": "Tegl",
    "6": "Metalplader",
    "7": "Stråtag",
    "10": "Fibercement (asbestfri)",
    "11": "PVC",
    "12": "Glas",
    "90": "Andet",
}

HEATING_TYPE = {
    "1": "Fjernvarme/blokvarme",
    "2": "Centralvarme fra eget anlæg, et-kammer fyr",
    "3": "Ovne",
    "5": "Varmepumpe",
    "6": "Centralvarme med to fyringsenheder",
    "7": "Elovne, elpaneler",
    "8": "Gasradiatorer",
    "9": "Ingen varmeinstallationer",
}

# Confirmed via Datafordeler documentation search: status 6 = "opført"
# (constructed/current). Full 1-9 table not found despite searching BBR's own
# docs - see docs/reviews/2026-08-17-engine-v1-review.md, finding 5.
STATUS_CURRENT = "6"


def decode(codelist: dict[str, str], code: str | None) -> str | None:
    if code is None:
        return None
    return codelist.get(code, f"Ukendt (kode {code})")
