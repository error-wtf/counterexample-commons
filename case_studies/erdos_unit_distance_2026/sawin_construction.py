"""Sawin n^1.014 announced refinement -- NOT YET IMPLEMENTED.

Claim: UD-SAWIN-2026-001 (SOURCE_DOCUMENTED only)

The OpenAI announcement reports a forthcoming Will Sawin refinement with
delta=0.014, equivalently exponent 1.014. The current official proof and
companion remarks PDFs do not provide the primary proof of that value.

This module is an intentional placeholder. The construction has NOT been
reproduced in this repository. Calling any function below raises
NotImplementedError.

See SAWIN_REPRODUCTION_ROADMAP.md for the planned reproduction path.
See rational_mesh_baseline.py for the finite exact baseline that IS
implemented.

DO NOT promote this module to a working implementation without:
  1. Locating and reviewing the primary proof of the announced refinement
  2. Implementing the actual algebraic-number-theoretic construction
  3. Adding passing tests in tests/test_sawin.py
  4. Upgrading UD-SAWIN-2026-001 status in claims.py
  5. Updating CLAIM_TO_SOURCE_MATRIX.md and README.md atomically
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
    """Return Sawin's announcement-documented exponent.

    This is SOURCE_DOCUMENTED as an OpenAI announcement of a forthcoming
    refinement. It has NOT been locally reproduced, and the current official
    proof/companion PDFs do not provide the primary proof of this value.
    """
    return 1.014
