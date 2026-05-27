"""Ollama Local provider adapter — no API key required."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from .base import GenerationRequest, GenerationResponse
from .errors import ProviderConnectionError, ProviderResponseError


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
        return False

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        payload = json.dumps({
            "model": request.model,
            "prompt": request.prompt,
            "stream": False,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            },
        }).encode("utf-8")
        req = urllib.request.Request(
            self._base_url.rstrip("/") + "/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                body = response.read().decode("utf-8")
        except urllib.error.URLError as exc:
            reason = exc.reason.__class__.__name__
            raise ProviderConnectionError(f"NETWORK_{reason}") from None

        try:
            data = json.loads(body)
            text = str(data["response"])
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise ProviderResponseError("INVALID_OLLAMA_RESPONSE") from exc
        return GenerationResponse(
            provider_name=self.name,
            model=request.model,
            raw_text=text,
            finish_reason=str(data.get("done_reason", "unknown")),
        )
