"""OpenAI API provider adapter."""

from __future__ import annotations

import os

from .base import GenerationRequest, GenerationResponse
from .errors import ProviderNotConfiguredError
from .http_json import openai_like_chat_text, post_json


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
        data = post_json(
            "https://api.openai.com/v1/chat/completions",
            {
                "Authorization": (
                    "Bearer " + os.environ[self.api_key_env_var]
                ),
            },
            {
                "model": request.model,
                "messages": [
                    {"role": "user", "content": request.prompt},
                ],
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
            },
        )
        return GenerationResponse(
            provider_name=self.name,
            model=request.model,
            raw_text=openai_like_chat_text(data),
            finish_reason=str(
                data.get("choices", [{}])[0].get(
                    "finish_reason", "unknown"
                )
            ),
            usage=data.get("usage", {}),
        )
