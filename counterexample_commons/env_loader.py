"""Secure env loader."""
from pathlib import Path
from dotenv import load_dotenv


def find_repo_root():
    h = Path(__file__).resolve()
    for c in [h.parent, *h.parents]:
        if (c / "pyproject.toml").exists():
            return c
    raise RuntimeError("Repo root not found")


def load_local_env():
    r = find_repo_root()
    d = r / ".env"
    if d.exists():
        load_dotenv(d, override=False)
        return True
    return False
