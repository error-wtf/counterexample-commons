"""Extract candidate coordinate JSON from raw model output."""

from __future__ import annotations

import json
import re
from typing import Any


def extract_candidate_coordinates(
    raw_text: str,
) -> dict[str, Any] | None:
    """Attempt to extract a JSON coordinate list from raw model text.

    Looks for a JSON array of [x, y] pairs, or a JSON object with a
    "points" key containing such an array.

    Returns parsed dict/list on success, None on failure.
    """
    # Try to find a JSON code block first
    code_blocks = re.findall(
        r"```(?:json)?\s*\n(.*?)```",
        raw_text,
        re.DOTALL,
    )

    candidates = list(code_blocks)
    # Also try the raw text itself
    candidates.append(raw_text)

    for text in candidates:
        text = text.strip()
        try:
            parsed = json.loads(text)
            if _is_valid_candidate(parsed):
                return (
                    parsed if isinstance(parsed, dict)
                    else {"points": parsed}
                )
        except (json.JSONDecodeError, ValueError):
            continue

    # Try to find any JSON array in the text
    array_match = re.search(
        r"\[\s*\[.*?\]\s*\]",
        raw_text,
        re.DOTALL,
    )
    if array_match:
        try:
            parsed = json.loads(array_match.group())
            if _is_valid_candidate(parsed):
                return {"points": parsed}
        except (json.JSONDecodeError, ValueError):
            pass

    return None


def _is_valid_candidate(data: Any) -> bool:
    """Check if data looks like a coordinate candidate."""
    if isinstance(data, list):
        return (
            len(data) > 0
            and all(
                isinstance(p, (list, tuple)) and len(p) == 2
                for p in data
            )
        )
    if isinstance(data, dict) and "points" in data:
        return _is_valid_candidate(data["points"])
    return False
