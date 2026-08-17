"""Manual test: python scripts/lookup_address.py Ryesgade 1, 8000 Aarhus"""

import sys
from pprint import pprint

from enrichment_engine.engine import property_profile

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "Ryesgade 1, 8000 Aarhus"
    profile = property_profile(query)
    pprint(profile)
