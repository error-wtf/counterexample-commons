"""Google Gemini API provider adapter."""

from __future__ import annotations

import os

from .base import GenerationRequest, GenerationResponse
from .errors import ProviderNotConfiguredError


class GoogleGeminiProvider:
    """Adapter for the Google Gemini API."""

    @property
    def name(self) -> str:
        return "google_gemini"

    @property
    def requires_api_key(self) -> bool:
        return True

    @property
    def api_key_env_var(self) -> str:
        return "GEMINI_API_KEY"

    def is_available(self) -> bool:
        return bool(os.environ.get(self.api_key_env_var))

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        if not self.is_available():
            raise ProviderNotConfiguredError(
                f"{self.api_key_env_var} not set"
            )
        raise NotImplementedError(
            "Live Gemini calls require explicit user action"
        )
