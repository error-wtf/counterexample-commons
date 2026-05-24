"""Tests for exact unit-distance validators."""

import pytest
from sympy import Rational

from counterexample_commons.validators.unit_distance import (
    count_unit_edges_exact,
    validate_line_configuration,
    validate_grid_configuration,
    validate_custom_configuration,
)


class TestCountUnitEdges:
    def test_two_points_at_distance_one(self):
        pts = [(Rational(0), Rational(0)), (Rational(1), Rational(0))]
        count, edges = count_unit_edges_exact(pts)
        assert count == 1
        assert edges == [(0, 1)]

    def test_two_points_not_at_distance_one(self):
        pts = [(Rational(0), Rational(0)), (Rational(2), Rational(0))]
        count, edges = count_unit_edges_exact(pts)
        assert count == 0
        assert edges == []

    def test_equilateral_triangle(self):
        # Not all rational — but 3/5, 4/5 right triangle works
        pts = [
            (Rational(0), Rational(0)),
            (Rational(1), Rational(0)),
            (Rational(0), Rational(1)),
        ]
        count, _ = count_unit_edges_exact(pts)
        # Only (0,0)-(1,0) and (0,0)-(0,1) are at distance 1
        # (1,0)-(0,1) is at distance sqrt(2)
        assert count == 2

    def test_single_point(self):
        pts = [(Rational(0), Rational(0))]
        count, edges = count_unit_edges_exact(pts)
        assert count == 0
        assert edges == []

    def test_empty(self):
        count, edges = count_unit_edges_exact([])
        assert count == 0
        assert edges == []


class TestLineConfiguration:
    @pytest.mark.parametrize("n,expected", [
        (1, 0),
        (2, 1),
        (5, 4),
        (16, 15),
        (100, 99),
    ])
    def test_line_edge_count(self, n, expected):
        result = validate_line_configuration(n)
        assert result["pass"] is True
        assert result["actual_edges"] == expected
        assert result["expected_edges"] == expected
        assert result["status"] == "LOCALLY_REPRODUCED_EXACT"

    def test_line_n_zero_raises(self):
        with pytest.raises(ValueError):
            validate_line_configuration(0)


class TestGridConfiguration:
    @pytest.mark.parametrize("k,expected", [
        (1, 0),
        (2, 4),
        (3, 12),
        (4, 24),
        (5, 40),
    ])
    def test_grid_edge_count(self, k, expected):
        result = validate_grid_configuration(k)
        assert result["pass"] is True
        assert result["actual_edges"] == expected
        assert result["expected_edges"] == expected
        assert result["status"] == "LOCALLY_REPRODUCED_EXACT"

    def test_grid_k_zero_raises(self):
        with pytest.raises(ValueError):
            validate_grid_configuration(0)


class TestCustomConfiguration:
    def test_four_point_square(self):
        coords = [("0", "0"), ("1", "0"), ("1", "1"), ("0", "1")]
        result = validate_custom_configuration(coords)
        assert result["actual_edges"] == 4
        assert result["n"] == 4

    def test_rational_coordinates(self):
        coords = [("0", "0"), ("3/5", "4/5")]
        result = validate_custom_configuration(coords)
        assert result["actual_edges"] == 1

    def test_duplicate_raises(self):
        coords = [("0", "0"), ("1", "0"), ("0", "0")]
        with pytest.raises(ValueError, match="Duplicate"):
            validate_custom_configuration(coords)

    def test_bad_coordinate_raises(self):
        coords = [("0", "0"), ("abc", "1")]
        with pytest.raises(ValueError, match="cannot parse"):
            validate_custom_configuration(coords)
