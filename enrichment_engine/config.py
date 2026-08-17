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


BBR_USERNAME = _require_env("BBR_USERNAME")
BBR_PASSWORD = _require_env("BBR_PASSWORD")
