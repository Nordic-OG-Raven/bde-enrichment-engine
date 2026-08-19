import os

from dotenv import load_dotenv

load_dotenv()


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable {name}. "
            f"Copy .env.example to .env and fill in real values."
        )
    return value


DATAFORDELER_API_KEY = _require_env("DATAFORDELER_API_KEY")

# Legacy tjenestebruger credential, shared with the aarhus_re project. As of
# 2026-08-19 only bfe.py still depends on this (DAR_BFE_Public REST service -
# no GraphQL equivalent found yet, not chased down since bfe.py is a small,
# already-best-effort component). bbr.py no longer needs these - migrated to
# GraphQL via DATAFORDELER_API_KEY above. See docs/implementation-log.md.
BBR_USERNAME = _require_env("BBR_USERNAME")
BBR_PASSWORD = _require_env("BBR_PASSWORD")
