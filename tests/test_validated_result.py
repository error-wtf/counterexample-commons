"""Tests for ValidatedConfigurationResult record."""
import inspect

import pytest

from counterexample_commons.validated_result import (
    ValidatedConfigurationResult,
)


class TestValidatedConfigurationResult:
    """Test the immutable validated result record."""

    def test_record_creation(self):
        """Record stores validation results correctly."""
        result = ValidatedConfigurationResult(
            name="Test Config",
            points=[("0", "0"), ("1", "0")],
            exact_edges=[(0, 1)],
            edge_count=1,
            validation_status="LOCALLY_REPRODUCED_EXACT",
            scientific_scope="Finite exact baseline",
            source_kind="TEST",
        )
        assert result.name == "Test Config"
        assert result.edge_count == 1
        assert result.validation_status == "LOCALLY_REPRODUCED_EXACT"

    def test_to_plot_data_converts_to_float(self):
        """Plot data converts rational strings to floats."""
        result = ValidatedConfigurationResult(
            name="Rational Test",
            points=[("0", "0"), ("3/5", "4/5")],
            exact_edges=[(0, 1)],
            edge_count=1,
            validation_status="LOCALLY_REPRODUCED_EXACT",
            scientific_scope="Test",
            source_kind="TEST",
        )
        points, edges = result.to_plot_data()
        assert len(points) == 2
        assert points[0] == (0.0, 0.0)
        assert abs(points[1][0] - 0.6) < 0.001  # 3/5 = 0.6
        assert abs(points[1][1] - 0.8) < 0.001  # 4/5 = 0.8
        assert edges == [(0, 1)]

    def test_record_is_immutable(self):
        """Frozen dataclass prevents modification."""
        result = ValidatedConfigurationResult(
            name="Test",
            points=[("0", "0")],
            exact_edges=[],
            edge_count=0,
            validation_status="TEST",
            scientific_scope="Test",
            source_kind="TEST",
        )
        with pytest.raises(Exception):
            result.name = "Changed"

    def test_record_contains_no_edge_finding_logic(self):
        """ValidatedConfigurationResult is only an adapter record."""
        source = inspect.getsource(ValidatedConfigurationResult)
        assert "count_unit_edges" not in source
        assert "squared_distance" not in source

    def test_table_row_and_summary_are_readable(self):
        """Record can feed the GUI table and scientific summary."""
        result = ValidatedConfigurationResult(
            name="Line Configuration",
            points=[("0", "0"), ("1", "0")],
            exact_edges=[(0, 1)],
            edge_count=1,
            validation_status="LOCALLY_REPRODUCED_EXACT",
            scientific_scope="Finite exact validation only.",
            source_kind="baseline",
        )
        assert result.to_table_row() == [
            "Line Configuration",
            2,
            1,
            "LOCALLY_REPRODUCED_EXACT",
            "Finite exact validation only.",
        ]
        summary = result.to_summary_markdown()
        assert "Configuration: Line Configuration" in summary
        assert "Exactly validated unit-distance edges: 1" in summary

    def test_state_roundtrip_preserves_validated_edges(self):
        """Gradio state roundtrip must not recompute edges."""
        result = ValidatedConfigurationResult(
            name="State Test",
            points=[("0", "0"), ("1", "0")],
            exact_edges=[(0, 1)],
            edge_count=1,
            validation_status="LOCALLY_REPRODUCED_EXACT",
            scientific_scope="Finite exact validation only.",
            source_kind="baseline",
        )
        restored = ValidatedConfigurationResult.from_state_dict(
            result.to_state_dict(),
        )
        assert restored == result
