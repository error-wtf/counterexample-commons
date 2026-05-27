"""Google Gemini API provider adapter."""

from __future__ import annotations

import os
from urllib.parse import quote

from .base import GenerationRequest, GenerationResponse
from .errors import ProviderNotConfiguredError
from .http_json import gemini_text, post_json


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
        model = quote(request.model, safe="")
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key="
            f"{os.environ[self.api_key_env_var]}"
        )
        data = post_json(
            url,
            {},
            {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": request.prompt}],
                    },
                ],
                "generationConfig": {
                    "temperature": request.temperature,
                    "maxOutputTokens": request.max_tokens,
                },
            },
        )
        return GenerationResponse(
            provider_name=self.name,
            model=request.model,
            raw_text=gemini_text(data),
            finish_reason="unknown",
            usage=data.get("usageMetadata", {}),
        )
