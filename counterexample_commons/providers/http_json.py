"""Small secret-safe JSON HTTP helpers for provider adapters."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from .errors import ProviderConnectionError, ProviderResponseError


def post_json(
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any],
    timeout: int = 60,
) -> dict[str, Any]:
    """POST JSON and return parsed JSON without leaking headers."""
    data = json.dumps(payload).encode("utf-8")
    safe_headers = {
        "Content-Type": "application/json",
        **headers,
    }
    request = urllib.request.Request(
        url,
        data=data,
        headers=safe_headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise ProviderConnectionError(
            f"HTTP_{exc.code}"
        ) from None
    except urllib.error.URLError as exc:
        reason = exc.reason.__class__.__name__
        raise ProviderConnectionError(f"NETWORK_{reason}") from None
    except TimeoutError:
        raise ProviderConnectionError("NETWORK_TIMEOUT") from None

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ProviderResponseError("INVALID_JSON_RESPONSE") from exc
    if not isinstance(parsed, dict):
        raise ProviderResponseError("NON_OBJECT_JSON_RESPONSE")
    return parsed


def openai_like_chat_text(data: dict[str, Any]) -> str:
    """Extract content text from OpenAI-compatible chat responses."""
    try:
        return str(data["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderResponseError("MISSING_CHAT_CONTENT") from exc


def anthropic_text(data: dict[str, Any]) -> str:
    """Extract content text from Anthropic messages responses."""
    try:
        parts = data["content"]
        return "\n".join(
            str(part.get("text", ""))
            for part in parts
            if part.get("type") == "text"
        )
    except (KeyError, TypeError) as exc:
        raise ProviderResponseError("MISSING_ANTHROPIC_CONTENT") from exc


def gemini_text(data: dict[str, Any]) -> str:
    """Extract content text from Gemini generateContent responses."""
    try:
        parts = data["candidates"][0]["content"]["parts"]
        return "\n".join(str(part.get("text", "")) for part in parts)
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderResponseError("MISSING_GEMINI_CONTENT") from exc
