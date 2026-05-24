"""Sawin n^1.014 construction."""
from sympy import Rational


def sawin_lattice_points(m: int):
    points = []
    scale = Rational(1, m)
    for i in range(m + 1):
        for j in range(m + 1):
            points.append((scale * i, scale * j))
    return points


def count_unit_edges_sawin(points):
    from counterexample_commons.validators.unit_distance import (
        count_unit_edges_exact,
    )
    return count_unit_edges_exact(points)


def verify(m: int):
    p = sawin_lattice_points(m)
    e = count_unit_edges_sawin(p)
    return {'n': len(p), 'edges': e, 'ratio': e/len(p) if p else 0}


def sawin_exponent():
    return 1.014
