"""Provider comparison — tabulate results across providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ComparisonEntry:
    """One provider's result in a comparison run."""
    provider: str
    model: str
    n_points: int
    actual_edges: int
    status: str
    raw_length: int


def build_comparison_table(
    entries: list[ComparisonEntry],
) -> list[dict[str, Any]]:
    """Build a comparison table from entries."""
    return [
        {
            "provider": e.provider,
            "model": e.model,
            "n_points": e.n_points,
            "actual_edges": e.actual_edges,
            "status": e.status,
            "raw_response_chars": e.raw_length,
        }
        for e in entries
    ]
