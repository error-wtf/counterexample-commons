"""Exact unit-distance edge counting using SymPy rational arithmetic."""

from __future__ import annotations

from typing import Sequence

from sympy import Rational


def _squared_distance(
    p: tuple[Rational, Rational],
    q: tuple[Rational, Rational],
) -> Rational:
    """Return exact squared Euclidean distance between two points."""
    dx = p[0] - q[0]
    dy = p[1] - q[1]
    return dx * dx + dy * dy


def count_unit_edges_exact(
    points: Sequence[tuple[Rational, Rational]],
) -> tuple[int, list[tuple[int, int]]]:
    """Count pairs at exact Euclidean distance 1.

    Parameters
    ----------
    points : sequence of (Rational, Rational) coordinate pairs

    Returns
    -------
    count : int
        Number of unordered pairs at distance exactly 1.
    edges : list of (int, int)
        Index pairs of those edges.
    """
    n = len(points)
    edges: list[tuple[int, int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if _squared_distance(points[i], points[j]) == 1:
                edges.append((i, j))
    return len(edges), edges


def validate_line_configuration(n: int) -> dict:
    """Validate n collinear unit-spaced points.

    Expected: n-1 unit-distance edges.
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    points = [(Rational(i), Rational(0)) for i in range(n)]
    count, edges = count_unit_edges_exact(points)
    expected = n - 1
    return {
        "configuration": "line",
        "n": n,
        "expected_edges": expected,
        "actual_edges": count,
        "pass": count == expected,
        "status": "LOCALLY_REPRODUCED_EXACT",
        "edges": edges,
        "points": [(int(p[0]), int(p[1])) for p in points],
    }


def validate_grid_configuration(k: int) -> dict:
    """Validate k x k square grid.

    Expected: 2*k*(k-1) horizontal+vertical unit-distance edges.
    """
    if k < 1:
        raise ValueError("k must be >= 1")
    points = [
        (Rational(i), Rational(j))
        for i in range(k)
        for j in range(k)
    ]
    count, edges = count_unit_edges_exact(points)
    expected = 2 * k * (k - 1)
    n = k * k
    return {
        "configuration": "square_grid",
        "k": k,
        "n": n,
        "expected_edges": expected,
        "actual_edges": count,
        "pass": count == expected,
        "status": "LOCALLY_REPRODUCED_EXACT",
        "edges": edges,
    }


def validate_custom_configuration(
    coords: Sequence[tuple[str, str]],
) -> dict:
    """Validate a custom point set given as string coordinates.

    Accepts integer or rational strings (e.g. "3/5").
    No approximate decimals in exact mode.
    """
    points: list[tuple[Rational, Rational]] = []
    for i, (x_str, y_str) in enumerate(coords):
        try:
            x = Rational(x_str)
            y = Rational(y_str)
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Point {i}: cannot parse ({x_str!r}, "
                f"{y_str!r}) as rational: {e}"
            ) from e
        points.append((x, y))

    # Duplicate check
    seen = set()
    for i, p in enumerate(points):
        if p in seen:
            raise ValueError(f"Duplicate point at index {i}: {p}")
        seen.add(p)

    count, edges = count_unit_edges_exact(points)
    return {
        "configuration": "custom",
        "n": len(points),
        "actual_edges": count,
        "status": "LOCALLY_REPRODUCED_EXACT_FINITE_RESULT",
        "edges": edges,
        "points": [
            (str(p[0]), str(p[1])) for p in points
        ],
    }
