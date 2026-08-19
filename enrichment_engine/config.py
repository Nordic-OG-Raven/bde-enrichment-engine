import logging
import os

from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable {name}. "
            f"Copy .env.example to .env and fill in real values."
        )
    return value


DATAFORDELER_API_KEY = _require_env("DATAFORDELER_API_KEY")
# Diagnostic only - confirms the *value* actually loaded matches expectations
# without logging the full secret. Added 2026-08-19 to rule out a stale/wrong
# secret value as the cause of deployed-only 401s, as distinct from a genuine
# IP restriction - see docs/implementation-log.md. Safe to remove once that's
# settled either way.
log.info(
    "DATAFORDELER_API_KEY loaded: length=%d prefix=%s suffix=%s",
    len(DATAFORDELER_API_KEY), DATAFORDELER_API_KEY[:6], DATAFORDELER_API_KEY[-6:],
)

# Legacy tjenestebruger credential, shared with the aarhus_re project. As of
# 2026-08-19 only bfe.py still depends on this (DAR_BFE_Public REST service -
# no GraphQL equivalent found yet, not chased down since bfe.py is a small,
# already-best-effort component). bbr.py no longer needs these - migrated to
# GraphQL via DATAFORDELER_API_KEY above. See docs/implementation-log.md.
BBR_USERNAME = _require_env("BBR_USERNAME")
BBR_PASSWORD = _require_env("BBR_PASSWORD")
