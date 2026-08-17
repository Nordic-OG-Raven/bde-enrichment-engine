class EnrichmentError(Exception):
    """Base class for all enrichment_engine errors."""


class AddressLookupError(EnrichmentError):
    """The address API request itself failed (network, HTTP error, etc)."""


class AddressNotFoundError(EnrichmentError):
    """The address API responded fine but found no matching address."""


class BBRLookupError(EnrichmentError):
    """The BBR API request failed after retries."""
