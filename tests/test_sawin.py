"""Tests for Sawin placeholder and rational mesh baseline."""

import pytest

from case_studies.erdos_unit_distance_2026.sawin_construction import (
    sawin_lattice_points,
    count_unit_edges_sawin,
    verify,
    sawin_exponent,
)
from case_studies.erdos_unit_distance_2026.rational_mesh_baseline import (
    rational_mesh_points,
    count_unit_edges_rational_mesh,
    verify_rational_mesh,
)


class TestSawinPlaceholder:
    """Sawin construction raises NotImplementedError -- not yet implemented."""

    def test_sawin_lattice_points_raises(self):
        with pytest.raises(NotImplementedError):
            sawin_lattice_points(5)

    def test_count_unit_edges_sawin_raises(self):
        with pytest.raises(NotImplementedError):
            count_unit_edges_sawin([])

    def test_verify_raises(self):
        with pytest.raises(NotImplementedError):
            verify(3)

    def test_sawin_exponent_is_source_documented_value(self):
        exp = sawin_exponent()
        assert exp == 1.014, (
            "sawin_exponent() must return 1.014 (SOURCE_DOCUMENTED only)"
        )


class TestRationalMeshBaseline:
    """Rational mesh baseline is LOCALLY_REPRODUCED_EXACT."""

    def test_m1_point_count(self):
        pts = rational_mesh_points(1)
        assert len(pts) == 4

    def test_m2_point_count(self):
        pts = rational_mesh_points(2)
        assert len(pts) == 9

    def test_m_zero_raises(self):
        with pytest.raises(ValueError):
            rational_mesh_points(0)

    def test_all_points_rational(self):
        from sympy import Rational
        pts = rational_mesh_points(3)
        for x, y in pts:
            assert isinstance(x, Rational)
            assert isinstance(y, Rational)

    def test_verify_claim_id(self):
        result = verify_rational_mesh(2)
        assert result["claim_id"] == "UD-BASE-RATIONAL-MESH-001"

    def test_verify_claim_status(self):
        result = verify_rational_mesh(2)
        assert result["claim_status"] == "LOCALLY_REPRODUCED_EXACT"

    def test_verify_n_correct(self):
        result = verify_rational_mesh(2)
        assert result["n"] == 9

    def test_verify_unit_edges_positive_for_m2(self):
        result = verify_rational_mesh(2)
        assert result["unit_edges"] > 0

    def test_verify_note_not_sawin(self):
        result = verify_rational_mesh(2)
        assert "Not evidence for Sawin" in result["note"]

    def test_unit_edges_exact_m1(self):
        pts = rational_mesh_points(1)
        count, edges = count_unit_edges_rational_mesh(pts)
        assert count == 4

    @pytest.mark.parametrize("m", [1, 2, 3, 4])
    def test_verify_returns_dict_keys(self, m):
        result = verify_rational_mesh(m)
        for key in ("claim_id", "claim_status", "m", "n", "unit_edges"):
            assert key in result
