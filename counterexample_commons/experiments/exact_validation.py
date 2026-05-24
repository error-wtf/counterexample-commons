"""Exact independent validation of AI-generated candidates."""

from __future__ import annotations

from typing import Any

from sympy import Rational

from counterexample_commons.validators.unit_distance import (
    count_unit_edges_exact,
)
from .run_manager import ExperimentStatus


def validate_candidate(
    candidate: dict[str, Any],
    claimed_edge_count: int | None = None,
) -> dict[str, Any]:
    """Validate a candidate point configuration exactly.

    Parameters
    ----------
    candidate : dict with "points" key (list of [x, y] pairs)
    claimed_edge_count : if provided, compare against actual count

    Returns
    -------
    dict with status, actual_edges, details
    """
    points_raw = candidate.get("points", [])

    # Parse to exact rational coordinates
    try:
        points = [
            (Rational(str(p[0])), Rational(str(p[1])))
            for p in points_raw
        ]
    except (ValueError, TypeError, IndexError) as e:
        return {
            "status": ExperimentStatus.FAIL_INVALID_COORDINATES.value,
            "error": f"Cannot parse coordinates: {e}",
            "n": len(points_raw),
        }

    # Duplicate check
    seen = set()
    for i, p in enumerate(points):
        if p in seen:
            return {
                "status": ExperimentStatus.FAIL_INVALID_COORDINATES.value,
                "error": f"Duplicate point at index {i}: {p}",
                "n": len(points),
            }
        seen.add(p)

    # Exact edge count
    actual_count, edges = count_unit_edges_exact(points)

    result: dict[str, Any] = {
        "n": len(points),
        "actual_edges": actual_count,
        "edges": [(i, j) for i, j in edges],
    }

    if claimed_edge_count is not None:
        if actual_count == claimed_edge_count:
            result["status"] = (
                ExperimentStatus
                .PASS_FINITE_CONFIGURATION_VALIDATED
                .value
            )
        else:
            result["status"] = (
                ExperimentStatus
                .FAIL_CLAIMED_COUNT_INCORRECT
                .value
            )
            result["claimed_edges"] = claimed_edge_count
    else:
        result["status"] = (
            ExperimentStatus
            .PASS_FINITE_CONFIGURATION_VALIDATED
            .value
        )

    return result
