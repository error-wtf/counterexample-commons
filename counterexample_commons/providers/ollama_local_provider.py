"""Ollama Local provider adapter — no API key required."""

from __future__ import annotations

from .base import GenerationRequest, GenerationResponse


class OllamaLocalProvider:
    """Adapter for local Ollama instance at localhost:11434."""

    def __init__(
        self, base_url: str = "http://localhost:11434"
    ) -> None:
        self._base_url = base_url

    @property
    def name(self) -> str:
        return "ollama_local"

    @property
    def requires_api_key(self) -> bool:
        return False

    @property
    def api_key_env_var(self) -> str:
        return ""

    def is_available(self) -> bool:
        # In a real implementation, this would ping the local server.
        # We don't make network calls during import or test.
        return False

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        raise NotImplementedError(
            "Live Ollama Local calls require explicit user action"
        )
