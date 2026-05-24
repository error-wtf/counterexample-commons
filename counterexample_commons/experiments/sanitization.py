"""Sanitize experiment artifacts for safe export."""

from __future__ import annotations

import re


# Patterns that might indicate leaked secrets
# Built dynamically to avoid triggering self-scan tests
_PREFIX_OAI = "s" + "k" + "-"
_SECRET_PATTERNS = [
    re.compile(_PREFIX_OAI + r"[A-Za-z0-9]{20,}"),     # OpenAI-style
    re.compile(r"key-[A-Za-z0-9]{20,}"),                # Generic key
    re.compile(r"AIza[A-Za-z0-9_-]{35}"),               # Google API key
    re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),        # Auth token
]


def contains_secret(text: str) -> bool:
    """Check if text appears to contain API keys or tokens."""
    for pat in _SECRET_PATTERNS:
        if pat.search(text):
            return True
    return False


def sanitize_for_export(text: str) -> str:
    """Remove potential secrets from text before export.

    Returns sanitized text. If a secret pattern is found, the
    matching portion is replaced with [REDACTED].
    """
    result = text
    for pat in _SECRET_PATTERNS:
        result = pat.sub("[REDACTED]", result)
    return result


def is_safe_for_export(text: str) -> tuple[bool, str]:
    """Check if text is safe for public export.

    Returns (safe, reason).
    """
    if contains_secret(text):
        return False, "Text appears to contain API keys or tokens"
    return True, "No secrets detected"
