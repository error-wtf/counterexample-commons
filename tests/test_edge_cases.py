"""Edge case and stress tests for validators."""

import pytest
from sympy import Rational

from counterexample_commons.validators.unit_distance import (
    validate_line_configuration,
    validate_grid_configuration,
    validate_custom_configuration,
    _squared_distance,
)


class TestSquaredDistance:
    def test_same_point(self):
        p = (Rational(3, 7), Rational(11, 13))
        assert _squared_distance(p, p) == 0

    def test_unit_distance_diagonal(self):
        p = (Rational(0), Rational(0))
        q = (Rational(3, 5), Rational(4, 5))
        assert _squared_distance(p, q) == 1

    def test_negative_coordinates(self):
        p = (Rational(-1), Rational(0))
        q = (Rational(0), Rational(0))
        assert _squared_distance(p, q) == 1

    def test_large_rationals(self):
        p = (Rational(999999, 1000000), Rational(0))
        q = (Rational(0), Rational(0))
        d2 = _squared_distance(p, q)
        assert d2 != 1  # very close but not exactly 1


class TestLineEdgeCases:
    def test_line_n_1(self):
        result = validate_line_configuration(1)
        assert result["pass"] is True
        assert result["actual_edges"] == 0
        assert result["n"] == 1

    def test_line_negative_raises(self):
        with pytest.raises(ValueError):
            validate_line_configuration(-1)

    def test_line_result_has_all_keys(self):
        result = validate_line_configuration(5)
        required_keys = {
            "configuration", "n", "expected_edges",
            "actual_edges", "pass", "status", "edges", "points",
        }
        assert required_keys <= set(result.keys())


class TestGridEdgeCases:
    def test_grid_1x1(self):
        result = validate_grid_configuration(1)
        assert result["pass"] is True
        assert result["actual_edges"] == 0
        assert result["n"] == 1

    def test_grid_negative_raises(self):
        with pytest.raises(ValueError):
            validate_grid_configuration(-1)

    def test_grid_result_has_all_keys(self):
        result = validate_grid_configuration(3)
        required_keys = {
            "configuration", "k", "n", "expected_edges",
            "actual_edges", "pass", "status", "edges",
        }
        assert required_keys <= set(result.keys())


class TestCustomEdgeCases:
    def test_single_point(self):
        result = validate_custom_configuration([("0", "0")])
        assert result["n"] == 1
        assert result["actual_edges"] == 0

    def test_negative_coords(self):
        coords = [("-1", "0"), ("0", "0")]
        result = validate_custom_configuration(coords)
        assert result["actual_edges"] == 1

    def test_large_rational_fractions(self):
        coords = [("0", "0"), ("3/5", "4/5")]
        result = validate_custom_configuration(coords)
        assert result["actual_edges"] == 1

    def test_many_collinear_points(self):
        coords = [(str(i), "0") for i in range(50)]
        result = validate_custom_configuration(coords)
        assert result["n"] == 50
        assert result["actual_edges"] == 49

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            validate_custom_configuration([("", "0")])

    def test_result_points_are_strings(self):
        result = validate_custom_configuration(
            [("1/3", "2/3"), ("4/3", "2/3")]
        )
        for x, y in result["points"]:
            assert isinstance(x, str)
            assert isinstance(y, str)


class TestStress:
    def test_grid_10x10(self):
        result = validate_grid_configuration(10)
        assert result["pass"] is True
        assert result["actual_edges"] == 180
        assert result["n"] == 100

    def test_line_200(self):
        result = validate_line_configuration(200)
        assert result["pass"] is True
        assert result["actual_edges"] == 199
