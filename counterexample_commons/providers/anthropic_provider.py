"""Anthropic Claude API provider adapter."""

from __future__ import annotations

import os

from .base import GenerationRequest, GenerationResponse
from .errors import ProviderNotConfiguredError
from .http_json import anthropic_text, post_json


class AnthropicProvider:
    """Adapter for the Anthropic Claude API."""

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def requires_api_key(self) -> bool:
        return True

    @property
    def api_key_env_var(self) -> str:
        return "ANTHROPIC_API_KEY"

    def is_available(self) -> bool:
        return bool(os.environ.get(self.api_key_env_var))

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        if not self.is_available():
            raise ProviderNotConfiguredError(
                f"{self.api_key_env_var} not set"
            )
        data = post_json(
            "https://api.anthropic.com/v1/messages",
            {
                "x-api-key": os.environ[self.api_key_env_var],
                "anthropic-version": "2023-06-01",
            },
            {
                "model": request.model,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "messages": [
                    {"role": "user", "content": request.prompt},
                ],
            },
        )
        return GenerationResponse(
            provider_name=self.name,
            model=request.model,
            raw_text=anthropic_text(data),
            finish_reason=str(data.get("stop_reason", "unknown")),
            usage=data.get("usage", {}),
        )
