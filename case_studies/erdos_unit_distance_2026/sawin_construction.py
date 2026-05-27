"""Sawin n^1.014 construction -- NOT YET IMPLEMENTED.

Claim: UD-SAWIN-2026-001 (SOURCE_DOCUMENTED only)

Will Sawin (arXiv:2605.20579) gives an explicit construction achieving
u(n) >= n^1.014 for infinitely many n, using algebraic-number-theoretic
methods over Q(sqrt(d)) for specially chosen d.

This module is an intentional placeholder. The construction has NOT been
reproduced in this repository. Calling any function below raises
NotImplementedError.

See SAWIN_REPRODUCTION_ROADMAP.md for the planned reproduction path.
See rational_mesh_baseline.py for the finite exact baseline that IS
implemented.

DO NOT promote this module to a working implementation without:
  1. Implementing the actual algebraic construction from the paper
  2. Adding passing tests in tests/test_sawin.py
  3. Upgrading UD-SAWIN-2026-001 status in claims.py
  4. Updating CLAIM_TO_SOURCE_MATRIX.md and README.md atomically
"""


def sawin_lattice_points(m: int):
    """NOT IMPLEMENTED. See rational_mesh_baseline.py for finite baseline."""
    raise NotImplementedError(
        "Sawin's algebraic construction is not yet implemented. "
        "See SAWIN_REPRODUCTION_ROADMAP.md. "
        "For exact finite baselines use rational_mesh_baseline.py."
    )


def count_unit_edges_sawin(points):
    """NOT IMPLEMENTED."""
    raise NotImplementedError(
        "Sawin's construction is not yet implemented."
    )


def verify(m: int):
    """NOT IMPLEMENTED."""
    raise NotImplementedError(
        "Sawin's construction is not yet implemented."
    )


def sawin_exponent():
    """Return Sawin's documented exponent from the primary source.

    This is SOURCE_DOCUMENTED (arXiv:2605.20579). It has NOT been
    locally reproduced. Do not use this value as evidence of local
    reproduction.
    """
    return 1.014
