"""Finite rational mesh baseline for exact unit-distance experiments.

This module provides exact finite rational-grid point sets and edge counting.
It is NOT an implementation of Sawin's n^1.014 construction.

Claim: UD-BASE-RATIONAL-MESH-001 (LOCALLY_REPRODUCED_EXACT)

The rational mesh (i/m, j/m) for 0 <= i,j <= m is a finite grid of
(m+1)^2 points. Unit edges are counted exactly using SymPy rational
arithmetic. This is an exploratory exact baseline, not an asymptotic result.
"""
from sympy import Rational

from counterexample_commons.validators.unit_distance import (
    count_unit_edges_exact,
)


def rational_mesh_points(m: int):
    """Return the (m+1)^2 rational grid points {i/m, j/m : 0<=i,j<=m}.

    This is a finite exact baseline; not Sawin's construction.
    """
    if m < 1:
        raise ValueError("m must be >= 1")
    scale = Rational(1, m)
    points = []
    for i in range(m + 1):
        for j in range(m + 1):
            points.append((scale * i, scale * j))
    return points


def count_unit_edges_rational_mesh(points):
    """Count unit edges in a rational mesh exactly."""
    return count_unit_edges_exact(points)


def verify_rational_mesh(m: int) -> dict:
    """Generate rational mesh of parameter m, count unit edges exactly.

    Returns a dict with n, edges, ratio, and explicit claim_id.
    This does NOT constitute evidence for Sawin's exponent 1.014.
    """
    p = rational_mesh_points(m)
    count, edges = count_unit_edges_rational_mesh(p)
    n = len(p)
    return {
        "claim_id": "UD-BASE-RATIONAL-MESH-001",
        "claim_status": "LOCALLY_REPRODUCED_EXACT",
        "m": m,
        "n": n,
        "unit_edges": count,
        "ratio_edges_over_n": count / n if n else 0,
        "note": (
            "Finite exact baseline only. "
            "Not evidence for Sawin exponent 1.014."
        ),
    }
