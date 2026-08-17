"""Manual test: python scripts/lookup_address.py Ryesgade 1, 8000 Aarhus"""

import logging
import sys
from pathlib import Path
from pprint import pprint

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enrichment_engine.engine import property_profile
from enrichment_engine.exceptions import EnrichmentError

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    query = " ".join(sys.argv[1:]) or "Ryesgade 1, 8000 Aarhus"
    try:
        profile = property_profile(query)
    except EnrichmentError as e:
        print(f"Lookup failed: {e}")
        sys.exit(1)

    pprint(profile)
