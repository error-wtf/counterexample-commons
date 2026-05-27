"""Ollama Cloud API provider adapter."""

from __future__ import annotations

import os

from .base import GenerationRequest, GenerationResponse
from .errors import ProviderNotConfiguredError
from .ollama_local_provider import OllamaLocalProvider


class OllamaCloudProvider:
    """Adapter for hosted Ollama Cloud API."""

    @property
    def name(self) -> str:
        return "ollama_cloud"

    @property
    def requires_api_key(self) -> bool:
        return True

    @property
    def api_key_env_var(self) -> str:
        return "OLLAMA_API_KEY"

    def is_available(self) -> bool:
        return bool(os.environ.get(self.api_key_env_var))

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        if not self.is_available():
            raise ProviderNotConfiguredError(
                f"{self.api_key_env_var} not set"
            )
        base_url = os.environ.get(
            "OLLAMA_CLOUD_BASE_URL",
            "https://ollama.com",
        )
        # Hosted Ollama-compatible endpoints vary by account. Use the same
        # request shape as local Ollama and rely on sanitized failures.
        return OllamaLocalProvider(base_url).generate(request)
