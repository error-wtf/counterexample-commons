"""Common validated result record for exact validation workflows.

This module provides a single shared result structure used by:
- Exact Baselines Tab
- Configuration Explorer
- AI Candidate Lab
- Visualization
- Export

ONE EXACT VALIDATION PATH ONLY - No duplicate math logic.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class ValidatedConfigurationResult:
    """Immutable record of an exactly validated configuration.

    This record contains NO mathematical logic. It only stores
    results produced by the existing exact validators.
    """
    name: str
    points: Sequence[tuple[str, str]]
    exact_edges: Sequence[tuple[int, int]]
    edge_count: int
    validation_status: str
    scientific_scope: str
    source_kind: str

    @property
    def point_count(self) -> int:
        """Return the number of validated finite points."""
        return len(self.points)

    def to_table_row(self) -> list[str | int]:
        """Return a readable Exact Baselines table row."""
        return [
            self.name,
            self.point_count,
            self.edge_count,
            self.validation_status,
            self.scientific_scope,
        ]

    def to_state_dict(self) -> dict:
        """Return a plain dictionary suitable for Gradio state/JSON."""
        return {
            "name": self.name,
            "points": list(self.points),
            "exact_edges": list(self.exact_edges),
            "edge_count": self.edge_count,
            "validation_status": self.validation_status,
            "scientific_scope": self.scientific_scope,
            "source_kind": self.source_kind,
        }

    @classmethod
    def from_state_dict(cls, data: dict) -> "ValidatedConfigurationResult":
        """Rehydrate a result from Gradio state/JSON data."""
        return cls(
            name=data["name"],
            points=[tuple(point) for point in data["points"]],
            exact_edges=[tuple(edge) for edge in data["exact_edges"]],
            edge_count=int(data["edge_count"]),
            validation_status=data["validation_status"],
            scientific_scope=data["scientific_scope"],
            source_kind=data["source_kind"],
        )

    def to_summary_markdown(self) -> str:
        """Return a readable scientific summary."""
        return "\n".join([
            f"Configuration: {self.name}",
            f"Number of points: {self.point_count}",
            "Exactly validated unit-distance edges: "
            f"{self.edge_count}",
            f"Validation status: {self.validation_status}",
            "Scientific scope:",
            self.scientific_scope,
        ])

    def to_plot_data(
        self,
    ) -> tuple[list[tuple[float, float]], list[tuple[int, int]]]:
        """Convert to float coordinates for matplotlib.

        Points are converted from rational strings to floats.
        Edges remain index pairs (no approximation).
        """
        from sympy import Rational
        float_points = [
            (float(Rational(x)), float(Rational(y)))
            for x, y in self.points
        ]
        return float_points, list(self.exact_edges)
