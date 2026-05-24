"""OpenAI API provider adapter."""

from __future__ import annotations

import os

from .base import GenerationRequest, GenerationResponse
from .errors import ProviderNotConfiguredError


class OpenAIProvider:
    """Adapter for the OpenAI API."""

    @property
    def name(self) -> str:
        return "openai"

    @property
    def requires_api_key(self) -> bool:
        return True

    @property
    def api_key_env_var(self) -> str:
        return "OPENAI_API_KEY"

    def is_available(self) -> bool:
        return bool(os.environ.get(self.api_key_env_var))

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        if not self.is_available():
            raise ProviderNotConfiguredError(
                f"{self.api_key_env_var} not set"
            )
        # Real implementation would call openai.ChatCompletion.create()
        # This is the adapter skeleton — no live calls during build/test
        raise NotImplementedError(
            "Live OpenAI calls require explicit user action"
        )
