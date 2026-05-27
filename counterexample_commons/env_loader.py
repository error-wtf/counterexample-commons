"""Secret-safe local environment loading for the app."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROVIDER_ENV_VARS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "google_gemini": "GEMINI_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "ollama_cloud": "OLLAMA_API_KEY",
}


@dataclass(frozen=True)
class EnvironmentStatus:
    """Secret-free environment status."""

    repo_root: Path
    local_env_file: str
    providers: dict[str, str]

    @property
    def any_provider_configured(self) -> bool:
        """Return True if at least one provider key is present."""
        return any(v == "CONFIGURED" for v in self.providers.values())


def find_repo_root(start: Path | None = None) -> Path:
    """Find this repository root without searching sibling repositories."""
    current = (start or Path(__file__)).resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        if (candidate / "pyproject.toml").exists():
            return candidate
    raise RuntimeError("Repository root not found")


def load_local_env(repo_root: Path | None = None) -> EnvironmentStatus:
    """Load a root-local .env file without exposing any values."""
    root = find_repo_root(repo_root)
    env_path = root / ".env"
    local_env_file = "FOUND" if env_path.exists() else "NOT_FOUND"
    if env_path.exists():
        load_dotenv(env_path, override=False)

    providers = {
        name: ("CONFIGURED" if os.environ.get(var) else "NOT_CONFIGURED")
        for name, var in PROVIDER_ENV_VARS.items()
    }
    return EnvironmentStatus(
        repo_root=root,
        local_env_file=local_env_file,
        providers=providers,
    )
