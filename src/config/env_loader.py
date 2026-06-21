from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_ENV_FILE = _PROJECT_ROOT / ".env"


def load_project_env() -> None:
    """Load .env from project root; override shell vars so .env is authoritative."""
    load_dotenv(_ENV_FILE, override=True)
